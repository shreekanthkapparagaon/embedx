import click
from embedx.core.uploader import upload_firmware
from embedx.core.ui import info, success, error


@click.command(name="upload")
@click.option("--port", required=True, help="Serial port (e.g., COM3)")
def upload_cmd(port):
    try:
        info(f"Uploading to {port}...")
        upload_firmware(port)
        success("Upload successful")
    except Exception as e:
        error("Upload failed")
        raise e