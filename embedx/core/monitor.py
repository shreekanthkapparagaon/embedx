import serial
import time
from rich.console import Console

console = Console()


def monitor(port, baud=9600):
    console.print(f"[cyan]Starting monitor on {port} ({baud})...\n[/]")

    try:
        try:
            ser = serial.Serial(port, baud, timeout=1)
        except Exception as e:
            console.print(f"[red]Failed to open port: {e}[/]")
            return
        time.sleep(2)

        while True:
            if ser.in_waiting:
                line = ser.readline().decode(errors="ignore")
                console.print(line, end="")

    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/]")