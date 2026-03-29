import os
import platform
import subprocess
import zipfile
import tarfile
import urllib.request
import yaml

from embedx.core.ui import info, success, warn
from embedx.core.utils import run_cli, get_cli_path, get_config_path

from rich.console import Console
console = Console()

# ---------------- GLOBAL PATHS ---------------- #
HOME = os.path.expanduser("~")
SYSTEM = platform.system()

BASE_DIR = os.path.join(HOME, ".embedx")
TOOLS_DIR = os.path.join(BASE_DIR, "tools")


# ---------------- PLATFORM PATHS ---------------- #
def get_arduino_base():
    if SYSTEM == "Windows":
        return os.path.join(HOME, "AppData", "Local", "Arduino15")
    else:
        return os.path.join(HOME, ".arduino15")


def get_user_dir():
    if SYSTEM == "Windows":
        return os.path.join(HOME, "Documents", "Arduino")
    else:
        return os.path.join(HOME, "Arduino")


# ---------------- CLI DOWNLOAD ---------------- #
def get_cli_info():
    if SYSTEM == "Windows":
        return {
            "url": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip",
            "type": "zip",
            "binary": "arduino-cli.exe"
        }
    elif SYSTEM == "Linux":
        return {
            "url": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz",
            "type": "tar",
            "binary": "arduino-cli"
        }
    elif SYSTEM == "Darwin":
        return {
            "url": "https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz",
            "type": "tar",
            "binary": "arduino-cli"
        }
    else:
        raise Exception(f"Unsupported OS: {SYSTEM}")


# ---------------- CONFIG ---------------- #
def create_config():
    config_path = get_config_path()

    if os.path.exists(config_path):
        warn("Config already exists")
        return

    os.makedirs(BASE_DIR, exist_ok=True)

    base = get_arduino_base()

    config = {
        "directories": {
            "data": base,
            "downloads": os.path.join(base, "staging"),
            "user": get_user_dir()
        },
        "board_manager": {
            "additional_urls": []
        }
    }

    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        success("Arduino CLI config created")
    except Exception as e:
        console.print_exception()
        raise Exception(f"Failed to create config: {e}")


# ---------------- INSTALL CLI ---------------- #
def install_cli():
    cli_path = get_cli_path()

    if os.path.exists(cli_path):
        warn("Arduino CLI already installed")
        return

    os.makedirs(TOOLS_DIR, exist_ok=True)

    cli_info = get_cli_info()
    archive_path = os.path.join(TOOLS_DIR, "cli_download")

    info("Downloading Arduino CLI...")
    try:
        urllib.request.urlretrieve(cli_info["url"], archive_path)
    except Exception as e:
        raise Exception(f"Download failed: {e}")

    info("Extracting CLI...")

    try:
        if cli_info["type"] == "zip":
            with zipfile.ZipFile(archive_path, 'r') as z:
                z.extractall(TOOLS_DIR)

        elif cli_info["type"] == "tar":
            with tarfile.open(archive_path, "r:gz") as t:
                t.extractall(TOOLS_DIR)

    except Exception as e:
        raise Exception(f"Extraction failed: {e}")

    os.remove(archive_path)

    # 🔧 Ensure executable permission (Linux/macOS)
    cli_binary = os.path.join(TOOLS_DIR, cli_info["binary"])
    if SYSTEM != "Windows":
        os.chmod(cli_binary, 0o755)

    success("Arduino CLI installed successfully")


# ---------------- BOARD INSTALL ---------------- #
def install(board):
    try:
        install_cli()
        create_config()

        info(f"Installing board: {board}")

        if board == "esp32":
            run_cli(["core", "update-index"])
            run_cli(["core", "install", "esp32:esp32"])
            success("ESP32 installed")

        elif board == "esp8266":
            run_cli([
                "config", "add",
                "board_manager.additional_urls",
                "http://arduino.esp8266.com/stable/package_esp8266com_index.json"
            ])

            run_cli(["core", "update-index"])
            run_cli(["core", "install", "esp8266:esp8266"])
            success("ESP8266 installed")

        elif board == "arduino":
            run_cli(["core", "install", "arduino:avr"])
            success("Arduino AVR installed")

        else:
            warn(f"Unknown board: {board}")

    except Exception as e:
        console.print_exception()
        raise Exception(f"Installation failed: {e}")