import json
import subprocess
from embedx.core.utils import get_cli_path, get_config_path
from embedx.core.ui import info, success


def upload_firmware(port):
    with open("embedx.json") as f:
        config = json.load(f)

    fqbn = config["fqbn"]

    cli = get_cli_path()
    config_file = get_config_path()

    info(f"Using port: {port}")
    info("Uploading firmware...")

    cmd = [
        cli,
        "--config-file", config_file,
        "upload",
        "-p", port,
        "--fqbn", fqbn,
        "--input-dir", "build"
    ]

    subprocess.run(cmd, check=True)

    success("Upload successful")