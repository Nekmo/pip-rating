import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from pip_rating.sources.sourcerank import SourceRank


SOURCERANK_PAGE = """
<!DOCTYPE html>
<html lang="en">
<ul class="list-group">
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        Basic info present?
        &nbsp;<small class='text-muted'><i title="Description, homepage/repository link and keywords present?" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        Source repository present?
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        Readme present?
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        License present?
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        Has multiple versions?
        &nbsp;<small class='text-muted'><i title="Has the package had more than one release?" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-warning">
        0
        </span>
        Follows SemVer?
        &nbsp;<small class='text-muted'><i title="Every version has a valid SemVer number" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        Recent release?
        &nbsp;<small class='text-muted'><i title="Within the past 6 months?" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        Not brand new?
        &nbsp;<small class='text-muted'><i title="Existed for at least 6 months" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        1
        </span>
        1.0.0 or greater?
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        10
        </span>
        Dependent Packages
        &nbsp;<small class='text-muted'><i title="Logarithmic scale times two" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        5
        </span>
        Dependent Repositories
        &nbsp;<small class='text-muted'><i title="Logarithmic scale" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        5
        </span>
        Stars
        &nbsp;<small class='text-muted'><i title="Logarithmic scale" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        2
        </span>
        Contributors
        &nbsp;<small class='text-muted'><i title="Logarithmic scale divided by two" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class="list-group-item">
        <span class="badge alert-success">
        2
        </span>
        Libraries.io subscribers
        &nbsp;<small class='text-muted'><i title="Logarithmic scale divided by two" class="fa fa-question-circle tip"></i></small>
    </li>
    <li class='list-group-item'>
        <span class='badge alert-info'>
        32
        </span>
        <strong>Total</strong>
    </li>
</ul>
"""


class TestSourceRank(unittest.TestCase):
    """Test the SourceRank class."""

    @patch("pip_rating.sources.sourcerank.SourceRank.get_breakdown")
    @patch("pip_rating.sources.sourcerank.datetime")
    def test_get_cache_data(
        self, mock_datetime: MagicMock, mock_get_breakdown: MagicMock
    ):
        """Test the get_cache_data method."""
        package_name = "package_name"
        mock_get_breakdown.return_value = {"breakdown": "breakdown"}
        self.assertEqual(
            {
                "package_name": package_name,
                "updated_at": mock_datetime.datetime.now.return_value.isoformat.return_value,
                "breakdown": mock_get_breakdown.return_value,
            },
            SourceRank(package_name).get_cache_data(),
        )

    @patch(
        "pip_rating.sources.sourcerank.SourceBase.is_cache_expired",
        new_callable=PropertyMock,
    )
    def test_breakdown(self, mock_is_cache_expired: MagicMock):
        """Test the breakdown property."""
        mock_package = Mock()
        mock_breakdown = Mock()
        with self.subTest("Test cache not expired"), patch(
            "pip_rating.sources.sourcerank.SourceRank.get_from_cache"
        ) as mock_get_from_cache:
            mock_is_cache_expired.return_value = False
            mock_get_from_cache.return_value = {
                "breakdown": mock_breakdown,
            }
            sourcerank = SourceRank(mock_package)
            self.assertEqual(mock_breakdown, sourcerank.breakdown)
            mock_get_from_cache.assert_called_once_with()
        with self.subTest("Test cache expired"), patch(
            "pip_rating.sources.sourcerank.SourceRank.save_to_cache"
        ) as mock_save_to_cache:
            mock_is_cache_expired.return_value = True
            mock_save_to_cache.return_value = {
                "breakdown": mock_breakdown,
            }
            sourcerank = SourceRank(mock_package)
            self.assertEqual(mock_breakdown, sourcerank.breakdown)
            mock_save_to_cache.assert_called_once_with()

    @patch("pip_rating.sources.sourcerank.requests")
    def test_get_breakdown(self, mock_requests: MagicMock):
        """Test the get_breakdown method."""
        mock_requests.get.return_value.__enter__.return_value.content = SOURCERANK_PAGE
        package_name = "package_name"
        self.assertEqual(
            [
                ("basic_info_present", 1),
                ("source_repository_present", 1),
                ("readme_present", 1),
                ("license_present", 1),
                ("has_multiple_versions", 1),
                ("follows_semver", 0),
                ("recent_release", 1),
                ("not_brand_new", 1),
                ("is_1_or_greater", 1),
                ("dependent_projects", 10),
                ("dependent_repositories", 5),
                ("stars", 5),
                ("contributors", 2),
                ("librariesio_subscribers", 2),
                ("total", 32),
            ],
            list(SourceRank(package_name).get_breakdown()),
        )
