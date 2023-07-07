import datetime
import json
import os
from functools import cached_property
from pathlib import Path
from typing import Iterator, Tuple, TypedDict

import requests
from bs4 import BeautifulSoup
from platformdirs import user_cache_dir

SOURCERANK_CACHE_DIR = Path(user_cache_dir()) / "requirements-rating" / "sourcerank"
SOURCERANK_URL = "https://libraries.io/pypi/{package_name}/sourcerank"
BREAKDOWN_MAPPING = {
    "Basic info present?": "basic_info_present",
    "Source repository present?": "source_repository_present",
    "Readme present?": "readme_present",
    "License present?": "license_present",
    "Has multiple versions?": "has_multiple_versions",
    "Follows SemVer?": "follows_semver",
    "Recent release?": "recent_release",
    "Not brand new?": "not_brand_new",
    "1.0.0 or greater?": "is_1_or_greater",
    "Dependent Packages": "dependent_projects",
    "Dependent Repositories": "dependent_repositories",
    "Stars": "stars",
    "Contributors": "contributors",
    "Libraries.io subscribers": "librariesio_subscribers",
    "Total": "total",
}
MAX_CACHE_AGE = datetime.timedelta(days=7)


class SourceRankBreakdown(TypedDict):
    basic_info_present: int
    source_repository_present: int
    readme_present: int
    license_present: int
    has_multiple_versions: int
    follows_semver: int
    recent_release: int
    not_brand_new: int
    is_1_or_greater: int
    dependent_projects: int
    dependent_repositories: int
    stars: int
    contributors: int
    librariesio_subscribers: int
    total: int


class SourceRankCacheDict(TypedDict):
    package_name: str
    updated_at: str
    breakdown: SourceRankBreakdown


class SourceRank:
    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def cache_file(self) -> Path:
        return SOURCERANK_CACHE_DIR / f"{self.package_name}.json"

    @cached_property
    def is_cache_expired(self) -> bool:
        return not self.cache_file.exists() or \
            self.cache_file.stat().st_mtime < (datetime.datetime.now() - MAX_CACHE_AGE).timestamp()

    def get_from_cache(self) -> SourceRankCacheDict:
        with open(self.cache_file) as file:
            return json.load(file)

    def save_to_cache(self) -> SourceRankCacheDict:
        sourcerank_cache = {
            "package_name": self.package_name,
            "updated_at": datetime.datetime.now().isoformat(),
            "breakdown": dict(self.get_breakdown()),
        }
        os.makedirs(str(self.cache_file.parent), exist_ok=True)
        with open(self.cache_file, "w") as file:
            json.dump(sourcerank_cache, file)
        return sourcerank_cache

    @cached_property
    def breakdown(self) -> SourceRankBreakdown:
        if not self.is_cache_expired:
            sourcerank_cache = self.get_from_cache()
        else:
            sourcerank_cache = self.save_to_cache()
        return sourcerank_cache["breakdown"]

    def get_breakdown(self) -> Iterator[Tuple[str, int]]:
        with requests.get(SOURCERANK_URL.format(package_name=self.package_name)) as response:
            response.raise_for_status()
            content = response.content
        soup = BeautifulSoup(content, "html.parser")
        for item in soup.find_all("li", "list-group-item"):
            stripped_strings = list(item.stripped_strings)
            if stripped_strings[1] in BREAKDOWN_MAPPING:
                yield BREAKDOWN_MAPPING[stripped_strings[1]], int(stripped_strings[0])
