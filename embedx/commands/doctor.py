import click
import os
import subprocess
import shutil
from embedx.core.utils import get_cli_path
from embedx.core.ui import info, success, warn, error


@click.command(name="doctor")
def doctor_cmd():

    info("Running diagnostics...\n")

    # CLI
    cli = get_cli_path()
    if os.path.exists(cli):
        success(f"Arduino CLI found: {cli}")
        try:
            out = subprocess.check_output([cli, "version"], text=True)
            info(f"Version: {out.strip()}")
        except:
            warn("CLI exists but failed to run")
    else:
        error("Arduino CLI not found")

    # Python
    info(f"Python: {shutil.which('python')}")

    # Project
    if os.path.exists("embedx.json"):
        success("embedx.json found")
    else:
        warn("embedx.json missing")

    if os.path.exists("build"):
        success("build folder exists")
    else:
        warn("build folder missing")

    info("\nDiagnostics complete")