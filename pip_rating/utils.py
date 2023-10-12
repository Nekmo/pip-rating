import sys
from datetime import datetime
from dateutil import parser as dateutil_parser

def parse_iso_datetime(iso_dt):
    if sys.version_info >= (3, 11):
        dt = datetime.fromisoformat(iso_dt)
    else:
        try:
            dt = datetime.fromisoformat(iso_dt)
        except ValueError:
            dt = dateutil_parser.isoparse(iso_dt)
    return dt