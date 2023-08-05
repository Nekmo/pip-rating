"""
Tests for the results module.

This tests can be improved. These tests do not verify the returned outputs.
"""
import unittest
from io import TextIOWrapper
from unittest import mock
from unittest.mock import patch, MagicMock, Mock

from rich.console import Console
from rich.status import Status
from rich.tree import Tree

from pip_rating import __version__
from pip_rating.rating import ScoreValue
from pip_rating.results import (
    colorize_score,
    colorize_rating,
    colorize_rating_package,
    add_tree_node,
    RatingLetter,
    Results,
)


class TestColorizeScore(unittest.TestCase):
    """Tests for the colorize_score function."""

    def test_colorize_score(self):
        """Test the colorize_score function."""
        with self.subTest("Test below 0"):
            self.assertIn("red", colorize_score(ScoreValue(-1)))
        with self.subTest("Test above 0"):
            self.assertIn("green", colorize_score(ScoreValue(1)))
        with self.subTest("Test is 0"):
            self.assertIn("bright_black", colorize_score(ScoreValue(0)))


class TestColorizeRating(unittest.TestCase):
    """Tests for the colorize_rating function."""

    def test_colorize_rating(self):
        """Test the colorize_rating function."""
        with self.subTest("Test below 0"):
            self.assertEqual("F", colorize_rating(ScoreValue(-1)).letter)
        with self.subTest("Test above 0"):
            self.assertIn("E", colorize_rating(ScoreValue(5)).letter)


class TestColorizeRatingPackage(unittest.TestCase):
    """Tests for the colorize_rating_package function."""

    @patch("pip_rating.results.colorize_rating")
    def test_colorize_rating_package(self, mock_colorize_rating: MagicMock):
        """Test the colorize_rating_package function."""
        mock_package = Mock()
        mock_parent_package = Mock()
        with self.subTest("Test with different rating"):
            mock_letter = MagicMock()
            mock_letter.__str__.return_value = "A"
            mock_letter.__gt__.return_value = True
            mock_colorize_rating.side_effect = [mock_letter, "C"]
            self.assertEqual(
                "A -> C", colorize_rating_package(mock_package, mock_parent_package)
            )
        with self.subTest("Test with equal rating"):
            mock_colorize_rating.side_effect = ["E", "E"]
            self.assertIn(
                "E", colorize_rating_package(mock_package, mock_parent_package)
            )


class TestAddTreeNode(unittest.TestCase):
    """Tests for the add_tree_node function."""

    @patch("pip_rating.results.colorize_rating_package")
    def test_add_tree_node(self, mock_colorize_rating_package: MagicMock):
        """Test the add_tree_node function."""
        mock_colorize_rating_package.side_effect = ["A", "B"]
        mock_subpackage = Mock()
        mock_subpackage.get_node_from_parent.return_value.children = []
        mock_subpackage.name = "subpackage"
        mock_dependencies = Mock()
        mock_dependencies.packages = {"subpackage": mock_subpackage}
        mock_tree = Mock()
        mock_package = Mock()
        mock_subnode = Mock()
        mock_subnode.name = "subpackage"
        mock_missing_subnode = Mock()
        mock_missing_subnode.name = "missing_subpackage"
        mock_package.get_node_from_parent.return_value.children = [mock_subnode]
        add_tree_node(mock_dependencies, mock_tree, mock_package)
        mock_tree.add.assert_called_once()
        mock_tree.add.return_value.add.assert_called_once()
        mock_colorize_rating_package.assert_has_calls(
            [
                mock.call(mock_package),
                mock.call(mock_subpackage, mock_package),
            ]
        )


class TestRatingLetter(unittest.TestCase):
    """Tests for the RatingLetter class."""

    def test_init(self):
        """Test the __init__ method of RatingLetter."""
        letter = "A"
        score = 25
        color = "green"
        rating_letter = RatingLetter(letter, score, color)
        self.assertEqual(letter, rating_letter.letter)
        self.assertEqual(score, rating_letter.score)
        self.assertEqual(color, rating_letter.color)

    def test_lt(self):
        """Test the __lt__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertLess(rating_letter, RatingLetter("S", 30, "cyan"))

    def test_gt(self):
        """Test the __gt__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertGreater(rating_letter, RatingLetter("C", 15, "gold"))

    def test_le(self):
        """Test the __le__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertLessEqual(rating_letter, RatingLetter("A", 25, "green"))
        self.assertLessEqual(rating_letter, RatingLetter("S", 30, "cyan"))

    def test_ge(self):
        """Test the __ge__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertGreaterEqual(rating_letter, RatingLetter("A", 25, "green"))
        self.assertGreaterEqual(rating_letter, RatingLetter("C", 15, "gold"))

    def test_eq(self):
        """Test the __eq__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertEqual(rating_letter, RatingLetter("A", 25, "green"))

    def test_ne(self):
        """Test the __ne__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertNotEqual(rating_letter, RatingLetter("S", 30, "cyan"))

    def test_str(self):
        """Test the __str__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertEqual("[bold green]A[/bold green]", str(rating_letter))

    def test_repr(self):
        """Test the __repr__ method of RatingLetter."""
        rating_letter = RatingLetter("A", 25, "green")
        self.assertEqual("<RatingLetter A>", repr(rating_letter))


class TestResults(unittest.TestCase):
    """Tests for the Results class."""

    def test_init(self):
        """Test the __init__ method of Results."""
        with self.subTest("Test without file output"):
            test_results = Results()
            self.assertIsInstance(test_results.progress_console, Console)
            self.assertIsInstance(test_results.results_console, Console)
            self.assertTrue(test_results.progress_console.stderr)
            self.assertIsNone(test_results._status)
            self.assertIsNone(test_results.progress)
            self.assertIsNone(test_results.task)
        with self.subTest("Test with file output"):
            to_file = "output.txt"
            test_results = Results(to_file=to_file)
            self.assertIsInstance(test_results.results_console.file, TextIOWrapper)
            self.assertEqual(to_file, test_results.results_console.file.name)

    def test_status(self):
        """Test the status property of Results."""
        test_results = Results()
        status = test_results.status
        self.assertEqual(status, test_results._status)
        self.assertIsInstance(status, Status)

    def test_processing_package(self):
        """Test the processing_package method of Results."""
        test_results = Results()
        test_results._status = Mock()
        test_results.processing_package("test_package")
        test_results._status.update.assert_called_once()

    @patch("pip_rating.results.Progress")
    def test_analyzing_package(self, mock_progress: MagicMock):
        """Test the analyzing_package method of Results."""
        total = 100
        test_results = Results()
        test_results._status = Mock()
        test_results.analizing_package("test_package", total)
        mock_progress.assert_called_once()
        mock_progress.return_value.add_task.assert_called_once()
        self.assertEqual(
            mock_progress.return_value.add_task.return_value, test_results.task
        )
        mock_progress.return_value.start.assert_called_once()
        mock_progress.return_value.update.assert_called_once()

    def test_get_global_rating_score(self):
        """Test the get_global_rating_score method of Results."""
        mock_dependencies = Mock()
        test_results = Results()
        test_results.progress = Mock()
        global_rating_score = test_results.get_global_rating_score(mock_dependencies)
        self.assertEqual(
            mock_dependencies.get_global_rating_score.return_value, global_rating_score
        )
        mock_dependencies.get_global_rating_score.assert_called_once()
        test_results.progress.update.assert_called_once()
        test_results.progress.stop.assert_called_once()

    def test_show_results(self):
        """Test the show_results method of Results."""
        mock_dependencies = Mock()
        test_results = Results()
        with self.subTest("Invalid format_name"), self.assertRaises(ValueError):
            test_results.show_results(mock_dependencies, "invalid")
        with self.subTest("Test text format"), patch(
            "pip_rating.results.Results.show_packages_results"
        ) as mock_show_packages_results:
            test_results.show_results(mock_dependencies, "text")
            mock_show_packages_results.assert_called_once_with(mock_dependencies)
        with self.subTest("Test tree format"), patch(
            "pip_rating.results.Results.show_tree_results"
        ) as mock_show_tree_results:
            test_results.show_results(mock_dependencies, "tree")
            mock_show_tree_results.assert_called_once_with(mock_dependencies)
        with self.subTest("Test json format"), patch(
            "pip_rating.results.Results.show_json_results"
        ) as mock_show_json_results:
            test_results.show_results(mock_dependencies, "json")
            mock_show_json_results.assert_called_once_with(mock_dependencies)
        with self.subTest("Test only-rating format"), patch(
            "pip_rating.results.Results.show_only_rating_results"
        ) as mock_show_only_rating_results:
            test_results.show_results(mock_dependencies, "only-rating")
            mock_show_only_rating_results.assert_called_once_with(mock_dependencies)

    def test_show_packages_results(self):
        """Test the show_packages_results method of Results."""
        mock_dependencies = MagicMock()
        mock_package = MagicMock()
        mock_package.rating.get_global_rating_score.return_value = 0
        mock_package.rating.rating_score = 15
        mock_package.rating.breakdown_scores = [("key", 5)]
        mock_package.rating.get_vulnerabilities.return_value = [{"id": "CVE-2020-0001"}]
        mock_package.name = "name"
        mock_dependencies.packages = {"name": mock_package}
        mock_dependencies.req_file = ["name"]
        test_results = Results()
        test_results.results_console = Mock()
        test_results.show_packages_results(mock_dependencies)
        self.assertEqual(7, test_results.results_console.print.call_count)

    def test_show_tree_results(self):
        """Test the show_tree_results method of Results."""
        mock_dependencies = MagicMock()
        mock_package = MagicMock()
        mock_package.name = "name"
        mock_dependencies.packages = {"name": mock_package, "missing": Mock()}
        mock_dependencies.req_file = ["name"]
        test_results = Results()
        test_results.results_console = Mock()
        test_results.show_tree_results(mock_dependencies)
        tree = test_results.results_console.print.mock_calls[0].args[0]
        self.assertEqual(1, len(tree.children))
        self.assertIsInstance(tree.children[0], Tree)

    @patch("pip_rating.results.datetime")
    def test_get_json_results(self, mock_datetime: MagicMock):
        """Test the get_json_results method of Results."""
        mock_dependencies = MagicMock()
        mock_package = MagicMock()
        mock_package.name = "name"
        mock_dependencies.packages = {"name": mock_package}
        mock_dependencies.req_file = ["name"]
        test_results = Results()
        json_results = test_results.get_json_results(mock_dependencies)
        self.assertEqual(
            {
                "requirements": mock_dependencies.req_file,
                "updated_at": mock_datetime.datetime.now.return_value.isoformat.return_value,
                "schema_version": __version__,
                "global_rating_letter": "F",
                "global_rating_score": mock_dependencies.get_global_rating_score.return_value,
                "packages": [mock_package.as_json.return_value],
            },
            json_results,
        )

    @patch("pip_rating.results.json")
    @patch("builtins.print")
    @patch("pip_rating.results.Results.get_json_results")
    def test_show_json_results(
        self,
        mock_get_json_results: MagicMock,
        mock_print: MagicMock,
        mock_json: MagicMock,
    ):
        """Test the show_json_results method of Results."""
        mock_dependencies = MagicMock()
        with self.subTest("Test output to console"):
            test_results = Results()
            test_results.show_json_results(mock_dependencies)
            mock_get_json_results.assert_called_once_with(mock_dependencies)
            mock_json.dumps.assert_called_once_with(
                mock_get_json_results.return_value, indent=4, sort_keys=False
            )
            mock_print.assert_called_once_with(mock_json.dumps.return_value)
        mock_get_json_results.reset_mock()
        mock_print.reset_mock()
        with self.subTest("Test output to file"), patch("builtins.open") as mock_open:
            to_file = "output.json"
            test_results = Results(to_file=to_file)
            test_results.show_json_results(mock_dependencies)
            mock_get_json_results.assert_called_once_with(mock_dependencies)
            mock_json.dump.assert_called_once_with(
                mock_get_json_results.return_value,
                mock_open.return_value.__enter__.return_value,
                indent=4,
                sort_keys=False,
            )
            mock_open.assert_has_calls(
                [
                    mock.call(to_file, "w"),  # Call in __init__
                    mock.call(to_file, "w"),  # Call in show_json_results
                ],
                any_order=True,
            )
            mock_print.assert_not_called()

    @patch("pip_rating.results.Results.get_global_rating_score")
    @patch("pip_rating.results.Console")
    def test_show_only_rating_results(
        self, mock_console: MagicMock, mock_get_global_rating_score: MagicMock
    ):
        """Test the show_only_rating_results method of Results."""
        mock_dependencies = MagicMock()
        test_results = Results()
        test_results.show_only_rating_results(mock_dependencies)
        mock_get_global_rating_score.assert_called_once_with(mock_dependencies)
        mock_console.return_value.print.assert_called_once()
