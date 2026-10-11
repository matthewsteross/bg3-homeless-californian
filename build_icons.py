"""
Process generated icons into BG3 texture atlas, Content/GUI definitions,
Character Creation race silhouettes, and Patch 7 CC metadata/loose icon banks.
"""

import os
import glob
import subprocess
import numpy as np
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src", "HomelessCalifornian")

# Public Game directories (Merged base VFS for CC engine lookups)
PUBLIC_GAME_DIR = os.path.join(SRC_DIR, "Public", "Game", "GUI")
GAME_RACE_ICONS_DIR = os.path.join(PUBLIC_GAME_DIR, "Assets", "CC", "icons_races")
GAME_RACE_LOWRES_DIR = os.path.join(PUBLIC_GAME_DIR, "AssetsLowRes", "CC", "icons_races")
GAME_CLASS_ICONS_DIR = os.path.join(PUBLIC_GAME_DIR, "Assets", "ClassIcons")
GAME_HOTBAR_DIR = os.path.join(GAME_CLASS_ICONS_DIR, "hotbar")
GAME_LOWRES_CLASS_DIR = os.path.join(PUBLIC_GAME_DIR, "AssetsLowRes", "ClassIcons")
GAME_LOWRES_HOTBAR_DIR = os.path.join(GAME_LOWRES_CLASS_DIR, "hotbar")
GAME_TOOLTIPS_DIR = os.path.join(PUBLIC_GAME_DIR, "Assets", "Tooltips", "Icons")
GAME_CONTROLLER_DIR = os.path.join(PUBLIC_GAME_DIR, "Assets", "ControllerUIIcons", "skills_png")

# Public Mod directories
PUBLIC_DIR = os.path.join(SRC_DIR, "Public", "HomelessCalifornian")
TEXTURE_DIR = os.path.join(PUBLIC_DIR, "Assets", "Textures", "Icons")
GUI_DIR = os.path.join(PUBLIC_DIR, "GUI")
CONTENT_DIR = os.path.join(PUBLIC_DIR, "Content", "[PAK]_HomelessCalifornian")

PUB_RACE_ICONS_DIR = os.path.join(GUI_DIR, "Assets", "CC", "icons_races")
PUB_RACE_LOWRES_DIR = os.path.join(GUI_DIR, "AssetsLowRes", "CC", "icons_races")
PUB_CLASS_ICONS_DIR = os.path.join(GUI_DIR, "Assets", "ClassIcons")
PUB_HOTBAR_DIR = os.path.join(PUB_CLASS_ICONS_DIR, "hotbar")
PUB_LOWRES_CLASS_DIR = os.path.join(GUI_DIR, "AssetsLowRes", "ClassIcons")
PUB_LOWRES_HOTBAR_DIR = os.path.join(PUB_LOWRES_CLASS_DIR, "hotbar")

# Patch 7 Mods GUI directories
MODS_DIR = os.path.join(SRC_DIR, "Mods", "HomelessCalifornian")
MODS_GUI_DIR = os.path.join(MODS_DIR, "GUI")
MODS_ASSETS_DIR = os.path.join(MODS_GUI_DIR, "Assets")
MODS_LOWRES_DIR = os.path.join(MODS_GUI_DIR, "AssetsLowRes")
MODS_CLASS_ICONS_DIR = os.path.join(MODS_ASSETS_DIR, "ClassIcons")
MODS_HOTBAR_DIR = os.path.join(MODS_CLASS_ICONS_DIR, "hotbar")
MODS_LOWRES_CLASS_DIR = os.path.join(MODS_LOWRES_DIR, "ClassIcons")
MODS_LOWRES_HOTBAR_DIR = os.path.join(MODS_LOWRES_CLASS_DIR, "hotbar")
MODS_RACE_ICONS_DIR = os.path.join(MODS_ASSETS_DIR, "CC", "icons_races")
MODS_RACE_LOWRES_DIR = os.path.join(MODS_LOWRES_DIR, "CC", "icons_races")

TOOLS_DIR = os.path.join(ROOT_DIR, "tools", "Packed", "Tools")
DIVINE_EXE = os.path.join(TOOLS_DIR, "Divine.exe")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets", "icons")

ALL_DIRS = [
    ASSETS_DIR, TEXTURE_DIR, GUI_DIR, CONTENT_DIR,
    PUBLIC_GAME_DIR, GAME_RACE_ICONS_DIR, GAME_RACE_LOWRES_DIR,
    GAME_CLASS_ICONS_DIR, GAME_HOTBAR_DIR, GAME_LOWRES_CLASS_DIR, GAME_LOWRES_HOTBAR_DIR,
    GAME_TOOLTIPS_DIR, GAME_CONTROLLER_DIR,
    PUB_RACE_ICONS_DIR, PUB_RACE_LOWRES_DIR, PUB_CLASS_ICONS_DIR, PUB_HOTBAR_DIR,
    PUB_LOWRES_CLASS_DIR, PUB_LOWRES_HOTBAR_DIR,
    MODS_GUI_DIR, MODS_ASSETS_DIR, MODS_LOWRES_DIR,
    MODS_CLASS_ICONS_DIR, MODS_HOTBAR_DIR, MODS_LOWRES_CLASS_DIR, MODS_LOWRES_HOTBAR_DIR,
    MODS_RACE_ICONS_DIR, MODS_RACE_LOWRES_DIR
]

for d in ALL_DIRS:
    os.makedirs(d, exist_ok=True)

# Fixed UUID for Texture Resource
ATLAS_TEXTURE_UUID = "e4a28f11-9a70-4f51-b847-a89a0cb1d923"

app_data = os.path.join(os.environ.get("USERPROFILE", ""), ".gemini", "antigravity", "brain")

def find_img(pattern, fallback_name):
    local_path = os.path.join(ASSETS_DIR, fallback_name)
    if os.path.exists(local_path):
        return local_path
    matches = glob.glob(f"{app_data}/**/{pattern}*.jpg", recursive=True)
    if matches:
        return matches[-1]
    matches_png = glob.glob(f"{app_data}/**/{pattern}*.png", recursive=True)
    if matches_png:
        return matches_png[-1]
    raise FileNotFoundError(f"Image for pattern {pattern} or {local_path} not found")


def make_white_silhouette(in_path, size):
    """
    Convert a black & white graphic into a pure white RGBA silhouette with smooth alpha,
    centered with margins matching vanilla race icons.
    """
    im = Image.open(in_path).convert("L")
    arr = np.array(im, dtype=np.float32)
    # Smooth step alpha threshold
    alpha = np.clip((arr - 40.0) / (200.0 - 40.0) * 255.0, 0.0, 255.0).astype(np.uint8)
    h, w = arr.shape
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., 0] = 255
    out[..., 1] = 255
    out[..., 2] = 255
    out[..., 3] = alpha
    res = Image.fromarray(out, mode="RGBA")

    bbox = res.getbbox()
    if bbox:
        cropped = res.crop(bbox)
        target_inner = int(size[0] * 0.72)
        cw, ch = cropped.size
        scale = min(target_inner / cw, target_inner / ch)
        new_w = max(1, int(cw * scale))
        new_h = max(1, int(ch * scale))
        scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        final_im = Image.new("RGBA", size, (255, 255, 255, 0))
        ox = (size[0] - new_w) // 2
        oy = (size[1] - new_h) // 2
        final_im.paste(scaled, (ox, oy), scaled)
        return final_im
    return res.resize(size, Image.Resampling.LANCZOS)


def save_dds_dxt5(im, path):
    """Write a BC3/DXT5 DDS with a full mip chain - the format working class mods
    (e.g. MindWeaver) ship for ClassIcons. Returns the mip count."""
    import struct
    im = im.convert("RGBA")
    w, h = im.size
    levels, data = [], b""
    lw, lh = w, h
    while True:
        lvl = im if (lw, lh) == (w, h) else im.resize((lw, lh), Image.Resampling.LANCZOS)
        # BC3 works on 4x4 blocks; pad tiny mips up to a whole block
        pw, ph = max(4, (lw + 3) // 4 * 4), max(4, (lh + 3) // 4 * 4)
        if (pw, ph) != (lw, lh):
            padded = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            padded.paste(lvl, (0, 0))
            lvl = padded
        data += lvl.tobytes("bcn", 3)
        levels.append((lw, lh))
        if lw == 1 and lh == 1:
            break
        lw, lh = max(1, lw // 2), max(1, lh // 2)
    mips = len(levels)
    linear = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * 16
    # DDSD_CAPS|HEIGHT|WIDTH|PIXELFORMAT|MIPMAPCOUNT|LINEARSIZE
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000
    header = struct.pack("<4sIIIIIII44x", b"DDS ", 124, flags, h, w, linear, 0, mips)
    header += struct.pack("<II4s20x", 32, 0x4, b"DXT5")          # pixel format: FourCC DXT5
    header += struct.pack("<II12x", 0x1000 | 0x8 | 0x400000, 0)     # caps: TEXTURE|COMPLEX|MIPMAP
    assert len(header) == 128
    with open(path, "wb") as f:
        f.write(header + data)
    return mips


def save_image_variants(im, dir_list, base_name):
    """Save an image in DDS (uppercase), dds (lowercase), and png formats across specified directories."""
    for directory in dir_list:
        os.makedirs(directory, exist_ok=True)
        # DDS uppercase
        dds_upper = os.path.join(directory, f"{base_name}.DDS")
        im.save(dds_upper)
        # dds lowercase
        dds_lower = os.path.join(directory, f"{base_name}.dds")
        im.save(dds_lower)
        # png
        png_path = os.path.join(directory, f"{base_name}.png")
        im.save(png_path)


raw_icons = {
    "Spell_FentLean": ("icon_fent_lean", "FentLean.png"),
    "Spell_SlingPoop": ("icon_sling_poop", "SlingPoop.png"),
    "Spell_SlingFentanyl": ("icon_sling_fentanyl", "SlingFentanyl.png"),
    "Spell_SnapOutLean": ("icon_snap_out_lean", "SnapOutLean.png"),
    "Spell_Panhandling": ("icon_panhandling", "AggressivePanhandling.png"),
    "Class_HomelessCalifornian": ("icon_class_crest", "HomelessCalifornianCrest.png"),
    "Spell_AvocadoToast": ("AvocadoToast", "AvocadoToast.png")
}

# Optional spell art: picked up from assets/icons/<MapKey>.png when present
# (generate_mod.icon_line() falls back to an existing icon otherwise).
OPTIONAL_ICONS = [
    "Spell_SidewalkScramble", "Spell_FeralScreech", "Spell_EvictionNotice", "Spell_TentEncampment",
    "Spell_Call311", "Spell_BiohazardBomb", "Spell_BottleShank", "Spell_CartCharge", "Spell_TurnstileHop",
]

CLASS_IDENTIFIERS = [
    "HomelessCalifornian",
    "TenderloinBiohazard",
    "VeniceBoardwalkBrawler",
    "BARTPlatformMenace"
]

RACE_IDENTIFIERS = {
    "Californian": ("icon_race_californian", "Race_Californian.jpg"),
    "Californian_Beachborn": ("icon_subrace_beachborn", "Subrace_Beachborn.jpg"),
    "Californian_Siliconite": ("icon_subrace_siliconite", "Subrace_Siliconite.jpg"),
    "Californian_InlandEmperor": ("icon_subrace_inland", "Subrace_InlandEmperor.jpg")
}


def main():
    print("=== Processing Mod Icons and Texture Atlas ===")
    atlas_size = 512
    tile_size = 128
    atlas_img = Image.new("RGBA", (atlas_size, atlas_size), (0, 0, 0, 0))

    positions = {
        "Spell_FentLean": (0, 0),
        "Spell_SlingPoop": (1, 0),
        "Spell_SlingFentanyl": (2, 0),
        "Spell_SnapOutLean": (3, 0),
        "Spell_Panhandling": (0, 1),
        "Class_HomelessCalifornian": (1, 1),
        "Spell_AvocadoToast": (2, 1)
    }

    # Fill the remaining 4x4 atlas cells with any optional art that exists
    free_cells = [(c, r) for r in range(4) for c in range(4) if (c, r) not in positions.values()]
    icon_sources = dict(raw_icons)
    for key in OPTIONAL_ICONS:
        if os.path.exists(os.path.join(ASSETS_DIR, f"{key}.png")) and free_cells:
            icon_sources[key] = (None, f"{key}.png")
            positions[key] = free_cells.pop(0)

    uv_map = {}
    crest_img = None
    loaded_imgs = {}

    for map_key, (pattern, fallback_name) in icon_sources.items():
        src_path = find_img(pattern, fallback_name) if pattern else os.path.join(ASSETS_DIR, fallback_name)
        img = Image.open(src_path).convert("RGBA")
        loaded_imgs[map_key] = img

        # Save local copy in assets as PNG
        png_name = fallback_name.rsplit(".", 1)[0] + ".png"
        local_dest = os.path.join(ASSETS_DIR, png_name)
        img.save(local_dest)

        if map_key == "Class_HomelessCalifornian":
            crest_img = img

        tile = img.resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        col, row = positions[map_key]
        x = col * tile_size
        y = row * tile_size
        atlas_img.paste(tile, (x, y))

        u1 = (x + 0.5) / atlas_size
        u2 = (x + tile_size - 0.5) / atlas_size
        v1 = (y + 0.5) / atlas_size
        v2 = (y + tile_size - 0.5) / atlas_size
        uv_map[map_key] = (u1, u2, v1, v2)

    # Alias class UV coordinates for CC and subclasses
    class_uv = uv_map["Class_HomelessCalifornian"]
    for c_id in CLASS_IDENTIFIERS:
        uv_map[c_id] = class_uv
        uv_map[f"Class_{c_id}"] = class_uv

    # Save Tooltips (380x380) and ControllerUIIcons (144x144)
    print("Generating Tooltips and Controller UI loose icons...")
    for map_key, img in loaded_imgs.items():
        tt_img = img.resize((380, 380), Image.Resampling.LANCZOS)
        ctrl_img = img.resize((144, 144), Image.Resampling.LANCZOS)
        tt_img.save(os.path.join(GAME_TOOLTIPS_DIR, f"{map_key}.DDS"))
        ctrl_img.save(os.path.join(GAME_CONTROLLER_DIR, f"{map_key}.DDS"))

    if crest_img is not None:
        crest_380 = crest_img.resize((380, 380), Image.Resampling.LANCZOS)
        crest_144 = crest_img.resize((144, 144), Image.Resampling.LANCZOS)
        for c_id in CLASS_IDENTIFIERS:
            for k in [c_id, f"Class_{c_id}"]:
                crest_380.save(os.path.join(GAME_TOOLTIPS_DIR, f"{k}.DDS"))
                crest_144.save(os.path.join(GAME_CONTROLLER_DIR, f"{k}.DDS"))

    # Save texture atlas in DDS and PNG
    atlas_dds_path = os.path.join(TEXTURE_DIR, "HomelessCalifornianAtlas.dds")
    atlas_png_path = os.path.join(TEXTURE_DIR, "HomelessCalifornianAtlas.png")
    atlas_img.save(atlas_png_path)
    atlas_img.save(atlas_dds_path)
    print(f"Saved texture atlas: {atlas_dds_path}")

    # Generate GUI/HomelessCalifornianAtlas.lsx and GUI/Icons_Items.lsx
    gui_lsx_path = os.path.join(GUI_DIR, "HomelessCalifornianAtlas.lsx")
    icons_items_path = os.path.join(GUI_DIR, "Icons_Items.lsx")
    uv_nodes = []
    for map_key, (u1, u2, v1, v2) in uv_map.items():
        uv_nodes.append(f"""                <node id="IconUV">
                    <attribute id="MapKey" type="FixedString" value="{map_key}"/>
                    <attribute id="U1" type="float" value="{u1:.8f}"/>
                    <attribute id="U2" type="float" value="{u2:.8f}"/>
                    <attribute id="V1" type="float" value="{v1:.8f}"/>
                    <attribute id="V2" type="float" value="{v2:.8f}"/>
                </node>""")

    gui_lsx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="7" revision="1" build="3"/>
    <region id="IconUVList">
        <node id="root">
            <children>
{chr(10).join(uv_nodes)}
            </children>
        </node>
    </region>
    <region id="TextureAtlasInfo">
        <node id="root">
            <children>
                <node id="TextureAtlasIconSize">
                    <attribute id="Height" type="int32" value="128"/>
                    <attribute id="Width" type="int32" value="128"/>
                </node>
                <node id="TextureAtlasPath">
                    <attribute id="Path" type="string" value="Assets/Textures/Icons/HomelessCalifornianAtlas.dds"/>
                    <attribute id="UUID" type="FixedString" value="{ATLAS_TEXTURE_UUID}"/>
                </node>
                <node id="TextureAtlasTextureSize">
                    <attribute id="Height" type="int32" value="{atlas_size}"/>
                    <attribute id="Width" type="int32" value="{atlas_size}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(gui_lsx_path, "w", encoding="utf-8") as f:
        f.write(gui_lsx_content)
    with open(icons_items_path, "w", encoding="utf-8") as f:
        f.write(gui_lsx_content)
    print(f"Generated GUI atlas LSX: {gui_lsx_path} and {icons_items_path}")

    # Generate Content/[PAK]_HomelessCalifornian/{UUID}.lsx and convert to .lsf
    content_lsx_path = os.path.join(CONTENT_DIR, f"{ATLAS_TEXTURE_UUID}.lsx")
    content_lsf_path = os.path.join(CONTENT_DIR, f"{ATLAS_TEXTURE_UUID}.lsf")

    content_lsx_body = f"""<?xml version="1.0" encoding="utf-8"?>
<save>
    <version major="4" minor="7" revision="1" build="3"/>
    <region id="TextureBank">
        <node id="TextureBank">
            <children>
                <node id="Resource">
                    <attribute id="ID" type="FixedString" value="{ATLAS_TEXTURE_UUID}"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornianAtlas"/>
                    <attribute id="SourceFile" type="LSString" value="Public/HomelessCalifornian/Assets/Textures/Icons/HomelessCalifornianAtlas.dds"/>
                    <attribute id="Template" type="FixedString" value="HomelessCalifornianAtlas"/>
                    <attribute id="Streaming" type="bool" value="True"/>
                    <attribute id="Type" type="int32" value="1"/>
                    <attribute id="SRGB" type="bool" value="False"/>
                    <attribute id="Width" type="int32" value="{atlas_size}"/>
                    <attribute id="Height" type="int32" value="{atlas_size}"/>
                    <attribute id="Depth" type="int32" value="1"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(content_lsx_path, "w", encoding="utf-8") as f:
        f.write(content_lsx_body)

    subprocess.run([DIVINE_EXE, "-g", "bg3", "-a", "convert-resource", "-s", content_lsx_path, "-d", content_lsf_path], check=True)
    print(f"Compiled Content LSF: {content_lsf_path}")

    # -------------------------------------------------------------
    # 2. Race Silhouettes (Fixes "Brown Window" in CC)
    # -------------------------------------------------------------
    print("Generating Character Creation Race silhouette icons...")
    for race_name, (pat, fb_name) in RACE_IDENTIFIERS.items():
        src_path = find_img(pat, fb_name)
        sil_196 = make_white_silhouette(src_path, (196, 196))
        sil_100 = make_white_silhouette(src_path, (100, 100))

        # Save 196x196 HighRes
        save_image_variants(sil_196, [GAME_RACE_ICONS_DIR, PUB_RACE_ICONS_DIR, MODS_RACE_ICONS_DIR], race_name)
        # Save 100x100 LowRes
        save_image_variants(sil_100, [GAME_RACE_LOWRES_DIR, PUB_RACE_LOWRES_DIR, MODS_RACE_LOWRES_DIR], race_name)
        print(f"  [OK] Generated race icons for {race_name}")

    # -------------------------------------------------------------
    # 3. Class Icons (Fixes "Black Box" in CC)
    # -------------------------------------------------------------
    # Matches working class mods on disk (MindWeaver): only
    #   Mods/<Folder>/GUI/Assets/ClassIcons/<ClassName>.DDS         300x300 DXT5 + mips
    #   Mods/<Folder>/GUI/Assets/ClassIcons/hotbar/<ClassName>.DDS  112x112 DXT5 + mips
    # with upper-case .DDS and matching GUI/metadata.lsf entries (keys use .png).
    # Earlier builds scattered uncompressed, lower-case .dds copies; remove them.
    print("Generating Character Creation Class icons...")
    for d in [GAME_CLASS_ICONS_DIR, GAME_HOTBAR_DIR, GAME_LOWRES_CLASS_DIR, GAME_LOWRES_HOTBAR_DIR,
              PUB_CLASS_ICONS_DIR, PUB_HOTBAR_DIR, PUB_LOWRES_CLASS_DIR, PUB_LOWRES_HOTBAR_DIR,
              MODS_CLASS_ICONS_DIR, MODS_HOTBAR_DIR, MODS_LOWRES_CLASS_DIR, MODS_LOWRES_HOTBAR_DIR,
              MODS_ASSETS_DIR, MODS_LOWRES_DIR]:
        for c_id in CLASS_IDENTIFIERS:
            for ext in (".DDS", ".dds", ".png"):
                stale = os.path.join(d, c_id + ext)
                if os.path.exists(stale):
                    os.remove(stale)
    for d in [GAME_CLASS_ICONS_DIR, GAME_HOTBAR_DIR, GAME_LOWRES_CLASS_DIR, GAME_LOWRES_HOTBAR_DIR,
              PUB_CLASS_ICONS_DIR, PUB_HOTBAR_DIR, PUB_LOWRES_CLASS_DIR, PUB_LOWRES_HOTBAR_DIR,
              MODS_LOWRES_CLASS_DIR, MODS_LOWRES_HOTBAR_DIR]:
        try:
            os.removedirs(d)  # only removes now-empty folders
        except OSError:
            pass
    os.makedirs(MODS_HOTBAR_DIR, exist_ok=True)

    class_mips = {}
    for c_id in CLASS_IDENTIFIERS:
        art_path = os.path.join(ASSETS_DIR, f"Class_{c_id}.png")
        art = Image.open(art_path).convert("RGBA") if os.path.exists(art_path) else crest_img
        if art is None:
            continue
        m_big = save_dds_dxt5(art.resize((300, 300), Image.Resampling.LANCZOS),
                              os.path.join(MODS_CLASS_ICONS_DIR, f"{c_id}.DDS"))
        m_bar = save_dds_dxt5(art.resize((112, 112), Image.Resampling.LANCZOS),
                              os.path.join(MODS_HOTBAR_DIR, f"{c_id}.DDS"))
        class_mips[c_id] = (m_big, m_bar)
        print(f"  [OK] Class icon for {c_id} ({'own art' if art is not crest_img else 'class crest'})")

    # -------------------------------------------------------------
    # 4. Patch 7 Metadata
    # -------------------------------------------------------------
    print("Generating Patch 7 metadata.lsx and metadata.lsf...")
    metadata_objects = []

    for c_id, (m_big, m_bar) in class_mips.items():
        for key, w, h, mips in [
            (f"Assets/ClassIcons/{c_id}.png", 300, 300, m_big),
            (f"Assets/ClassIcons/hotbar/{c_id}.png", 112, 112, m_bar),
        ]:
            metadata_objects.append(f"""						<node id="Object">
							<attribute id="MapKey" type="FixedString" value="{key}" />
							<children>
								<node id="entries">
									<attribute id="h" type="int16" value="{h}" />
									<attribute id="mipcount" type="int8" value="{mips}" />
									<attribute id="w" type="int16" value="{w}" />
								</node>
							</children>
						</node>""")

    for r_id in RACE_IDENTIFIERS.keys():
        for key, w, h in [
            (f"Assets/CC/icons_races/{r_id}.png", 196, 196),
            (f"AssetsLowRes/CC/icons_races/{r_id}.png", 100, 100)
        ]:
            metadata_objects.append(f"""						<node id="Object">
							<attribute id="MapKey" type="FixedString" value="{key}" />
							<children>
								<node id="entries">
									<attribute id="h" type="int16" value="{h}" />
									<attribute id="mipcount" type="int8" value="1" />
									<attribute id="w" type="int16" value="{w}" />
								</node>
							</children>
						</node>""")

    metadata_lsx_content = f"""<?xml version="1.0" encoding="utf-8"?>
<save>
	<version major="4" minor="8" revision="0" build="10" lslib_meta="v1,bswap_guids,lsf_keys_adjacency" />
	<region id="config">
		<node id="config">
			<children>
				<node id="entries">
					<children>
{chr(10).join(metadata_objects)}
					</children>
				</node>
			</children>
		</node>
	</region>
</save>
"""
    metadata_lsx_path = os.path.join(MODS_GUI_DIR, "metadata.lsx")
    metadata_lsf_path = os.path.join(MODS_GUI_DIR, "metadata.lsf")

    with open(metadata_lsx_path, "w", encoding="utf-8") as f:
        f.write(metadata_lsx_content)

    subprocess.run([DIVINE_EXE, "-g", "bg3", "-a", "convert-resource", "-s", metadata_lsx_path, "-d", metadata_lsf_path], check=True)
    print(f"Compiled Patch 7 metadata LSF: {metadata_lsf_path}")

    print("\nIcon processing and loose assets generated successfully!")

if __name__ == "__main__":
    main()
