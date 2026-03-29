import subprocess


def get_version():
    # -----------------------
    # 1. Try Git (dev mode)
    # -----------------------
    try:
        version = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        if version.startswith("v"):
            version = version[1:]

        return version

    except Exception:
        pass

    # -----------------------
    # 2. Try installed package
    # -----------------------
    try:
        from importlib.metadata import version
        return version("embedx")
    except Exception:
        pass

    # -----------------------
    # 3. Final fallback
    # -----------------------
    return "0.0.0"


__version__ = get_version()