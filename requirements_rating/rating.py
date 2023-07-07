import datetime
import json
import os
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, Optional, Union, List, Tuple

from platformdirs import user_cache_dir
from requests import __version__

from requirements_rating.sources.sourcerank import SourceRankBreakdown

if TYPE_CHECKING:
    from requirements_rating.packages import Package


RATING_CACHE_DIR = Path(user_cache_dir()) / "requirements-rating" / "rating"
MAX_CACHE_AGE = datetime.timedelta(days=7)


class PackageRatingParams(TypedDict):
    sourcerank_breakdown: SourceRankBreakdown


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
        return self.current_score

    def __repr__(self) -> str:
        return f"<Max current: {self.current_score} max: {self.max_score}>"


class PackageBreakdown:
    def __init__(self, breakdown_key: str, score: Optional[Union[int, Max]] = None):
        self.breakdown_key = breakdown_key
        self._score = score

    def get_breakdown_value(self, package_rating: "PackageRating") -> Union[int, bool]:
        value = package_rating.params
        for subkey in self.breakdown_key.split("."):
            value = value[subkey]
        return value

    def get_score(self, package_rating: "PackageRating") -> ScoreBase:
        value = self.get_breakdown_value(package_rating)
        if value and self._score:
            return ScoreValue(self._score)
        if not value and self._score:
            return ScoreValue(0)
        if isinstance(value, bool):
            raise ValueError("Cannot calculate score for boolean value")
        return ScoreValue(value)


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
]


class PackageRating:
    def __init__(self, package: "Package", params: Optional[PackageRatingParams] = None):
        self.package = package
        if not params and self.is_cache_expired:
            params = self.get_params_from_package()
            self.save_to_cache()
        elif not params:
            params = self.get_params_from_cache()
        self.params = params

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
            (package, package.rating.rating_score)
            for package in self.package.get_descendant_packages()
        ]

    @cached_property
    def rating_score(self):
        scores = dict(self.breakdown_scores).values()
        value = ScoreValue(0)
        for score in scores:
            value += score
        return int(value)

    @cached_property
    def global_rating_score(self):
        return min([self.rating_score] + list(dict(self.descendant_rating_scores).values()), default=0)
