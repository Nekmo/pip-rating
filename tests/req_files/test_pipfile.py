import unittest
from unittest.mock import patch, MagicMock, Mock

from pip_rating.req_files import PipfileReqFile


class TestPipfileReqFile(unittest.TestCase):
    """Test PipfileReqFile class."""

    @patch("pip_rating.req_files.pipfile.PipfileReqFile.__init__")
    @patch("pip_rating.req_files.pipfile.Path")
    def test_find_in_directory(self, mock_path: MagicMock, mock_init: MagicMock):
        """Test the find_in_directory method in the PipfileReqFile class."""
        mock_init.return_value = None
        req = PipfileReqFile.find_in_directory("directory")
        self.assertIsInstance(req, PipfileReqFile)
        mock_path.return_value.__truediv__.assert_called_once_with("Pipfile")
        mock_path.return_value.__truediv__.return_value.exists.assert_called_once_with()
        mock_init.assert_called_once_with(
            mock_path.return_value.__truediv__.return_value
        )

    @patch("pip_rating.req_files.pipfile.Path")
    def test_is_valid(self, mock_path: MagicMock):
        """Test the is_valid method in the PipfileReqFile class."""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.name = "Pipfile"
        self.assertTrue(PipfileReqFile.is_valid("path"))
        mock_path.return_value.exists.assert_called_once_with()

    @patch("pip_rating.req_files.pipfile.Pipfile")
    @patch("pip_rating.req_files.pipfile.PipfileReqFile.__init__")
    def test_get_dependencies(self, mock_init: MagicMock, mock_pipfile: MagicMock):
        """Test the get_dependencies method in the PipfileReqFile class."""
        mock_init.return_value = None
        mock_pipfile.load.return_value.data = {"default": {"package": "==1.0.0"}}
        req = PipfileReqFile("path")
        req.path = Mock()
        self.assertEqual(["package==1.0.0"], req.get_dependencies())
        mock_pipfile.load.assert_called_once_with(req.path)
