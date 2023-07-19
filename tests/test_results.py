import unittest
from unittest import mock
from unittest.mock import patch, MagicMock, Mock

from pip_rating.rating import ScoreValue
from pip_rating.results import (
    colorize_score,
    colorize_rating,
    colorize_rating_package,
    add_tree_node,
    RatingLetter,
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
