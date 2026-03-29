import click
from embedx.core.utils import list_ports


@click.group(name="device")
def device_cmd():
    """Manage connected devices"""
    pass


@device_cmd.command("list")
def list_devices():
    ports = list_ports()

    if not ports:
        click.echo("❌ No devices found")
        return

    click.echo("🔌 Connected devices:\n")

    for p in ports:
        click.echo(f"{p['device']}  →  {p['description']}")