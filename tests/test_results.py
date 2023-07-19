import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, Mock

from pip_rating.rating import ScoreValue
from pip_rating.results import (
    colorize_score,
    colorize_rating,
    colorize_rating_package,
    add_tree_node,
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
