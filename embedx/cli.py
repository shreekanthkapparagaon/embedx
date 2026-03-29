import click
from embedx.core.ui import header
from embedx.virsion import __version__
from embedx.commands.init import init_cmd
from embedx.commands.setup import setup_cmd
from embedx.commands.build import build_cmd
from embedx.commands.upload import upload_cmd
from embedx.commands.run import run_cmd
from embedx.commands.clean import clean_cmd
from embedx.commands.lib import lib_cmd
from embedx.commands.monitor import monitor_cmd
from embedx.commands.ports import ports_cmd
from embedx.commands.board import board_cmd
from embedx.commands.device import device_cmd
from embedx.commands.doctor import doctor_cmd


@click.group(help="🚀 EmbedX - Fast Embedded Development CLI")
@click.version_option(__version__, prog_name="EmbedX")
def cli():
    header("⚡ EmbedX CLI - Fast Embedded Toolkit")

@click.command(name="version")
def version_cmd():
    from embedx.core.ui import info
    info(f"EmbedX version {__version__}")
    

cli.add_command(board_cmd)
cli.add_command(device_cmd)
cli.add_command(init_cmd)
cli.add_command(setup_cmd)
cli.add_command(lib_cmd)
cli.add_command(build_cmd)
cli.add_command(upload_cmd)
cli.add_command(run_cmd)
cli.add_command(monitor_cmd)
cli.add_command(ports_cmd)
cli.add_command(clean_cmd)
cli.add_command(doctor_cmd)
cli.add_command(version_cmd)


if __name__ == "__main__":
    cli()
