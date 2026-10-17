"""Municipal Hostile Architecture Bench: a custom 3D prop (heavy dark-green cast-iron bus-stop bench on a concrete pad, five
oversized chrome armrest dividers across the seat, jagged steel pyramid studs, a neon-yellow municipal asset-tag barcode plate on
the backrest, a cheerful hot-pink sponsor ad panel with a 'no lying down' pictogram, and one pigeon sitting on it quite happily)
and the ground-target spell HC_Target_HostileArchitectureBench that spawns it, with a 3-turn self status: resistance to Piercing
and Bludgeoning damage and immunity to being knocked Prone.

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were
produced by Claude, see assets/models/HC_Bench/ (build_bench_model.py, bench_paint.py, render_bench.py;
Blender is used only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket
skeleton, exactly the pipeline of the shopping cart (hc_cart.py), the blue tarp (hc_tarp.py), the barricade (hc_barricade.py),
the tent (hc_tent.py) and the porta-potty (hc_portapotty.py): visual resource (Texture/Material/VisualBank) -> root template ->
Object stat -> GROUND:Spawn(template).

Vanilla evidence (temp_race/Public): donor Projectile_GEB_Perform_TossCoin (Shared/Stats/Generated/Data/Spell_Projectile.txt:5335,
the same donor as HC_Target_AbandonedCart, the barricade and the porta-potty spells; its own SpellProperties is
GROUND:Spawn(<guid>), line 5338), and ApplyStatus(SELF,...) appears in Projectile spells (Spell_Projectile.txt:4 and :161).
The status Boosts use three vanilla tokens verbatim: Resistance(Piercing,Resistant) and Resistance(Bludgeoning,Resistant)
(Gustav/Stats/Generated/Data/Status_BOOST.txt:96, FOR_OWLBEAR_ENRAGE_HARDCORE, and the Piercing/Bludgeoning/Slashing set in
Status_INCAPACITATED.txt) and StatusImmunity(SG_Prone) (GustavDev/Stats/Generated/Data/Status_BOOST.txt:10972, MAG_UNMOVABLE:
"Attribute(Grounded);StatusImmunity(SG_Prone)"). There is NO vanilla token for "advantage on saves against being knocked
Prone" (no save-by-status-group boost exists), so the brief's suggestion was replaced by the vanilla StatusImmunity(SG_Prone).
Cooldown "OncePerRest" is the long-rest cooldown (no "OncePerLongRest" token exists in vanilla). Icons Spell_Transmutation_SpikeGrowth
(spell) and Spell_Abjuration_Stoneskin (status) are existing vanilla icon names.
File-level verified only. UNVERIFIED in game: that the extra ApplyStatus(SELF) functor still runs next to GROUND:Spawn on
this Projectile donor, spawn facing (+Z front vs. caster), collision bounds, scale, the texture look (no emissive map, the
chrome is only a painted reflection band, so it may look chalky under dungeon lighting) and whether StatusImmunity(SG_Prone)
really stops every knock-prone effect (e.g. Shove) when applied as a plain BOOST status.
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_Bench"
ASSET_FILES = ("HC_Bench.GR2", "HC_Bench_BM.DDS", "HC_Bench_NM.DDS", "HC_Bench_PM.DDS")

# Model bounds in metres (work/bench/out/bench_bounds.json): ground origin, +Z front (the seat side).
BMIN = (-1.6, 0.0, -0.62)
BMAX = (1.6, 1.256, 0.62)
TRIANGLES = 3112
OBJECT_STAT = "HC_OBJ_HostileBench"
TEMPLATE_KEY = "HC_Bench_RootTemplate"
SPELL = "HC_Target_HostileArchitectureBench"
STATUS = "HC_CERTIFIED_BENCH_SLEEPER"
SPELL_TITLE = "Municipal Hostile Architecture Installation"
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Parent template of Ducq's grill and truck props (vanilla), used for a static world item (same as cart, tarp, barricade, tent, porta-potty).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"
DONOR = "Projectile_GEB_Perform_TossCoin"
SPELL_ICON_FALLBACK = "Spell_Transmutation_SpikeGrowth"
STATUS_ICON_FALLBACK = "Spell_Abjuration_Stoneskin"
# Collision: the bench itself (frames, seat, hoops and backrest); the concrete pad, ad post and pigeon stay outside the inner bound.
INNER_MIN = (-1.34, 0.0, -0.46)
INNER_MAX = (0.74, 1.0, 0.30)


def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_Bench_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_Bench_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_Bench_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_Bench.{mesh}.{i}" />
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
					<attribute id="Name" type="LSString" value="HC_Bench_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_Bench" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_Bench.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_Bench.{FIRE_BASKET_SKELETON}.0" />
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


def generate_bench(public_dir, add_loca, get_guid):
    """Write the bench assets, resources, root template, Object stat, status and spell. Returns the spell grants."""
    from hc_icon_keys import icon_for_spell
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_Bench"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_Bench/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_Bench" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_Bench).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing bench asset {source}; rebuild it with assets/models/HC_Bench/build_bench_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_Bench_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the other props.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Municipal Hostile Architecture Bench"
    item_desc = ("Heavy dark-green cast iron on a concrete pad, with five chrome dividers looping across the seat and steel studs "
                 "where the seat should be. A neon-yellow asset tag with a barcode is bolted to the backrest. A cheerful pink "
                 "sign nearby shows a smiley face and a person lying on a bench inside a red crossed circle. A pigeon is "
                 "sitting on the backrest, and it is perfectly comfortable.")
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
    fmt = lambda v: " ".join(f"{x:g}" for x in v)
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, (INNER_MIN, INNER_MAX), 0.35)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        for attr, kind, value in (("Height", "float", f"{hi[1]:g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_Bench.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart, HC_OBJ_BlueTarp, HC_OBJ_Barricade, HC_OBJ_PopUpTent, HC_OBJ_PortaPotty).
    (stats / "HC_Object_Bench.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "400"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    # 5. Status on the caster: Piercing and Bludgeoning resistance plus Prone immunity (duration comes from ApplyStatus in the spell).
    status_title = add_loca(STATUS + "_Name", "Certified Bench Sleeper")
    status_desc = add_loca(STATUS + "_Description",
                           "Resistance to Piercing and Bludgeoning damage. Immune to being knocked Prone. "
                           "You know exactly how to sleep on a bench designed so that you cannot.")
    (stats / "HC_Status_Bench.txt").write_text(f'''new entry "{STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "StackId" "{STATUS}"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Icon" "{icon_for_spell(SPELL, STATUS_ICON_FALLBACK)}"
data "Boosts" "Resistance(Piercing,Resistant);Resistance(Bludgeoning,Resistant);StatusImmunity(SG_Prone)"
data "DisplayName" "{status_title};1"
data "Description" "{status_desc};1"
''', encoding="utf-8")

    # 6. Spell: single-point ground target, donor Toss a Coin (a projectile that GROUND:Spawns one item), as the other props.
    spell_title = add_loca(SPELL + "_Name", SPELL_TITLE)
    spell_desc = add_loca(SPELL + "_Description",
                          "Bolt a city bus-stop bench to the ground at a point within 9 m: dark-green cast iron, five chrome armrest "
                          "dividers, steel studs on the seat and a neon asset-tag barcode on the back. "
                          "Costs an action and no Junk; once per long rest. "
                          "You gain Certified Bench Sleeper for 3 turns: resistance to Piercing and Bludgeoning damage and immunity to being knocked Prone. "
                          "A committee spent real money making it impossible to lie down on, and you are about to nap on it anyway.")
    (stats / "HC_Spells_Bench.txt").write_text(f'''new entry "{SPELL}"
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
    return {"base": {10: [SPELL]}, "subclasses": {}, "existing_list_spells": {}}
