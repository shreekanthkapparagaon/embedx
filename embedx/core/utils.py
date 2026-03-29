import os
import subprocess
import hashlib
import platform
import serial.tools.list_ports


# -------------------------
# PATHS
# -------------------------
def get_cli_path():
    binary = "arduino-cli.exe" if platform.system() == "Windows" else "arduino-cli"

    return os.path.join(
        os.path.expanduser("~"),
        ".embedx",
        "tools",
        binary
    )


def get_config_path():
    return os.path.join(
        os.path.expanduser("~"),
        ".embedx",
        "arduino-cli.yaml"
    )


# -------------------------
# CLI RUNNER
# -------------------------
def run_cli(args, capture=False):
    cli = get_cli_path()
    config = get_config_path()

    if not os.path.exists(cli):
        raise Exception("❌ Arduino CLI not found. Run: embedx install")

    cmd = [cli, "--config-file", config] + args

    try:
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        else:
            subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print("❌ CLI command failed")
        print("CMD:", cmd)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise


# -------------------------
# INSTALLED BOARDS
# -------------------------
def get_installed_boards():
    output = run_cli(["core", "list"], capture=True)

    boards = []

    for line in output.splitlines():
        line = line.strip()

        # skip headers or empty lines
        if not line or line.startswith("ID"):
            continue

        parts = line.split()

        if parts and ":" in parts[0]:
            boards.append(parts[0])  # e.g., esp32:esp32

    return boards


# -------------------------
# SERIAL
# -------------------------
def detect_port():
    ports = list(serial.tools.list_ports.comports())

    if not ports:
        raise Exception("❌ No serial ports found")

    preferred_keywords = ["USB", "UART", "CH340", "CP210", "FTDI"]

    for port in ports:
        desc = (port.description or "").upper()

        if any(k in desc for k in preferred_keywords):
            return port.device

    # fallback (more reliable than first)
    return ports[-1].device


def list_ports():
    ports = list(serial.tools.list_ports.comports())

    return [
        {
            "device": p.device,
            "description": p.description
        }
        for p in ports
    ]


# -------------------------
# BUILD CACHE HASH
# -------------------------
def hash_project(src_dir):
    h = hashlib.md5()

    for root, _, files in os.walk(src_dir):
        for f in sorted(files):
            path = os.path.join(root, f)

            try:
                with open(path, "rb") as file:
                    while chunk := file.read(4096):  # memory-safe
                        h.update(chunk)
            except Exception:
                # skip unreadable files instead of crashing
                continue

    return h.hexdigest()