import datetime
from functools import cached_property
from hashlib import sha1
from pathlib import Path
from typing import List, TypedDict, Optional

from pip_audit._service.pypi import PyPIService
from pip_audit._service.osv import OsvService
from pip_audit._service.interface import ResolvedDependency, VulnerabilityResult
from packaging.version import Version

from pip_rating.sources.base import SourceBase


class Vulnerability(TypedDict):
    id: str
    description: str
    fix_versions: List[str]
    aliases: List[str]
    published_iso_dt: Optional[str]


def vulns_to_dict(vulnerabilities: List[VulnerabilityResult]) -> List[Vulnerability]:
    return [
        {
            "id": vulnerability.id,
            "description": vulnerability.description,
            "fix_versions": [str(version) for version in vulnerability.fix_versions],
            "aliases": list(vulnerability.aliases),
            "published_iso_dt": vulnerability.published.isoformat() if vulnerability.published else None,
        }
        for vulnerability in vulnerabilities
    ]


class Audit(SourceBase):
    """Audit source"""

    source_name = "audit"

    def __init__(self, package_name: str, version: str):
        self.version = version
        super().__init__(package_name)

    @property
    def cache_file(self) -> Path:
        return self.cache_dir / f"{self.package_name}_{sha1(self.version.encode('utf-8')).hexdigest()}.json"

    @cached_property
    def vulnerabilities(self) -> List[Vulnerability]:
        if not self.is_cache_expired:
            cache = self.get_from_cache()
        else:
            cache = self.save_to_cache()
        return cache["vulnerabilities"]

    @cached_property
    def is_vulnerable(self) -> bool:
        return bool(self.vulnerabilities)

    def get_cache_data(self) -> dict:
        dependency = ResolvedDependency(self.package_name, Version(self.version))
        vulnerabilities = vulns_to_dict(PyPIService().query(dependency)[1])
        vulnerability_ids = [vuln["id"] for vuln in vulnerabilities]
        osv_vulnerabilities = vulns_to_dict(OsvService().query(dependency)[1])
        for vuln in osv_vulnerabilities:
            if vuln["id"] not in vulnerability_ids:
                vulnerabilities.append(vuln)
        return {
            "package_name": self.package_name,
            "version": self.version,
            "updated_at": datetime.datetime.now().isoformat(),
            "vulnerabilities": vulnerabilities,
        }
