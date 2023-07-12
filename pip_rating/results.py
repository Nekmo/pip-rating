import datetime
import json
from typing import Optional, TYPE_CHECKING, Union, TypedDict, List

from requests import __version__
from rich.console import Console
from rich.progress import Progress, TaskID, TaskProgressColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.status import Status
from rich.table import Table
from rich.tree import Tree


if TYPE_CHECKING:
    from pip_rating.packages import Package
    from pip_rating.rating import ScoreBase
    from pip_rating.dependencies import Dependencies


MIN_PACKAGE_NAME = 15
FORMATS = ["text", "tree", "json", "only-rating"]


def colorize_score(score: Union["ScoreBase", int]) -> str:
    """Colorize the score."""
    if int(score) < 0:
        return f"[bold red]{score}[/bold red]"
    if int(score) > 0:
        return f"[bold green]+{score}[/bold green]"
    return f"[bold bright_black]{score}[/bold bright_black]"


def colorize_rating(score: Union["ScoreBase", int]) -> "RatingLetter":
    """Colorize the rating."""
    for rating_letter in RATING_LETTERS:
        if max(0, int(score)) >= rating_letter.score:
            return rating_letter


def colorize_rating_package(package: "Package", parent_package: Optional["Package"] = None) -> str:
    """Colorize the rating of the package."""
    colorized_rating = colorize_rating(package.rating.get_rating_score(parent_package))
    colorized_global_rating = colorize_rating(package.rating.get_global_rating_score(parent_package))
    if colorized_rating > colorized_global_rating:
        return f"{colorized_rating} -> {colorized_global_rating}"
    else:
        return f"{colorized_rating}"


def add_tree_node(dependencies: "Dependencies", tree: "Tree", package: "Package",
                  parent_package: Optional["Package"] = None):
    if parent_package is None:
        tree = tree.add(
            f"[bold]:package: {package.name} ({colorize_rating_package(package)})[/bold]"
        )
    for child in package.get_node_from_parent(parent_package).children:
        subpackage = dependencies.packages[child.name]
        subtree_package = tree.add(
            f"[bold]{child.name} ({colorize_rating_package(subpackage, package)})[/bold]"
        )
        add_tree_node(dependencies, subtree_package, subpackage, package)


class RatingLetter:
    """Rating letter."""

    def __init__(self, letter: str, score: int, color: str):
        self.letter = letter
        self.score = score
        self.color = color

    def __lt__(self, other):
        return self.score < other.score

    def __gt__(self, other):
        return self.score > other.score

    def __le__(self, other):
        return self.score <= other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __eq__(self, other):
        return self.score == other.score

    def __ne__(self, other):
        return self.score != other.score

    def __str__(self) -> str:
        return f"[bold {self.color}]{self.letter}[/bold {self.color}]"

    def __repr__(self) -> str:
        return f"<RatingLetter {self.letter}>"


RATING_LETTERS = [
    RatingLetter("S", 30, "bright_cyan"),
    RatingLetter("A", 25, "green3"),
    RatingLetter("B", 20, "green_yellow"),
    RatingLetter("C", 15, "gold1"),
    RatingLetter("D", 10, "orange1"),
    RatingLetter("E", 5, "orange_red1"),
    RatingLetter("F", 0, "bright_red"),
]


class JsonResults(TypedDict):
    """JSON results"""

    requirements: List[str]
    updated_at: str
    schema_version: str
    global_rating_letter: str
    global_rating_score: int
    packages: List[dict]


class Results:
    """Print pip-ratings results to the terminal."""
    _status: Optional[Status]
    progress: Optional[Progress]
    task: Optional[TaskID]

    def __init__(self):
        self.console = Console()
        self.console.status("[bold green]Loading...")
        self._status = None
        self.progress = None
        self.task = None

    @property
    def status(self) -> Optional[Status]:
        if not self._status:
            self._status = self.console.status("[bold green]Waiting...")
            self._status.start()
        return self._status

    def processing_package(self, package):
        self.status.update(f"Processing package [bold green]{package}[/bold green]...")

    def analizing_package(self, package: str, total: int):
        if self._status:
            self._status.stop()
        if not self.progress:
            self.progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="blue"),
                TaskProgressColumn(),
                TimeRemainingColumn(),
                console=self.console,
            )
            self.task = self.progress.add_task("Analizing packages...", total=total)
            self.progress.start()
        spaces = " " * (MIN_PACKAGE_NAME - len(package))
        self.progress.update(
            self.task,
            description=f"Analizing package [bold blue]{package}[/bold blue]..." + spaces,
            advance=1,
            refresh=True,
        )

    def get_global_rating_score(self, dependencies: "Dependencies") -> int:
        global_rating_score = dependencies.get_global_rating_score()
        if self.progress:
            self.progress.update(self.task, description="[bold green]Analyzed all packages[/bold green]", refresh=True)
            self.progress.stop()
        return global_rating_score

    def show_results(self, dependencies: "Dependencies", format_name: str = "text"):
        if format_name not in FORMATS:
            raise ValueError(f"Format name must be one of {FORMATS}")
        if format_name == "text":
            self.show_packages_results(dependencies)
        elif format_name == "tree":
            self.show_tree_results(dependencies)
        elif format_name == "json":
            self.show_json_results(dependencies)
        elif format_name == "only-rating":
            self.show_only_rating_results(dependencies)
        else:
            raise ValueError(f"Format name must be one of {', '.join(FORMATS)}")

    def show_packages_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        for package in dependencies.packages.values():
            if package.name not in dependencies.req_file:
                continue
            global_rating_score = package.rating.get_global_rating_score()
            global_rating_score_letter = colorize_rating(global_rating_score)
            rating_score_letter = colorize_rating(package.rating.get_rating_score())
            vulnerabilities = []
            if not global_rating_score:
                vulnerabilities = package.rating.get_vulnerabilities()
            if vulnerabilities or global_rating_score_letter >= rating_score_letter:
                print_score = f"{global_rating_score_letter}"
            else:
                print_score = f"{rating_score_letter} -> {global_rating_score_letter}"
            self.console.print(
                f":package: Package [bold blue]{package.name}[/bold blue]: " + print_score
            )
            for key, value in package.rating.breakdown_scores:
                key = key.split(".")[-1].replace("iso_dt", "").replace("_", " ").capitalize()
                self.console.print(f"  :black_medium-small_square: {key}: {colorize_score(value)}")
            if global_rating_score < package.rating.rating_score:
                low_rating_dependences = [
                    f'{pkg.name} ({colorize_rating(score)})' for pkg, score
                    in package.rating.descendant_rating_scores if colorize_rating(score) < rating_score_letter
                ]
                self.console.print(
                    f"  :arrow_lower_right: Low rating dependencies: {', '.join(low_rating_dependences)}"
                )
            if vulnerabilities:
                self.console.print(
                    f"  :biohazard: Vulnerabilities found: [bold grey53]"
                    f"{', '.join([vuln['id'] for vuln in vulnerabilities])}[/bold grey53]"
                )
            self.console.print("")
        self.console.print("")
        table = Table(show_header=False)
        table.add_row(f"Global rating score: {colorize_rating(global_rating_score)}")
        self.console.print(table)

    def show_tree_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        req_file_name = str(dependencies.req_file) if dependencies.req_file else "Packages list"
        tree = Tree(f"[bold]{req_file_name} ({colorize_rating(global_rating_score)})[/bold]")
        for package in dependencies.packages.values():
            if package.name not in dependencies.req_file:
                continue
            add_tree_node(dependencies, tree, package)
        self.console.print(tree)

    def get_json_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        packages = [package for package in dependencies.packages.values() if package.name in dependencies.req_file]
        return {
            "requirements": dependencies.req_file,
            "updated_at": datetime.datetime.now().isoformat(),
            "schema_version": __version__,
            "global_rating_letter": colorize_rating(global_rating_score).letter,
            "global_rating_score": global_rating_score,
            "packages": [package.as_json() for package in packages]
        }

    def show_json_results(self, dependencies: "Dependencies"):
        self.console = Console(stderr=True)
        results = self.get_json_results(dependencies)
        print(json.dumps(results, indent=4, sort_keys=False))

    def show_only_rating_results(self, dependencies: "Dependencies"):
        self.console = Console(stderr=True)
        global_rating_score = self.get_global_rating_score(dependencies)
        self.console = Console()
        self.console.print(f"{colorize_rating(global_rating_score)}")
