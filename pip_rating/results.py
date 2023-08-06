import datetime
import json
import os
from typing import Optional, TYPE_CHECKING, Union, TypedDict, List, Any

from pip_rating import __version__
from rich.console import Console
from rich.progress import (
    Progress,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.status import Status
from rich.table import Table
from rich.tree import Tree


if TYPE_CHECKING:
    from pip_rating.packages import Package
    from pip_rating.rating import ScoreBase
    from pip_rating.dependencies import Dependencies


MIN_PACKAGE_NAME = 15
FORMATS = ["text", "tree", "json", "only-rating", "badge"]
BADGE_FLAT_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="82"
     height="20" role="img" aria-label="pip-rating: {letter}">
    <title>pip-rating: {letter}</title>
    <linearGradient id="s" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="r"><rect width="82" height="20" rx="3" fill="#fff"/></clipPath>
    <g clip-path="url(#r)">
        <rect width="65" height="20" fill="#555"/><rect x="65" width="17" height="20" fill="{bgcolor}"/>
        <rect width="82" height="20" fill="url(#s)"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
       text-rendering="geometricPrecision" font-size="110">
       <text aria-hidden="true" x="335" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="550">
       pip-rating
       </text>
       <text x="335" y="140" transform="scale(.1)" fill="#fff" textLength="550">pip-rating</text>
       <text aria-hidden="true" x="725" y="150" fill="{shcolor}" fill-opacity=".3" transform="scale(.1)"
             textLength="70">
       {letter}
       </text>
       <text x="725" y="140" transform="scale(.1)" fill="{color}" textLength="70">{letter}</text>
    </g>
</svg>
"""
BADGE_FLAT_SQUARE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="82" height="20" role="img"
     aria-label="pip-rating: {letter}">
    <title>pip-rating: {letter}</title>
    <g shape-rendering="crispEdges">
        <rect width="65" height="20" fill="#555"/><rect x="65" width="17" height="20" fill="{bgcolor}"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
       text-rendering="geometricPrecision" font-size="110">
        <text x="335" y="140" transform="scale(.1)" fill="#fff" textLength="550">pip-rating</text>
        <text x="725" y="140" transform="scale(.1)" fill="{color}" textLength="70">{letter}</text>
    </g>
</svg>
"""
BADGE_FOR_THE_BADGE_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="128.75" height="28" role="img"
     aria-label="PIP-RATING: {letter}">
    <title>PIP-RATING: {letter}</title>
    <g shape-rendering="crispEdges">
        <rect width="96.5" height="28" fill="#555"/>
        <rect x="96.5" width="32.25" height="28" fill="{bgcolor}"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
       text-rendering="geometricPrecision" font-size="100">
        <text transform="scale(.1)" x="482.5" y="175"
              textLength="725" fill="#fff">
            PIP-RATING
        </text>
        <text transform="scale(.1)" x="1126.25" y="175" textLength="82.5" fill="{color}"
              font-weight="bold">
            {letter}
        </text>
    </g>
</svg>
"""
PIP_RATING_BADGE_COLORS = {
    "S": os.environ.get("PIP_RATING_BADGE_S_COLOR") or "#007EC6",
    "A": os.environ.get("PIP_RATING_BADGE_A_COLOR") or "#44CC11",
    "B": os.environ.get("PIP_RATING_BADGE_B_COLOR") or "#97CA00",
    "C": os.environ.get("PIP_RATING_BADGE_C_COLOR") or "#FFD700",
    "D": os.environ.get("PIP_RATING_BADGE_D_COLOR") or "#FFAF00",
    "E": os.environ.get("PIP_RATING_BADGE_E_COLOR") or "#FF5F00",
    "F": os.environ.get("PIP_RATING_BADGE_F_COLOR") or "#E05D44",
}
PIP_RATING_BADGES = {
    "flat": BADGE_FLAT_SVG,
    "flat-square": BADGE_FLAT_SQUARE_SVG,
    "for-the-badge": BADGE_FOR_THE_BADGE_SVG,
}
PIP_RATING_BADGE_DEFAULT_STYLE = "flat"
PIP_RATING_BADGE_STYLE = os.environ.get(
    "PIP_RATING_BADGE_STYLE", PIP_RATING_BADGE_DEFAULT_STYLE
)


def get_luminance(hex_color: str) -> float:
    """Get the luminance of a color as float."""
    color = hex_color[1:]
    hex_red = int(color[0:2], base=16)
    hex_green = int(color[2:4], base=16)
    hex_blue = int(color[4:6], base=16)
    return hex_red * 0.2126 + hex_green * 0.7152 + hex_blue * 0.0722


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


def colorize_rating_package(
    package: "Package", parent_package: Optional["Package"] = None
) -> str:
    """Colorize the rating of the package."""
    colorized_rating = colorize_rating(package.rating.get_rating_score(parent_package))
    colorized_global_rating = colorize_rating(
        package.rating.get_global_rating_score(parent_package)
    )
    if colorized_rating > colorized_global_rating:
        return f"{colorized_rating} -> {colorized_global_rating}"
    else:
        return f"{colorized_rating}"


def add_tree_node(
    dependencies: "Dependencies",
    tree: "Tree",
    package: "Package",
    parent_package: Optional["Package"] = None,
):
    if parent_package is None:
        tree = tree.add(
            f"[bold]:package: {package.name} ({colorize_rating_package(package)})[/bold]"
        )
    for child in package.get_node_from_parent(parent_package).children:
        if child.name not in dependencies.packages:
            continue
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

    def __init__(self, to_file: Optional[str] = None):
        results_file = None
        if to_file:
            results_file = open(to_file, "w")
        self.progress_console = Console(stderr=True)
        self.progress_console.status("[bold green]Loading...")
        self.results_console = Console(file=results_file)
        self._status = None
        self.progress = None
        self.task = None
        self.to_file = to_file

    @property
    def status(self) -> Optional[Status]:
        if not self._status:
            self._status = self.progress_console.status("[bold green]Waiting...")
            self._status.start()
        return self._status

    def processing_package(self, package: Any):
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
                console=self.progress_console,
            )
            self.task = self.progress.add_task("Analizing packages...", total=total)
            self.progress.start()
        spaces = " " * (MIN_PACKAGE_NAME - len(package))
        self.progress.update(
            self.task,
            description=f"Analizing package [bold blue]{package}[/bold blue]..."
            + spaces,
            advance=1,
            refresh=True,
        )

    def get_global_rating_score(self, dependencies: "Dependencies") -> int:
        global_rating_score = dependencies.get_global_rating_score()
        if self.progress:
            self.progress.update(
                self.task,
                description="[bold green]Analyzed all packages[/bold green]",
                refresh=True,
            )
            self.progress.stop()
        return global_rating_score

    def show_results(self, dependencies: "Dependencies", format_name: str = "text"):
        """Show results depending on the format. Optionally save to a file.

        :param dependencies: Dependencies
        :param format_name: Format name. Choices: FORMATS
        """
        if format_name == "text":
            self.show_packages_results(dependencies)
        elif format_name == "tree":
            self.show_tree_results(dependencies)
        elif format_name == "json":
            self.show_json_results(dependencies)
        elif format_name == "only-rating":
            self.show_only_rating_results(dependencies)
        elif format_name == "badge":
            self.show_badge_results(dependencies)
        else:
            raise ValueError(f"Format name must be one of {', '.join(FORMATS)}")

    def show_packages_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        for package in dependencies.packages.values():
            if package.name not in dependencies.req_file:
                continue
            package_global_rating_score = package.rating.get_global_rating_score()
            package_global_rating_score_letter = colorize_rating(
                package_global_rating_score
            )
            rating_score_letter = colorize_rating(package.rating.get_rating_score())
            vulnerabilities = []
            if not package_global_rating_score:
                vulnerabilities = package.rating.get_vulnerabilities()
            if (
                vulnerabilities
                or package_global_rating_score_letter >= rating_score_letter
            ):
                print_score = f"{package_global_rating_score_letter}"
            else:
                print_score = (
                    f"{rating_score_letter} -> {package_global_rating_score_letter}"
                )
            self.results_console.print(
                f":package: Package [bold blue]{package.name}[/bold blue]: "
                + print_score
            )
            for key, value in package.rating.breakdown_scores:
                key = (
                    key.split(".")[-1]
                    .replace("iso_dt", "")
                    .replace("_", " ")
                    .capitalize()
                )
                self.results_console.print(
                    f"  :black_medium-small_square: {key}: {colorize_score(value)}"
                )
            if package_global_rating_score < package.rating.rating_score:
                low_rating_dependences = [
                    f"{pkg.name} ({colorize_rating(score)})"
                    for pkg, score in package.rating.descendant_rating_scores
                    if colorize_rating(score) < rating_score_letter
                ]
                self.results_console.print(
                    f"  :arrow_lower_right: Low rating dependencies: {', '.join(low_rating_dependences)}"
                )
            if vulnerabilities:
                self.results_console.print(
                    f"  :biohazard: Vulnerabilities found: [bold grey53]"
                    f"{', '.join([vuln['id'] for vuln in vulnerabilities])}[/bold grey53]"
                )
            self.results_console.print("")
        self.results_console.print("")
        table = Table(show_header=False)
        table.add_row(f"Global rating score: {colorize_rating(global_rating_score)}")
        self.results_console.print(table)

    def show_tree_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        req_file_name = (
            str(dependencies.req_file) if dependencies.req_file else "Packages list"
        )
        tree = Tree(
            f"[bold]{req_file_name} ({colorize_rating(global_rating_score)})[/bold]"
        )
        for package in dependencies.packages.values():
            if package.name not in dependencies.req_file:
                continue
            add_tree_node(dependencies, tree, package)
        self.results_console.print(tree)

    def get_json_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        packages = [
            package
            for package in dependencies.packages.values()
            if package.name in dependencies.req_file
        ]
        return {
            "requirements": dependencies.req_file,
            "updated_at": datetime.datetime.now().isoformat(),
            "schema_version": __version__,
            "global_rating_letter": colorize_rating(global_rating_score).letter,
            "global_rating_score": global_rating_score,
            "packages": [package.as_json() for package in packages],
        }

    def show_json_results(self, dependencies: "Dependencies"):
        results = self.get_json_results(dependencies)
        if self.to_file:
            with open(self.to_file, "w") as file:
                json.dump(results, file, indent=4, sort_keys=False)
        else:
            print(json.dumps(results, indent=4, sort_keys=False))

    def show_only_rating_results(self, dependencies: "Dependencies"):
        global_rating_score = self.get_global_rating_score(dependencies)
        self.results_console.print(f"{colorize_rating(global_rating_score)}")

    def show_badge_results(self, dependencies: "Dependencies") -> None:
        """Show the badge depending on the global rating score.
        The badge is printed as a svg image

        :param dependencies: Dependencies
        """
        letter = colorize_rating(self.get_global_rating_score(dependencies)).letter
        badge = PIP_RATING_BADGES.get(
            PIP_RATING_BADGE_STYLE, PIP_RATING_BADGE_DEFAULT_STYLE
        )
        badge_color = PIP_RATING_BADGE_COLORS[letter]
        luminance = get_luminance(badge_color)
        if luminance < 180:
            color = "fff"
            shcolor = "#010101"
        else:
            color = "#333"
            shcolor = "#ccc"
        self.results_console.print(
            badge.format(
                letter=letter,
                bgcolor=badge_color,
                color=color,
                shcolor=shcolor,
            )
        )
