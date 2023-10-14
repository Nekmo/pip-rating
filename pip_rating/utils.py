import sys
from datetime import datetime


def parse_iso_datetime(iso_dt):
    if sys.version_info >= (3, 11):
        dt = datetime.fromisoformat(iso_dt)
    else:
        from dateutil import parser as dateutil_parser

        try:
            dt = datetime.fromisoformat(iso_dt)
        except ValueError:
            dt = dateutil_parser.isoparse(iso_dt)
    return dt
