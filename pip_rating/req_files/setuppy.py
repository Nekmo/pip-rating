from pathlib import Path
from typing import Union, List
from unittest.mock import patch

from pip_rating.exceptions import RequirementsRatingParseError
from pip_rating.req_files import ReqFileBase


class SetuppyReqFile(ReqFileBase):
    """Parse install_requires from Setup.py file."""
    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> "SetuppyReqFile":
        """Find setup.py in the given directory."""
        if isinstance(directory, str):
            directory = Path(directory)
        path = directory / "setup.py"
        if path.exists():
            return cls(path)

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid setup.py file."""
        if isinstance(path, str):
            path = Path(path)
        return path.exists() and path.name == "setup.py"

    def get_dependencies(self) -> List[str]:
        """Get the dependencies from the setup.py file."""
        with patch("setuptools.setup") as mock_setuptools_setup, \
             patch("distutils.core.setup") as mock_distutils_setup, \
             open(self.path, "r") as file:
            try:
                exec(file.read())
            except Exception as e:
                raise RequirementsRatingParseError(f"Error executing '{self.path}' to parse dependencies.") from e
            mock_setup = None
            if mock_setuptools_setup.call_count:
                mock_setup = mock_setuptools_setup
            elif mock_distutils_setup.call_count:
                mock_setup = mock_distutils_setup
            if mock_setup is None:
                raise RequirementsRatingParseError(f"setup() function not called in '{self.path}'.")
            return mock_setup.mock_calls[0].kwargs.get("install_requires") or []
