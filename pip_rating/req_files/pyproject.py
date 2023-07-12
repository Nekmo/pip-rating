import re
from pathlib import Path
from typing import Union, List

from packaging.version import Version

from pip_rating.exceptions import RequirementsRatingParseError
from pip_rating.req_files import ReqFileBase
from pip_rating._compat import tomllib


def poetry_version(version: Union[str, dict, None]) -> str:
    """Convert Poetry version to PEP440 version."""
    if version is None:
        return ""
    if isinstance(version, dict):
        version_value = version.get("version")
        output = poetry_version(version_value)
        markers = []
        if version.get("python"):
            python_version = poetry_version(version['python']).split(",")
            python_version = [re.sub(r"(\d.*)", r"'\1'", version.strip()) for version in python_version]
            markers.append(" and ".join(f"python_version {version}" for version in python_version))
        if version.get("markers"):
            markers.append(version['markers'])
        if version.get("platform"):
            markers.append(f"platform_system=='{version['platform']}'")
        if markers:
            output += f" ; {' and '.join(markers)}"
        return output
    if version.startswith("^"):
        version = Version(version[1:])
        if version.major:
            return f">={version},<{version.major + 1}.0.0"
        elif version.minor:
            return f">={version},<{version.major}.{version.minor + 1}.0"
        elif version.micro:
            return f">={version},<{version.major}.{version.minor}.{version.micro + 1}"
        else:
            raise RequirementsRatingParseError(f"Invalid version '{version}'")
    if version and (version[0].isdigit() or version[0].startswith('*.')):
        return f"=={version}"
    if version and version[0] in "=<>!":
        return version
    raise RequirementsRatingParseError(f"Invalid version '{version}'")


class PyprojectReqFile(ReqFileBase):
    """Parse dependencies from pyproject.toml file."""
    @classmethod
    def find_in_directory(cls, directory: Union[str, Path]) -> "PyprojectReqFile":
        """Find pyproject.toml in the given directory."""
        if isinstance(directory, str):
            directory = Path(directory)
        path = directory / "pyproject.toml"
        if path.exists():
            return cls(path)

    @classmethod
    def is_valid(cls, path: Union[str, Path]) -> bool:
        """Check if the given path is a valid pyproject.toml file."""
        if isinstance(path, str):
            path = Path(path)
        return path.exists() and path.name == "pyproject.toml"

    def get_dependencies(self) -> List[str]:
        """Get the dependencies from the pyproject.toml file."""
        with open(str(self.path), "rb") as file:
            data = tomllib.load(file)
        sentinel = object()
        project_dependencies = data.get("project", {}).get("dependencies") or sentinel
        if project_dependencies is not sentinel:
            return project_dependencies
        poetry_dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        if poetry_dependencies is not sentinel:
            return [
                f"{name}{poetry_version(version)}"
                for name, version in poetry_dependencies.items() if name != "python"
            ]
        raise RequirementsRatingParseError(f"Dependencies not found in the file '{self.path}'.")
