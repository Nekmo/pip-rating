import unittest
from unittest.mock import MagicMock, patch

from pip_rating.exceptions import RequirementsRatingParseError
from pip_rating.req_files.pyproject import poetry_version, PyprojectReqFile


PROJECT_FILE = """
[project]
dependencies = [
  'PyYAML ~= 5.0',
  'requests[security] < 3',
  'subprocess32; python_version < "3.2"',
]
"""

POETRY_FILE = r"""
[tool.poetry]
name = "test"

[tool.poetry.dependencies]
python = "^3.11"
telegram-upload = "^0.7.0"
dirhunt = ">=0.8.0,<1.0.0"
amazon-dash = "1.4.0"
gkeep = {markers = "python_version < \"3.12\" and platform_system == \"linux\"", version = "^1.0.1"}
proxy-db = {version = "^0.3.1", platform = "linux", python = "^3.11"}
"""

INVALID_FILE = """
[foo]
spam = "eggs"
"""


class TestPoetryVersion(unittest.TestCase):
    """Test poetry_version function."""

    def test_without_version(self):
        """Test poetry_version function without version."""
        self.assertEqual("", poetry_version(None))

    def test_with_dict(self):
        """Test poetry_version function with dict."""
        self.assertEqual(
            "==1.0.0 ; python_version >='3' and python_version <'4.0.0' "
            "and extra == 'dev' and platform_system=='linux'",
            poetry_version(
                {
                    "version": "1.0.0",
                    "python": "^3",
                    "platform": "linux",
                    "markers": "extra == 'dev'",
                }
            ),
        )

    def test_caret(self):
        """Test poetry_version function with caret."""
        with self.subTest("Test major version"):
            self.assertEqual(">=1.0.0,<2.0.0", poetry_version("^1.0.0"))
            self.assertEqual(">=1,<2.0.0", poetry_version("^1"))
            self.assertEqual(">=1.2.0,<2.0.0", poetry_version("^1.2.0"))
            self.assertEqual(">=1.2,<2.0.0", poetry_version("^1.2"))
            self.assertEqual(">=0,<1.0.0", poetry_version("^0"))
        with self.subTest("Test minor version"):
            self.assertEqual(">=0.2.3,<0.3.0", poetry_version("^0.2.3"))
            self.assertEqual(">=0.0,<0.1.0", poetry_version("^0.0"))
        with self.subTest("Test patch version"):
            self.assertEqual(">=0.0.3,<0.0.4", poetry_version("^0.0.3"))

    def test_numeric_wildcard(self):
        """Test poetry_version function with numeric or wildcard."""
        with self.subTest("Test numeric version"):
            self.assertEqual("==1.2.3", poetry_version("1.2.3"))
        with self.subTest("Test wildcard version"):
            self.assertEqual("==*.3", poetry_version("*.3"))

    def test_operators(self):
        """Test poetry_version function with operators."""
        with self.subTest("Test equal operator"):
            self.assertEqual("==1.2.3", poetry_version("==1.2.3"))
        with self.subTest("Test not equal operator"):
            self.assertEqual("!=1.2.3", poetry_version("!=1.2.3"))
        with self.subTest("Test less than operator"):
            self.assertEqual("<1.2.3", poetry_version("<1.2.3"))
        with self.subTest("Test less than or equal operator"):
            self.assertEqual("<=1.2.3", poetry_version("<=1.2.3"))
        with self.subTest("Test greater than operator"):
            self.assertEqual(">1.2.3", poetry_version(">1.2.3"))
        with self.subTest("Test greater than or equal operator"):
            self.assertEqual(">=1.2.3", poetry_version(">=1.2.3"))

    def test_invalid_version(self):
        """Test poetry_version function with invalid version."""
        with self.assertRaises(RequirementsRatingParseError):
            poetry_version("invalid")


class TestPyprojectReqFile(unittest.TestCase):
    """Test PyprojectReqFile class."""

    @patch("pip_rating.req_files.pyproject.PyprojectReqFile.__init__")
    @patch("pip_rating.req_files.pyproject.Path")
    def test_find_in_directory(self, mock_path: MagicMock, mock_init: MagicMock):
        """Test the find_in_directory method in the PyprojectReqFile class."""
        mock_init.return_value = None
        req = PyprojectReqFile.find_in_directory("directory")
        self.assertIsInstance(req, PyprojectReqFile)
        mock_path.return_value.__truediv__.assert_called_once_with("pyproject.toml")
        mock_path.return_value.__truediv__.return_value.exists.assert_called_once_with()
        mock_init.assert_called_once_with(
            mock_path.return_value.__truediv__.return_value
        )

    @patch("pip_rating.req_files.pyproject.Path")
    def test_is_valid(self, mock_path: MagicMock):
        """Test the is_valid method in the PyprojectReqFile class."""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.name = "pyproject.toml"
        self.assertTrue(PyprojectReqFile.is_valid("path"))
        mock_path.return_value.exists.assert_called_once_with()

    @patch("builtins.open")
    @patch("pip_rating.req_files.pyproject.PyprojectReqFile.__init__")
    def test_get_dependencies(self, mock_init: MagicMock, mock_open: MagicMock):
        """Test the get_dependencies method in the PyprojectReqFile class."""
        mock_init.return_value = None
        pyproject_req_file = PyprojectReqFile("path")
        pyproject_req_file.path = "path"
        with self.subTest("Test with standard project file"):
            mock_open.return_value.__enter__.return_value.read.return_value = (
                PROJECT_FILE.encode("utf-8")
            )
            dependencies = pyproject_req_file.get_dependencies()
            self.assertEqual(
                [
                    "PyYAML ~= 5.0",
                    "requests[security] < 3",
                    'subprocess32; python_version < "3.2"',
                ],
                dependencies,
            )
        with self.subTest("Test with Poetry file"):
            mock_open.return_value.__enter__.return_value.read.return_value = (
                POETRY_FILE.encode("utf-8")
            )
            dependencies = pyproject_req_file.get_dependencies()
            self.assertEqual(
                [
                    "telegram-upload>=0.7.0,<0.8.0",
                    "dirhunt>=0.8.0,<1.0.0",
                    "amazon-dash==1.4.0",
                    'gkeep>=1.0.1,<2.0.0 ; python_version < "3.12" and platform_system == "linux"',
                    "proxy-db>=0.3.1,<0.4.0 ; python_version >='3.11' and python_version <'4.0.0' "
                    "and platform_system=='linux'",
                ],
                dependencies,
            )
        with self.subTest("Invalid file"):
            mock_open.return_value.__enter__.return_value.read.return_value = (
                INVALID_FILE.encode("utf-8")
            )
            with self.assertRaises(RequirementsRatingParseError):
                pyproject_req_file.get_dependencies()
