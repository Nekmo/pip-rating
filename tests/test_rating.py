import datetime
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
    BreakdownBase,
    PackageBreakdown,
    DateBreakdown,
    NullBoolBreakdown,
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
        with self.subTest("Test adding ScoreValue"):
            score_value_1 = ScoreValue(1)
            score_value_2 = ScoreValue(2)
            self.assertEqual(3, int(score_value_1 + score_value_2))
        with self.subTest("Test adding Max"):
            score_value = ScoreValue(1)
            max_score = Max(2)
            self.assertEqual(max_score, score_value + max_score)

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


class TestBreakdownBase(unittest.TestCase):
    """Tests for the BreakdownBase class."""

    def test_get_score(self):
        """Test the get_score method of BreakdownBase."""
        mock_package_rating = Mock()
        breakdown_base = BreakdownBase()
        with self.assertRaises(NotImplementedError):
            breakdown_base.get_score(mock_package_rating)

    def test_get_breakdown_value(self):
        """Test the get_breakdown_value method of BreakdownBase."""
        mock_package_rating = Mock()
        mock_package_rating.params = {"key": {"subkey": {"value": "test_value"}}}
        breakdown_base = BreakdownBase()
        breakdown_base.breakdown_key = "key.subkey.value"
        breakdown_value = breakdown_base.get_breakdown_value(mock_package_rating)
        self.assertEqual("test_value", breakdown_value)


class TestPackageBreakdown(unittest.TestCase):
    """Tests for the PackageBreakdown class."""

    def test_init(self):
        """Test the __init__ method of PackageBreakdown."""
        package_breakdown = PackageBreakdown("test_key", 10)
        self.assertEqual("test_key", package_breakdown.breakdown_key)
        self.assertEqual(10, package_breakdown._score)

    def test_get_score(self):
        """Test the get_score method of PackageBreakdown."""
        mock_package_rating = Mock()
        with self.subTest("Test with value True and score"):
            mock_package_rating.params = {"key": {"subkey": {"value": True}}}
            package_breakdown = PackageBreakdown("key.subkey.value", 10)
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(10).value, score.value)
        with self.subTest("Test with value True and score"):
            mock_package_rating.params = {"key": {"subkey": {"value": True}}}
            package_breakdown = PackageBreakdown("key.subkey.value", 1)
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(1).value, score.value)
        with self.subTest("Test with value False and score"):
            mock_package_rating.params = {"key": {"subkey": {"value": False}}}
            package_breakdown = PackageBreakdown("key.subkey.value", 10)
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(0).value, score.value)
        with self.subTest("Test with value True and no score"):
            mock_package_rating.params = {"key": {"subkey": {"value": True}}}
            package_breakdown = PackageBreakdown("key.subkey.value")
            with self.assertRaises(ValueError):
                package_breakdown.get_score(mock_package_rating)
        with self.subTest("Test with integer value and no score"):
            mock_package_rating.params = {"key": {"subkey": {"value": 5}}}
            package_breakdown = PackageBreakdown("key.subkey.value")
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(5).value, score.value)


class TestDateBreakdown(unittest.TestCase):
    """Tests for the DateBreakdown class."""

    def test_init(self):
        """Test the __init__ method of DateBreakdown."""
        breakdown_key = "test_key"
        scores = {datetime.timedelta(days=1): 1}
        default = 10
        date_breakdown = DateBreakdown(breakdown_key, scores, default)
        self.assertEqual(breakdown_key, date_breakdown.breakdown_key)
        self.assertEqual(scores, date_breakdown.scores)
        self.assertEqual(default, date_breakdown.default)

    def test_get_score(self):
        """Test the get_score method of DateBreakdown."""
        with self.subTest("Test without date"):
            mock_package_rating = Mock()
            mock_package_rating.params = {"key": {"subkey": {"value": None}}}
            package_breakdown = DateBreakdown("key.subkey.value", {}, 1)
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(0).value, score.value)
        with self.subTest("Test with date below scores"):
            mock_package_rating = Mock()
            mock_package_rating.params = {
                "key": {
                    "subkey": {
                        "value": datetime.datetime.now(
                            datetime.timezone.utc
                        ).isoformat()
                    }
                }
            }
            scores = {datetime.timedelta(days=1): 1}
            package_breakdown = DateBreakdown("key.subkey.value", scores, 2)
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(1).value, score.value)
        with self.subTest("Test with date above scores"):
            mock_package_rating = Mock()
            value = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
                days=2
            )
            mock_package_rating.params = {
                "key": {"subkey": {"value": value.isoformat()}}
            }
            scores = {datetime.timedelta(days=1): 1}
            package_breakdown = DateBreakdown("key.subkey.value", scores, 2)
            score = package_breakdown.get_score(mock_package_rating)
            self.assertEqual(ScoreValue(2).value, score.value)


class TestNullBoolBreakdown(unittest.TestCase):
    """Tests for the NullBoolBreakdown class."""

    def test_init(self):
        """Test the __init__ method of NullBoolBreakdown."""
        breakdown_key = "test_key"
        scores = {True: ScoreValue(1)}
        null_bool_breakdown = NullBoolBreakdown(breakdown_key, scores)
        self.assertEqual(breakdown_key, null_bool_breakdown.breakdown_key)
        self.assertEqual(scores, null_bool_breakdown.scores)

    def test_get_score(self):
        """Tests the get_score method of NullBoolBreakdown."""
        mock_package_rating = Mock()
        mock_package_rating.params = {"key": {"subkey": {"value": True}}}
        score_value = ScoreValue(1)
        null_bool_breakdown = NullBoolBreakdown("key.subkey.value", {True: score_value})
        score = null_bool_breakdown.get_score(mock_package_rating)
        self.assertEqual(score_value, score)


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

    @patch("pip_rating.rating.PackageRating.save_to_cache")
    @patch("pip_rating.rating.PackageRating.get_from_cache")
    @patch("pip_rating.rating.PackageRating.get_from_cache")
    def test_get_params_from_cache(
        self,
        mock_init: MagicMock,
        mock_get_from_cache: MagicMock,
        mock_save_to_cache: MagicMock,
    ):
        """Test the get_params_from_cache method of PackageRating."""
        mock_init.return_value = None
        with self.subTest("Cache expired"):
            mock_params = Mock()
            mock_get_from_cache.return_value = None
            mock_save_to_cache.return_value = {"params": mock_params}
            package_rating = PackageRating(Mock())
            self.assertEqual(mock_params, package_rating.get_params_from_cache())
        with self.subTest("Cache not expired"):
            mock_params = Mock()
            mock_get_from_cache.return_value = {"params": mock_params}
            package_rating = PackageRating(Mock())
            self.assertEqual(mock_params, package_rating.get_params_from_cache())

    @patch("pip_rating.rating.PackageRating.__init__")
    def test_get_params_from_package(self, mock_init: MagicMock):
        """Test the get_params_from_package method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        self.assertEqual(
            {
                "sourcerank_breakdown": mock_package.sourcerank.breakdown,
                "pypi_package": {
                    "latest_upload_iso_dt": mock_package.pypi.latest_upload_iso_dt,
                    "first_upload_iso_dt": mock_package.pypi.first_upload_iso_dt,
                },
                "sourcecode_page": {
                    "package_in_readme": mock_package.sourcecode_page.package_in_readme,
                },
            },
            package_rating.get_params_from_package(),
        )

    @patch("pip_rating.rating.PackageRating.__init__")
    def test_breakdown_scores(self, mock_init: MagicMock):
        """Test the breakdown_scores method of PackageRating."""
        mock_init.return_value = None
        mock_breakdown = Mock()
        with patch("pip_rating.rating.BREAKDOWN_SCORES", [mock_breakdown]):
            mock_package = Mock()
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            breakdown_scores = package_rating.breakdown_scores
            self.assertEqual(
                [(mock_breakdown.breakdown_key, mock_breakdown.get_score.return_value)],
                breakdown_scores,
            )
            mock_breakdown.get_score.assert_called_once_with(package_rating)

    @patch("pip_rating.rating.PackageRating.__init__")
    def test_descendant_rating_scores(self, mock_init: MagicMock):
        """Test the descendant_rating_scores method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        mock_descendant = MagicMock()
        mock_package.get_descendant_packages.return_value = [mock_descendant]
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        descendant_rating_scores = package_rating.descendant_rating_scores
        self.assertEqual(
            [(mock_descendant, mock_descendant.rating.get_rating_score.return_value)],
            descendant_rating_scores,
        )
        mock_package.get_descendant_packages.assert_called_once_with()
        mock_descendant.rating.get_rating_score.assert_called_once_with(mock_package)

    @patch(
        "pip_rating.rating.PackageRating.breakdown_scores", new_callable=PropertyMock
    )
    @patch("pip_rating.rating.PackageRating.__init__")
    def test_rating_score(self, mock_init: MagicMock, mock_breakdown_scores: MagicMock):
        """Test the rating_score method of PackageRating."""
        mock_init.return_value = None
        mock_breakdown_scores.return_value = [("key", ScoreValue(1))]
        mock_package = Mock()
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        rating_score = package_rating.rating_score
        self.assertEqual(1, rating_score)

    @patch("pip_rating.rating.PackageRating.__init__")
    def test_get_vulnerabilities(self, mock_init: MagicMock):
        """Test the get_vulnerabilities method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        with self.subTest("from_package is None"):
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            vulnerabilities = package_rating.get_vulnerabilities()
            mock_package.get_node_from_parent.assert_not_called()
            self.assertEqual(
                mock_package.get_audit.return_value.vulnerabilities, vulnerabilities
            )
            mock_package.get_audit.assert_called_once_with(mock_package.first_node)
        mock_package.reset_mock()
        with self.subTest("from_package is not None"):
            mock_from_package = Mock()
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            vulnerabilities = package_rating.get_vulnerabilities(mock_from_package)
            mock_package.get_node_from_parent.assert_called_once_with(mock_from_package)
            self.assertEqual(
                mock_package.get_audit.return_value.vulnerabilities, vulnerabilities
            )
            mock_package.get_audit.assert_called_once_with(
                mock_package.get_node_from_parent.return_value
            )
        mock_package.reset_mock()
        with self.subTest("from_package is not None and node is None"):
            mock_from_package = Mock()
            mock_package.get_node_from_parent.return_value = None
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            vulnerabilities = package_rating.get_vulnerabilities(mock_from_package)
            mock_package.get_node_from_parent.assert_called_once_with(mock_from_package)
            self.assertEqual([], vulnerabilities)
            mock_package.get_audit.assert_not_called()

    @patch("pip_rating.rating.PackageRating.get_vulnerabilities")
    @patch("pip_rating.rating.PackageRating.rating_score", new_callable=PropertyMock)
    @patch("pip_rating.rating.PackageRating.__init__")
    def test_get_rating_score(
        self,
        mock_init: MagicMock,
        mock_rating_score: MagicMock,
        mock_get_vulnerabilities: MagicMock,
    ):
        """Test the get_rating_score method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        mock_from_package = Mock()
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        with self.subTest("No vulnerabilities"):
            mock_get_vulnerabilities.return_value = []
            rating_score = package_rating.get_rating_score(mock_from_package)
            self.assertEqual(mock_rating_score.return_value, rating_score)
            mock_package.dependencies.results.analizing_package.assert_called_once_with(
                mock_package.name,
                mock_package.dependencies.total_size,
            )
            mock_get_vulnerabilities.assert_called_once_with(mock_from_package)
        mock_package.reset_mock()
        mock_get_vulnerabilities.reset_mock()
        with self.subTest("With vulnerabilities"):
            mock_get_vulnerabilities.return_value = [Mock()]
            rating_score = package_rating.get_rating_score(mock_from_package)
            self.assertEqual(0, rating_score)
            mock_package.dependencies.results.analizing_package.assert_called_once_with(
                mock_package.name,
                mock_package.dependencies.total_size,
            )
            mock_get_vulnerabilities.assert_called_once_with(mock_from_package)

    @patch(
        "pip_rating.rating.PackageRating.descendant_rating_scores",
        new_callable=PropertyMock,
    )
    @patch("pip_rating.rating.PackageRating.get_rating_score")
    @patch("pip_rating.rating.PackageRating.__init__")
    def test_get_global_rating_score(
        self,
        mock_init: MagicMock,
        mock_get_rating_score: MagicMock,
        mock_descendant_rating_scores: MagicMock,
    ):
        """Test the get_global_rating_score method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        mock_from_package = Mock()
        with self.subTest("The package has the minimum score"):
            mock_get_rating_score.return_value = 1
            mock_descendant_rating_scores.return_value = [("key", 2)]
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            global_rating_score = package_rating.get_global_rating_score(
                mock_from_package
            )
            self.assertEqual(1, global_rating_score)
        with self.subTest("The dependency has the minimum score"):
            mock_get_rating_score.return_value = 2
            mock_descendant_rating_scores.return_value = [("key", 1)]
            package_rating = PackageRating(mock_package)
            package_rating.package = mock_package
            global_rating_score = package_rating.get_global_rating_score(
                mock_from_package
            )
            self.assertEqual(1, global_rating_score)

    @patch("pip_rating.rating.PackageRating.get_vulnerabilities")
    @patch("pip_rating.rating.PackageRating.get_global_rating_score")
    @patch("pip_rating.rating.PackageRating.get_rating_score")
    @patch("pip_rating.rating.PackageRating.__init__")
    def test_as_json(
        self,
        mock_init: MagicMock,
        mock_get_rating_score: MagicMock,
        mock_get_global_rating_score: MagicMock,
        mock_get_vulnerabilities: MagicMock,
    ):
        """Test the as_json method of PackageRating."""
        mock_init.return_value = None
        mock_package = Mock()
        mock_from_package = Mock()
        package_rating = PackageRating(mock_package)
        package_rating.package = mock_package
        package_rating.params = Mock()
        package_rating_json = package_rating.as_json(mock_from_package)
        self.assertEqual(
            {
                "rating_score": mock_get_rating_score.return_value,
                "global_rating_score": mock_get_global_rating_score.return_value,
                "vulnerabilities": mock_get_vulnerabilities.return_value,
                "params": package_rating.params,
            },
            package_rating_json,
        )
        mock_get_rating_score.assert_called_once_with(mock_from_package)
        mock_get_global_rating_score.assert_called_once_with(mock_from_package)
        mock_get_vulnerabilities.assert_called_once_with(mock_from_package)
