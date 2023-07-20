import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock, mock_open

from pip_rating.sources.base import SourceBase


class TestSourceBase(unittest.TestCase):
    """Test the SourceBase class."""

    def test_init(self):
        """Test the __init__ method."""
        package_name = "package_name"
        source_base = SourceBase(package_name)
        self.assertEqual(package_name, source_base.package_name)

    @patch("pip_rating.sources.base.user_cache_dir")
    def test_cache_dir(self, mock_user_cache_dir: MagicMock):
        """Test the cache_dir property."""
        mock_user_cache_dir.return_value = "user_cache_dir"
        package_name = "package_name"
        source_base = SourceBase(package_name)
        source_base.source_name = "source_name"
        self.assertEqual(
            f"{source_base.cache_dir}",
            f"{mock_user_cache_dir.return_value}/pip-rating/{source_base.source_name}",
        )

    @patch("pip_rating.sources.base.SourceBase.cache_dir", new_callable=PropertyMock)
    def test_cache_file(self, mock_cache_dir: MagicMock):
        """Test the cache_file property."""
        mock_cache_dir.return_value = Path("cache_dir")
        package_name = "package_name"
        source_base = SourceBase(package_name)
        self.assertEqual(
            f"{source_base.cache_file}",
            f"{mock_cache_dir.return_value}/{package_name}.json",
        )

    @patch("pip_rating.sources.base.SourceBase.cache_file", new_callable=PropertyMock)
    def test_is_cache_expired(self, mock_cache_file: MagicMock):
        """Test the is_cache_expired property."""
        with self.subTest("Test cache file does not exist"):
            mock_cache_file.return_value.exists.return_value = False
            source_base = SourceBase("package_name")
            self.assertTrue(source_base.is_cache_expired)
        with self.subTest("Test cache file exists and is expired"):
            mock_cache_file.return_value.exists.return_value = True
            mock_cache_file.return_value.stat.return_value.st_mtime = 0
            source_base = SourceBase("package_name")
            self.assertTrue(source_base.is_cache_expired)

    @patch("builtins.open", mock_open(read_data='{"key": "value"}'))
    @patch("pip_rating.sources.base.SourceBase.cache_file")
    def test_get_from_cache(self, _: MagicMock):
        """Test the get_from_cache method."""
        source_base = SourceBase("package_name")
        self.assertEqual(source_base.get_from_cache(), {"key": "value"})

    def test_get_cache_data(self):
        """Test the get_cache_data method."""
        source_base = SourceBase("package_name")
        with self.assertRaises(NotImplementedError):
            source_base.get_cache_data()

    @patch("pip_rating.sources.base.json.dump")
    @patch("builtins.open")
    @patch("pip_rating.sources.base.os.makedirs")
    @patch("pip_rating.sources.base.SourceBase.cache_file")
    @patch("pip_rating.sources.base.SourceBase.get_cache_data")
    def test_save_to_cache(
        self,
        mock_get_cache_data: MagicMock,
        _: MagicMock,
        mock_makedirs: MagicMock,
        mock_open_: MagicMock,
        mock_json_dump: MagicMock,
    ):
        """Test the save_to_cache method."""
        mock_get_cache_data.return_value = {"key": "value"}
        source_base = SourceBase("package_name")
        self.assertEqual(mock_get_cache_data.return_value, source_base.save_to_cache())
        mock_makedirs.assert_called_once_with(
            str(source_base.cache_file.parent), exist_ok=True
        )
        mock_open_.assert_called_once_with(source_base.cache_file, "w")
        mock_json_dump.assert_called_once_with(
            {"key": "value"}, mock_open_.return_value.__enter__.return_value
        )
