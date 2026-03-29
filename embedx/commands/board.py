import click
from embedx.core.board import (
    list_boards,
    install_board,
    uninstall_board
)


@click.group(name="board")
def board_cmd():
    """Manage boards"""
    pass


@board_cmd.command("list")
def list_cmd():
    boards = list_boards()

    if not boards:
        click.echo("❌ No boards installed")
        return

    for b in boards:
        click.echo(f"✅ {b}")


@board_cmd.command("install")
@click.argument("name")
def install_cmd(name):
    install_board(name)


@board_cmd.command("uninstall")
@click.argument("name")
def uninstall_cmd(name):
    uninstall_board(name)