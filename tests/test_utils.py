import sys
import unittest
import datetime
from pip_rating.utils import parse_iso_datetime

class TestParseIsoDatetime(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 11), "Test for Python 3.11 or higher")
    def test_python_311_or_higher(self):
        expected_dt = datetime.datetime(2023, 9, 14, 18, 56, 29, 702900, tzinfo=datetime.timezone.utc)
        iso_dt = '2023-09-14T18:56:29.702900Z'
        result = parse_iso_datetime(iso_dt)
        self.assertEqual(result, expected_dt)

    @unittest.skipIf(sys.version_info >= (3, 11), "Test for Python 3.10 or lower")
    def test_python_310_or_lower(self):
        expected_dt = datetime.datetime(2023, 9, 14, 18, 56, 29, 702900, tzinfo=datetime.timezone.utc)
        iso_dt = '2023-09-14T18:56:29.702900Z'
        result = parse_iso_datetime(iso_dt)
        self.assertEqual(result, expected_dt)



