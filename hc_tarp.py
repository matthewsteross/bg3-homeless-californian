"""Blue Tarp Lean-To: a custom 3D prop (blue plastic tarp over a ridge pole on two rebar uprights, with grommets,
rope guy lines, stakes and bricks) spawned by the Overpass shout HC_Shout_BlueTarpLeanTo (hc_overpass.py).

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were
produced by Claude, see assets/models/HC_BlueTarp/ (build_tarp_model.py, tarp_paint.py, render_tarp.py; Blender is
used only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket skeleton,
exactly the pipeline of the shopping cart (hc_cart.py), which is verified spawning in game:
visual resource (Texture/Material/VisualBank) -> root template -> Object stat -> GROUND:Spawn(template) on a spell.
File-level verified only. UNVERIFIED in game: that the Shout's GROUND:Spawn resolves at a useful point (a self-centred
Shout may drop the prop under the caster), facing, collision bounds, scale and the texture look.
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_BlueTarp"
ASSET_FILES = ("HC_BlueTarp.GR2", "HC_BlueTarp_BM.DDS", "HC_BlueTarp_NM.DDS", "HC_BlueTarp_PM.DDS")

# Model bounds in metres (work/tarp/out/tarp_bounds.json): ground origin, +Z open front, ridge runs along X.
BMIN = (-1.2286, -0.002, -1.163)
BMAX = (1.2286, 1.4036, 1.183)
TRIANGLES = 2544
OBJECT_STAT = "HC_OBJ_BlueTarp"
TEMPLATE_KEY = "HC_BlueTarp_RootTemplate"   # get_guid key of the root template; hc_overpass.py spawns it
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Parent template of Ducq's grill and truck props (vanilla), used for a static world item (same as the cart).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"


def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_BlueTarp_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_BlueTarp_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_BlueTarp_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_BlueTarp.{mesh}.{i}" />
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
{tex('BM', 'bm', 'True', 512)}{tex('NM', 'nm', 'False', 256)}{tex('PM', 'pm', 'False', 256)}			</children>
		</node>
	</region>
	<region id="MaterialBank">
		<node id="MaterialBank">
			<children>
				<node id="Resource">
					<attribute id="DiffusionProfileUUID" type="FixedString" value="" />
					<attribute id="ID" type="FixedString" value="{ids['mat']}" />
					<attribute id="MaterialType" type="uint8" value="0" />
					<attribute id="Name" type="LSString" value="HC_BlueTarp_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_BlueTarp" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_BlueTarp.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_BlueTarp.{FIRE_BASKET_SKELETON}.0" />
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


def generate_tarp(public_dir, add_loca, get_guid):
    """Write the tarp assets, resources, root template and Object stat. Grants no spells (hc_overpass.py spawns it)."""
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_BlueTarp"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_BlueTarp/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_BlueTarp" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_BlueTarp).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing tarp asset {source}; rebuild it with assets/models/HC_BlueTarp/build_tarp_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_BlueTarp_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the cart.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Blue Tarp Lean-To"
    item_desc = ("A blue tarp, two pieces of rebar and a great deal of optimism. It sheds rain, wind and "
                 "questions from the city, in roughly that order. The rope is knotted with the confidence of "
                 "someone who has watched one video about it.")
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
    height = BMAX[1]
    # Collision: the two rebar uprights and the slopes make the interior walkable at the ends, so the inner
    # (type 0) bound is a slim block along the ridge instead of the full footprint.
    inner = ((-1.0, 0.0, -0.45), (1.0, height, 0.45))
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, inner, 0.35)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        fmt = lambda v: " ".join(f"{x:g}" for x in v)
        for attr, kind, value in (("Height", "float", f"{height:g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_BlueTarp.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart).
    (stats / "HC_Object_BlueTarp.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "20"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")
    return {"base": {}, "subclasses": {}}
