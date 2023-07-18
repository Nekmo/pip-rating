import unittest

from pip_rating.exceptions import (
    RequirementsRatingError,
    RequirementsRatingMissingReqFile,
)


class TestRequirementsRatingError(unittest.TestCase):
    """Tests for the RequirementsRatingError exception."""

    def test_init(self):
        """Test the __init__ method of RequirementsRatingError."""
        with self.subTest("Test with no arguments"):
            exception = RequirementsRatingError()
            self.assertEqual(exception.extra_body, "")
        with self.subTest("Test with extra_body argument"):
            exception = RequirementsRatingError("foo")
            self.assertEqual(exception.extra_body, "foo")

    def test_str(self):
        """Test the __str__ method of RequirementsRatingError."""
        with self.subTest("Test with no arguments"):
            exception = RequirementsRatingError()
            self.assertEqual(str(exception), "RequirementsRatingError")
        with self.subTest("Test with body argument"):
            exception = RequirementsRatingError()
            exception.body = "bar"
            self.assertEqual(str(exception), "RequirementsRatingError: bar")
        with self.subTest("Test with extra_body argument"):
            exception = RequirementsRatingError(extra_body="foo")
            self.assertEqual(str(exception), "RequirementsRatingError: foo")
        with self.subTest("Test with body and extra_body arguments"):
            exception = RequirementsRatingError("foo")
            exception.body = "bar"
            self.assertEqual(str(exception), "RequirementsRatingError: bar. foo")


class TestRequirementsRatingMissingReqFile(unittest.TestCase):
    """Tests for the RequirementsRatingMissingReqFile exception."""

    def test_init(self):
        """Test the __init__ method of RequirementsRatingMissingReqFile."""
        directory = "directory"
        exception = RequirementsRatingMissingReqFile(directory)
        self.assertEqual(exception.directory, directory)
        self.assertEqual(
            f"Missing requirements file in {directory}", exception.extra_body
        )
