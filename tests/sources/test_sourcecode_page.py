import unittest
from unittest.mock import patch, MagicMock, Mock, PropertyMock

from requests import RequestException

from pip_rating.sources.sourcecode_page import (
    get_github_readme,
    search_in_readme,
    SourcecodePage,
)


class TestGetGithubReadme(unittest.TestCase):
    """Test the get_github_readme function."""

    @patch("pip_rating.sources.sourcecode_page.click.echo")
    @patch("pip_rating.sources.sourcecode_page.github_token", new="token")
    @patch("pip_rating.sources.sourcecode_page.requests.get")
    def test_get_github_readme(
        self, mock_requests_get: MagicMock, mock_echo: MagicMock
    ):
        """Test the get_github_readme function."""
        with self.subTest("Test with readme"):
            mock_requests_get.return_value.__enter__.return_value.json.return_value = {
                "content": "Y29udGVudA=="
            }
            self.assertEqual("content", get_github_readme("owner", "repo"))
            mock_requests_get.return_value.__enter__.return_value.raise_for_status.assert_called_once_with()
            mock_requests_get.assert_called_once_with(
                "https://api.github.com/repos/owner/repo/readme",
                headers={"Authorization": "Bearer token"},
            )
        with self.subTest("Test rate limit exceded with GITHUB_TOKEN defined"):
            mock_requests_get.return_value.__enter__.return_value.raise_for_status.side_effect = RequestException(
                response=MagicMock(status_code=403, reason="rate limit exceeded")
            )
            self.assertEqual("", get_github_readme("owner", "repo"))
            mock_echo.assert_called_once_with(
                "GitHub rate limit exceeded. Check your GITHUB_TOKEN environment variable.",
                err=True,
            )
        mock_echo.reset_mock()
        with self.subTest(
            "Test rate limit exceded without GITHUB_TOKEN defined"
        ), patch("pip_rating.sources.sourcecode_page.github_token", new=None), patch(
            "pip_rating.sources.sourcecode_page.github_warning", new=False
        ):
            mock_requests_get.return_value.__enter__.return_value.raise_for_status.side_effect = RequestException(
                response=MagicMock(status_code=403, reason="rate limit exceeded")
            )
            self.assertEqual("", get_github_readme("owner", "repo"))
            mock_echo.assert_called_once_with(
                "GitHub rate limit exceeded. Set GITHUB_TOKEN environment variable to increase the limit.",
                err=True,
            )


class TestSearchInReadme(unittest.TestCase):
    """Test the search_in_readme function."""

    def test_search_in_readme(self):
        """Test the search_in_readme function."""
        with self.subTest("Test with pip install pattern"):
            self.assertTrue(
                search_in_readme("pip  install -U  package_name123", "package-name123")
            )
        with self.subTest("Test with poetry add pattern"):
            self.assertTrue(
                search_in_readme("poetry  add  package-name123", "package-name123")
            )
        with self.subTest("Test with pipenv install pattern"):
            self.assertTrue(
                search_in_readme("pipenv  install  package-name123", "package-name123")
            )
        with self.subTest("Test with pipenv invalid pattern"):
            self.assertIsNone(search_in_readme("pip install -P", "package-name123"))
        with self.subTest("Test package name not in readme"):
            self.assertFalse(
                search_in_readme("pip install other-package", "package-name123")
            )


class TestSourcecodePage(unittest.TestCase):
    """Test the SourcecodePage class."""

    @patch("pip_rating.sources.sourcecode_page.SourceBase.__init__")
    def test_init(self, mock_init: MagicMock):
        """Test the __init__ method."""
        mock_init.return_value = None
        mock_package = Mock()
        sourcecode_page = SourcecodePage(mock_package)
        self.assertEqual(mock_package, sourcecode_page.package)
        mock_init.assert_called_once_with(mock_package.name)

    @patch("pip_rating.sources.sourcecode_page.datetime")
    @patch("pip_rating.sources.sourcecode_page.get_github_readme")
    def test_get_cache_data(
        self, mock_get_github_readme: MagicMock, mock_datetime: MagicMock
    ):
        """Test the get_cache_data method."""
        mock_get_github_readme.return_value = "pip install repo"
        mock_package = Mock()
        mock_package.name = "repo"
        mock_package.pypi.package = {
            "info": {"project_urls": {"Source": "https://github.com/owner/repo"}}
        }
        cache_dict = SourcecodePage(mock_package).get_cache_data()
        self.assertEqual(
            {
                "package_name": "repo",
                "updated_at": mock_datetime.datetime.now.return_value.isoformat.return_value,
                "source": "github",
                "sourcecode": {
                    "package_in_readme": True,
                    "readme_content": mock_get_github_readme.return_value,
                },
            },
            cache_dict,
        )
        mock_get_github_readme.assert_called_once_with("owner", "repo")

    @patch(
        "pip_rating.sources.sourcecode_page.SourceBase.is_cache_expired",
        new_callable=PropertyMock,
    )
    def test_package(self, mock_is_cache_expired: MagicMock):
        """Test the package property."""
        mock_package = Mock()
        with self.subTest("Test cache not expired"), patch(
            "pip_rating.sources.sourcecode_page.SourcecodePage.get_from_cache"
        ) as mock_get_from_cache:
            mock_is_cache_expired.return_value = False
            mock_get_from_cache.return_value = {
                "sourcecode": {"package_in_readme": True}
            }
            sourcecode_page = SourcecodePage(mock_package)
            self.assertTrue(sourcecode_page.package_in_readme)
            mock_get_from_cache.assert_called_once_with()
        with self.subTest("Test cache expired"), patch(
            "pip_rating.sources.sourcecode_page.SourcecodePage.save_to_cache"
        ) as mock_save_to_cache:
            mock_is_cache_expired.return_value = True
            mock_save_to_cache.return_value = {
                "sourcecode": {"package_in_readme": True}
            }
            sourcecode_page = SourcecodePage(mock_package)
            self.assertTrue(sourcecode_page.package_in_readme)
            mock_save_to_cache.assert_called_once_with()
