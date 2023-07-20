import unittest
from unittest.mock import patch, MagicMock, mock_open

from pip_rating.exceptions import RequirementsRatingParseError
from pip_rating.req_files import SetuppyReqFile


SETUPPY_SETUPTOOLS_FILE = """
from setuptools import setup

setup(
    name="mypackage",
    version="0.1.0",
    install_requires=["telegram-upload"],
)
"""
SETUPPY_DISTUTILS_FILE = """
from distutils.core import setup

setup(
    name="mypackage",
    version="0.1.0",
    install_requires=["telegram-upload"],
)
"""


class TestSetuppyReqFile(unittest.TestCase):
    """Test SetuppyReqFile class."""

    @patch("pip_rating.req_files.setuppy.SetuppyReqFile.__init__")
    @patch("pip_rating.req_files.setuppy.Path")
    def test_find_in_directory(self, mock_path: MagicMock, mock_init: MagicMock):
        """Test the find_in_directory method in the SetuppyReqFile class."""
        mock_init.return_value = None
        req = SetuppyReqFile.find_in_directory("directory")
        self.assertIsInstance(req, SetuppyReqFile)
        mock_path.return_value.__truediv__.assert_called_once_with("setup.py")
        mock_path.return_value.__truediv__.return_value.exists.assert_called_once_with()
        mock_init.assert_called_once_with(
            mock_path.return_value.__truediv__.return_value
        )

    @patch("pip_rating.req_files.setuppy.Path")
    def test_is_valid(self, mock_path: MagicMock):
        """Test the is_valid method in the SetuppyReqFile class."""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.name = "setup.py"
        self.assertTrue(SetuppyReqFile.is_valid("path"))
        mock_path.return_value.exists.assert_called_once_with()

    @patch("pip_rating.req_files.setuppy.SetuppyReqFile.__init__")
    def test_get_dependencies(self, mock_init: MagicMock):
        """Test the get_dependencies method in the SetuppyReqFile class."""
        mock_init.return_value = None
        req = SetuppyReqFile("path")
        req.path = "path"
        with self.subTest("Test with setuptools"), patch(
            "builtins.open", mock_open(read_data=SETUPPY_SETUPTOOLS_FILE)
        ):
            self.assertEqual(["telegram-upload"], req.get_dependencies())
        with self.subTest("Test with distutils"), patch(
            "builtins.open", mock_open(read_data=SETUPPY_DISTUTILS_FILE)
        ):
            self.assertEqual(["telegram-upload"], req.get_dependencies())
        with self.subTest("Test with invalid python file"), patch(
            "builtins.open", mock_open(read_data="invalid")
        ), self.assertRaises(RequirementsRatingParseError):
            req.get_dependencies()
        with self.subTest("Test python file without setup"), patch(
            "builtins.open", mock_open(read_data="")
        ), self.assertRaises(RequirementsRatingParseError):
            req.get_dependencies()
