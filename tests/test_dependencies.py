import setuptools  # noqa: F401
import unittest
from unittest.mock import patch, MagicMock, Mock

from pip_rating.dependencies import (
    DependenciesVersionSolver,
    Dependencies,
    version_resolver_threads,
)
from pip_rating.packages import Package


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
        mock_results = Mock()
        mock_source = Mock()
        with self.subTest("Test with package name equal to _root_."):
            mock_package = Mock()
            mock_package.name = "_root_"
            solver = DependenciesVersionSolver(mock_results, mock_source)
            solver._propagate(mock_package)
            mock_results.processing_package.assert_not_called()
            mock_propagate.assert_called_once_with(mock_package)
        mock_propagate.reset_mock()
        with self.subTest("Test with package name different to _root_."):
            mock_package = Mock()
            solver = DependenciesVersionSolver(mock_results, mock_source)
            solver._propagate(mock_package)
            mock_results.processing_package.assert_called_once_with(mock_package)
            mock_propagate.assert_called_once_with(mock_package)


class TestDependencies(unittest.TestCase):
    """Test the class Dependencies."""

    def test_init(self):
        """Test the method init."""
        mock_results = Mock()
        mock_req_file = Mock()
        cache_dir = "cache_dir"
        index_url = "index_url"
        extra_index_url = "extra_index_url"
        pre = True
        ignore_packages = ["package1", "package2"]
        dependencies = Dependencies(
            mock_results,
            mock_req_file,
            cache_dir,
            index_url,
            extra_index_url,
            pre,
            ignore_packages,
        )
        self.assertEqual(mock_results, dependencies.results)
        self.assertEqual(mock_req_file, dependencies.req_file)
        self.assertEqual(cache_dir, dependencies.cache_dir)
        self.assertEqual(index_url, dependencies.index_url)
        self.assertEqual(extra_index_url, dependencies.extra_index_url)
        self.assertEqual(pre, dependencies.pre)
        self.assertEqual(ignore_packages, dependencies.ignore_packages)

    @patch("pip_rating.dependencies.PackageSource")
    def test_package_source(self, mock_package_source: MagicMock):
        """Test the method package_source."""
        mock_results = Mock()
        mock_req_file = Mock()
        cache_dir = "cache_dir"
        index_url = "index_url"
        extra_index_url = "extra_index_url"
        pre = True
        ignore_packages = ["package1", "package2"]
        dependencies = Dependencies(
            mock_results,
            mock_req_file,
            cache_dir,
            index_url,
            extra_index_url,
            pre,
            ignore_packages,
        )
        self.assertEqual(mock_package_source.return_value, dependencies.package_source)
        mock_package_source.assert_called_once_with(
            cache_dir=cache_dir,
            index_url=index_url,
            extra_index_url=extra_index_url,
            pre=pre,
        )

    @patch("pip_rating.dependencies.Dependencies.package_source")
    @patch("pip_rating.dependencies.DependenciesVersionSolver")
    def test_version_solution(
        self, mock_version_solver: MagicMock, mock_package_source: MagicMock
    ):
        """Test the method version_solution."""
        mock_results = Mock()
        mock_req_file = Mock()
        mock_root_dependency = Mock()
        mock_req_file.__iter__ = Mock(return_value=iter([mock_root_dependency]))
        cache_dir = "cache_dir"
        index_url = "index_url"
        extra_index_url = "extra_index_url"
        with self.subTest("Test download the wheel"):
            dependencies = Dependencies(
                mock_results, mock_req_file, cache_dir, index_url, extra_index_url
            )
            self.assertEqual(
                mock_version_solver.return_value.solve.return_value,
                dependencies.version_solution,
            )
            mock_version_solver.assert_called_once_with(
                mock_results,
                dependencies.package_source,
                threads=version_resolver_threads,
            )
            mock_package_source.root_dep.assert_called_once_with(mock_root_dependency)
        mock_req_file.__iter__ = Mock(return_value=iter([mock_root_dependency]))
        mock_version_solver.reset_mock()
        mock_package_source.reset_mock()
        with self.subTest("Test failed to download the wheel"):
            mock_version_solver.return_value.solve.side_effect = RuntimeError(
                "Failed to download/build wheel"
            )
            dependencies = Dependencies(
                mock_results, mock_req_file, cache_dir, index_url, extra_index_url
            )
            self.assertEqual(
                mock_version_solver.return_value.solution, dependencies.version_solution
            )
            mock_version_solver.assert_called_once_with(
                mock_results,
                dependencies.package_source,
                threads=version_resolver_threads,
            )
            mock_package_source.root_dep.assert_called_once_with(mock_root_dependency)
        with self.subTest("Test RuntimeError"):
            mock_version_solver.return_value.solve.side_effect = RuntimeError("Error")
            dependencies = Dependencies(
                mock_results, mock_req_file, cache_dir, index_url, extra_index_url
            )
            with self.assertRaises(RuntimeError):
                dependencies.version_solution  # noqa

    @patch("pip_rating.dependencies.build_tree")
    @patch("pip_rating.dependencies.Dependencies.version_solution")
    def test_dependencies_tree(
        self, mock_version_solution: MagicMock, mock_build_tree: MagicMock
    ):
        """Test the method dependencies_tree."""
        mock_results = Mock()
        mock_req_file = Mock()
        mock_tree_root = Mock()
        mock_packages_tree_dict = Mock()
        mock_packages_flat = Mock()
        packages_versions = [
            (MagicMock(), "0.0.1"),
            (MagicMock(__eq__=Mock(return_value=True)), "0.0.2"),
        ]
        mock_build_tree.return_value = [
            mock_tree_root,
            mock_packages_tree_dict,
            mock_packages_flat,
        ]
        mock_version_solution.decisions.items.return_value = packages_versions
        dependencies = Dependencies(mock_results, mock_req_file)
        self.assertEqual(mock_tree_root, dependencies.dependencies_tree)
        mock_version_solution.decisions.items.assert_called_once_with()
        mock_build_tree.assert_called_once_with(
            dependencies.package_source,
            {packages_versions[0][0]: packages_versions[0][1]},
        )

    def test_add_node_package(self):
        """Test the method add_node_package."""
        mock_results = Mock()
        mock_req_file = Mock()
        mock_ignored_node = MagicMock()
        mock_ignored_node.name = "ignored_package"
        mock_node = MagicMock()
        mock_node.name = "package"
        dependencies = Dependencies(
            mock_results, mock_req_file, ignore_packages=[mock_ignored_node.name]
        )
        with self.subTest("Test ignored package"):
            self.assertIsNone(dependencies.add_node_package(mock_ignored_node))
            self.assertFalse(dependencies.packages)
        with self.subTest("Test add new package"):
            package = dependencies.add_node_package(mock_node)
            self.assertEqual(dependencies.packages[mock_node.name], package)
            self.assertIsInstance(package, Package)
            self.assertEqual(dependencies, package.dependencies)
            self.assertEqual(mock_node.name, package.name)
            self.assertEqual({mock_node}, package.nodes)
        with self.subTest("Test add existing package"):
            existing_mock_node = MagicMock()
            existing_mock_node.name = "package"
            existing_package = dependencies.add_node_package(existing_mock_node)
            self.assertEqual(package, existing_package)
            self.assertEqual({mock_node, existing_mock_node}, package.nodes)

    @patch("pip_rating.dependencies.Dependencies.dependencies_tree")
    def test_get_packages(self, mock_dependencies_tree: MagicMock):
        """Test the method get_packages."""
        mock_results = Mock()
        mock_req_file = Mock()
        mock_node = MagicMock()
        mock_node.name = "package"
        mock_dependencies_tree.children = [mock_node]
        dependencies = Dependencies(mock_results, mock_req_file)
        packages = dependencies.get_packages()
        self.assertEqual(dependencies.packages, packages)
        self.assertEqual(1, len(packages))
        self.assertEqual(mock_node.name, packages[mock_node.name].name)

    def test_total_size(self):
        """Test the method total_size."""
        mock_results = Mock()
        mock_req_file = Mock()
        mock_package = Mock()
        mock_node_1 = Mock()
        mock_node_1.size = 1
        mock_node_2 = Mock()
        mock_node_2.size = 2
        mock_package.nodes = [mock_node_1, mock_node_2]
        dependencies = Dependencies(mock_results, mock_req_file)
        dependencies.packages = {"package": mock_package}
        self.assertEqual(3, dependencies.total_size)

    @patch("pip_rating.dependencies.Dependencies.get_packages")
    def test_get_global_rating_score(self, mock_get_packages: MagicMock):
        """Test the method get_global_rating_score."""
        mock_results = Mock()
        mock_req_file = Mock()
        mock_package_1 = Mock()
        mock_package_1.rating.get_global_rating_score.return_value = 2
        mock_package_2 = Mock()
        mock_package_2.rating.get_global_rating_score.return_value = 1
        mock_get_packages.return_value = {
            "package_1": mock_package_1,
            "package_2": mock_package_2,
        }
        dependencies = Dependencies(mock_results, mock_req_file)
        self.assertEqual(1, dependencies.get_global_rating_score())
