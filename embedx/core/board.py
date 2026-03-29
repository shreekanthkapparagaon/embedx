import subprocess
from embedx.core.utils import get_cli_path
from embedx.core.ui import info, success, error


def run_cli(args):
    cli = get_cli_path()
    cmd = [cli] + args
    subprocess.run(cmd, check=True)


def install_board(name):
    info(f"Installing {name}...")

    if name == "esp32":
        run_cli(["core", "update-index"])
        run_cli(["core", "install", "esp32:esp32"])
        success("ESP32 installed")

    elif name == "arduino":
        run_cli(["core", "install", "arduino:avr"])
        success("Arduino AVR installed")

    else:
        error("Unsupported board")


def list_boards():
    cli = get_cli_path()
    result = subprocess.run(
        [cli, "core", "list"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.strip().split("\n")[1:]
    boards = []

    for line in lines:
        if line:
            boards.append(line.split()[0])

    return boards


def uninstall_board(name):
    info(f"Removing {name}...")

    if name == "esp32":
        run_cli(["core", "uninstall", "esp32:esp32"])

    elif name == "arduino":
        run_cli(["core", "uninstall", "arduino:avr"])

    else:
        error("Unsupported board")
        return

    success("Removed")