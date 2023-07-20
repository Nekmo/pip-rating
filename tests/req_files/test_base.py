import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from pip_rating.req_files import ReqFileBase


class TestReqFileBase(unittest.TestCase):
    """Test ReqFileBase class."""

    @patch("pip_rating.req_files.base.ReqFileBase.get_dependencies")
    @patch("pip_rating.req_files.base.Path")
    def test_init(self, mock_path: MagicMock, mock_get_dependencies: MagicMock):
        """Test the __init__ method in the ReqFileBase class."""
        path = "tests/req_files/requirements.txt"
        with self.subTest("Path does not exist"):
            mock_path.return_value.exists.return_value = False
            with self.assertRaises(IOError):
                ReqFileBase(path)
            mock_path.assert_called_once_with(path)
        mock_path.reset_mock()
        with self.subTest("Path exists"):
            mock_path.return_value.exists.return_value = True
            ReqFileBase(path)
            mock_path.assert_called_once_with(path)
            mock_get_dependencies.assert_called_once_with()

    def test_find_in_directory(self):
        """Test the find_in_directory method in the ReqFileBase class."""
        with self.assertRaises(NotImplementedError):
            ReqFileBase.find_in_directory("tests/req_files")

    def test_is_valid(self):
        """Test the is_valid method in the ReqFileBase class."""
        with self.assertRaises(NotImplementedError):
            ReqFileBase.is_valid("tests/req_files/requirements.txt")

    @patch("pip_rating.req_files.base.ReqFileBase.__init__")
    def test_get_dependencies(self, mock_init: MagicMock):
        """Test the get_dependencies method in the ReqFileBase class."""
        mock_init.return_value = None
        req_file = ReqFileBase("tests/req_files/requirements.txt")
        with self.assertRaises(NotImplementedError):
            req_file.get_dependencies()

    @patch("pip_rating.req_files.base.ReqFileBase.__init__", new=list.__init__)
    def test_contains(self):
        """Test the __contains__ method in the ReqFileBase class."""
        # mock_init.return_value = None
        req_file = ReqFileBase()  # noqa
        req_file.append("package==1.0.0")
        with self.subTest("Package is in file with no specifier"):
            self.assertIn("PACKAGE", req_file)
        with self.subTest("Package is in file with specifier"):
            self.assertIn("package==1.0.0", req_file)
        with self.subTest("Package is not in file"):
            self.assertNotIn("other", req_file)

    @patch("pip_rating.req_files.base.ReqFileBase.__init__")
    def test_str(self, mock_init: MagicMock):
        """Test the __str__ method in the ReqFileBase class."""
        mock_init.return_value = None
        path = Path("tests/req_files/requirements.txt")
        req_file = ReqFileBase(path)
        req_file.path = path
        self.assertEqual(str(req_file), "requirements.txt")

    @patch("pip_rating.req_files.base.ReqFileBase.__init__")
    def test_repr(self, mock_init: MagicMock):
        """Test the __repr__ method in the ReqFileBase class."""
        mock_init.return_value = None
        path = Path("tests/req_files/requirements.txt")
        req_file = ReqFileBase(path)
        req_file.path = path
        self.assertEqual(repr(req_file), "<ReqFile tests/req_files/requirements.txt>")
