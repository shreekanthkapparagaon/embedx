# embedx/core/ui.py

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def success(msg):
    console.print(f"[bold green]✔ {msg}[/]")

def error(msg):
    console.print(f"[bold red]✖ {msg}[/]")

def info(msg):
    console.print(f"[bold cyan]➜ {msg}[/]")

def warn(msg):
    console.print(f"[bold yellow]⚠ {msg}[/]")

def header(title):
    console.print(Panel.fit(title, style="bold blue"))

def spinner(text):
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[cyan]{text}"),
        transient=True
    )