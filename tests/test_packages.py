import unittest
from unittest.mock import Mock, patch

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
        mock_source_rank.assert_called_once_with(name)
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
