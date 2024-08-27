from rich import print
from rich.console import Console
from rich.tree import Tree
from time import sleep
from rich.progress import Progress
from rich.live import Live
from rich.table import Table
import time

console = Console(width=160)

error_console = Console(
    width=100, stderr=True,
    style="bold red on black")


def long_task():
    with Progress() as progress:
        task = progress.add_task("Chargement...", total=100)
        for _ in range(100):
            time.sleep(0.1)
            progress.update(task, advance=1)
