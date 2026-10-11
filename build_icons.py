"""
Process generated icons into BG3 texture atlas and Content/GUI definitions.
"""

import os
import glob
import subprocess
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src", "HomelessCalifornian")
PUBLIC_DIR = os.path.join(SRC_DIR, "Public", "HomelessCalifornian")
TOOLS_DIR = os.path.join(ROOT_DIR, "tools", "Packed", "Tools")
DIVINE_EXE = os.path.join(TOOLS_DIR, "Divine.exe")

ASSETS_DIR = os.path.join(ROOT_DIR, "assets", "icons")
TEXTURE_DIR = os.path.join(PUBLIC_DIR, "Assets", "Textures", "Icons")
GUI_DIR = os.path.join(PUBLIC_DIR, "GUI")
CONTENT_DIR = os.path.join(PUBLIC_DIR, "Content", "[PAK]_HomelessCalifornian")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(TEXTURE_DIR, exist_ok=True)
os.makedirs(GUI_DIR, exist_ok=True)
os.makedirs(CONTENT_DIR, exist_ok=True)

# Fixed UUID for the Texture Resource
ATLAS_TEXTURE_UUID = "e4a28f11-9a70-4f51-b847-a89a0cb1d923"

app_data = os.path.join(os.environ["USERPROFILE"], ".gemini", "antigravity", "brain")

def find_img(pattern):
    matches = glob.glob(f"{app_data}/**/{pattern}*.jpg", recursive=True)
    if not matches:
        raise FileNotFoundError(f"Image for pattern {pattern} not found")
    return matches[-1]

raw_icons = {
    "Spell_FentLean": ("icon_fent_lean", "FentLean.png"),
    "Spell_SlingPoop": ("icon_sling_poop", "SlingPoop.png"),
    "Spell_SlingFentanyl": ("icon_sling_fentanyl", "SlingFentanyl.png"),
    "Spell_SnapOutLean": ("icon_snap_out_lean", "SnapOutLean.png"),
    "Spell_Panhandling": ("icon_panhandling", "AggressivePanhandling.png"),
    "Class_HomelessCalifornian": ("icon_class_crest", "HomelessCalifornianCrest.png")
}

# 1. Save PNG copies and assemble 512x512 atlas
def main():
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
    }

    uv_map = {}

    for map_key, (pattern, png_name) in raw_icons.items():
        src_path = find_img(pattern)
        img = Image.open(src_path).convert("RGBA")
        
        # Save high-res png
        png_dest = os.path.join(ASSETS_DIR, png_name)
        img.save(png_dest)
        print(f"Saved asset: {png_dest}")
        
        # Resize to tile
        tile = img.resize((tile_size, tile_size), Image.Resampling.LANCZOS)
        col, row = positions[map_key]
        x = col * tile_size
        y = row * tile_size
        atlas_img.paste(tile, (x, y))
        
        # Half-pixel inset to avoid edge bleeding
        u1 = (x + 0.5) / atlas_size
        u2 = (x + tile_size - 0.5) / atlas_size
        v1 = (y + 0.5) / atlas_size
        v2 = (y + tile_size - 0.5) / atlas_size
        uv_map[map_key] = (u1, u2, v1, v2)

    # Save atlas DDS
    atlas_dds_path = os.path.join(TEXTURE_DIR, "HomelessCalifornianAtlas.dds")
    atlas_png_path = os.path.join(TEXTURE_DIR, "HomelessCalifornianAtlas.png")
    atlas_img.save(atlas_png_path)
    atlas_img.save(atlas_dds_path)
    print(f"Saved texture atlas: {atlas_dds_path}")

    # 2. Generate GUI/HomelessCalifornianAtlas.lsx
    gui_lsx_path = os.path.join(GUI_DIR, "HomelessCalifornianAtlas.lsx")
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
    print(f"Generated GUI atlas LSX: {gui_lsx_path}")

    # 3. Generate Content/[PAK]_HomelessCalifornian/{ATLAS_TEXTURE_UUID}.lsx and convert to .lsf
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
    print("Icon processing and registration complete!")

if __name__ == "__main__":
    main()
