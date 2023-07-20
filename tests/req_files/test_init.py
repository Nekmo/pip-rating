import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from pip_rating.exceptions import (
    RequirementsRatingInvalidFile,
    RequirementsRatingMissingReqFile,
)
from pip_rating.req_files import get_req_file_cls, find_in_directory


class TestGetReqFileCls(unittest.TestCase):
    """Test the get_req_file_cls function."""

    def test_get_req_file_cls(self):
        """Test the get_req_file_cls function."""
        mock_requirements_req_file = MagicMock()
        with self.subTest("Test with valid file"), patch(
            "pip_rating.req_files.REQ_FILE_CLASSES",
            {"requirements": mock_requirements_req_file},
        ):
            path = "requirements.txt"
            self.assertEqual(mock_requirements_req_file, get_req_file_cls(path))
            mock_requirements_req_file.is_valid.assert_called_once_with(path)
        with self.subTest("Test with valid file"), patch(
            "pip_rating.req_files.REQ_FILE_CLASSES",
            {"requirements": mock_requirements_req_file},
        ), self.assertRaises(RequirementsRatingInvalidFile):
            path = "unknown"
            mock_requirements_req_file.is_valid.return_value = False
            self.assertEqual(mock_requirements_req_file, get_req_file_cls(path))
            mock_requirements_req_file.is_valid.assert_called_once_with(path)


class TestFindIndirectory(unittest.TestCase):
    """Test the find_in_directory function."""

    def test_find_in_directory(self):
        """Test the find_in_directory function."""
        mock_requirements_req_file = MagicMock()
        directory = "directory"
        with self.subTest("Test with valid file"), patch(
            "pip_rating.req_files.REQ_FILE_CLASSES",
            {"requirements": mock_requirements_req_file},
        ):
            self.assertEqual(
                mock_requirements_req_file.find_in_directory.return_value,
                find_in_directory(directory),
            )
            mock_requirements_req_file.find_in_directory.assert_called_once_with(
                Path(directory)
            )
        with self.subTest("Test with unknown file"), patch(
            "pip_rating.req_files.REQ_FILE_CLASSES",
            {"requirements": mock_requirements_req_file},
        ), self.assertRaises(RequirementsRatingMissingReqFile):
            mock_requirements_req_file.find_in_directory.return_value = None
            self.assertEqual(
                mock_requirements_req_file.find_in_directory.return_value,
                find_in_directory("directory"),
            )
