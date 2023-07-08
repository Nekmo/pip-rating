from typing import Optional, TYPE_CHECKING

from rich.console import Console
from rich.progress import Progress, TaskID, TaskProgressColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.status import Status

if TYPE_CHECKING:
    from requirements_rating.dependencies import Dependencies


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
            if package.rating.global_rating_score >= package.rating.rating_score:
                print_score = f"{package.rating.global_rating_score}"
            else:
                print_score = f"{package.rating.rating_score} -> {package.rating.global_rating_score}"
            self.console.print(
                f"Package [bold blue]{package.name}[/bold blue]: " + print_score
            )
            for key, value in package.rating.breakdown_scores:
                self.console.print(f"  {key}: {value}")
            if package.rating.global_rating_score < package.rating.rating_score:
                self.console.print(
                    f"  Low rating dependencies: "
                    f"{', '.join([f'{dep.name} ({score})' for dep, score in package.rating.low_rating_dependencies])}"
                )
            self.console.print("")
        self.console.print("")
        self.console.print(f"Global rating score: [bold blue]{global_rating_score}[/bold blue]")
