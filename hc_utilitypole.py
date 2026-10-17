"""Sparking Utility Pole: a custom 3D prop (weathered dark-brown wooden pole leaning about 15 degrees, a crossarm with
blue-green glass pin insulators, a bracket with three grey transformer cans (the middle one cooked), snapped copper cables
dangling and one trailing across the ground, a red HIGH VOLTAGE placard (bolt symbol, no lettering), stapled flyers, a nest of
dead phone wires with a pair of sneakers and a junction box, a shredded Mylar birthday smiley snagged on the crossarm, and
painted (not emissive) cyan-and-gold spark arcs at the cable tips) and the ground-target spell HC_Target_SparkingUtilityPole
that spawns it, with a 3-turn self status: resistance to lightning damage, +1 to attack rolls and +1 to spell save DC.
No real utility logo or trademark is used: the fictional operator is "Pacific Grid & Excuse" (named only in text).

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were
produced by Claude, see assets/models/HC_UtilityPole/ (build_utilitypole_model.py, utilitypole_paint.py, render_utilitypole.py;
Blender is used only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket
skeleton, exactly the pipeline of the shopping cart (hc_cart.py), the blue tarp (hc_tarp.py), the barricade (hc_barricade.py),
the tent (hc_tent.py) and the porta-potty (hc_portapotty.py): visual resource (Texture/Material/VisualBank) -> root template ->
Object stat -> GROUND:Spawn(template).

Vanilla evidence (temp_race/Public): donor Projectile_GEB_Perform_TossCoin (Spell_Projectile.txt, the same donor as
HC_Target_AbandonedCart and the other prop spells), GROUND:Spawn(template) is its own SpellProperties term and
ApplyStatus(SELF,...) appears in Projectile spells. The status Boosts use three vanilla tokens verbatim:
Resistance(Lightning,Resistant) (GustavDev Status_BOOST.txt:4079, a status that also grants Resistance(Fire/Cold,Resistant);
also the downed-state boosts in Shared Status_INCAPACITATED.txt:131), RollBonus(Attack,1) (GustavDev Status_BOOST.txt:301 and
Gustav Status_BOOST.txt:648) and SpellSaveDC(1) (GustavDev Passive.txt:2184, 2357 and Armor.txt:1948; the status form
SpellSaveDC(2) is Shared Status_BOOST.txt:6250). Cooldown "OncePerRest" is the long-rest cooldown (no "OncePerLongRest" token
exists in vanilla). Icons Spell_Conjuration_CallLightning (Spell_Target.txt) and Spell_Abjuration_ProtectionFromEnergy_Lightning
(Status_BOOST.txt) are existing vanilla icon names. The HC_Junk cost mirrors the other base-class prop spells (barricade and tent:
1 Junk at levels 9 and 7); the heavy once-per-rest base spells cost 2 (hc_round8.py NIMBY Public Comment Period, hc_capstone.py
Biohazard Condemn), so this level-11 spell costs ActionPoint:1;HC_Junk:2.
File-level verified only. UNVERIFIED in game: that the extra ApplyStatus(SELF) functor still runs next to GROUND:Spawn on
this Projectile donor, spawn facing (+Z front vs. caster), the 5 m tall model's scale and the camera feel, collision bounds
(only the lower 1.6 m of the pole blocks), the texture look (no emissive map: the sparks are bold painted cyan and gold), and
whether the stacked boosts apply as written. The pole needs a tall-prop check (does the top clip the camera or fade?).
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_UtilityPole"
ASSET_FILES = ("HC_UtilityPole.GR2", "HC_UtilityPole_BM.DDS", "HC_UtilityPole_NM.DDS", "HC_UtilityPole_PM.DDS")

# Model bounds in metres (work/utilitypole/out/utilitypole_bounds.json): ground origin, +Z front (placard side), pole leans to +X.
BMIN = (-0.743, 0.0, -0.55)
BMAX = (2.404, 5.086, 1.84)
TRIANGLES = 3255
OBJECT_STAT = "HC_OBJ_UtilityPole"
TEMPLATE_KEY = "HC_UtilityPole_RootTemplate"
SPELL = "HC_Target_SparkingUtilityPole"
STATUS = "HC_GRID_SAFETY_FEE"
SPELL_TITLE = "Deferred Maintenance Pole Drop"
BASE_LEVEL = 11
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Parent template of Ducq's grill and truck props (vanilla), used for a static world item (same as cart, tarp, barricade, tent).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"
DONOR = "Projectile_GEB_Perform_TossCoin"
SPELL_ICON_FALLBACK = "Spell_Conjuration_CallLightning"
STATUS_ICON_FALLBACK = "Spell_Abjuration_ProtectionFromEnergy_Lightning"
BOOSTS = "Resistance(Lightning,Resistant);RollBonus(Attack,1);SpellSaveDC(1)"
# Collision: the lower 1.6 m of the leaning pole only (the upper pole, arms, cables, sparks and the ground cable stay outside it).
INNER_MIN = (-0.25, 0.0, -0.22)
INNER_MAX = (0.62, 1.6, 0.3)


def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_UtilityPole_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_UtilityPole_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_UtilityPole_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_UtilityPole.{mesh}.{i}" />
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
					<attribute id="Name" type="LSString" value="HC_UtilityPole_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_UtilityPole" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_UtilityPole.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_UtilityPole.{FIRE_BASKET_SKELETON}.0" />
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


def generate_utilitypole(public_dir, add_loca, get_guid):
    """Write the utility pole assets, resources, root template, Object stat, status and spell. Returns the spell grants."""
    from hc_icon_keys import icon_for_spell
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_UtilityPole"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_UtilityPole/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_UtilityPole" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_UtilityPole).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing utility pole asset {source}; rebuild it with work/utilitypole/run.sh")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_UtilityPole_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the other props.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Sparking Utility Pole"
    item_desc = ("Leaning about fifteen degrees and held up mostly by habit. Three grey transformer cans hang off the bracket "
                 "and the middle one is visibly cooked. Copper cables dangle off glass insulators and one trails across the "
                 "ground, spitting cyan and gold sparks. A red high-voltage placard sits above a nest of dead phone wires, "
                 "a pair of sneakers and several flyers, and a shredded birthday balloon is snagged on the crossarm. "
                 "The inspection tag says 1998 and the asset belongs to Pacific Grid & Excuse.")
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
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, (INNER_MIN, INNER_MAX), 0.3)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        for attr, kind, value in (("Height", "float", f"{hi[1]:g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_UtilityPole.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart, HC_OBJ_BlueTarp, HC_OBJ_Barricade and HC_OBJ_PopUpTent).
    (stats / "HC_Object_UtilityPole.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "400"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    # 5. Status on the caster: lightning resistance, +1 attack rolls, +1 spell save DC (duration comes from ApplyStatus in the spell).
    status_title = add_loca(STATUS + "_Name", "Grid Safety Fee")
    status_desc = add_loca(STATUS + "_Description",
                           "Resistance to lightning damage. +1 to attack rolls and +1 to your spell save DC. "
                           "Pacific Grid & Excuse thanks you for your patience, and for the surcharge.")
    (stats / "HC_Status_UtilityPole.txt").write_text(f'''new entry "{STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "StackId" "{STATUS}"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Icon" "{icon_for_spell(SPELL, STATUS_ICON_FALLBACK)}"
data "Boosts" "{BOOSTS}"
data "DisplayName" "{status_title};1"
data "Description" "{status_desc};1"
''', encoding="utf-8")

    # 6. Spell: single-point ground target, donor Toss a Coin (a projectile that GROUND:Spawns one item), as the other prop spells.
    spell_title = add_loca(SPELL + "_Name", SPELL_TITLE)
    spell_desc = add_loca(SPELL + "_Description",
                          "Drop a leaning, sparking utility pole onto a point within 9 m. "
                          "Costs an action and 2 Junk; once per long rest. "
                          "You gain Grid Safety Fee for 3 turns: resistance to lightning damage, +1 to attack rolls and +1 to your spell save DC. "
                          "The cables are snapped, one transformer is scorched, and a birthday balloon stays snagged on the crossarm through all of it. "
                          "Pacific Grid & Excuse calls the sparks decorative and has been wrong before.")
    (stats / "HC_Spells_UtilityPole.txt").write_text(f'''new entry "{SPELL}"
type "SpellData"
using "{DONOR}"
data "SpellProperties" "GROUND:Spawn({template_id});ApplyStatus(SELF,{STATUS},100,3)"
data "TargetRadius" "9"
data "Icon" "{icon_for_spell(SPELL, SPELL_ICON_FALLBACK)}"
data "DisplayName" "{spell_title};1"
data "Description" "{spell_desc};1"
data "UseCosts" "ActionPoint:1;HC_Junk:2"
data "Cooldown" "OncePerRest"
''', encoding="utf-8")
    return {"base": {BASE_LEVEL: [SPELL]}, "subclasses": {}, "existing_list_spells": {}}
