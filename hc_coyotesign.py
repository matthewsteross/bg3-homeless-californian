"""Meshy AI text-to-3D coyotesign; converted by our GLB/DAE/Divine/DDS pipeline.
Vanilla evidence: Shared/Stats/Generated/Data/Object.txt:1 (_BaseItem);
GustavDev/Stats/Generated/Data/Spell_ProjectileStrike.txt:71 (Spawn with status).
Lifetime recipe and exact citations: hc_prop_lifetime.py.
UNVERIFIED in game: spawn on HC_Shout_NextdoorLostCoyoteThread alongside existing effects,
facing, collision, scale, texture look and ten-turn (~60 s) Kill removal.
BM uses original Meshy colour; flat NM; PM derives from Meshy roughness.
No new spell, icon or grant. Preview review and dimensions: work/coyotesign-report.md.
"""
from pathlib import Path
import shutil
from hc_prop_lifetime import prop_lifetime
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_CoyoteSign"
ASSET_FILES = ("HC_CoyoteSign.GR2", "HC_CoyoteSign_BM.DDS", "HC_CoyoteSign_NM.DDS", "HC_CoyoteSign_PM.DDS")

import json
_bounds = json.loads((ASSET_SRC / 'coyotesign_bounds.json').read_text())
BMIN = tuple(_bounds['min'])
BMAX = tuple(_bounds['max'])
TRIANGLES = _bounds['tris']
OBJECT_STAT = "HC_CoyoteSign_Object"
TEMPLATE_KEY = "HC_CoyoteSign_RootTemplate"
SPELL = "HC_Shout_NextdoorLostCoyoteThread"
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Vanilla static-world-item parent template, used for a static world item (same as cart, tarp, barricade, tent).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"
# Conservative central bounds; outer bounds include every mesh vertex.
INNER_MIN = (BMIN[0] * 0.8, BMIN[1], BMIN[2] * 0.8)
INNER_MAX = (BMAX[0] * 0.8, BMAX[1], BMAX[2] * 0.8)



def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_CoyoteSign_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_CoyoteSign_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_CoyoteSign_{name}" />
					<attribute id="Type" type="int32" value="1" />
					<attribute id="Width" type="int32" value="{size}" />
					<attribute id="_OriginalFileVersion_" type="int64" value="144115207403209024" />
				</node>
'''

    def tex_param(group_key, param):
        return f'''						<node id="Texture2DParameters">
							<attribute id="Enabled" type="bool" value="True" />
							<attribute id="ExportAsPreset" type="bool" value="True" />
							<attribute id="GroupName" type="FixedString" value="Texture Map" />
							<attribute id="ID" type="FixedString" value="{ids[group_key]}" />
							<attribute id="ParameterName" type="FixedString" value="{param}" />
						</node>
'''

    lods = ''.join(f'''						<node id="Objects">
							<attribute id="LOD" type="uint8" value="{i}" />
							<attribute id="MaterialID" type="FixedString" value="{ids['mat']}" />
							<attribute id="ObjectID" type="FixedString" value="HC_CoyoteSign.{mesh}.{i}" />
							<attribute id="Physics" type="FixedString" value="" />
							<attribute id="Slot" type="FixedString" value="" />
						</node>
''' for i, mesh in enumerate(FIRE_BASKET_MESHES))
    center = tuple((a + b) / 2 for a, b in zip(BMIN, BMAX))
    radius = sum(((b - a) / 2) ** 2 for a, b in zip(BMIN, BMAX)) ** 0.5
    fmt = lambda v: ' '.join(f'{x:g}' for x in v)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<save>
	<version major="4" minor="0" revision="9" build="0" lslib_meta="v1,bswap_guids,lsf_adjacency" />
	<region id="TextureBank">
		<node id="TextureBank">
			<children>
{tex('BM', 'bm', 'True', 1024)}{tex('NM', 'nm', 'False', 256)}{tex('PM', 'pm', 'False', 256)}			</children>
		</node>
	</region>
	<region id="MaterialBank">
		<node id="MaterialBank">
			<children>
				<node id="Resource">
					<attribute id="DiffusionProfileUUID" type="FixedString" value="" />
					<attribute id="ID" type="FixedString" value="{ids['mat']}" />
					<attribute id="MaterialType" type="uint8" value="0" />
					<attribute id="Name" type="LSString" value="HC_CoyoteSign_Mat" />
					<attribute id="SourceFile" type="LSString" value="Public/Shared/Assets/Materials/Base/Base.lsf" />
					<attribute id="_OriginalFileVersion_" type="int64" value="144115207403209030" />
					<children>
						<node id="ScalarParameters">
							<attribute id="BaseValue" type="float" value="0" />
							<attribute id="Enabled" type="bool" value="False" />
							<attribute id="ExportAsPreset" type="bool" value="False" />
							<attribute id="GroupName" type="FixedString" value="" />
							<attribute id="ParameterName" type="FixedString" value="SeeThroughEnabled" />
							<attribute id="Value" type="float" value="0" />
						</node>
						<node id="ScalarParameters">
							<attribute id="BaseValue" type="float" value="0.5" />
							<attribute id="Enabled" type="bool" value="False" />
							<attribute id="ExportAsPreset" type="bool" value="True" />
							<attribute id="GroupName" type="FixedString" value="" />
							<attribute id="ParameterName" type="FixedString" value="Reflectance" />
							<attribute id="Value" type="float" value="0.5" />
						</node>
{tex_param('nm', 'normalmap')}{tex_param('bm', 'basecolor')}{tex_param('pm', 'physicalmap')}					</children>
				</node>
			</children>
		</node>
	</region>
	<region id="VisualBank">
		<node id="VisualBank">
			<children>
				<node id="Resource">
					<attribute id="AttachBone" type="FixedString" value="" />
					<attribute id="AttachmentSkeletonResource" type="FixedString" value="" />
					<attribute id="BlueprintInstanceResourceID" type="FixedString" value="" />
					<attribute id="BoundsMax" type="fvec3" value="{fmt(BMAX)}" />
					<attribute id="BoundsMin" type="fvec3" value="{fmt(BMIN)}" />
					<attribute id="Center" type="fvec3" value="{fmt(center)}" />
					<attribute id="ID" type="FixedString" value="{ids['visual']}" />
					<attribute id="Initialized" type="bool" value="True" />
					<attribute id="Localized" type="bool" value="False" />
					<attribute id="MaterialType" type="uint8" value="0" />
					<attribute id="Name" type="LSString" value="HC_CoyoteSign" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_CoyoteSign.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_CoyoteSign.{FIRE_BASKET_SKELETON}.0" />
					<attribute id="_OriginalFileVersion_" type="int64" value="144115188075855912" />
					<children>
						<node id="AnimationWaterfall">
							<attribute id="Object" type="FixedString" value="" />
						</node>
						<node id="Base" />
{lods}					</children>
				</node>
			</children>
		</node>
	</region>
</save>
'''


def generate_coyotesign(public_dir, add_loca, get_guid):
    """Write coyotesign assets and object resources, then patch HC_Shout_NextdoorLostCoyoteThread."""
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_CoyoteSign"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_CoyoteSign/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_CoyoteSign" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_CoyoteSign).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing coyotesign asset {source}; rebuild it with assets/models/HC_CoyoteSign/build_coyotesign_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_CoyoteSign_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the cart, tarp, barricade and tent.
    template_id = get_guid(TEMPLATE_KEY)
    title = 'Lost Coyote Sandwich Board'
    item_desc = 'Last seen near the dumpster. 214 comments, no coyote.'
    title_handle = add_loca(OBJECT_STAT + "_Name", title)
    desc_handle = add_loca(OBJECT_STAT + "_Description", item_desc)
    save = ET.Element("save")
    ET.SubElement(save, "version", major="4", minor="0", revision="9", build="0")
    region = ET.SubElement(save, "region", id="Templates")
    templates = ET.SubElement(region, "node", id="Templates")
    children = ET.SubElement(templates, "children")
    obj = ET.SubElement(children, "node", id="GameObjects")
    for attr, kind, value in (
        ("CanBeMoved", "bool", "False"),
        ("CanBePickedUp", "bool", "False"),
        ("Flag", "int32", "0"),
        ("LevelName", "FixedString", ""),
        ("MapKey", "FixedString", template_id),
        ("Name", "LSString", OBJECT_STAT),
        ("ParentTemplateId", "FixedString", PARENT_TEMPLATE),
        ("ReadinessFlags", "uint32", "144"),
        ("RecieveDecal", "bool", "False"),
        ("Stats", "FixedString", OBJECT_STAT),
        ("Tooltip", "uint8", "2"),
        ("Type", "FixedString", "item"),
        ("VisualTemplate", "FixedString", ids["visual"]),
    ):
        ET.SubElement(obj, "attribute", id=attr, type=kind, value=value)
    for attr, handle in (("DisplayName", title_handle), ("Description", desc_handle)):
        ET.SubElement(obj, "attribute", id=attr, type="TranslatedString", handle=handle, version="1")
    kids = ET.SubElement(obj, "children")
    bounds = ET.SubElement(kids, "node", id="Bounds")
    bchildren = ET.SubElement(bounds, "children")
    fmt = lambda v: " ".join(f"{x:.9g}" for x in v)
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, (INNER_MIN, INNER_MAX), 0.35)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        for attr, kind, value in (("Height", "float", f"{hi[1]:.9g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_CoyoteSign.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart, HC_OBJ_BlueTarp, HC_OBJ_Barricade and HC_OBJ_PopUpTent).
    (stats / "HC_CoyoteSign_Object.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "120"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    status_text, _ = prop_lifetime(template_id)
    (stats / 'HC_Status_PropLifetime.txt').write_text(status_text, encoding='utf-8', newline='\n')
    patch_coyotesign_spell(stats, template_id)
    return {"base": {}, "subclasses": {}, "existing_list_spells": {}}


def patch_coyotesign_spell(stats, template_id):
    """Patch exactly one existing spell, preserving every other byte and functor."""
    import re
    matches = []
    pattern = re.compile(r'(new entry "HC_Shout_NextdoorLostCoyoteThread"[^\S\r\n]*\r?\n)(.*?)(?=^new entry |\Z)', re.M | re.S)
    for path in sorted(Path(stats).glob('*.txt')):
        text = path.read_bytes().decode('utf-8')
        for match in pattern.finditer(text):
            matches.append((path, text, match))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one HC_Shout_NextdoorLostCoyoteThread spell; found {len(matches)} in {stats}')
    path, text, match = matches[0]
    block = match.group(0)
    prop = re.search(r'(data "SpellProperties" ")([^"]*)(")', block)
    if prop is None:
        raise ValueError('HC_Shout_NextdoorLostCoyoteThread has no SpellProperties value')
    _, spawn = prop_lifetime(template_id)
    legacy = f'GROUND:Spawn({template_id})'
    value = prop.group(2)
    terms = value.split(';')
    if spawn in terms and legacy not in terms:
        return
    # Upgrade an old plain spawn rather than creating a second prop.
    terms = [term for term in terms if term not in (legacy, spawn)]
    value = ';'.join(terms) + ';' + spawn
    block = block[:prop.start(2)] + value + block[prop.end(2):]
    path.write_bytes((text[:match.start()] + block + text[match.end():]).encode('utf-8'))
