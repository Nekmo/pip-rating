import unittest

from pip_rating.req_files.package_list import PackageList


class TestPackageList(unittest.TestCase):
    """Test PackageList class."""

    def test_init(self):
        """Test the __init__ method in the PackageList class."""
        package_name = "package==1.0.0"
        package_list = PackageList([package_name])
        package_list.append(package_name)
        self.assertEqual(package_name, package_list[0])

    def test_get_dependencies(self):
        """Test the get_dependencies method in the PackageList class."""
        package_list = PackageList([])
        self.assertEqual(package_list, package_list.get_dependencies())

    def test_find_in_directory(self):
        """Test the find_in_directory method in the PackageList class."""
        with self.assertRaises(NotImplementedError):
            PackageList.find_in_directory("directory")

    def test_is_valid(self):
        """Test the is_valid method in the PackageList class."""
        with self.assertRaises(NotImplementedError):
            PackageList.is_valid("path")

    def test_str(self):
        """Test the __str__ method in the PackageList class."""
        package_list = PackageList(["package", "other"])
        self.assertEqual("['package', 'other']", str(package_list))

    def test_repr(self):
        """Test the __repr__ method in the PackageList class."""
        package_list = PackageList(["package", "other"])
        self.assertEqual("<ReqFile (2)>", repr(package_list))
