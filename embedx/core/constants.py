# embedx/core/constants.py
import os
import platform

HOME = os.path.expanduser("~")
SYSTEM = platform.system()

BASE_DIR = os.path.join(HOME, ".embedx")
TOOLS_DIR = os.path.join(BASE_DIR, "tools")

CLI_BINARY = "arduino-cli.exe" if SYSTEM == "Windows" else "arduino-cli"
CLI_PATH = os.path.join(TOOLS_DIR, CLI_BINARY)

CONFIG_PATH = os.path.join(BASE_DIR, "arduino-cli.yaml")