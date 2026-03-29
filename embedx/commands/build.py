import click
from embedx.core.builder import build
from embedx.core.ui import info, success, error


@click.command(name="build")
def build_cmd():
    try:
        info("Building project...")
        build()
        success("Build complete")
    except Exception as e:
        error("Build failed")
        raise e