import unittest
from unittest.mock import Mock, patch, PropertyMock

from pip_rating.exceptions import RequirementsRatingMissingPackage
from pip_rating.packages import Package


class TestPackage(unittest.TestCase):
    """Tests for the Package class."""

    def test_init(self):
        """Test the __init__ method of Package."""
        mock_dependencies = Mock()
        name = "name"
        package = Package(mock_dependencies, name)
        self.assertEqual(mock_dependencies, package.dependencies)
        self.assertEqual(name, package.name)

    def test_first_node(self):
        """Test the first_node property of Package."""
        mock_dependencies = Mock()
        mock_node_1 = Mock()
        mock_node_1.depth = 2
        mock_node_2 = Mock()
        mock_node_2.depth = 1
        package = Package(mock_dependencies, "name")
        package.nodes = {mock_node_1, mock_node_2}
        self.assertEqual(mock_node_2, package.first_node)

    def test_first_node_with_version(self):
        """Test the first_node_with_version property of Package."""
        mock_dependencies = Mock()
        mock_node = Mock()
        mock_node.name = "name"
        mock_node.version = "version"
        package = Package(mock_dependencies, "name")
        package.nodes = {mock_node}
        self.assertEqual("name==version", package.first_node_with_version)

    @patch("pip_rating.packages.SourceRank")
    def test_sourcerank(self, mock_source_rank: Mock):
        """Test the sourcerank property of Package."""
        mock_dependencies = Mock()
        name = "name"
        package = Package(mock_dependencies, name)
        sourcerank = package.sourcerank
        mock_source_rank.assert_called_once_with(package)
        self.assertEqual(mock_source_rank.return_value, sourcerank)

    @patch("pip_rating.packages.Pypi")
    def test_PYPI(self, mock_pypi: Mock):
        """Test the PYPI property of Package."""
        mock_dependencies = Mock()
        name = "name"
        package = Package(mock_dependencies, name)
        pypi = package.pypi
        mock_pypi.assert_called_once_with(name)
        self.assertEqual(mock_pypi.return_value, pypi)

    @patch("pip_rating.packages.SourcecodePage")
    def test_sourcecode_page(self, mock_sourcecode_page: Mock):
        """Test the sourcecode_page property of Package."""
        mock_dependencies = Mock()
        name = "name"
        package = Package(mock_dependencies, name)
        sourcecode_page = package.sourcecode_page
        mock_sourcecode_page.assert_called_once_with(package)
        self.assertEqual(mock_sourcecode_page.return_value, sourcecode_page)

    @patch("pip_rating.packages.Audit")
    def test_get_audit(self, mock_audit: Mock):
        """Test the get_audit method of Package."""
        mock_dependencies = Mock()
        name = "name"
        version = "version"
        package = Package(mock_dependencies, name)
        node = Mock()
        node.version = version
        audit = package.get_audit(node)
        mock_audit.assert_called_once_with(name, version)
        self.assertEqual(mock_audit.return_value, audit)

    @patch("pip_rating.packages.PackageRating")
    def test_rating(self, mock_package_rating: Mock):
        """Test the rating property of Package."""
        mock_dependencies = Mock()
        package = Package(mock_dependencies, "name")
        rating = package.rating
        mock_package_rating.assert_called_once_with(package)
        self.assertEqual(mock_package_rating.return_value, rating)

    def test_get_node_from_parent(self):
        """Test the get_node_from_parent method of Package."""
        mock_dependencies = Mock()
        with self.subTest("Test with from_package is None"):
            mock_node = Mock()
            package = Package(mock_dependencies, "name")
            package.nodes = {mock_node}
            self.assertEqual(mock_node, package.get_node_from_parent())
        with self.subTest("Test with from_package is not None"):
            mock_node = Mock()
            parent_package = Mock()
            mock_parent_node = Mock()
            mock_parent_node.descendants = {mock_node}
            parent_package.nodes = [mock_parent_node]
            package = Package(mock_dependencies, "name")
            package.nodes = {mock_node}
            self.assertEqual(mock_node, package.get_node_from_parent(parent_package))

    def test_get_descendant_packages(self):
        """Test the get_descendant_packages method of Package."""
        mock_descendant = Mock()
        mock_node = Mock()
        mock_node.descendants = {mock_descendant}
        mock_dependencies = Mock()
        package = Package(mock_dependencies, "name")
        package.nodes = {mock_node}
        descendant_packages = list(package.get_descendant_packages())
        self.assertEqual(
            [mock_dependencies.add_node_package.return_value], descendant_packages
        )
        mock_dependencies.add_node_package.assert_called_once_with(mock_descendant)

    def test_get_child_packages(self):
        """Test the get_child_packages method of Package."""
        mock_child = Mock()
        mock_node = Mock()
        mock_node.children = {mock_child}
        mock_dependencies = Mock()
        package = Package(mock_dependencies, "name")
        package.nodes = {mock_node}
        child_packages = list(package.get_child_packages())
        self.assertEqual(
            [mock_dependencies.add_node_package.return_value], child_packages
        )
        mock_dependencies.add_node_package.assert_called_once_with(mock_child)

    def test_add_node(self):
        """Test the add_node method of Package."""
        mock_dependencies = Mock()
        package = Package(mock_dependencies, "name")
        mock_node = Mock()
        package.add_node(mock_node)
        self.assertEqual({mock_node}, package.nodes)

    @patch("pip_rating.packages.Package.rating")
    @patch("pip_rating.packages.Package.get_audit")
    @patch("pip_rating.packages.Package.pypi")
    @patch("pip_rating.packages.Package.sourcerank")
    def test_as_json(
        self,
        mock_sourcerank: Mock,
        mock_pypi: Mock,
        mock_get_audit: Mock,
        mock_rating: Mock,
    ):
        """Test the as_json method of Package."""
        mock_node = Mock()
        mock_node_child = Mock()
        mock_node_child.name = "dependency"
        mock_node.children = {mock_node_child}
        mock_dependency = Mock()
        mock_dependencies = Mock()
        mock_dependencies.packages = {"dependency": mock_dependency}
        name = "name"
        with self.subTest("Test package JSON data"):
            package = Package(mock_dependencies, name)
            package.nodes = {mock_node}
            self.assertEqual(
                {
                    "name": name,
                    "version": mock_node.version,
                    "sourcerank_breakdown": mock_sourcerank.breakdown,
                    "pypi_package": mock_pypi.package,
                    "audit_vulnerabilities": mock_get_audit.return_value.vulnerabilities,
                    "rating": mock_rating.as_json.return_value,
                    "dependencies": [mock_dependency.as_json.return_value],
                },
                package.as_json(),
            )
            mock_get_audit.assert_called_once_with(mock_node)
            mock_rating.as_json.assert_called_once_with(None)
            mock_dependency.as_json.assert_called_once_with(package)
        with self.subTest("Test missing package JSON data"):
            package = Package(mock_dependencies, name)
            type(package).pypi = PropertyMock(
                side_effect=RequirementsRatingMissingPackage(None)
            )  # noqa
            package.nodes = {mock_node}
            self.assertEqual(
                {
                    "name": name,
                    "version": mock_node.version,
                    "sourcerank_breakdown": None,
                    "pypi_package": None,
                    "audit_vulnerabilities": [],
                    "rating": None,
                    "dependencies": [],
                },
                package.as_json(),
            )
            mock_get_audit.assert_called_once_with(mock_node)
            mock_rating.as_json.assert_called_once_with(None)

    def test_repr(self):
        """Test the __repr__ method of Package."""
        mock_dependencies = Mock()
        name = "name"
        package = Package(mock_dependencies, name)
        self.assertEqual(f"<Package {name}>", repr(package))
