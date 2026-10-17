"""Evicted Studio Spin Bike: a custom 3D prop (angular boutique stationary bike in matte millennial pink with a polished chrome
flywheel guard, handlebars and seat post, a tilted tablet console showing a neon "RIDE OR DIE 98%" screen of the invented brand
SoulCyclone, a water bottle in a cage, clip-in cycling shoes dangling by their laces from a pedal, a sweaty towel over the
handlebar, a healing crystal on a grip, a sweat puddle, a violet yoga mat and a laminated EVICTION NOTICE taped to the saddle)
and the ground-target spell HC_Target_EvictedSpinBike that spawns it, with a 3-turn self status: advantage on Athletics and
Intimidation checks and on Constitution saving throws ("Motivational Energy").

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were
produced by Claude, see assets/models/HC_SpinBike/ (build_spinbike_model.py, spinbike_paint.py, render_spinbike.py;
Blender is used only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket
skeleton, exactly the pipeline of the shopping cart (hc_cart.py), the blue tarp (hc_tarp.py), the barricade (hc_barricade.py),
the tent (hc_tent.py) and the porta-potty (hc_portapotty.py): visual resource (Texture/Material/VisualBank) -> root template ->
Object stat -> GROUND:Spawn(template).

Vanilla evidence (temp_race/Public): donor Projectile_GEB_Perform_TossCoin (Shared Spell_Projectile.txt:5335, the same donor as
HC_Target_AbandonedCart, the barricade and the porta-potty); GROUND:Spawn(template) is its own SpellProperties term
(Gustav Spell_Target.txt:751, GustavDev Spell_Projectile.txt:163) and ApplyStatus(SELF,...) appears in Projectile spells
(GustavDev Spell_Projectile.txt:161). The status Boosts use three vanilla tokens: Advantage(Skill,Athletics) (Shared Passive.txt:2691),
Advantage(Skill,Intimidation) (Shared Status_BOOST.txt:4961 as a status Boost, written "Advantage(Skill, Intimidation)" there;
GustavDev Status_BOOST.txt:6094 in the no-space form used here) and Advantage(SavingThrow,Constitution) (GustavDev Passive.txt:515 in
the no-space form used here; Gustav Armor.txt:265 as a lone boost). Cooldown "OncePerRest" is the long-rest cooldown (no
"OncePerLongRest" token exists in vanilla). Costs "ActionPoint:1;HC_Junk:1" mirror the base-class props (tent: action and 1 Junk;
barricade and cart: bonus action and 1 Junk; racial props have no Junk cost). Icons Skill_Fighter_ActionSurge (spell) and
Spell_Enchantment_Heroism (status) are existing vanilla icon names (Shared Spell_Shout.txt:8 / Status_BOOST.txt:1651 and
Spell_Target.txt:2236 / Status_BOOST.txt:3115).
File-level verified only. UNVERIFIED in game: that the extra ApplyStatus(SELF) functor still runs next to GROUND:Spawn on
this Projectile donor, spawn facing (+Z front = saddle side, where the notice and the screen face), collision bounds, scale, the
texture look (no emissive map: the neon screen is only a very bright base colour) and, above all, whether BG3 mirrors the painted
lettering (screen: SOULCYCLONE / 98% / RIDE OR DIE; notice: EVICTION NOTICE / PAY OR QUIT; set MIRROR_TEXT in spinbike_paint.py and
rebuild if it does).
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_SpinBike"
ASSET_FILES = ("HC_SpinBike.GR2", "HC_SpinBike_BM.DDS", "HC_SpinBike_NM.DDS", "HC_SpinBike_PM.DDS")

# Model bounds in metres (work/spinbike/out/spinbike_bounds.json): ground origin, +Z front (saddle / screen side).
BMIN = (-0.45, 0.0, -1.272)
BMAX = (0.45, 1.6725, 0.98)
TRIANGLES = 2968
OBJECT_STAT = "HC_OBJ_SpinBike"
TEMPLATE_KEY = "HC_SpinBike_RootTemplate"
SPELL = "HC_Target_EvictedSpinBike"
STATUS = "HC_SOULCYCLONE_ENERGY"
SPELL_TITLE = "Studio Cycle Eviction Notice"
STATUS_BOOSTS = "Advantage(Skill,Athletics);Advantage(Skill,Intimidation);Advantage(SavingThrow,Constitution)"
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Parent template of Ducq's grill and truck props (vanilla), used for a static world item (same as cart, tarp, barricade, tent).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"
DONOR = "Projectile_GEB_Perform_TossCoin"
SPELL_ICON_FALLBACK = "Skill_Fighter_ActionSurge"
STATUS_ICON_FALLBACK = "Spell_Enchantment_Heroism"
# Collision: the bike body only (mat, towel ends, shoes, puddle and the mat roll stay outside the inner bound).
INNER_MIN = (-0.37, 0.0, -0.74)
INNER_MAX = (0.37, 1.45, 0.68)


def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_SpinBike_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_SpinBike_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_SpinBike_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_SpinBike.{mesh}.{i}" />
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
					<attribute id="Name" type="LSString" value="HC_SpinBike_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_SpinBike" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_SpinBike.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_SpinBike.{FIRE_BASKET_SKELETON}.0" />
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


def generate_spinbike(public_dir, add_loca, get_guid):
    """Write the spin-bike assets, resources, root template, Object stat, status and spell. Returns the spell grants."""
    from hc_icon_keys import icon_for_spell
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_SpinBike"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_SpinBike/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_SpinBike" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_SpinBike).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing spin-bike asset {source}; rebuild it with assets/models/HC_SpinBike/build_spinbike_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_SpinBike_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the cart, tarp, barricade and tent.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Evicted Studio Spin Bike"
    item_desc = ("A matte millennial-pink studio bike dragged onto the curb mid-class. The tablet is still shouting RIDE OR DIE at 98 percent, "
                 "a sweaty towel is over the handlebar, a pair of clip-in shoes dangle from a pedal by their laces and a laminated "
                 "eviction notice is taped to the saddle. The studio is gone. The landlord could not lift the bike, so it is now technically a tenant.")
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
    ET.ElementTree(save).write(roots / "HC_SpinBike.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart, HC_OBJ_BlueTarp, HC_OBJ_Barricade and HC_OBJ_PopUpTent).
    (stats / "HC_Object_SpinBike.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "120"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    # 5. Status on the caster: advantage on Athletics and Intimidation checks and Constitution saving throws (duration from ApplyStatus).
    status_title = add_loca(STATUS + "_Name", "Motivational Energy")
    status_desc = add_loca(STATUS + "_Description",
                           "Advantage on Athletics and Intimidation checks and on Constitution saving throws. "
                           "You are 98 percent endorphins and 2 percent unpaid membership dues.")
    (stats / "HC_Status_SpinBike.txt").write_text(f'''new entry "{STATUS}"
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
                          "Drag a studio spin bike onto the curb at a point within 9 m. "
                          "Costs an action and 1 Junk; once per long rest. "
                          "You gain Motivational Energy for 3 turns: advantage on Athletics and Intimidation checks and on Constitution saving throws. "
                          "The bike arrives pink and chrome, with a tablet reading 98 percent, a sweaty towel, dangling clip-in shoes and an eviction notice taped to the saddle. "
                          "The studio is gone, but the leaderboard lives on and it still ranks you dead last.")
    (stats / "HC_Spells_SpinBike.txt").write_text(f'''new entry "{SPELL}"
type "SpellData"
using "{DONOR}"
data "SpellProperties" "GROUND:Spawn({template_id});ApplyStatus(SELF,{STATUS},100,3)"
data "TargetRadius" "9"
data "Icon" "{icon_for_spell(SPELL, SPELL_ICON_FALLBACK)}"
data "DisplayName" "{spell_title};1"
data "Description" "{spell_desc};1"
data "UseCosts" "ActionPoint:1;HC_Junk:1"
data "Cooldown" "OncePerRest"
''', encoding="utf-8")
    return {"base": {6: [SPELL]}, "subclasses": {}, "existing_list_spells": {}}   # base class level 6 (has a progression node)
