import click
from embedx.core.builder import build
from embedx.core.uploader import upload_firmware as upload
from embedx.core.utils import detect_port
from embedx.core.monitor import monitor as start_monitor
from embedx.core.ui import info, success, warn


@click.command(name="run")
@click.option("--port", default=None)
@click.option("--monitor", default="on", type=click.Choice(["on", "off"]))
@click.option("--no-upload", is_flag=True)
@click.option("--verbose", is_flag=True)
@click.option("--baud", default=9600)
def run_cmd(port, monitor, no_upload, verbose, baud):

    info("Running project...")

    # Build
    build(verbose=verbose)

    # Port
    if not port:
        try:
            port = detect_port()
            success(f"Auto-detected port: {port}")
        except Exception as e:
            warn(str(e))
            return
    else:
        info(f"Using port: {port}")

    # Upload
    if not no_upload:
        info("Uploading firmware...")
        upload(port)
        success("Upload complete")
    else:
        warn("Upload skipped")

    # Monitor
    if monitor == "on":
        info("Starting monitor...")
        try:
            start_monitor(port, baud)
        except KeyboardInterrupt:
            warn("Monitor stopped")