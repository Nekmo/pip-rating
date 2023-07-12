from pathlib import Path
from typing import Union, List, Optional

from pkg_resources import Requirement


class ReqFileBase(list):
    """Base class for requirement files."""
    def __init__(self, path: Union[str, Path]):
        """Initialize the requirement file."""
        if isinstance(path, str):
            path = Path(path)
        self.path = path
        if not self.path.exists():
            raise IOError(f"File {self.path} does not exist")
        super().__init__(self.get_dependencies())

    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> Optional["ReqFileBase"]:
        """Find requirement file in the given directory."""
        raise NotImplementedError

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid requirement file."""
        raise NotImplementedError

    def get_dependencies(self) -> List[str]:
        """Get the dependencies from the file."""
        raise NotImplementedError

    def __contains__(self, item: str) -> bool:
        req = Requirement(item)
        for package in self:
            package = Requirement(package)
            if (not req.specifier and package.name.lower() == req.name.lower()) or package == req:
                return True
        return False

    def __str__(self) -> str:
        return self.path.name

    def __repr__(self) -> str:
        return f"<ReqFile {self.path}>"
