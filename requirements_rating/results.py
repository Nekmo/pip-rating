from typing import Optional, TYPE_CHECKING, Union

from rich.console import Console
from rich.progress import Progress, TaskID, TaskProgressColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.status import Status
from rich.table import Table

if TYPE_CHECKING:
    from requirements_rating.rating import ScoreBase
    from requirements_rating.dependencies import Dependencies


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


class Results:
    """Print requirements-ratings results to the terminal."""
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

    def analizing_package(self, package, total: int):
        if self._status:
            self._status.stop()
        if not self.progress:
            self.progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(complete_style="blue"),
                TaskProgressColumn(),
                TimeRemainingColumn(),
            )
            self.task = self.progress.add_task("Analizing packages...", total=total)
            self.progress.start()
        self.progress.update(
            self.task, description=f"Analizing package [bold blue]{package}[/bold blue]...", advance=1, refresh=True,
        )

    def show_packages_results(self, dependencies: "Dependencies"):
        global_rating_score = dependencies.get_global_rating_score()
        if self.progress:
            self.progress.update(self.task, description="[bold green]Analyzed all packages[/bold green]", refresh=True)
            self.progress.stop()
        for package in dependencies.packages.values():
            if package.name not in dependencies.req_file:
                continue
            global_rating_score_letter = colorize_rating(package.rating.global_rating_score)
            rating_score_letter = colorize_rating(package.rating.rating_score)
            if global_rating_score_letter >= rating_score_letter:
                print_score = f"{global_rating_score_letter}"
            else:
                print_score = f"{rating_score_letter} -> {global_rating_score_letter}"
            self.console.print(
                f":package: Package [bold blue]{package.name}[/bold blue]: " + print_score
            )
            for key, value in package.rating.breakdown_scores:
                key = key.split(".")[-1].replace("iso_dt", "").replace("_", " ").capitalize()
                self.console.print(f"  :black_medium-small_square: {key}: {colorize_score(value)}")
            if package.rating.global_rating_score < package.rating.rating_score:
                low_rating_dependences = [
                    f'{pkg.name} ({colorize_rating(score)})' for pkg, score
                    in package.rating.descendant_rating_scores if colorize_rating(score) < rating_score_letter
                ]
                self.console.print(
                    f"  :arrow_lower_right: Low rating dependencies: {', '.join(low_rating_dependences)}"
                )
            self.console.print("")
        self.console.print("")
        table = Table(show_header=False)
        table.add_row(f"Global rating score: {colorize_rating(global_rating_score)}")
        self.console.print(table)
