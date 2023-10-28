import os.path
import re
from functools import cached_property
from multiprocessing import cpu_count
from typing import Optional, Union, Dict, TYPE_CHECKING, Hashable

from anytree import Node
from pipgrip.cli import build_tree
from pipgrip.libs.mixology.package import Package as PipgripPackage
from pipgrip.libs.mixology.partial_solution import PartialSolution
from pipgrip.libs.mixology.result import SolverResult
from pipgrip.libs.mixology.version_solver import VersionSolver
from pipgrip.package_source import PackageSource

from pip_rating.packages import Package

if TYPE_CHECKING:
    from pip_rating.req_files.base import ReqFileBase
    from pip_rating.results import Results


COMMENT_REGEX = re.compile(r"(#.*)")
PACKAGE_NAME_REGEX = re.compile(
    r"([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])", re.IGNORECASE
)
version_resolver_threads = os.environ.get(
    "VERSION_RESOLVER_THREADS", max(8, cpu_count() * 2)
)


def get_package_name(value: str) -> str:
    """Get the package name from the given value.

    :param value: The value to get the package name from.
    :return: The package name. If the value is not a package name, the value will be returned.
    """
    r = PACKAGE_NAME_REGEX.search(value)
    if r:
        return r.group(1)
    return value


class DependenciesVersionSolver(VersionSolver):
    def __init__(self, results: "Results", source: "PackageSource", threads: int = 1):
        self.results = results
        super().__init__(source, threads=threads)

    def _propagate(self, package: PipgripPackage):  # type: (Hashable) -> None
        if package.name != "_root_":
            self.results.processing_package(package)
        return super()._propagate(package)


class Dependencies:
    """
    Dependencies class. This class is responsible for getting the packages tree.
    """

    def __init__(
        self,
        results: "Results",
        req_file: "ReqFileBase",
        cache_dir: Optional[str] = None,
        index_url: Optional[str] = None,
        extra_index_url: Optional[str] = None,
        pre: bool = False,
        ignore_packages: Optional[list] = None,
    ):
        """Initialize the Dependencies class using the given req_file.

        :param results: The results instance. This instance will be used to print the results in the console.
        :param req_file: Dependencies list as req_file.
        :param cache_dir: The cache directory path.
        :param index_url: The index URL.
        :param extra_index_url: The extra index URL.
        :param pre: Whether to include pre-release and development versions. Defaults to False.
        :param ignore_packages: List of packages to ignore.
        """
        self.results = results
        self.req_file = req_file
        self.cache_dir = cache_dir
        self.index_url = index_url
        self.extra_index_url = extra_index_url
        self.pre = pre
        self.packages = {}  # type: Dict[str, Package]
        self.ignore_packages = ignore_packages or []

    @cached_property
    def package_source(self) -> PackageSource:
        """Describe requirements, and discover dependencies on demand."""
        return PackageSource(
            cache_dir=self.cache_dir,
            index_url=self.index_url,
            extra_index_url=self.extra_index_url,
            pre=self.pre,
        )

    def _get_version_solution(self) -> Union[SolverResult, PartialSolution]:
        """Get the version solution for the packages. The version solver that finds a
        set of package versions that satisfy the root package's dependencies.
        """
        solver = DependenciesVersionSolver(
            self.results, self.package_source, threads=version_resolver_threads
        )
        for root_dependency in self.req_file:
            if get_package_name(root_dependency) in self.ignore_packages:
                continue
            self.package_source.root_dep(root_dependency)
        try:
            return solver.solve()
        except RuntimeError as e:
            if "Failed to download/build wheel" not in str(e):
                # only continue handling expected RuntimeErrors
                raise
            # Remove the failed package from the package source
            r = re.match("Failed to download/build wheel for (.+)", str(e))
            failed_package_name = r.group(1)
            failed_package_name = get_package_name(failed_package_name)
            if failed_package_name in self.ignore_packages:
                # The package is already in the ignore packages list. This is probably a bug.
                raise RuntimeError(
                    "An already ignored packet has been used. It can't be ignored again. "
                    "This is probably a programming error."
                )
            self.ignore_packages.append(failed_package_name)
            # Clear the cached package_source property
            del self.__dict__["package_source"]
            # Retry the version solver without the failed package
            return self._get_version_solution()

    @cached_property
    def version_solution(self) -> Union[SolverResult, PartialSolution]:
        """Get the version solution for the packages. The version solver that finds a
        set of package versions that satisfy the root package's dependencies.
        """
        return self._get_version_solution()

    @cached_property
    def dependencies_tree(self) -> Node:
        """Get the dependencies tree."""
        decision_packages = {}
        for package, version in self.version_solution.decisions.items():
            if package == PipgripPackage.root():
                continue
            decision_packages[package] = version
        tree_root, packages_tree_dict, packages_flat = build_tree(
            self.package_source, decision_packages
        )
        return tree_root

    def add_node_package(self, node: Node) -> Optional[Package]:
        """Add the package as a node to the packages' dict."""
        if node.name in self.ignore_packages:
            return
        if node.name not in self.packages:
            self.packages[node.name] = Package(self, node.name)
        self.packages[node.name].add_node(node)
        return self.packages[node.name]

    def get_packages(self):
        for dependency_node in self.dependencies_tree.children:
            self.add_node_package(dependency_node)
        return self.packages

    @cached_property
    def total_size(self):
        return sum(
            sum([node.size for node in package.nodes])
            for package in self.packages.values()
        )

    def get_global_rating_score(self):
        final_global_rating_score = None
        packages = dict(self.get_packages()).values()
        for package in packages:
            if package.rating is None:
                continue
            global_rating_score = package.rating.get_global_rating_score()
            if final_global_rating_score is None:
                final_global_rating_score = global_rating_score
            else:
                final_global_rating_score = min(
                    global_rating_score, final_global_rating_score
                )
        return final_global_rating_score
