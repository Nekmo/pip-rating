import datetime
import json
import os
from functools import cached_property
from pathlib import Path

from platformdirs import user_cache_dir


class SourceBase:
    """Base class for all sources"""
    source_name: str
    max_cache_age = datetime.timedelta(days=7)

    def __init__(self, package_name: str):
        self.package_name = package_name

    @property
    def cache_dir(self) -> Path:
        return Path(user_cache_dir()) / "pip-rating" / self.source_name

    @property
    def cache_file(self) -> Path:
        return self.cache_dir / f"{self.package_name}.json"

    @cached_property
    def is_cache_expired(self) -> bool:
        return not self.cache_file.exists() or \
            self.cache_file.stat().st_mtime < (datetime.datetime.now() - self.max_cache_age).timestamp()

    def get_from_cache(self) -> dict:
        with open(self.cache_file) as file:
            return json.load(file)

    def get_cache_data(self) -> dict:
        raise NotImplementedError

    def save_to_cache(self) -> dict:
        cache_data = self.get_cache_data()
        os.makedirs(str(self.cache_file.parent), exist_ok=True)
        with open(self.cache_file, "w") as file:
            json.dump(cache_data, file)
        return cache_data
