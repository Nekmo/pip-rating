import datetime
import json
import os
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, Optional, Union, List, Tuple, Dict

from platformdirs import user_cache_dir
from requests import __version__
from pip_rating._compat import cache
from pip_rating.sources.audit import Vulnerability

from pip_rating.sources.sourcerank import SourceRankBreakdown

if TYPE_CHECKING:
    from pip_rating.packages import Package


RATING_CACHE_DIR = Path(user_cache_dir()) / "pip-rating" / "rating"
MAX_CACHE_AGE = datetime.timedelta(days=7)


class PypiPackage(TypedDict):
    latest_upload_iso_dt: Optional[str]
    first_upload_iso_dt: Optional[str]


class SourcecodePage(TypedDict):
    package_in_readme: Optional[bool]


class PackageRatingParams(TypedDict):
    sourcerank_breakdown: SourceRankBreakdown
    pypi_package: PypiPackage
    sourcecode_page: SourcecodePage


class PackageRatingCache(TypedDict):
    package_name: str
    updated_at: str
    schema_version: str
    params: PackageRatingParams


class ScoreBase:
    def __add__(self, other: "ScoreBase"):
        raise NotImplementedError

    def __int__(self) -> int:
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return repr(self)


class ScoreValue(ScoreBase):
    def __init__(self, value: int):
        self.value = value

    def __add__(self, other: "ScoreBase") -> "ScoreBase":
        if isinstance(other, ScoreValue):
            return ScoreValue(int(self) + int(other))
        elif isinstance(other, Max):
            return other + self

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        return f"{self.value}"


class Max(ScoreBase):
    def __init__(self, max_score: int, current_score: int = 0):
        self.max_score = max_score
        self.current_score = current_score

    def __add__(self, other: ScoreBase):
        if isinstance(other, ScoreValue):
            score = self.current_score + int(other)
            self.current_score = max(self.max_score, score)
        if isinstance(other, Max) and other.max_score < self.max_score:
            other.current_score = self.current_score
            return other
        return self

    def __int__(self) -> int:
        return self.max_score

    def __str__(self):
        return f"Max({self.max_score})"

    def __repr__(self) -> str:
        return f"<Max current: {self.current_score} max: {self.max_score}>"


class BreakdownBase:
    breakdown_key: str

    def get_score(self, package_rating: "PackageRating") -> ScoreBase:
        raise NotImplementedError

    def get_breakdown_value(self, package_rating: "PackageRating") -> Union[int, bool, str]:
        value = package_rating.params
        for subkey in self.breakdown_key.split("."):
            value = value[subkey]
        return value


class PackageBreakdown(BreakdownBase):
    def __init__(self, breakdown_key: str, score: Optional[Union[int, Max]] = None):
        self.breakdown_key = breakdown_key
        self._score = score

    def get_score(self, package_rating: "PackageRating") -> ScoreBase:
        value = self.get_breakdown_value(package_rating)
        if value and self._score:
            return ScoreValue(self._score)
        if not value and self._score:
            return ScoreValue(0)
        if isinstance(value, bool):
            raise ValueError("Cannot calculate score for boolean value")
        return ScoreValue(value)


class DateBreakdown(BreakdownBase):

    def __init__(self, breakdown_key: str, scores: Dict[datetime.timedelta, int], default: int):
        self.breakdown_key = breakdown_key
        self.scores = scores
        self.default = default

    def get_score(self, package_rating: "PackageRating") -> ScoreBase:
        iso_dt = self.get_breakdown_value(package_rating)
        if not iso_dt:
            return ScoreValue(0)
        dt = datetime.datetime.fromisoformat(iso_dt)
        dt_delta = datetime.datetime.now(datetime.timezone.utc) - dt
        for delta, score in self.scores.items():
            if dt_delta < delta:
                return ScoreValue(score)
        return ScoreValue(self.default)


class NullBoolBreakdown(BreakdownBase):
    def __init__(self, breakdown_key: str, scores: Dict[bool, ScoreBase]):
        self.breakdown_key = breakdown_key
        self.scores = scores

    def get_score(self, package_rating: "PackageRating") -> ScoreBase:
        value = self.get_breakdown_value(package_rating)
        return self.scores[value]


BREAKDOWN_SCORES = [
    PackageBreakdown("sourcerank_breakdown.basic_info_present", 1),
    PackageBreakdown("sourcerank_breakdown.source_repository_present", 1),
    PackageBreakdown("sourcerank_breakdown.readme_present", 1),
    PackageBreakdown("sourcerank_breakdown.license_present", 1),
    PackageBreakdown("sourcerank_breakdown.has_multiple_versions", 3),
    PackageBreakdown("sourcerank_breakdown.dependent_projects"),
    PackageBreakdown("sourcerank_breakdown.dependent_repositories"),
    PackageBreakdown("sourcerank_breakdown.stars"),
    PackageBreakdown("sourcerank_breakdown.contributors"),
    DateBreakdown(
        "pypi_package.latest_upload_iso_dt",
        {
            datetime.timedelta(days=30 * 4): 4,
            datetime.timedelta(days=30 * 6): 3,
            datetime.timedelta(days=365): 2,
            datetime.timedelta(days=365 + (30 * 6)): 1,
            datetime.timedelta(days=365 * 3): 0,
            datetime.timedelta(days=365 * 4): -2,
        },
        default=-4
    ),
    DateBreakdown(
        "pypi_package.first_upload_iso_dt",
        {
            datetime.timedelta(days=15): Max(0),
            datetime.timedelta(days=30): -3,
            datetime.timedelta(days=60): -2,
            datetime.timedelta(days=90): -1,
            datetime.timedelta(days=180): 0,
            datetime.timedelta(days=360): 1,
            datetime.timedelta(days=360 * 2): 2,
            datetime.timedelta(days=360 * 4): 3,
        },
        default=4
    ),
    NullBoolBreakdown(
        "sourcecode_page.package_in_readme",
        {True: ScoreValue(1), False: Max(0), None: ScoreValue(0)}
    ),
]


class PackageRatingJson(TypedDict):
    rating_score: int
    global_rating_score: int
    vulnerabilities: List[Vulnerability]
    params: PackageRatingParams


class PackageRating:
    def __init__(self, package: "Package", params: Optional[PackageRatingParams] = None):
        self.package = package
        if not params and self.is_cache_expired:
            params = self.get_params_from_package()
            self.save_to_cache()
        elif not params:
            params = self.get_params_from_cache()
        self.params: PackageRatingParams = params

    @property
    def is_cache_expired(self) -> bool:
        return not self.cache_path.exists() or \
            self.cache_path.stat().st_mtime < (datetime.datetime.now() - MAX_CACHE_AGE).timestamp()

    @property
    def cache_path(self) -> Path:
        return RATING_CACHE_DIR / f"{self.package.name}.json"

    def get_from_cache(self) -> Optional[PackageRatingCache]:
        with open(self.cache_path) as file:
            data = json.load(file)
        if data["schema_version"] != __version__:
            return None
        return data

    def save_to_cache(self) -> PackageRatingCache:
        cache = {
            "package_name": self.package.name,
            "updated_at": datetime.datetime.now().isoformat(),
            "schema_version": __version__,
            "params": self.get_params_from_package(),
        }
        os.makedirs(str(self.cache_path.parent), exist_ok=True)
        with open(str(self.cache_path), "w") as file:
            json.dump(cache, file)
        return cache

    def get_params_from_cache(self) -> PackageRatingParams:
        cache = self.get_from_cache()
        if cache is None:
            cache = self.save_to_cache()
        return cache["params"]

    def get_params_from_package(self) -> PackageRatingParams:
        return {
            "sourcerank_breakdown": self.package.sourcerank.breakdown,
            "pypi_package": {
                "latest_upload_iso_dt": self.package.pypi.latest_upload_iso_dt,
                "first_upload_iso_dt": self.package.pypi.first_upload_iso_dt,
            },
            "sourcecode_page": {
                "package_in_readme": self.package.sourcecode_page.package_in_readme,
            }
        }

    @cached_property
    def breakdown_scores(self) -> List[Tuple[str, ScoreBase]]:
        return [
            (breakdown.breakdown_key, breakdown.get_score(self))
            for breakdown in BREAKDOWN_SCORES
        ]

    @cached_property
    def descendant_rating_scores(self) -> List[Tuple["Package", int]]:
        return [
            (package, package.rating.get_rating_score(self.package))
            for package in self.package.get_descendant_packages()
        ]

    @cached_property
    def rating_score(self):
        scores = dict(self.breakdown_scores).values()
        value = ScoreValue(0)
        for score in scores:
            value += score
        return int(value)

    @cache
    def get_vulnerabilities(self, from_package: Optional["Package"] = None) -> List["Vulnerability"]:
        node = None
        if from_package is not None:
            node = self.package.get_node_from_parent(from_package)
        elif from_package is None:
            node = self.package.first_node
        # get_audit requires a node, so we only call it if we have one and this is used
        # instead of the package's own rating score
        if node is not None:
            return self.package.get_audit(node).vulnerabilities
        return []

    def get_rating_score(self, from_package: Optional["Package"] = None) -> int:
        self.package.dependencies.results.analizing_package(self.package.name, self.package.dependencies.total_size)
        if len(self.get_vulnerabilities(from_package)):
            return 0
        return self.rating_score

    def get_global_rating_score(self, from_package: Optional["Optional"] = None) -> int:
        return min(
            [self.get_rating_score(from_package)] + list(dict(self.descendant_rating_scores).values()),
            default=0
        )

    def as_json(self, from_package: Optional["Package"] = None) -> PackageRatingJson:
        return {
            "rating_score": self.get_rating_score(from_package),
            "global_rating_score": self.get_global_rating_score(from_package),
            "vulnerabilities": self.get_vulnerabilities(from_package),
            "params": self.params,
        }
