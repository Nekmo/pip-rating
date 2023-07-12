from pathlib import Path
from typing import Union, Type

from pip_rating.exceptions import RequirementsRatingInvalidFile, RequirementsRatingMissingReqFile
from pip_rating.req_files.base import ReqFileBase
from pip_rating.req_files.pipfile import PipfileReqFile
from pip_rating.req_files.pyproject import PyprojectReqFile
from pip_rating.req_files.requirements import RequirementsReqFile
from pip_rating.req_files.setupcfg import SetupcfgReqFile
from pip_rating.req_files.setuppy import SetuppyReqFile


REQ_FILE_CLASSES = {
    "requirements": RequirementsReqFile,
    "setup.cfg": SetupcfgReqFile,
    "setup.py": SetuppyReqFile,
    "Pipfile": PipfileReqFile,
    "pyproject.toml": PyprojectReqFile,
}


def get_req_file_cls(path: Union[str, Path]) -> Type[ReqFileBase]:
    """Get the requirement file class for the given path."""
    for req_file_cls in REQ_FILE_CLASSES.values():
        if req_file_cls.is_valid(path):
            return req_file_cls
    raise RequirementsRatingInvalidFile(f"Could not find requirement file class for {path}")


def find_in_directory(directory: Union[str, Path]) -> ReqFileBase:
    """Find requirement file in the given directory."""
    if isinstance(directory, str):
        directory = Path(directory)
    for req_file_cls in REQ_FILE_CLASSES.values():
        req_file = req_file_cls.find_in_directory(directory)
        if req_file:
            return req_file
    raise RequirementsRatingMissingReqFile(str(directory))
