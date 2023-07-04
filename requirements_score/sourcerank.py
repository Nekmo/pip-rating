import os
from typing import Iterator, Tuple

import requests
from bs4 import BeautifulSoup
from platformdirs import user_cache_dir

SOURCERANK_CACHE_DIR = os.path.join(user_cache_dir(), "requirements-score", "sourcerank")
SOURCERANK_URL = "https://libraries.io/pypi/{package_name}/sourcerank"
SECTIONS = {
    "Basic info present?": "basic-info-present",
    "Source repository present?": "source-repository-present",
    "Readme present?": "readme-present",
    "License present?": "license-present",
    "Has multiple versions?": "has-multiple-versions",
    "Follows SemVer?": "follows-semver",
    "Recent release?": "recent-release",
    "Not brand new?": "not-brand-new",
    "1.0.0 or greater?": "1.0.0-or-greater",
    "Dependent Packages": "dependent-projects",
    "Dependent Repositories": "dependent-repositories",
    "Stars": "stars",
    "Contributors": "contributors",
    "Libraries.io subscribers": "libraries.io-subscribers",
    "Total": "total",
}


class SourceRank:
    def __init__(self, package_name: str):
        self.package_name = package_name

    def get_breakdown(self) -> Iterator[Tuple[str, int]]:
        with requests.get(SOURCERANK_URL.format(package_name=self.package_name)) as response:
            response.raise_for_status()
            content = response.content
        soup = BeautifulSoup(content, "html.parser")
        for item in soup.find_all("li", "list-group-item"):
            stripped_strings = list(item.stripped_strings)
            if stripped_strings[1] in SECTIONS:
                yield SECTIONS[stripped_strings[1]], int(stripped_strings[0])
