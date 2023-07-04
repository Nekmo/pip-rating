import os.path
import re
from functools import cached_property
from multiprocessing import cpu_count
from typing import Optional, List, Union, Dict

from anytree import Node
from pipgrip.cli import build_tree
from pipgrip.libs.mixology.package import Package as PipgripPackage
from pipgrip.libs.mixology.partial_solution import PartialSolution
from pipgrip.libs.mixology.result import SolverResult
from pipgrip.libs.mixology.version_solver import VersionSolver
from pipgrip.package_source import PackageSource

from requirements_rating.packages import Package

COMMENT_REGEX = re.compile(r"(#.*)")
version_resolver_threads = os.environ.get("VERSION_RESOLVER_THREADS", max(8, cpu_count() * 2))


class Requirements:
    """
    Requirements class. This class is responsible for parsing the requirements file and
    getting the packages tree.
    """
    def __init__(self, requirements_file: str, cache_dir: Optional[str] = None, index_url: Optional[str] = None,
                 extra_index_url: Optional[str] = None, pre: bool = False):
        """Initialize the Requirements class using the given requirements file.

        :param requirements_file: The requirements file path.
        :param cache_dir: The cache directory path.
        :param index_url: The index URL.
        :param extra_index_url: The extra index URL.
        :param pre: Whether to include pre-release and development versions. Defaults to False.
        """
        self.requirements_file = requirements_file
        self.cache_dir = cache_dir
        self.index_url = index_url
        self.extra_index_url = extra_index_url
        self.pre = pre
        self.packages = {}  # type: Dict[str, Package]

    @cached_property
    def main_requirements(self) -> List[str]:
        """Get the requirements from the requirements file."""
        if not os.path.lexists(self.requirements_file):
            raise IOError(f"Requirements file {self.requirements_file} does not exist")
        lines = []
        with open(self.requirements_file) as f:
            for line in f:
                line = re.sub(COMMENT_REGEX, "", line).strip()
                if line:
                    lines.append(line)
        return lines

    @cached_property
    def package_source(self) -> PackageSource:
        """Describe requirements, and discover dependencies on demand."""
        return PackageSource(
            cache_dir=self.cache_dir,
            index_url=self.index_url,
            extra_index_url=self.extra_index_url,
            pre=self.pre,
        )

    @cached_property
    def version_solution(self) -> Union[SolverResult, PartialSolution]:
        """Get the version solution for the packages. The version solver that finds a
        set of package versions that satisfy the root package's dependencies.
        """
        solver = VersionSolver(self.package_source, threads=version_resolver_threads)
        for root_dependency in self.main_requirements:
            self.package_source.root_dep(root_dependency)
        try:
            return solver.solve()
        except RuntimeError as e:
            if "Failed to download/build wheel" not in str(e):
                # only continue handling expected RuntimeErrors
                raise
            return solver.solution

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

    def add_node_package(self, node: Node) -> Package:
        """Add the package as a node to the packages' dict."""
        if node.name not in self.packages:
            self.packages[node.name] = Package(self, node.name)
        self.packages[node.name].add_node(node)
        return self.packages[node.name]

    def get_packages(self):
        for dependency_node in self.dependencies_tree.children:
            self.add_node_package(dependency_node)
        return self.packages
