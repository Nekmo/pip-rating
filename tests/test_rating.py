import json
import time
import unittest
from unittest.mock import patch, MagicMock, Mock, PropertyMock, mock_open

from pip_rating import __version__
from pip_rating.rating import (
    ScoreBase,
    ScoreValue,
    Max,
    PackageRating,
    RATING_CACHE_DIR,
)


class TestScoreBase(unittest.TestCase):
    """Tests for the ScoreBase class."""

    def test_add(self):
        """Test the __add__ method of ScoreBase."""
        score_base = ScoreBase()
        with self.assertRaises(NotImplementedError):
            score_base + score_base

    def test_int(self):
        """Test the __int__ method of ScoreBase."""
        score_base = ScoreBase()
        with self.assertRaises(NotImplementedError):
            int(score_base)

    def test_repr(self):
        """Test the __repr__ method of ScoreBase."""
        score_base = ScoreBase()
        with self.assertRaises(NotImplementedError):
            repr(score_base)

    def test_str(self):
        """Test the __str__ method of ScoreBase."""
        score_base = ScoreBase()
        with self.assertRaises(NotImplementedError):
            str(score_base)


class TestScoreValue(unittest.TestCase):
    """Tests for the ScoreValue class."""

    def test_init(self):
        """Test the __init__ method of ScoreValue."""
        score_value = ScoreValue(1)
        self.assertEqual(1, score_value.value)

    def test_add(self):
        """Test the __add__ method of ScoreValue."""
        score_value_1 = ScoreValue(1)
        score_value_2 = ScoreValue(2)
        self.assertEqual(3, int(score_value_1 + score_value_2))

    def test_int(self):
        """Test the __int__ method of ScoreValue."""
        score_value = ScoreValue(1)
        self.assertEqual(1, int(score_value))

    def test_repr(self):
        """Test the __repr__ method of ScoreValue."""
        score_value = ScoreValue(1)
        self.assertEqual("1", repr(score_value))


class TestMax(unittest.TestCase):
    """Tests for the Max class."""

    def test_init(self):
        """Test the __init__ method of Max."""
        max_score = Max(0, 1)
        self.assertEqual(0, max_score.max_score)
        self.assertEqual(1, max_score.current_score)

    def test_add(self):
        """Test the __add__ method of Max."""
        with self.subTest("Add ScoreValue below max_score"):
            max_score = Max(10)
            score_value = ScoreValue(1)
            self.assertEqual(1, int(max_score + score_value))
        with self.subTest("Add ScoreValue above max_score"):
            max_score = Max(0)
            score_value = ScoreValue(1)
            self.assertEqual(0, int(max_score + score_value))
        with self.subTest("Add Max below max_score"):
            max_score = Max(10, 5)
            other_max_score = Max(0, 3)
            new_max_score = max_score + other_max_score
            self.assertEqual(0, new_max_score.max_score)
            self.assertEqual(8, new_max_score.current_score)
            self.assertEqual(0, int(new_max_score))
        with self.subTest("Add Max above max_score"):
            max_score = Max(0, 3)
            other_max_score = Max(10, 5)
            new_max_score = max_score + other_max_score
            self.assertEqual(0, new_max_score.max_score)
            self.assertEqual(8, new_max_score.current_score)
            self.assertEqual(0, int(new_max_score))

    def test_int(self):
        """Test the __int__ method of Max."""
        max_score = Max(0, 1)
        self.assertEqual(0, int(max_score))

    def test_str(self):
        """Test the __str__ method of Max."""
        max_score = Max(0)
        self.assertEqual("Max(0)", str(max_score))

    def test_repr(self):
        """Test the __repr__ method of Max."""
        max_score = Max(0, 1)
        self.assertEqual("<Max current: 1 max: 0>", repr(max_score))


class TestPackageRating(unittest.TestCase):
    """Tests for the PackageRating class."""

    @patch("pip_rating.rating.PackageRating.get_params_from_cache")
    @patch("pip_rating.rating.PackageRating.save_to_cache")
    @patch("pip_rating.rating.PackageRating.get_params_from_package")
    @patch(
        "pip_rating.rating.PackageRating.is_cache_expired", new_callable=PropertyMock
    )
    def test_init(
        self,
        mock_is_cache_expired: MagicMock,
        mock_get_params_from_package: MagicMock,
        mock_save_to_cache: MagicMock,
        mock_get_params_from_cache: MagicMock,
    ):
        """Test the __init__ method of PackageRating."""
        mock_package = Mock()
        with self.subTest("No params & cache expired"):
            mock_is_cache_expired.return_value = True
            package_rating = PackageRating(mock_package)
            mock_save_to_cache.assert_called_once()
            mock_get_params_from_package.assert_called_once()
            self.assertEqual(
                mock_get_params_from_package.return_value, package_rating.params
            )
            mock_get_params_from_cache.assert_not_called()
        mock_save_to_cache.reset_mock()
        mock_get_params_from_package.reset_mock()
        mock_get_params_from_cache.reset_mock()
        with self.subTest("No params & cache not expired"):
            mock_is_cache_expired.return_value = False
            package_rating = PackageRating(mock_package)
            mock_save_to_cache.assert_not_called()
            mock_get_params_from_package.assert_not_called()
            mock_get_params_from_cache.assert_called_once()
            self.assertEqual(
                mock_get_params_from_cache.return_value, package_rating.params
            )

    @patch("pip_rating.rating.PackageRating.cache_path", new_callable=PropertyMock)
    @patch("pip_rating.rating.PackageRating.__init__")
    def test_is_cache_expired(self, mock_init: MagicMock, mock_cache_path: MagicMock):
        """Test the is_cache_expired property of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        with self.subTest("Cache path not exists"):
            mock_cache_path.return_value.exists.return_value = False
            package_rating = PackageRating(mock_package)
            self.assertTrue(package_rating.is_cache_expired)
        with self.subTest("Cache path exists & cache expired"):
            mock_cache_path.return_value.exists.return_value = True
            mock_cache_path.return_value.stat.return_value.st_mtime = 0
            package_rating = PackageRating(mock_package)
            self.assertTrue(package_rating.is_cache_expired)
        with self.subTest("Cache path exists & cache not expired"):
            mock_cache_path.return_value.exists.return_value = True
            mock_cache_path.return_value.stat.return_value.st_mtime = time.time()
            package_rating = PackageRating(mock_package)
            self.assertFalse(package_rating.is_cache_expired)

    @patch("pip_rating.rating.PackageRating.__init__")
    def test_cache_path(self, mock_init: MagicMock):
        """Test the cache_path property of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        mock_package.name = "name"
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        self.assertEqual(RATING_CACHE_DIR / "name.json", package_rating.cache_path)

    @patch("pip_rating.rating.PackageRating.__init__")
    def test_get_from_cache(self, mock_init: MagicMock):
        """Test the get_from_cache method of PackageRating."""
        json_data = {"schema_version": "other"}
        mock_init.return_value = None
        mock_package = Mock()
        with self.subTest("Unsupported schema_version"), patch(
            "builtins.open", mock_open(read_data=json.dumps(json_data))
        ):
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            self.assertIsNone(package_rating.get_from_cache())
        json_data = {"schema_version": __version__}
        with self.subTest("Supported schema_version"), patch(
            "builtins.open", mock_open(read_data=json.dumps(json_data))
        ):
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            self.assertEqual(json_data, package_rating.get_from_cache())

    @patch("pip_rating.rating.datetime")
    @patch("pip_rating.rating.json")
    @patch("builtins.open")
    @patch("pip_rating.rating.os")
    @patch("pip_rating.rating.PackageRating.cache_path", new_callable=PropertyMock)
    @patch("pip_rating.rating.PackageRating.get_params_from_package")
    @patch("pip_rating.rating.PackageRating.__init__")
    def test_save_to_cache(
        self,
        mock_init: MagicMock,
        mock_get_params_from_package: MagicMock,
        mock_cache_path: MagicMock,
        mock_os: MagicMock,
        mock_open_: MagicMock,
        mock_json: MagicMock,
        mock_datetime: MagicMock,
    ):
        """Test the save_to_cache method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        mock_package.name = "name"
        mock_get_params_from_package.return_value = {"test": "test"}
        mock_cache_path.return_value.parent = "parent"
        mock_cache_path.return_value.__str__.return_value = "cache_path"
        mock_os.makedirs.return_value = None
        mock_open_.return_value = MagicMock()
        mock_datetime.datetime.now.return_value.isoformat.return_value = "now"
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        package_rating.save_to_cache()
        mock_os.makedirs.assert_called_once_with(
            mock_cache_path.return_value.parent, exist_ok=True
        )
        mock_open_.assert_called_once_with("cache_path", "w")
        mock_json.dump.assert_called_once_with(
            {
                "package_name": mock_package.name,
                "updated_at": "now",
                "schema_version": __version__,
                "params": mock_get_params_from_package.return_value,
            },
            mock_open_.return_value.__enter__.return_value,
        )
