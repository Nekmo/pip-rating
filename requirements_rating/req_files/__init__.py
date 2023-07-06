from pathlib import Path
from typing import Union, Type

from requirements_rating.req_files.base import ReqFileBase
from requirements_rating.req_files.requirements import RequirementsReqFile


REQ_FILE_CLASSES = {
    "requirements": RequirementsReqFile,
}


def get_req_file_cls(path: Union[str, Path]) -> Type[ReqFileBase]:
    """Get the requirement file class for the given path."""
    for req_file_cls in REQ_FILE_CLASSES.values():
        if req_file_cls.is_valid(path):
            return req_file_cls
    raise IOError(f"Could not find requirement file class for {path}")
