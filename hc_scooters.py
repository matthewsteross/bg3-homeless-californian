"""Dockless Scooter Graveyard: a custom 3D prop (six abandoned rental e-scooters in lime, cyan and white heaped against a
chain-link fence panel on a cracked sidewalk slab, with zip ties, stickers, glowing LED strips, green low-battery lights, an
orphaned helmet and a stray traffic cone balanced on top) and the ground-target spell HC_Target_ScooterGraveyard that spawns
it and gives the caster a short lightning-and-speed status. Granted through the Beachborn level-5 racial spell list (wired by
generate_mod.py), so it costs an action but no Junk.

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were produced by
Claude, see assets/models/HC_ScooterGraveyard/ (build_scooters_model.py, scooters_paint.py, render_scooters.py; Blender is
used only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket skeleton, exactly the
pipeline of the shopping cart (hc_cart.py), the blue tarp (hc_tarp.py) and the barricade (hc_barricade.py): visual resource
(Texture/Material/VisualBank) -> root template -> Object stat -> GROUND:Spawn(template).

Vanilla evidence (temp_race/Public): donor Projectile_GEB_Perform_TossCoin (Spell_Projectile.txt, the same donor as the
barricade and HC_Target_AbandonedCart), GROUND:Spawn(template) is its own SpellProperties term, ApplyStatus(SELF,...) appears
in Projectile spells (AI_HELPER_EXTRAATTACK), the BOOST pair "CharacterWeaponDamage(<dice>, <type>);ActionResource(Movement,n,0)"
is the GOB_DROWCOM_BUFF status and the Round 7 Trenbolone status, and CharacterWeaponDamage(1d8,Lightning) exists verbatim in
Passive.txt. The exact form CharacterWeaponDamage(1d4,Lightning) does NOT exist in vanilla (only 1d8 and 2d4 Lightning), so the
status uses the verbatim 1d8 form; the Cooldown is "OncePerRest" (the long-rest token in vanilla). Icons: Spell_Conjuration_AcidSplash
and Spell_Abjuration_MageArmor are existing vanilla names already used by the barricade.
File-level verified only. UNVERIFIED in game: that the extra ApplyStatus(SELF) functor still runs next to GROUND:Spawn on this
Projectile donor, spawn facing (+Z front vs. caster), collision bounds, scale, and the texture look (LEDs, low-battery lights
and the pavement light pools are only bright colours in the base texture; there is no emissive map).
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_ScooterGraveyard"
ASSET_FILES = ("HC_ScooterGraveyard.GR2", "HC_ScooterGraveyard_BM.DDS", "HC_ScooterGraveyard_NM.DDS", "HC_ScooterGraveyard_PM.DDS")

# Model bounds in metres (work/scooters/out/scooters_bounds.json): ground origin, +Z front (away from the fence).
BMIN = (-1.2, 0.0, -0.8)
BMAX = (1.21, 1.311, 0.8)
TRIANGLES = 3296
OBJECT_STAT = "HC_OBJ_ScooterGraveyard"
TEMPLATE_KEY = "HC_ScooterGraveyard_RootTemplate"
SPELL = "HC_Target_ScooterGraveyard"
STATUS = "HC_SCOOTER_CHARGED"
STATUS_BOOSTS = "CharacterWeaponDamage(1d8,Lightning);ActionResource(Movement,3,0)"
SPELL_TITLE = "Dockless Scooter Graveyard (Please Do Not Block the Sidewalk)"
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
					<attribute id="Name" type="LSString" value="HC_ScooterGraveyard_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_ScooterGraveyard_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_ScooterGraveyard_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_ScooterGraveyard.{mesh}.{i}" />
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
					<attribute id="Name" type="LSString" value="HC_ScooterGraveyard_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_ScooterGraveyard" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_ScooterGraveyard.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_ScooterGraveyard.{FIRE_BASKET_SKELETON}.0" />
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


def generate_scooters(public_dir, add_loca, get_guid):
    """Write the scooter-graveyard assets, resources, root template, Object stat, status and spell. Returns the spell grants."""
    from hc_icon_keys import icon_for_spell
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_ScooterGraveyard"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_ScooterGraveyard/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_ScooterGraveyard" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_ScooterGraveyard).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing scooter asset {source}; rebuild it with assets/models/HC_ScooterGraveyard/build_scooters_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_ScooterGraveyard_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the cart and tarp.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Dockless Scooter Graveyard"
    item_desc = ("Six rental scooters in lime, cyan and white, heaped against a fence and held together by zip ties, "
                 "stickers and spite. One is upside-down with its wheel in the air, one has a kickstand bent into a question "
                 "mark, and every display still says it has range. The painted parking corral is eight steps away and "
                 "nobody has ever used it.")
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
    # Collision: the heap itself against the fence (the slab edge, helmet and chunks stay outside the inner bound).
    inner = ((-1.1, 0.0, -0.7), (1.1, 0.9, 0.45))
    fmt = lambda v: " ".join(f"{x:g}" for x in v)
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, inner, 0.35)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        for attr, kind, value in (("Height", "float", f"{hi[1]:g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_ScooterGraveyard.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart and HC_OBJ_BlueTarp).
    (stats / "HC_Object_ScooterGraveyard.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "40"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    # 5. Status on the caster: +1d8 Lightning weapon damage and +3 m movement for 3 turns (BOOST pair as GOB_DROWCOM_BUFF).
    status_title = add_loca(STATUS + "_Name", "Static Charge From the Pile")
    status_desc = add_loca(STATUS + "_Description",
                           "Weapon attacks deal an extra 1d8 Lightning damage and you move 3 m faster. "
                           "Smells like ozone and rented freedom.")
    (stats / "HC_Status_ScooterGraveyard.txt").write_text(f'''new entry "{STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "StackId" "{STATUS}"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Icon" "{icon_for_spell(SPELL, STATUS_ICON_FALLBACK)}"
data "Boosts" "{STATUS_BOOSTS}"
data "DisplayName" "{status_title};1"
data "Description" "{status_desc};1"
''', encoding="utf-8")

    # 6. Spell: single-point ground target, donor Toss a Coin (a projectile that GROUND:Spawns one item), as the cart and barricade.
    spell_title = add_loca(SPELL + "_Name", SPELL_TITLE)
    spell_desc = add_loca(SPELL + "_Description",
                          "Dump a heap of abandoned rental scooters on the ground within 9 m, wedged against a chain-link fence. "
                          "Costs an action, once per long rest, and no Junk. "
                          "For 3 turns you also gain Static Charge From the Pile: your weapon attacks deal an extra 1d8 Lightning damage "
                          "and you move 3 m faster. "
                          "The batteries are all still live, every display says low battery, and nobody has ever found the last scooter's owner.")
    (stats / "HC_Spells_ScooterGraveyard.txt").write_text(f'''new entry "{SPELL}"
type "SpellData"
using "{DONOR}"
data "SpellProperties" "GROUND:Spawn({template_id});ApplyStatus(SELF,{STATUS},100,3)"
data "TargetRadius" "9"
data "Icon" "{icon_for_spell(SPELL, SPELL_ICON_FALLBACK)}"
data "DisplayName" "{spell_title};1"
data "Description" "{spell_desc};1"
data "UseCosts" "ActionPoint:1"
data "Cooldown" "OncePerRest"
''', encoding="utf-8")
    # Racial spell: no HC_Junk cost. generate_mod.py puts it on the Beachborn level-5 spell list (existing_list_spells).
    return {"base": {}, "subclasses": {}, "existing_list_spells": {"Beachborn_L5": SPELL}}
