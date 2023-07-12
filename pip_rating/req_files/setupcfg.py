from pathlib import Path
from typing import Union, List

from setuptools.config.setupcfg import read_configuration

from pip_rating.req_files import ReqFileBase


class SetupcfgReqFile(ReqFileBase):
    """Parse install_requires from Setup.cfg file."""
    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> "SetupcfgReqFile":
        """Find setup.cfg in the given directory."""
        if isinstance(directory, str):
            directory = Path(directory)
        path = directory / "setup.cfg"
        if path.exists():
            return cls(path)

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid setup.cfg file."""
        if isinstance(path, str):
            path = Path(path)
        return path.exists() and path.name == "setup.cfg"

    def get_dependencies(self) -> List[str]:
        """Get the dependencies from the setup.cfg file."""
        configuration = read_configuration(self.path)
        return configuration.get("options", {}).get("install_requires") or []
