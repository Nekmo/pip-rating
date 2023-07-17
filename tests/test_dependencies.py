import setuptools  # noqa: F401
import unittest
from unittest.mock import patch, MagicMock, Mock

from pip_rating.dependencies import DependenciesVersionSolver


class TestDependenciesVersionSolver(unittest.TestCase):
    """Test the class DependenciesVersionSolver."""

    @patch("pip_rating.dependencies.VersionSolver.__init__")
    def test_init(self, mock_init: MagicMock):
        """Test the method init."""
        mock_results = Mock()
        mock_source = Mock()
        threads = 2
        DependenciesVersionSolver(mock_results, mock_source, threads)
        mock_init.assert_called_once_with(mock_source, threads=threads)

    @patch("pip_rating.dependencies.VersionSolver._propagate")
    def test_propagate(self, mock_propagate: MagicMock):
        """Test the method propagate."""
        with self.subTest("Test with package name equal to _root_."):
            mock_results = Mock()
            mock_source = Mock()
            mock_package = Mock()
            mock_package.name = "_root_"
            solver = DependenciesVersionSolver(mock_results, mock_source)
            solver._propagate(mock_package)
            mock_results.processing_package.assert_not_called()
            mock_propagate.assert_called_once_with(mock_package)
        mock_propagate.reset_mock()
        with self.subTest("Test with package name different to _root_."):
            mock_results = Mock()
            mock_source = Mock()
            mock_package = Mock()
            solver = DependenciesVersionSolver(mock_results, mock_source)
            solver._propagate(mock_package)
            mock_results.processing_package.assert_called_once_with(mock_package)
            mock_propagate.assert_called_once_with(mock_package)
