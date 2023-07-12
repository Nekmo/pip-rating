from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Set, Optional, TypedDict, List

from anytree import Node

from pip_rating.rating import PackageRating, PackageRatingJson
from pip_rating.sources.audit import Audit, Vulnerability
from pip_rating.sources.pypi import Pypi
from pip_rating.sources.sourcecode_page import SourcecodePage
from pip_rating.sources.sourcerank import SourceRank

if TYPE_CHECKING:
    from pip_rating.dependencies import Dependencies
    from pip_rating.sources.sourcerank import SourceRankBreakdown
    from pip_rating.sources.pypi import PypiPackage


class PackageJson(TypedDict):
    name: str
    version: str
    sourcerank_breakdown: "SourceRankBreakdown"
    pypi_package: "PypiPackage"
    audit_vulnerabilities: List[Vulnerability]
    rating: PackageRatingJson
    dependencies: List["PackageJson"]


class Package:
    nodes: Set[Node]

    def __init__(self, dependencies: "Dependencies", name: str):
        self.name = name
        self.dependencies = dependencies
        self.nodes = set()

    @cached_property
    def first_node(self) -> Node:
        return next(iter(sorted(self.nodes, key=lambda n: n.depth)))

    @property
    def first_node_with_version(self) -> str:
        return f"{self.first_node.name}=={self.first_node.version}"

    @cached_property
    def sourcerank(self) -> SourceRank:
        return SourceRank(self.name)

    @cached_property
    def pypi(self) -> "Pypi":
        return Pypi(self.name)

    @cached_property
    def sourcecode_page(self) -> "SourcecodePage":
        return SourcecodePage(self)

    def get_audit(self, node: Node) -> "Audit":
        return Audit(self.name, node.version)

    @cached_property
    def rating(self) -> "PackageRating":
        return PackageRating(self)

    def get_node_from_parent(self, from_package: Optional["Package"]) -> Optional["Node"]:
        """Given this package and a parent package, return the node in the package that
        is a descendant of the parent package
        """
        if from_package is None:
            return self.first_node
        for node in self.nodes:
            for parent_node in from_package.nodes:
                if node in parent_node.descendants:
                    return node

    def get_descendant_packages(self) -> Iterator["Package"]:
        for descendant in self.first_node.descendants:
            yield self.dependencies.add_node_package(descendant)

    def get_child_packages(self) -> Iterator["Package"]:
        for child in self.first_node.children:
            yield self.dependencies.add_node_package(child)

    def add_node(self, node: Node):
        self.nodes.add(node)

    def as_json(self, from_package: Optional["Package"] = None) -> PackageJson:
        node = self.get_node_from_parent(from_package)
        return {
            "name": self.name,
            "version": node.version,
            "sourcerank_breakdown": self.sourcerank.breakdown,
            "pypi_package": self.pypi.package,
            "audit_vulnerabilities": self.get_audit(node).vulnerabilities,
            "rating": self.rating.as_json(from_package),
            "dependencies": [self.dependencies.packages[subnode.name].as_json(self) for subnode in node.children],
        }

    def __repr__(self) -> str:
        return f"<Package {self.name}>"
