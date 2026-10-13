"""
Build and Deployment Pipeline for BG3 Homeless Californian Class Mod.

Usage:
    python build.py              # Build source files and create dist/HomelessCalifornian.pak
    python build.py --install    # Build and copy .pak to BG3 Mods directory
    python build.py --activate   # Build, install, and add to modsettings.lsx
    python build.py --status     # Check current status of the mod in BG3 installation
"""

import os
import sys
import shutil
import subprocess
import xml.etree.ElementTree as ET
from generate_mod import MOD_NAME, MOD_UUID, main as generate_all

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(ROOT_DIR, "tools", "Packed", "Tools")
DIVINE_EXE = os.path.join(TOOLS_DIR, "Divine.exe")
SRC_DIR = os.path.join(ROOT_DIR, "src", MOD_NAME)
DIST_DIR = os.path.join(ROOT_DIR, "dist")
PAK_NAME = f"{MOD_NAME}.pak"
PAK_PATH = os.path.join(DIST_DIR, PAK_NAME)

BG3_LOCAL_MODS = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Larian Studios", "Baldur's Gate 3", "Mods"
)

BG3_MODSETTINGS = os.path.join(
    os.environ.get("LOCALAPPDATA", ""),
    "Larian Studios", "Baldur's Gate 3", "PlayerProfiles", "Public", "modsettings.lsx"
)


def run_cmd(cmd_list):
    res = subprocess.run(cmd_list, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error running {' '.join(cmd_list)}:\n{res.stderr or res.stdout}")
        sys.exit(1)
    return res.stdout


def compile_localization():
    print("Compiling localization files...")
    loca_xml_mods = os.path.join(SRC_DIR, "Mods", MOD_NAME, "Localization", "English", f"{MOD_NAME}.loca.xml")
    loca_bin_mods = os.path.join(SRC_DIR, "Mods", MOD_NAME, "Localization", "English", f"{MOD_NAME}.loca")
    loca_xml_pub = os.path.join(SRC_DIR, "Public", MOD_NAME, "Localization", "English", f"{MOD_NAME}.loca.xml")
    loca_bin_pub = os.path.join(SRC_DIR, "Public", MOD_NAME, "Localization", "English", f"{MOD_NAME}.loca")

    if os.path.exists(loca_xml_mods):
        run_cmd([DIVINE_EXE, "-g", "bg3", "-a", "convert-loca", "-s", loca_xml_mods, "-d", loca_bin_mods])
        print(f"  [OK] {loca_bin_mods}")

    if os.path.exists(loca_xml_pub):
        run_cmd([DIVINE_EXE, "-g", "bg3", "-a", "convert-loca", "-s", loca_xml_pub, "-d", loca_bin_pub])
        print(f"  [OK] {loca_bin_pub}")


def build_pak():
    os.makedirs(DIST_DIR, exist_ok=True)
    print(f"Packaging mod into {PAK_PATH}...")
    import tempfile
    staging_root = os.path.join(ROOT_DIR, 'work', 'pak-staging')
    os.makedirs(staging_root, exist_ok=True)
    # Match the shared packer's convention: .lsf.lsx is authoring input;
    # the game receives its freshly compiled .lsf counterpart.
    with tempfile.TemporaryDirectory(prefix='hc-build-', dir=staging_root) as staging:
        shutil.copytree(SRC_DIR, staging, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('*.lsf.lsx'))
        run_cmd([DIVINE_EXE, "-g", "bg3", "-a", "create-package", "-s", staging, "-d", PAK_PATH])
    size = os.path.getsize(PAK_PATH)
    print(f"  [OK] Built {PAK_NAME} ({size:,} bytes)")


def compile_resources():
    """Compile added root-template authoring XML before packing."""
    from pathlib import Path
    for authoring in Path(SRC_DIR).rglob('*.lsf.lsx'):
        run_cmd([DIVINE_EXE, '-g', 'bg3', '-a', 'convert-resource',
                 '-s', str(authoring), '-d', str(authoring.with_suffix(''))])


def verify_candidate():
    run_cmd([sys.executable, os.path.join(ROOT_DIR, 'validation', 'validate.py'),
             '--pak', PAK_PATH])
    print('  [OK] Source and package checks passed (file level only)')


def install_pak(allow_running_game=False):
    from datetime import datetime
    running = subprocess.run(['tasklist'], capture_output=True, text=True, check=True).stdout.lower()
    if not allow_running_game and ('bg3.exe' in running or 'bg3_dx11.exe' in running):
        raise RuntimeError('Close Baldur\'s Gate 3 before installing this build.')
    if not os.path.exists(BG3_LOCAL_MODS):
        print(f"Error: BG3 Mods directory not found at {BG3_LOCAL_MODS}")
        return False
    dest = os.path.join(BG3_LOCAL_MODS, PAK_NAME)
    if os.path.exists(dest):
        backups = os.path.join(ROOT_DIR, 'work', 'installed-backups')
        os.makedirs(backups, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        shutil.copy2(dest, os.path.join(backups, f'HomelessCalifornian-{stamp}.pak'))
    # Stage beside the destination so readers never see a partial package.
    # Windows may still reject replacement if the game holds a blocking handle.
    import tempfile
    with tempfile.NamedTemporaryFile(prefix='hc-install-', suffix='.pending',
                                     dir=BG3_LOCAL_MODS, delete=False) as staged:
        staged_path = staged.name
    try:
        shutil.copy2(PAK_PATH, staged_path)
        os.replace(staged_path, dest)
    finally:
        if os.path.exists(staged_path):
            os.remove(staged_path)
    print(f"  [OK] Installed {PAK_NAME} -> {dest}")
    return True


def activate_in_modsettings():
    if not os.path.exists(BG3_MODSETTINGS):
        print(f"Notice: modsettings.lsx not found at {BG3_MODSETTINGS}")
        return False

    # Read modsettings XML
    with open(BG3_MODSETTINGS, "r", encoding="utf-8") as f:
        content = f.read()

    if MOD_UUID in content:
        print(f"  [INFO] {MOD_NAME} is already active in modsettings.lsx")
        return True

    from datetime import datetime
    backup_path = BG3_MODSETTINGS + '.bak-' + datetime.now().strftime('%Y%m%d-%H%M%S')
    shutil.copy2(BG3_MODSETTINGS, backup_path)
    print(f'  [OK] Created backup at {backup_path}')

    # Parse XML and insert entry into <children> under <node id="Mods">
    tree = ET.parse(BG3_MODSETTINGS)
    root = tree.getroot()
    mods_children = None

    for node in root.findall(".//node[@id='Mods']/children"):
        mods_children = node
        break

    if mods_children is None:
        print("  [ERROR] Could not find <node id='Mods'><children> in modsettings.lsx")
        return False

    # Create new ModuleShortDesc node
    new_node = ET.SubElement(mods_children, "node", id="ModuleShortDesc")
    ET.SubElement(new_node, "attribute", id="Folder", type="LSString", value=MOD_NAME)
    ET.SubElement(new_node, "attribute", id="MD5", type="LSString", value="")
    ET.SubElement(new_node, "attribute", id="Name", type="LSString", value="Homeless Californian Class")
    ET.SubElement(new_node, "attribute", id="PublishHandle", type="uint64", value="0")
    ET.SubElement(new_node, "attribute", id="UUID", type="guid", value=MOD_UUID)
    ET.SubElement(new_node, "attribute", id="Version64", type="int64", value="36028797018963969")

    tree.write(BG3_MODSETTINGS, encoding="utf-8", xml_declaration=True)
    print("  [OK] Added Homeless Californian to modsettings.lsx")
    return True


def check_status():
    print("=== Baldur's Gate 3 Mod Status ===")
    print(f"Mod UUID: {MOD_UUID}")
    installed_pak = os.path.join(BG3_LOCAL_MODS, PAK_NAME)
    if os.path.exists(installed_pak):
        print(f"Installed PAK: YES ({installed_pak}, {os.path.getsize(installed_pak):,} bytes)")
    else:
        print(f"Installed PAK: NO (Not found at {installed_pak})")

    if os.path.exists(BG3_MODSETTINGS):
        with open(BG3_MODSETTINGS, "r", encoding="utf-8") as f:
            active = MOD_UUID in f.read()
        print(f"Active in modsettings.lsx: {'YES' if active else 'NO'}")
    else:
        print("modsettings.lsx: NOT FOUND")


def main():
    args = sys.argv[1:]
    if "--status" in args:
        check_status()
        return

    # 1. Regenerate mod source files
    generate_all()

    # 2. Build icon atlas and GUI/Content resources
    try:
        from build_icons import main as build_icons_main
        build_icons_main()
    except Exception as e:
        import subprocess
        subprocess.run([sys.executable, "build_icons.py"], check=True)

    # 3. Compile localization
    compile_localization()
    compile_resources()

    # 4. Build .pak
    build_pak()
    verify_candidate()

    # 4. Optional install / activate
    if "--install" in args or "--activate" in args:
        if not install_pak(allow_running_game='--allow-running-game' in args):
            sys.exit('Installation failed; game configuration was not changed.')

    if "--activate" in args:
        activate_in_modsettings()

    print("\nMod build completed successfully!")


if __name__ == "__main__":
    main()
