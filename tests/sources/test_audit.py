import unittest
from pathlib import Path
from typing import cast
from unittest.mock import Mock, patch, MagicMock, PropertyMock

from packaging.version import Version
from pip_audit._service import VulnerabilityResult
from pip_audit._service.interface import VulnerabilityID

from pip_rating.sources.audit import vulns_to_dict, Audit


class TestVulnsToDict(unittest.TestCase):
    """Test the vulns_to_dict function."""

    def test_vulns_to_dict(self):
        """Test the vulns_to_dict function."""
        mock_vulnerability = Mock()
        mock_vulnerability.fix_versions = ["1.0.0"]
        mock_vulnerability.aliases = ["CVE-1234"]
        vulnerabilities = [
            {
                "id": mock_vulnerability.id,
                "description": mock_vulnerability.description,
                "fix_versions": [
                    str(version) for version in mock_vulnerability.fix_versions
                ],
                "aliases": mock_vulnerability.aliases,
                "published_iso_dt": mock_vulnerability.published.isoformat(),
            }
        ]
        self.assertEqual(vulnerabilities, vulns_to_dict([mock_vulnerability]))


class TestAudit(unittest.TestCase):
    """Test the Audit class."""

    @patch("pip_rating.sources.audit.SourceBase.__init__")
    def test_init(self, mock_init: MagicMock):
        """Test the __init__ method."""
        package_name = "package_name"
        version = "version"
        audit = Audit(package_name, version)
        mock_init.assert_called_once_with(package_name)
        self.assertEqual(version, audit.version)

    @patch("pip_rating.sources.audit.Audit.cache_dir", new_callable=PropertyMock)
    def test_cache_file(self, mock_cache_dir: MagicMock):
        """Test the cache_file property."""
        package_name = "package_name"
        mock_cache_dir.return_value = Path("cache_dir")
        audit = Audit(package_name, "version")
        self.assertEqual(
            f"cache_dir/{package_name}_c692273deb2772da307ffe37041fef77bf4baa97.json",
            str(audit.cache_file),
        )

    @patch("pip_rating.sources.audit.Audit.is_cache_expired", new_callable=PropertyMock)
    @patch("pip_rating.sources.audit.Audit.__init__")
    def test_vulnerabilities(
        self, mock_init: MagicMock, mock_is_cache_expired: MagicMock
    ):
        """Test the vulnerabilities' property."""
        mock_init.return_value = None
        with self.subTest("Test is_cache_expired is False"), patch(
            "pip_rating.sources.audit.Audit.get_from_cache"
        ) as mock_get_from_cache:
            mock_is_cache_expired.return_value = False
            mock_get_from_cache.return_value = {"vulnerabilities": "vulnerabilities"}
            audit = Audit("package_name", "version")
            self.assertEqual("vulnerabilities", audit.vulnerabilities)
        with self.subTest("Test is_cache_expired is True"), patch(
            "pip_rating.sources.audit.Audit.save_to_cache"
        ) as mock_save_to_cache:
            mock_is_cache_expired.return_value = True
            mock_save_to_cache.return_value = {"vulnerabilities": "vulnerabilities"}
            audit = Audit("package_name", "version")
            self.assertEqual("vulnerabilities", audit.vulnerabilities)

    @patch("pip_rating.sources.audit.Audit.vulnerabilities")
    def test_is_vulnerable(self, mock_vulnerabilities: MagicMock):
        """Test the is_vulnerable property."""
        mock_vulnerabilities.return_value = ["vulnerability"]
        audit = Audit("package_name", "version")
        self.assertTrue(audit.is_vulnerable)

    @patch("pip_rating.sources.audit.datetime")
    @patch("pip_rating.sources.audit.OsvService")
    @patch("pip_rating.sources.audit.PyPIService")
    def test_get_cache_data(
        self,
        mock_pypi_service: MagicMock,
        mock_osv_service: MagicMock,
        mock_datetime: MagicMock,
    ):
        """Test the get_cache_data method."""
        mock_datetime.datetime.now.return_value.isoformat.return_value = "isoformat"
        vulnerability_result = VulnerabilityResult(
            id=cast(VulnerabilityID, "id"),
            description="description",
            fix_versions=[Version("1.0.0")],
            aliases={"CVE-1234"},
        )
        vulnerability_result2 = VulnerabilityResult(
            id=cast(VulnerabilityID, "id2"),
            description="description",
            fix_versions=[Version("2.0.0")],
            aliases={"CVE-12345"},
        )
        mock_pypi_service.return_value.query.return_value = [
            None,
            [vulnerability_result],
        ]
        mock_osv_service.return_value.query.return_value = [
            None,
            [vulnerability_result, vulnerability_result2],
        ]
        audit = Audit("package_name", "1.0.0")
        self.assertEqual(
            {
                "package_name": "package_name",
                "updated_at": mock_datetime.datetime.now.return_value.isoformat.return_value,
                "version": "1.0.0",
                "vulnerabilities": [
                    {
                        "aliases": ["CVE-1234"],
                        "description": "description",
                        "fix_versions": ["1.0.0"],
                        "id": "id",
                        "published_iso_dt": None,
                    },
                    {
                        "aliases": ["CVE-12345"],
                        "description": "description",
                        "fix_versions": ["2.0.0"],
                        "id": "id2",
                        "published_iso_dt": None,
                    },
                ],
            },
            audit.get_cache_data(),
        )
