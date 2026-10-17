"""Pop-Up Encampment Tent: a custom 3D prop (two-person dome tent in mismatched teal and hot orange, duct tape, blue tarp
corner, rain-fly stripe, string lights, neon guy lines, milk-crate side table with a camp stove, a sun-and-heart sign and
a pigeon in sunglasses) and the self-centred shout HC_Shout_PopUpTentEncampment that spawns it, with 8 temporary hit points.

AI-generated asset: the mesh (procedural Python geometry) and the textures (procedural PIL/numpy painting) were
produced by Claude, see assets/models/HC_PopUpTent/ (build_tent_model.py, tent_paint.py, render_tent.py; Blender is used
only for previews). The GR2 was converted with LSLib Divine and conformed to the vanilla fire-basket skeleton, exactly the
pipeline of the shopping cart (hc_cart.py), the blue tarp (hc_tarp.py) and the barricade (hc_barricade.py): visual resource
(Texture/Material/VisualBank) -> root template -> Object stat -> GROUND:Spawn(template).

Vanilla evidence (temp_race/Public): donor Shout_SecondWind (Spell_Shout.txt, the same donor as HC_Shout_BlueTarpLeanTo in
hc_overpass.py); GROUND:Spawn(template) is its own SpellProperties term (cart, tarp, barricade); the status is a BOOST with
Boosts "TemporaryHP(n)" exactly as ARMOR_OF_AGATHYS_2 and POTION_OF_HEROISM_TEMPHP in Status_BOOST.txt. The Cooldown is
"OncePerRest" (vanilla has 23 uses, no "OncePerLongRest" token exists, "OncePerRest" is the long-rest cooldown).
Icon Spell_Abjuration_MageArmor is an existing vanilla name already used by the tarp shout and the barricade status.
File-level verified only. UNVERIFIED in game: that GROUND:Spawn resolves once at the caster's feet for a self Shout (the
same open question as the tarp), spawn facing (+Z front vs. caster), collision bounds, scale, the 1024 px base texture
and the look (the string-light bulbs are bright yellow in the base colour with painted glows; there is no emissive map).
"""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ASSET_SRC = Path(__file__).resolve().parent / "assets" / "models" / "HC_PopUpTent"
ASSET_FILES = ("HC_PopUpTent.GR2", "HC_PopUpTent_BM.DDS", "HC_PopUpTent_NM.DDS", "HC_PopUpTent_PM.DDS")

# Model bounds in metres (work/tent/out/tent_bounds.json): ground origin, +Z front (door side).
BMIN = (-1.22, 0.0, -1.063)
BMAX = (1.242, 1.602, 1.15)
TRIANGLES = 2999
OBJECT_STAT = "HC_OBJ_PopUpTent"
TEMPLATE_KEY = "HC_PopUpTent_RootTemplate"
SPELL = "HC_Shout_PopUpTentEncampment"
STATUS = "HC_TENT_CITY_COZY"
FIRE_BASKET_SKELETON = "Dummy_LTS_GEN_Fire_Basket_A"
FIRE_BASKET_MESHES = ("LTS_GEN_Fire_Basket_A_Mesh", "LTS_GEN_Fire_Basket_A_Mesh_LOD1", "LTS_GEN_Fire_Basket_A_Mesh_LOD2")
# Parent template of Ducq's grill and truck props (vanilla), used for a static world item (same as cart, tarp, barricade).
PARENT_TEMPLATE = "c9e45e5a-f089-480b-ab3a-7f5f76dccc3b"
DONOR = "Shout_SecondWind"
SPELL_ICON_FALLBACK = "Spell_Abjuration_MageArmor"
STATUS_ICON_FALLBACK = "Spell_Abjuration_MageArmor"
SPELL_TITLE = "Pop-Up Tent City Encampment (Permit Pending)"


def _visual_resource(ids, resources_path):
    """Copy of the cart's TextureBank/MaterialBank/VisualBank attribute pattern, tab indented."""
    def tex(name, key, srgb, size):
        return f'''				<node id="Resource">
					<attribute id="Depth" type="int32" value="1" />
					<attribute id="Height" type="int32" value="{size}" />
					<attribute id="ID" type="FixedString" value="{ids[key]}" />
					<attribute id="Name" type="LSString" value="HC_PopUpTent_{name}" />
					<attribute id="SRGB" type="bool" value="{srgb}" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_PopUpTent_{name}.DDS" />
					<attribute id="Streaming" type="bool" value="True" />
					<attribute id="Template" type="FixedString" value="HC_PopUpTent_{name}" />
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
							<attribute id="ObjectID" type="FixedString" value="HC_PopUpTent.{mesh}.{i}" />
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
					<attribute id="Name" type="LSString" value="HC_PopUpTent_Mat" />
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
					<attribute id="Name" type="LSString" value="HC_PopUpTent" />
					<attribute id="NeedsSkeletonRemap" type="bool" value="False" />
					<attribute id="Radius" type="float" value="{radius:.5f}" />
					<attribute id="SkeletonResource" type="FixedString" value="" />
					<attribute id="SkeletonSlot" type="FixedString" value="" />
					<attribute id="Slot" type="FixedString" value="Unassigned" />
					<attribute id="SoftbodyResourceID" type="FixedString" value="" />
					<attribute id="SourceFile" type="LSString" value="{resources_path}/HC_PopUpTent.GR2" />
					<attribute id="SupportsVertexColorMask" type="bool" value="False" />
					<attribute id="Template" type="FixedString" value="{resources_path}/HC_PopUpTent.{FIRE_BASKET_SKELETON}.0" />
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


def generate_tent(public_dir, add_loca, get_guid):
    """Write the tent assets, resources, root template, Object stat, status and spell. Returns the spell grants."""
    from hc_icon_keys import icon_for_spell
    public = Path(public_dir)
    mod = public.name
    src_root = public.parents[1]
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    content = public / "Content" / "Assets" / "Props" / "[PAK]_HC_PopUpTent"
    resources_rel = f"Generated/Public/{mod}/Assets/Props/HC_PopUpTent/Resources"
    resources_dir = src_root / "Generated" / "Public" / mod / "Assets" / "Props" / "HC_PopUpTent" / "Resources"
    for d in (stats, roots, content, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Binary assets (tracked copies live in assets/models/HC_PopUpTent).
    for name in ASSET_FILES:
        source = ASSET_SRC / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing tent asset {source}; rebuild it with assets/models/HC_PopUpTent/build_tent_model.py")
        shutil.copy2(source, resources_dir / name)

    # 2. Visual resource: fresh deterministic GUIDs.
    ids = {k: get_guid(f"HC_PopUpTent_{k}") for k in ("bm", "nm", "pm", "mat", "visual")}
    (content / "_merged.lsf.lsx").write_text(_visual_resource(ids, resources_rel), encoding="utf-8", newline="\n")

    # 3. Root template (static prop: no physics, cannot be moved or picked up). Own file, as for the cart, tarp and barricade.
    template_id = get_guid(TEMPLATE_KEY)
    title = "Pop-Up Encampment Tent"
    item_desc = ("A two-person dome in teal on one side and hot orange on the other, because the fabric arrived in three "
                 "separate donations. Held together by duct tape, string lights and optimism, with a blue tarp where the "
                 "roof gave up. The permit has been pending longer than the tent has existed, and the pigeon on the sign "
                 "is under witness protection.")
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
    # Collision: the dome footprint and body (guy lines, pegs, sign and crate stay outside the inner bound).
    inner = ((-0.88, 0.0, -0.84), (0.88, 1.25, 0.84))
    fmt = lambda v: " ".join(f"{x:g}" for x in v)
    for btype, (lo, hi), radius in ((1, (BMIN, BMAX), 0.5), (2, (BMIN, BMAX), 0.5), (0, inner, 0.35)):
        b = ET.SubElement(bchildren, "node", id="Bound")
        for attr, kind, value in (("Height", "float", f"{height:g}"), ("Max", "fvec3", fmt(hi)), ("Min", "fvec3", fmt(lo)),
                                  ("Radius", "float", f"{radius:g}"), ("Shape", "uint8", "1"), ("Type", "uint8", str(btype))):
            ET.SubElement(b, "attribute", id=attr, type=kind, value=value)
    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_PopUpTent.lsf.lsx", encoding="utf-8", xml_declaration=True)

    # 4. Object stat (static prop, same fields as HC_OBJ_ShoppingCart, HC_OBJ_BlueTarp and HC_OBJ_Barricade).
    (stats / "HC_Object_PopUpTent.txt").write_text(f'''new entry "{OBJECT_STAT}"
type "Object"
using "_BaseItem"
data "RootTemplate" "{template_id}"
data "Weight" "60"
data "GameSize" "Large"
data "Vitality" "-1"
''', encoding="utf-8")

    # 5. Status on the caster: 8 temporary hit points for 3 turns (duration comes from ApplyStatus in the spell).
    status_title = add_loca(STATUS + "_Name", "Illegally Cozy")
    status_desc = add_loca(STATUS + "_Description",
                           "Gain 8 temporary hit points. Cozy. Illegal, but cozy.")
    (stats / "HC_Status_PopUpTent.txt").write_text(f'''new entry "{STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "StackId" "{STATUS}"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Icon" "{STATUS_ICON_FALLBACK}"
data "Boosts" "TemporaryHP(8)"
data "DisplayName" "{status_title};1"
data "Description" "{status_desc};1"
''', encoding="utf-8")

    # 6. Spell: self-centred shout (donor Second Wind, like the Blue Tarp Lean-To). Every inherited tooltip fact is blanked.
    spell_title = add_loca(SPELL + "_Name", SPELL_TITLE)
    spell_desc = add_loca(SPELL + "_Description",
                          "Pitch a two-person dome tent at your feet in one smooth motion. "
                          "Costs an action and 1 Junk; once per long rest. "
                          "You gain 8 temporary hit points for 3 turns while you zip yourself in, and the tent is left standing where you stood. "
                          "It comes with duct tape, string lights, a milk-crate side table and a pigeon in sunglasses guarding the sign. "
                          "The permit is still pending, and has been since before tents were invented.")
    fields = dict(Level='0', Cooldown='OncePerRest', DescriptionParams='', ExtraDescription='', MemoryCost='0',
                  RechargeValues='', TooltipUpcastDescription='', TooltipUpcastDescriptionParams='',
                  TooltipDamageList='', TooltipStatusApply=f'ApplyStatus({STATUS},100,3)', TooltipAttackSave='',
                  TooltipPermanentWarnings='', TooltipOnSave='', SpellRoll='', SpellSuccess='', SpellFail='',
                  CastTextEvent='Cast',
                  UseCosts='ActionPoint:1;HC_Junk:1',
                  Icon=icon_for_spell(SPELL, SPELL_ICON_FALLBACK),
                  TargetConditions='Self()',
                  SpellProperties=f'ApplyStatus({STATUS},100,3);GROUND:Spawn({template_id})',
                  DisplayName=f'{spell_title};1', Description=f'{spell_desc};1')
    lines = [f'new entry "{SPELL}"', 'type "SpellData"', f'using "{DONOR}"']
    for k, v in fields.items():
        if '"' in v or '\n' in v:
            raise ValueError(f'Unsafe field {SPELL}.{k}')
        lines.append(f'data "{k}" "{v}"')
    (stats / "HC_Spells_PopUpTent.txt").write_text('\n'.join(lines) + '\n', encoding="utf-8")
    return {"base": {7: [SPELL]}, "subclasses": {}}   # base class level 7 has a progression node (no level-3 node)
