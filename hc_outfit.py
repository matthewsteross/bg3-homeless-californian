"""Optional scavenged wardrobe, using inherited vanilla equipment visuals.

No vanilla meshes or textures are copied. These are intentionally a destroyed
robe and an ordinary cloak, not a newly modelled safety vest or blue tarp.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


def generate_outfit(public_dir, add_loca, get_guid):
    """Write HC-only stats/templates and return the class wardrobe spell name."""
    public = Path(public_dir)
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    stats.mkdir(parents=True, exist_ok=True)
    roots.mkdir(parents=True, exist_ok=True)

    items = (
        ("HC_ARM_MunicipallyApprovedLayers", "ARM_Robe_Destroyed",
         "14c13bc9-ab35-4cab-a220-23a61cd43845",
         "Item_ARM_Robe_Destroyed_Crash", "Municipally Approved Layers",
         "Several layers of disputed ownership. The holes provide essential ventilation."),
        ("HC_ARM_LoadBearingTarp", "ARM_Cloak",
         "a1978b4d-3d93-49ec-9a8b-d19171ed35d5",
         "Generated_ARM_Cloak", "Load-Bearing Tarp",
         "A cloak promoted to roof, blanket, and legal address. Structurally sound until asked."),
    )
    save = ET.Element("save")
    ET.SubElement(save, "version", major="4", minor="0", revision="9", build="0")
    region = ET.SubElement(save, "region", id="Templates")
    templates = ET.SubElement(region, "node", id="Templates")
    children = ET.SubElement(templates, "children")
    armor_blocks = []
    summoned = []
    for name, base_stat, parent, icon, title, description in items:
        template_id = get_guid(name + "_RootTemplate")
        title_handle = add_loca(name + "_Name", title)
        description_handle = add_loca(name + "_Description", description)
        obj = ET.SubElement(children, "node", id="GameObjects")
        for attr, kind, value in (
            ("MapKey", "FixedString", template_id),
            ("Name", "LSString", name),
            ("ParentTemplateId", "FixedString", parent),
            ("Stats", "FixedString", name),
            ("Type", "FixedString", "item"),
            ("Icon", "FixedString", icon),
        ):
            ET.SubElement(obj, "attribute", id=attr, type=kind, value=value)
        for attr, handle in (("DisplayName", title_handle), ("Description", description_handle)):
            ET.SubElement(obj, "attribute", id=attr, type="TranslatedString", handle=handle, version="1")
        # Inheriting the root preserves vanilla body/race visual support. No
        # Equipment child is supplied, since an empty one could erase mappings.
        armor_blocks.append(f'''new entry "{name}"
type "Armor"
using "{base_stat}"
data "RootTemplate" "{template_id}"
data "Rarity" "Common"
data "ValueOverride" "0"
''')
        # Goodberry uses this exact persistent, non-equipped summon pattern.
        summoned.append(f"SummonInInventory({template_id},-1,1,false,false,false)")

    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_Wardrobe.lsf.lsx", encoding="utf-8", xml_declaration=True)
    (stats / "HC_Armor_Wardrobe.txt").write_text("\n".join(armor_blocks), encoding="utf-8")

    from hc_icon_keys import icon_for_spell
    spell = "HC_Shout_ClaimUnclaimedWardrobe"
    wardrobe_icon = icon_for_spell(spell, 'Spell_Transmutation_Goodberry')
    title = add_loca(spell + "_Name", "Unclaimed Wardrobe")
    description = add_loca(spell + "_Description",
                           "Find a set of Municipally Approved Layers and a Load-Bearing Tarp. "
                           "Added to your inventory; equip them yourself. Ownership investigations are ongoing.")
    (stats / "HC_Spell_Shout_Wardrobe.txt").write_text(f'''new entry "{spell}"
type "SpellData"
using "Shout_SecondWind"
data "SpellType" "Shout"
data "Level" "0"
data "SpellProperties" "{';'.join(summoned)}"
data "TargetConditions" "Self()"
data "TooltipDamageList" ""
data "TooltipStatusApply" ""
data "DescriptionParams" ""
data "CastTextEvent" "Cast"
data "Icon" "{wardrobe_icon}"
data "DisplayName" "{title};1"
data "Description" "{description};1"
data "Cooldown" "OncePerRest"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "IgnoreSilence;UnavailableInDialogs"
data "TargetRadius" "0"
''', encoding="utf-8")
    return spell
