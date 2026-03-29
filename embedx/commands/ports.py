import click
from embedx.core.utils import list_ports


@click.command(name="ports")
def ports_cmd():
    """List available serial ports"""
    ports = list_ports()

    if not ports:
        click.echo("❌ No ports found")
        return

    for p in ports:
        click.echo(f"{p['device']} - {p['description']}")