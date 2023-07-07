import datetime
from functools import cached_property
from typing import TypedDict, Optional

import requests

from requirements_rating.sources.base import SourceBase

URL = "https://pypi.org/pypi/{package_name}/json"


class PyPackageInfo(TypedDict):
    author: str
    author_email: str
    bugtrack_url: str
    classifiers: list[str]
    description: str
    description_content_type: str
    docs_url: str
    download_url: str
    downloads: dict[str, int]
    home_page: str
    keywords: str
    license: str
    maintainer: str
    maintainer_email: str
    name: str
    package_url: str
    platform: Optional[str]
    project_url: str
    project_urls: dict[str, str]
    release_url: str
    requires_dist: list[str]
    requires_python: Optional[str]
    summary: str
    version: str
    yanked: bool
    yanked_reason: Optional[str]


class PypiPackageRelease(TypedDict):
    comment_text: str
    digests: dict[str, str]
    downloads: int
    filename: str
    has_sig: bool
    md5_digest: str
    packagetype: str
    python_version: str
    requires_python: Optional[str]
    size: int
    upload_time: str
    upload_time_iso_8601: str
    url: str
    yanked: bool
    yanked_reason: Optional[str]


class PypiPackage(TypedDict):
    info: PyPackageInfo
    last_serial: int
    releases: dict[str, list[PypiPackageRelease]]


class PypiCacheDict(TypedDict):
    package_name: str
    updated_at: str
    package: PypiPackage


class Pypi(SourceBase):

    def get_cache_data(self) -> dict:
        return {
            "package_name": self.package_name,
            "updated_at": datetime.datetime.now().isoformat(),
            "package": dict(self.get_package()),
        }

    @cached_property
    def package(self) -> PypiPackage:
        if not self.is_cache_expired:
            sourcerank_cache = self.get_from_cache()
        else:
            sourcerank_cache = self.save_to_cache()
        return sourcerank_cache["package"]

    def get_package(self) -> PypiPackage:
        with requests.get(URL.format(package_name=self.package_name)) as response:
            response.raise_for_status()
            return response.json()
