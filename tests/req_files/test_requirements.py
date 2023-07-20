import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from pip_rating.req_files import RequirementsReqFile


REQUIREMENTS_FILE = """
# Comment
package==1.0.0
other  # Comment
"""


class TestRequirementsReqFile(unittest.TestCase):
    """Test RequirementsReqFile class."""

    @patch("pip_rating.req_files.requirements.RequirementsReqFile.__init__")
    @patch("pip_rating.req_files.requirements.Path")
    def test_find_in_directory(self, mock_path: MagicMock, mock_init: MagicMock):
        """Test the find_in_directory method in the RequirementsReqFile class."""
        mock_init.return_value = None
        with self.subTest("Test requirements.in"):
            req = RequirementsReqFile.find_in_directory("directory")
            self.assertIsInstance(req, RequirementsReqFile)
            mock_path.return_value.__truediv__.assert_called_with("requirements.in")
            mock_path.return_value.__truediv__.return_value.exists.assert_called_once_with()
            mock_init.assert_called_once_with(
                mock_path.return_value.__truediv__.return_value
            )
        mock_path.reset_mock()
        mock_init.reset_mock()
        with self.subTest("Test requirements.txt"):
            mock_path.return_value.__truediv__.return_value.exists.side_effect = [
                False,
                True,
            ]
            req = RequirementsReqFile.find_in_directory("directory")
            self.assertIsInstance(req, RequirementsReqFile)
            mock_path.return_value.__truediv__.assert_has_calls(
                [
                    unittest.mock.call("requirements.in"),
                    unittest.mock.call("requirements.txt"),
                ],
                any_order=True,
            )
            self.assertEqual(
                2, mock_path.return_value.__truediv__.return_value.exists.call_count
            )
            mock_init.assert_called_once_with(
                mock_path.return_value.__truediv__.return_value
            )
        mock_path.reset_mock()
        mock_init.reset_mock()
        for file in ["requirements-dev.in", "requirements-dev.txt"]:
            with self.subTest(f"Test {file}"):
                posixpath = Path(file)
                mock_path.return_value.iterdir.return_value = [
                    posixpath,
                ]
                mock_path.return_value.__truediv__.return_value.exists.side_effect = [
                    False,
                    False,
                ]
                req = RequirementsReqFile.find_in_directory("directory")
                self.assertIsInstance(req, RequirementsReqFile)
                mock_path.return_value.__truediv__.assert_has_calls(
                    [
                        unittest.mock.call("requirements.in"),
                        unittest.mock.call("requirements.txt"),
                    ],
                    any_order=True,
                )
                self.assertEqual(
                    2, mock_path.return_value.__truediv__.return_value.exists.call_count
                )
                mock_init.assert_called_once_with(posixpath)
            mock_path.reset_mock()
            mock_init.reset_mock()

    @patch("pip_rating.req_files.requirements.Path")
    def test_is_valid(self, mock_path: MagicMock):
        """Test the is_valid method in the RequirementsReqFile class."""
        mock_path.return_value.exists.return_value = True
        for suffix in [".txt", ".in"]:
            with self.subTest(f"Test {suffix} suffix"):
                mock_path.return_value.suffix = suffix
                self.assertTrue(RequirementsReqFile.is_valid(f"requirements.{suffix}"))
                mock_path.return_value.exists.assert_called_once_with()
            mock_path.reset_mock()

    @patch("builtins.open", mock_open(read_data=REQUIREMENTS_FILE))
    @patch("pip_rating.req_files.requirements.RequirementsReqFile.__init__")
    def test_get_dependencies(self, mock_init: MagicMock):
        """Test the get_dependencies method in the RequirementsReqFile class."""
        mock_init.return_value = None
        path = "requirements.txt"
        req = RequirementsReqFile(path)
        req.path = path
        self.assertEqual(
            ["package==1.0.0", "other"],
            req.get_dependencies(),
        )
