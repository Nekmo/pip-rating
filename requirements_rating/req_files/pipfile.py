from pathlib import Path
from typing import Union, List

from pipfile import Pipfile

from requirements_rating.req_files import ReqFileBase


class PipfileReqFile(ReqFileBase):
    """Parse install_requires from Setup.cfg file."""
    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> "PipfileReqFile":
        """Find setup.cfg in the given directory."""
        if isinstance(directory, str):
            directory = Path(directory)
        path = directory / "Pipfile"
        if path.exists():
            return cls(path)

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid setup.cfg file."""
        if isinstance(path, str):
            path = Path(path)
        return path.exists() and path.name == "Pipfile"

    def get_dependencies(self) -> List[str]:
        """Get the dependencies from the setup.cfg file."""
        pipfile = Pipfile.load(self.path)
        return [f"{name}{ver}" for name, ver in pipfile.data["default"].items()]
