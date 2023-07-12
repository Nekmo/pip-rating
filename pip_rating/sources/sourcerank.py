import datetime
from functools import cached_property
from typing import Iterator, Tuple, TypedDict

import requests
from bs4 import BeautifulSoup

from pip_rating.sources.base import SourceBase

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


class SourceRank(SourceBase):
    source_name = "sourcerank"

    def get_cache_data(self) -> dict:
        return {
            "package_name": self.package_name,
            "updated_at": datetime.datetime.now().isoformat(),
            "breakdown": dict(self.get_breakdown()),
        }

    @cached_property
    def breakdown(self) -> SourceRankBreakdown:
        if not self.is_cache_expired:
            cache = self.get_from_cache()
        else:
            cache = self.save_to_cache()
        return cache["breakdown"]

    def get_breakdown(self) -> Iterator[Tuple[str, int]]:
        with requests.get(SOURCERANK_URL.format(package_name=self.package_name)) as response:
            response.raise_for_status()
            content = response.content
        soup = BeautifulSoup(content, "html.parser")
        for item in soup.find_all("li", "list-group-item"):
            stripped_strings = list(item.stripped_strings)
            if stripped_strings[1] in BREAKDOWN_MAPPING:
                yield BREAKDOWN_MAPPING[stripped_strings[1]], int(stripped_strings[0])
