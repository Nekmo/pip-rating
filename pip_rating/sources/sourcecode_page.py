import base64
import datetime
import re
from functools import cached_property
from typing import TYPE_CHECKING, TypedDict, Optional

import requests

from pip_rating.sources.base import SourceBase


if TYPE_CHECKING:
    from pip_rating.packages import Package


GITHUB_REPOSITORY_URL = "https://github.com/([^/]+)/([^/]+).*"
GITHUB_README_URL = "https://api.github.com/repos/{owner}/{repo}/readme"
PIP_INSTALL_PATTERNS = [
    re.compile(r"pip3? +install +(?:-U +|--upgrade +|)(\S+)"),
    re.compile(r"poetry +add +(\S+)"),
    re.compile(r"pipenv +install +(\S+)"),
]


def get_github_readme(owner: str, repo: str) -> str:
    try:
        with requests.get(GITHUB_README_URL.format(owner=owner, repo=repo)) as response:
            response.raise_for_status()
            content = response.json().get("content", "")
            return base64.b64decode(content).decode("utf-8") if content else ""
    except requests.RequestException:
        return ""


class Sourcecode(TypedDict):
    package_in_readme: Optional[bool]
    readme_content: str


class SourcecodeCacheDict(TypedDict):
    package_name: str
    updated_at: str
    source: str
    sourcecode: Sourcecode


def search_in_readme(content: str, package_name: str) -> Optional[bool]:
    """Search for patterns in readme. If found the pattern, check if the package name is package_name.
    If the package name found is package_name, return True, else continues searching. If after all
    patterns are searched and no package name is found, return False. If any pattern matches,
    return None.
    """
    package_in_readme = None
    for pattern in PIP_INSTALL_PATTERNS:
        results = pattern.findall(content)
        for result in results:
            package_in_readme = result.lower().replace("_", "-") == package_name.lower().replace("_", "-")
            if package_in_readme:
                return True
    return package_in_readme


class SourcecodePage(SourceBase):
    source_name = "sourcecode_page"

    def __init__(self, package: "Package"):
        self.package = package
        super().__init__(package.name)

    def get_cache_data(self) -> SourcecodeCacheDict:
        project_urls = self.package.pypi.package["info"].get("project_urls", {})
        content = ""
        for url in project_urls.values():
            github_match = re.match(GITHUB_REPOSITORY_URL, url)
            if github_match:
                content = get_github_readme(github_match.group(1), github_match.group(2))
                break
        package_in_readme = search_in_readme(content, self.package.name)
        return {
            "package_name": self.package_name,
            "updated_at": datetime.datetime.now().isoformat(),
            "source": "github",
            "sourcecode": {
                "package_in_readme": package_in_readme,
                "readme_content": content,
            },
        }

    @cached_property
    def package_in_readme(self) -> Optional[bool]:
        if not self.is_cache_expired:
            cache = self.get_from_cache()
        else:
            cache = self.save_to_cache()
        return cache["sourcecode"]["package_in_readme"]
