import click
from embedx.core.lib_manager import install_lib, uninstall_lib
from embedx.core.registry import load_lib_registry


@click.group(name="lib")
def lib_cmd():
    """Manage libraries"""
    pass


# =========================
# INSTALL
# =========================
@lib_cmd.command(name="install")
@click.argument("name")
def install_cmd(name):
    """Install a library"""
    install_lib(name)


# =========================
# UNINSTALL
# =========================
@lib_cmd.command(name="uninstall")
@click.argument("name")
def uninstall_cmd(name):
    """Remove a library"""
    uninstall_lib(name)


# =========================
# SEARCH
# =========================
@lib_cmd.command(name="search")
@click.argument("query")
def search_cmd(query):
    """Search library in registry"""
    registry = load_lib_registry()
    libs = registry.get("libraries", {})

    print("🔍 Searching...\n")

    found = False

    for name, meta in libs.items():
        if query.lower() in name.lower():
            print(f"📦 {name} - {meta.get('description', '')}")
            found = True

    if not found:
        print("❌ No libraries found")