import click
from embedx.core.monitor import monitor
from embedx.core.utils import detect_port
from embedx.core.ui import info, warn


@click.command(name="monitor")
@click.option("--port", default=None, help="Serial port")
@click.option("--baud", default=9600, help="Baud rate")
def monitor_cmd(port, baud):

    if not port:
        try:
            port = detect_port()
            info(f"Auto-detected port: {port}")
        except Exception as e:
            warn(str(e))
            return
    else:
        info(f"Using port: {port}")

    info(f"Starting serial monitor ({baud})...\n")

    try:
        monitor(port, baud)
    except KeyboardInterrupt:
        warn("Monitor stopped")