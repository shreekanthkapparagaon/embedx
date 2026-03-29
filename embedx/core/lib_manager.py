import os
import subprocess
import json
import shutil
import urllib.request
import zipfile
from embedx.core.registry import load_lib_registry
from embedx.core.ui import info, success, warn, error

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".embedx", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

INSTALLED = set()


def normalize(name):
    return name.strip().lower()


def is_installed(name):
    name = normalize(name)

    if not os.path.exists("embedx.lock"):
        return False

    with open("embedx.lock") as f:
        lock = json.load(f)

    if name not in lock.get("dependencies", {}):
        return False

    lib_path = os.path.join("lib", name)

    if not os.path.exists(lib_path):
        warn(f"Lockfile mismatch for {name}, reinstalling...")
        return False

    return True


def get_locked_version(name):
    if not os.path.exists("embedx.lock"):
        return None

    with open("embedx.lock") as f:
        lock = json.load(f)

    return lock.get("dependencies", {}).get(name, {}).get("version")


def install_libs(project_path):
    with open(os.path.join(project_path, "embedx.json")) as f:
        config = json.load(f)

    deps = config.get("dependencies", {})
    lib_dir = os.path.join(project_path, "lib")

    os.makedirs(lib_dir, exist_ok=True)

    for name, url in deps.items():
        dest = os.path.join(lib_dir, name)

        if os.path.exists(dest):
            success(f"{name} already installed")
            continue

        info(f"Installing {name}...")
        subprocess.run([
            "git", "clone",
            "--depth", "1",
            url,
            dest
        ], check=True)


def get_requested_version(name):
    if not os.path.exists("embedx.json"):
        return "latest"

    with open("embedx.json") as f:
        config = json.load(f)

    return config.get("dependencies", {}).get(name, "latest")


def resolve_version(requested, available_versions):
    versions = sorted(available_versions.keys(), reverse=True)

    if requested in versions:
        return requested

    if requested.startswith("^"):
        base = requested[1:]
        major = base.split(".")[0]

        for v in versions:
            if v.split(".")[0] == major:
                return v

    return versions[0]


# =========================
# INSTALL LIBRARY
# =========================
def install_lib(name):
    name = normalize(name)

    if is_installed(name):
        success(f"{name} already installed (lockfile)")
        return

    registry = load_lib_registry()
    libs = registry.get("libraries", {})

    os.makedirs("lib", exist_ok=True)

    if name in INSTALLED:
        return

    INSTALLED.add(name)

    # LOCAL SEARCH
    lib = None
    for key in libs:
        if key.lower() == name:
            lib = libs[key]
            name = key
            break

    if lib:
        info(f"Found locally: {name}")

    # ONLINE FALLBACK
    if not lib:
        info("Searching online registry...")

        from embedx.core.registry import search_online_library
        online_lib = search_online_library(name)

        if not online_lib:
            raise Exception("Library not found anywhere")

        success(f"Found {online_lib['name']} (latest version)")

        repo = online_lib.get("repository", "")

        if not repo:
            raise Exception("No repository found")

        name = online_lib["name"].lower()
        dest = os.path.join("lib", name)

        if os.path.exists(dest):
            warn(f"{online_lib['name']} already installed")
            return

        subprocess.run([
            "git", "clone",
            "--depth", "1",
            repo,
            dest
        ], check=True)

        _update_dependencies(name, "^latest")

        update_lockfile(online_lib["name"], {
            "version": "latest",
            "url": repo,
            "type": "git"
        })

        success(f"Installed {online_lib['name']}")
        return

    # LOCAL INSTALL
    versions = lib["versions"]
    requested_version = get_requested_version(name)
    locked = get_locked_version(name)

    if locked:
        info(f"Using locked version: {locked}")
        resolved_version = locked
    else:
        resolved_version = resolve_version(requested_version, versions)

    pkg = versions[resolved_version]

    install_dependencies(pkg.get("dependencies", {}))

    dest = os.path.join("lib", name)

    if os.path.exists(dest):
        warn(f"{name} already installed")
        return

    info(f"Installing {name} ({resolved_version})...")

    if pkg["type"] == "zip":
        tmp = os.path.join(CACHE_DIR, f"{name}.zip")

        if not os.path.exists(tmp):
            info("Downloading...")
            urllib.request.urlretrieve(pkg["url"], tmp)
        else:
            info("Using cached package")

        info("Extracting...")
        with zipfile.ZipFile(tmp, 'r') as zip_ref:
            zip_ref.extractall("lib")

        for folder in os.listdir("lib"):
            full_path = os.path.join("lib", folder)
            if os.path.isdir(full_path) and name in folder.lower():
                if full_path != dest:
                    os.rename(full_path, dest)
                break

    elif pkg["type"] == "git":
        subprocess.run([
            "git", "clone",
            "--depth", "1",
            pkg["url"],
            dest
        ], check=True)

    else:
        raise Exception("Unknown package type")

    _update_dependencies(name, f"^{resolved_version}")

    update_lockfile(name, {
        "version": resolved_version,
        "url": pkg["url"],
        "type": pkg["type"]
    })

    success(f"Installed {name}")


# =========================
# UNINSTALL LIBRARY
# =========================
def uninstall_lib(name):
    import stat

    name = name.lower()

    for folder in os.listdir("lib"):
        if folder.lower() == name:
            name = folder
            break

    path = os.path.join("lib", name)

    def remove_readonly(func, path, excinfo):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if os.path.exists(path):
        shutil.rmtree(path, onerror=remove_readonly)
        success(f"Removed {name}")
    else:
        warn(f"{name} not found")

    if os.path.exists("embedx.json"):
        with open("embedx.json") as f:
            config = json.load(f)

        deps = config.get("dependencies", {})

        if name in deps:
            del deps[name]

        config["dependencies"] = deps

        with open("embedx.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    lock_path = "embedx.lock"

    if os.path.exists(lock_path):
        with open(lock_path) as f:
            lock = json.load(f)

        deps = lock.get("dependencies", {})

        if name in deps:
            del deps[name]
            warn(f"Removed {name} from lockfile")

        lock["dependencies"] = deps

        with open(lock_path, "w", encoding="utf-8") as f:
            json.dump(lock, f, indent=4)


# =========================
# LOCKFILE
# =========================
def update_lockfile(name, lib):
    lock_path = "embedx.lock"

    if os.path.exists(lock_path):
        with open(lock_path) as f:
            lock = json.load(f)
    else:
        lock = {"dependencies": {}}

    lock["dependencies"][name] = {
        "version": lib.get("version"),
        "url": lib.get("url"),
        "type": lib.get("type")
    }

    with open(lock_path, "w", encoding="utf-8") as f:
        json.dump(lock, f, indent=4)


# =========================
# INTERNAL
# =========================
def _update_dependencies(name, version):
    if not os.path.exists("embedx.json"):
        return

    with open("embedx.json") as f:
        config = json.load(f)

    deps = config.get("dependencies", {})
    deps[name] = version
    config["dependencies"] = deps

    with open("embedx.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def install_dependencies(dependencies):
    if not dependencies:
        return

    info("Installing dependencies...")

    for dep, version in dependencies.items():
        if dep.lower() in INSTALLED:
            continue

        info(f"{dep} ({version})")

        if os.path.exists("embedx.json"):
            with open("embedx.json") as f:
                config = json.load(f)

            deps = config.get("dependencies", {})
            deps[dep] = version
            config["dependencies"] = deps

            with open("embedx.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

        _update_dependencies(dep, version)
        install_lib(dep)