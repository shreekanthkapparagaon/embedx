import click
import os
import json
import questionary

from embedx.core.utils import get_installed_boards
from embedx.core.registry import load_board_registry
from embedx.core.ui import info, success


def choose_board():
    registry = load_board_registry()
    installed = get_installed_boards()

    choices = []

    for name, fqbn in registry.items():
        core = ":".join(fqbn.split(":")[:2])
        if core in installed:
            choices.append(questionary.Choice(title=name, value=(name, fqbn)))

    if not choices:
        raise Exception("❌ No boards installed. Run `embedx setup` first.")

    answer = questionary.select(
        "Select board:",
        choices=choices
    ).ask()

    return answer


@click.command(name="init")
@click.argument("name", default="embedx_project")
def init_cmd(name):
    info(f"Creating project: {name}")

    os.makedirs(name, exist_ok=True)
    os.makedirs(f"{name}/src", exist_ok=True)
    os.makedirs(f"{name}/build", exist_ok=True)
    os.makedirs(f"{name}/lib", exist_ok=True)

    board, fqbn = choose_board()

    create_project(name, board, fqbn)

    success("Project created successfully")


def create_project(name, board, fqbn):
    with open(f"{name}/src/app.cpp", "w", encoding="utf-8") as f:
        f.write("""#include <Arduino.h>
#include "app.h"

void app_setup() {
    Serial.begin(115200);
}

void app_loop() {
    Serial.println("Hello from EmbedX 🚀");
    delay(1000);
}
""")

    with open(f"{name}/src/app.h", "w", encoding="utf-8") as f:
        f.write("""#pragma once

void app_setup();
void app_loop();
""")

    with open(f"{name}/{name}.ino", "w", encoding="utf-8") as f:
        f.write(f"""#include <Arduino.h>
#include "src/app.h"

void setup() {{
    app_setup();
}}

void loop() {{
    app_loop();
}}
""")

    with open(f"{name}/embedx.json", "w") as f:
        json.dump({
            "board": board,
            "framework": "arduino",
            "fqbn": fqbn
        }, f, indent=4)

    with open(f"{name}/embedx.lock", "w") as f:
        json.dump({"dependencies": {}}, f, indent=4)