import re
from pathlib import Path
from typing import Union, List, Optional

from pip_rating.req_files.base import ReqFileBase


COMMENT_REGEX = re.compile(r"(#.*)")
REQUIREMENTS_FILES = [
    "requirements.in", "requirements.txt",
    re.compile(r".*requirements.*\.in"), re.compile(r".*requirements.*\.txt")
]


class RequirementsReqFile(ReqFileBase):
    """Requirements requirement file."""
    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> Optional["ReqFileBase"]:
        """Find requirement file in the given directory."""
        if isinstance(directory, str):
            directory = Path(directory)
        for requirements_file in REQUIREMENTS_FILES:
            if isinstance(requirements_file, str) and (directory / requirements_file).exists():
                return cls(directory / requirements_file)
            if isinstance(requirements_file, re.Pattern):
                requirements_file = next(filter(lambda file: requirements_file.match(str(file)),
                                                directory.iterdir()), None)
                if requirements_file:
                    return cls(requirements_file)

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid requirement file."""
        if isinstance(path, str):
            path = Path(path)
        return path.exists() and path.suffix in [".txt", ".in"]

    def get_dependencies(self) -> List[str]:
        """Get the dependencies from the requirements file."""
        lines = []
        with open(str(self.path)) as f:
            for line in f:
                line = re.sub(COMMENT_REGEX, "", line).strip()
                if line:
                    lines.append(line)
        return lines
