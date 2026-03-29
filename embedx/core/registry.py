import os
import json
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# -------------------------
# LIB REGISTRY
# -------------------------
def load_lib_registry():
    path = os.path.join(BASE_DIR, "registry_libs.json")

    if not os.path.exists(path):
        return {"libraries": {}}

    with open(path, encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# BOARD REGISTRY
# -------------------------
def load_board_registry():
    path = os.path.join(BASE_DIR, "registry_boards.json")

    if not os.path.exists(path):
        raise Exception("❌ Board registry missing")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


# -------------------------
# ONLINE LIB SEARCH
# -------------------------
def search_online_library(name):
    url = "https://downloads.arduino.cc/libraries/library_index.json"

    try:
        data = json.loads(urllib.request.urlopen(url).read())

        for lib in data.get("libraries", []):
            if lib["name"].lower() == name.lower():
                return lib

    except Exception as e:
        print(f"⚠️ Failed to fetch online registry: {e}")

    return None