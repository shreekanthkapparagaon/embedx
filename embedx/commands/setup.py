import click
import json
import os
from embedx.core.installer import install
from embedx.core.ui import info, success, error


@click.command(name="setup")
@click.option("--board", default=None, help="Override board")
def setup_cmd(board):

    try:
        if not board:
            if not os.path.exists("embedx.json"):
                error("embedx.json not found. Run `embedx init` first.")
                return

            with open("embedx.json") as f:
                config = json.load(f)

            board = config.get("board")

        info(f"Setting up for {board}...")
        install(board)
        success("Setup complete")

    except Exception as e:
        error("Setup failed")
        raise e