import click
import shutil
import os
import subprocess
from embedx.core.ui import info, success


BASE_DIR = os.path.join(os.path.expanduser("~"), ".embedx", "tools")


@click.command(name="clean")
@click.option("--all", is_flag=True)
def clean_cmd(all):

    info("Cleaning project...")

    if os.path.exists("build"):
        shutil.rmtree("build")
        success("Removed build folder")

    os.makedirs("build", exist_ok=True)

    if all:
        info("Deep cleaning...")

        cli = os.path.join(BASE_DIR, "arduino-cli.exe")

        if os.path.exists(cli):
            subprocess.run([cli, "cache", "clean"], check=False)
            success("Arduino cache cleaned")

        embedx_home = os.path.join(os.path.expanduser("~"), ".embedx")

        if os.path.exists(embedx_home):
            shutil.rmtree(embedx_home)
            success("Removed EmbedX toolchain")

    success("Clean complete")