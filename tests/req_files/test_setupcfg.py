import unittest
from unittest.mock import patch, MagicMock

from pip_rating.req_files import SetupcfgReqFile


class TestSetupcfgReqFile(unittest.TestCase):
    """Test SetupcfgReqFile class."""

    @patch("pip_rating.req_files.setupcfg.SetupcfgReqFile.__init__")
    @patch("pip_rating.req_files.setupcfg.Path")
    def test_find_in_directory(self, mock_path: MagicMock, mock_init: MagicMock):
        """Test the find_in_directory method in the SetupcfgReqFile class."""
        mock_init.return_value = None
        req = SetupcfgReqFile.find_in_directory("directory")
        self.assertIsInstance(req, SetupcfgReqFile)
        mock_path.return_value.__truediv__.assert_called_once_with("setup.cfg")
        mock_path.return_value.__truediv__.return_value.exists.assert_called_once_with()
        mock_init.assert_called_once_with(
            mock_path.return_value.__truediv__.return_value
        )

    @patch("pip_rating.req_files.setupcfg.Path")
    def test_is_valid(self, mock_path: MagicMock):
        """Test the is_valid method in the SetupcfgReqFile class."""
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.name = "setup.cfg"
        self.assertTrue(SetupcfgReqFile.is_valid("path"))
        mock_path.return_value.exists.assert_called_once_with()

    @patch("pip_rating.req_files.setupcfg.read_configuration")
    @patch("pip_rating.req_files.setupcfg.SetupcfgReqFile.__init__")
    def test_get_dependencies(self, mock_init: MagicMock, mock_read: MagicMock):
        """Test the get_dependencies method in in the SetupcfgReqFile class."""
        mock_init.return_value = None
        mock_read.return_value = {"options": {"install_requires": ["package==1.0.0"]}}
        req = SetupcfgReqFile("path")
        req.path = "path"
        self.assertEqual(["package==1.0.0"], req.get_dependencies())
        mock_read.assert_called_once_with(req.path)
