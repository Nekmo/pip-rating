from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Set

from anytree import Node

from requirements_rating.rating import PackageRating
from requirements_rating.sources.audit import Audit
from requirements_rating.sources.pypi import Pypi
from requirements_rating.sources.sourcerank import SourceRank

if TYPE_CHECKING:
    from requirements_rating.dependencies import Dependencies


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

    def get_audit(self, node: Node) -> "Audit":
        return Audit(self.name, node.version)

    @cached_property
    def rating(self) -> "PackageRating":
        return PackageRating(self)

    def get_descendant_packages(self) -> Iterator["Package"]:
        for descendant in self.first_node.descendants:
            yield self.dependencies.add_node_package(descendant)

    def get_child_packages(self) -> Iterator["Package"]:
        for child in self.first_node.children:
            yield self.dependencies.add_node_package(child)

    def add_node(self, node: Node):
        self.nodes.add(node)

    def __repr__(self) -> str:
        return f"<Package {self.name}>"
