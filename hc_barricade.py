"""Caltrans "LANE CLOSED AHEAD" barricade: a custom 3D prop (orange-and-white Type III barricade with three striped
slat boards, two reflective-collar traffic cones, a sandbag on each foot and an amber lamp) and the ground-target
spell HC_Target_CaltransLaneClosure that spawns it, with a short +2 AC status on the caster.

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were
produced by Claude, see assets/models/HC_Barricade/ (build_barricade_model.py, barricade_paint.py, render_barricade.py;
Blender is used only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket
skeleton, exactly the pipeline of the shopping cart (hc_cart.py) and the blue tarp (hc_tarp.py), both verified spawning
in game: visual resource (Texture/Material/VisualBank) -> root template -> Object stat -> GROUND:Spawn(template).

Vanilla evidence (temp_race/Public): donor Projectile_GEB_Perform_TossCoin (Spell_Projectile.txt, the same donor as
HC_Target_AbandonedCart), GROUND:Spawn(template) is its own SpellProperties, and ApplyStatus(SELF,...) appears in
Projectile spells (the AI_HELPER_EXTRAATTACK weapon-projectile entry). Icons: Spell_Conjuration_AcidSplash and
Spell_Abjuration_MageArmor are existing vanilla names already used by Round 7.
File-level verified only. UNVERIFIED in game: that the extra ApplyStatus(SELF) functor still runs next to GROUND:Spawn on
this Projectile donor, spawn facing (+Z front vs. caster), collision bounds, scale, and the texture look (the lamp is
only a bright amber in the base colour; there is no emissive map).
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_Barricade"
ASSET_FILES = ("HC_Barricade.GR2", "HC_Barricade_BM.DDS", "HC_Barricade_NM.DDS", "HC_Barricade_PM.DDS")

# Model bounds in metres (work/barricade/out/barricade_bounds.json): ground origin, +Z front (sheeting side).
BMIN = (-1.19, 0.0, -0.31)
BMAX = (1.19, 1.1, 0.523)
TRIANGLES = 1580
OBJECT_STAT = "HC_OBJ_Barricade"
TEMPLATE_KEY = "HC_Barricade_RootTemplate"
SPELL = "HC_Target_CaltransLaneClosure"
STATUS = "HC_LANE_CLOSURE_SHIELD"
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Parent template of Ducq's grill and truck props (vanilla), used for a static world item (same as cart and tarp).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"
DONOR = "Projectile_GEB_Perform_TossCoin"
SPELL_ICON_FALLBACK = "Spell_Conjuration_AcidSplash"
STATUS_ICON_FALLBACK = "Spell_Abjuration_MageArmor"


def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_Barricade_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_Barricade_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_Barricade_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_Barricade.{mesh}.{i}" />
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
					<attribute id="Name" type="LSString" value="HC_Barricade_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_Barricade" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_Barricade.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_Barricade.{FIRE_BASKET_SKELETON}.0" />
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


def generate_barricade(public_dir, add_loca, get_guid):
    """Write the barricade assets, resources, root template, Object stat, status and spell. Returns the spell grants."""
    from hc_icon_keys import icon_for_spell
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_Barricade"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_Barricade/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_Barricade" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_Barricade).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing barricade asset {source}; rebuild it with assets/models/HC_Barricade/build_barricade_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_Barricade_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the cart and tarp.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Caltrans 'Lane Closed Ahead' Barricade"
    item_desc = ("Orange stripes, white stripes, two cones and a painted amber lamp that looks like it has been blinking since the "
                 "previous administration. No one has ever seen the road work, only the barricade. It does not "
                 "block traffic so much as ask politely, and it is the single most respected object in California.")
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
    # Collision: a slim wall along the rails (the feet and cones stay outside the inner bound).
    inner = ((-1.15, 0.0, -0.08), (1.15, 0.95, 0.10))
    fmt = lambda v: " ".join(f"{x:g}" for x in v)
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, inner, 0.35)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        for attr, kind, value in (("Height", "float", f"{hi[1]:g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_Barricade.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart and HC_OBJ_BlueTarp).
    (stats / "HC_Object_Barricade.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "40"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    # 5. Status on the caster: +2 AC for 2 turns (same BOOST field set as the Round 7 statuses).
    status_title = add_loca(STATUS + "_Name", "Cones of Untouchable Authority")
    status_desc = add_loca(STATUS + "_Description",
                           "+2 Armour Class. Orange cones: the one thing nobody in California will cross.")
    (stats / "HC_Status_Barricade.txt").write_text(f'''new entry "{STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "StackId" "{STATUS}"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Icon" "{icon_for_spell(SPELL, STATUS_ICON_FALLBACK)}"
data "Boosts" "AC(2)"
data "DisplayName" "{status_title};1"
data "Description" "{status_desc};1"
''', encoding="utf-8")

    # 6. Spell: single-point ground target, donor Toss a Coin (a projectile that GROUND:Spawns one item), as the cart.
    spell_title = add_loca(SPELL + "_Name", title)
    spell_desc = add_loca(SPELL + "_Description",
                          "Drop a full Caltrans lane-closure setup on the ground within 9 m: barricade, two reflective cones, "
                          "sandbags and a painted amber lamp. Costs a bonus action and 1 Junk; once per short rest. "
                          "You also gain +2 Armour Class for 2 turns. "
                          "The lane has been closed ahead since ahead was a place you could still reach.")
    (stats / "HC_Spells_Barricade.txt").write_text(f'''new entry "{SPELL}"
type "SpellData"
using "{DONOR}"
data "SpellProperties" "GROUND:Spawn({template_id});ApplyStatus(SELF,{STATUS},100,2)"
data "TargetRadius" "9"
data "Icon" "{icon_for_spell(SPELL, SPELL_ICON_FALLBACK)}"
data "DisplayName" "{spell_title};1"
data "Description" "{spell_desc};1"
data "UseCosts" "BonusActionPoint:1;HC_Junk:1"
data "Cooldown" "OncePerShortRest"
''', encoding="utf-8")
    return {"base": {9: [SPELL]}, "subclasses": {}}   # base class has no level-3 progression node (subclass pick)
