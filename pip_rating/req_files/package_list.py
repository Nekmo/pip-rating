from pathlib import Path
from typing import List, Union, Optional

from pip_rating.req_files import ReqFileBase


class PackageList(ReqFileBase):
    """Package list."""

    def __init__(self, packages: List[str]):
        """Initialize the package list."""
        list.__init__(self, packages)

    def get_dependencies(self) -> List[str]:
        """Get the dependencies."""
        return self

    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> Optional["ReqFileBase"]:
        """Find requirement file in the given directory."""
        raise NotImplementedError

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid requirement file."""
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self)

    def __repr__(self) -> str:
        return f"<ReqFile ({len(self)})>"
