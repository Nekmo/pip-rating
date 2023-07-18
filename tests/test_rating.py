import unittest

from pip_rating.rating import ScoreBase, ScoreValue, Max


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
