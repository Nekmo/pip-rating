import unittest
from unittest.mock import patch, MagicMock, PropertyMock

from pip_rating.sources.pypi import Pypi


class TestPypi(unittest.TestCase):
    """Test the PyPI class."""

    @patch("pip_rating.sources.pypi.Pypi.get_package")
    @patch("pip_rating.sources.pypi.datetime")
    def test_get_cache_data(
        self, mock_datetime: MagicMock, mock_get_package: MagicMock
    ):
        """Test the get_cache_data method."""
        package_name = "package_name"
        mock_datetime.datetime.now.return_value.isoformat.return_value = "isoformat"
        mock_get_package.return_value = {"releases": "releases"}
        self.assertEqual(
            {
                "package_name": package_name,
                "updated_at": mock_datetime.datetime.now.return_value.isoformat.return_value,
                "package": mock_get_package.return_value,
            },
            Pypi(package_name).get_cache_data(),
        )

    @patch(
        "pip_rating.sources.pypi.SourceBase.is_cache_expired", new_callable=PropertyMock
    )
    def test_package(self, mock_is_cache_expired: MagicMock):
        """Test the package property."""
        with self.subTest("Test cache not expired"), patch(
            "pip_rating.sources.pypi.Pypi.get_from_cache"
        ) as mock_get_package:
            mock_is_cache_expired.return_value = False
            mock_get_package.return_value = {"package": "package"}
            source_base = Pypi("package_name")
            self.assertEqual("package", source_base.package)
        with self.subTest("Test cache expired"), patch(
            "pip_rating.sources.pypi.Pypi.save_to_cache"
        ) as mock_save_to_cache:
            mock_is_cache_expired.return_value = True
            mock_save_to_cache.return_value = {"package": "package"}
            source_base = Pypi("package_name")
            self.assertEqual("package", source_base.package)

    @patch("pip_rating.sources.pypi.Pypi.package", new_callable=PropertyMock)
    def test_uploads(self, mock_package: MagicMock):
        """Test the uploads' property."""
        release_2 = {"upload_time_iso_8601": "2"}
        release_1 = {"upload_time_iso_8601": "1"}
        mock_package.return_value = {
            "releases": {
                "1.0.0": [release_2],
                "0.9.0": [release_1],
            }
        }
        self.assertEqual([release_1, release_2], Pypi("package_name").uploads)

    @patch("pip_rating.sources.pypi.Pypi.uploads", new_callable=PropertyMock)
    def test_latest_upload(self, mock_uploads: MagicMock):
        """Test the latest_upload property."""
        mock_uploads.return_value = ["upload_1", "upload_2"]
        self.assertEqual("upload_2", Pypi("package_name").latest_upload)

    @patch("pip_rating.sources.pypi.Pypi.uploads", new_callable=PropertyMock)
    def test_first_upload(self, mock_uploads: MagicMock):
        """Test the first_upload property."""
        mock_uploads.return_value = ["upload_1", "upload_2"]
        self.assertEqual("upload_1", Pypi("package_name").first_upload)

    @patch("pip_rating.sources.pypi.Pypi.latest_upload", new_callable=PropertyMock)
    def test_latest_upload_iso_dt(self, mock_latest_upload: MagicMock):
        """Test the latest_upload_iso_dt property."""
        with self.subTest("Test latest_upload is not None"):
            mock_latest_upload.return_value = {"upload_time_iso_8601": "iso_dt"}
            self.assertEqual("iso_dt", Pypi("package_name").latest_upload_iso_dt)
        with self.subTest("Test latest_upload is None"):
            mock_latest_upload.return_value = None
            self.assertIsNone(Pypi("package_name").latest_upload_iso_dt)

    @patch("pip_rating.sources.pypi.Pypi.first_upload", new_callable=PropertyMock)
    def test_first_upload_iso_dt(self, mock_first_upload: MagicMock):
        """Test the first_upload_iso_dt property."""
        with self.subTest("Test first_upload is not None"):
            mock_first_upload.return_value = {"upload_time_iso_8601": "iso_dt"}
            self.assertEqual("iso_dt", Pypi("package_name").first_upload_iso_dt)
        with self.subTest("Test first_upload is None"):
            mock_first_upload.return_value = None
            self.assertIsNone(Pypi("package_name").first_upload_iso_dt)

    @patch("pip_rating.sources.pypi.requests")
    def test_get_package(self, mock_requests: MagicMock):
        """Test the get_package method."""
        package_name = "package_name"
        self.assertEqual(
            mock_requests.get.return_value.__enter__.return_value.json.return_value,
            Pypi(package_name).get_package(),
        )
        mock_requests.get.return_value.__enter__.return_value.raise_for_status.assert_called_once()
        mock_requests.get.assert_called_once_with(
            f"https://pypi.org/pypi/{package_name}/json"
        )
