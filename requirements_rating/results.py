from typing import Optional

from rich.console import Console
from rich.progress import Progress, TaskID, TaskProgressColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.status import Status


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
            self.task, description=f"Analizing package [bold blue]{package}[/bold blue]...", advance=1
        )
