import os
import json
import shutil
import tempfile
from embedx.core.utils import get_cli_path, get_config_path, run_cli, hash_project
from embedx.core.ui import info, success, warn, error
from rich.console import Console
console = Console()

BASE_DIR = os.path.expanduser("~/.embedx/tools")


def prepare_build_workspace(project_path):
    temp_dir = tempfile.mkdtemp(prefix="embedx_build_")

    shutil.copytree(
        os.path.join(project_path, "src"),
        os.path.join(temp_dir, "src")
    )

    lib_path = os.path.join(project_path, "lib")
    if os.path.exists(lib_path):
        shutil.copytree(lib_path, os.path.join(temp_dir, "lib"))

    folder_name = os.path.basename(temp_dir)
    ino_path = os.path.join(temp_dir, f"{folder_name}.ino")

    with open(ino_path, "w", encoding="utf-8") as f:
        f.write("""#include <Arduino.h>
#include "src/app.h"

void setup() {
    app_setup();
}

void loop() {
    app_loop();
}
""")
    return temp_dir, ino_path


def build(verbose=False):
    project_path = os.getcwd()
    cache_file = os.path.join(project_path, ".embedx_cache")

    current_hash = hash_project(os.path.join(project_path, "src"))

    build_dir = os.path.join(project_path, "build")

    artifact_exists = False
    if os.path.exists(build_dir):
        artifact_exists = any(f.endswith(".bin") for f in os.listdir(build_dir))

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            if f.read() == current_hash and artifact_exists:
                warn("No changes detected, skipping build")
                return

    with open("embedx.json") as f:
        config = json.load(f)

    fqbn = config["fqbn"]

    cli = get_cli_path()
    config_path = get_config_path()

    if not os.path.exists(config_path):
        info("Config missing, creating...")
        from embedx.core.installer import create_config
        create_config()

    temp_dir, ino = prepare_build_workspace(project_path)

    include_flags = []
    lib_dir = os.path.join(project_path, "lib")

    if os.path.exists(lib_dir):
        for lib in os.listdir(lib_dir):
            lib_path = os.path.join(lib_dir, lib)
            if os.path.isdir(lib_path):
                include_flags.append(f"-I{lib_path}")

    includes = " ".join(include_flags)

    info("Building project...")
    build_dir = os.path.join(project_path, "build")

    if os.path.exists(build_dir):
        for f in os.listdir(build_dir):
            path = os.path.join(build_dir, f)
            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)
    else:
        os.makedirs(build_dir)

    try:
        args = [
            "compile",
            "--fqbn", fqbn,
            "--output-dir", build_dir,
        ]

        if includes:
            args.extend([
                "--build-property",
                f"compiler.cpp.extra_flags={includes}"
            ])

        args.append(temp_dir)

        run_cli(args)

    except Exception as e:
        error("Build failed")
        
        console.print_exception()

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    success("Build complete")

    with open(cache_file, "w") as f:
        f.write(current_hash)