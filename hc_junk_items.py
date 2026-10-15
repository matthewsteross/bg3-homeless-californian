"""Round 3 junk items and the Curb Alert shout that hands them out.

Same pattern as hc_outfit.py (Unclaimed Wardrobe): every item is an HC-only
stat that `using`s a vanilla stat, with an HC root template whose
ParentTemplateId is a vanilla template id, so meshes, textures, body and race
mappings are all inherited. No vanilla asset is copied. Items are placed in the
inventory by a Shout using the Goodberry-style SummonInInventory pattern.

Vanilla evidence (temp_race, extracted from the game):
  WPN_Greatclub        Weapon.txt  stat -> template 19ce6720-03b6-4d22-bf35-4963b510d1da
  ARM_Boots_Leather    Armor.txt   stat -> template 969bab00-b269-46a5-a7e9-dd4887814719
  ARM_Helmet_Leather   Armor.txt   stat -> template c58a1f91-ec1b-49c8-96ab-d94d4be4b584
  OBJ_Potion_Healing   Object.txt  stat -> template d47006e9-8a51-453d-b200-9e0d42e9bbab
Each template id was confirmed as the MapKey of a GameObjects node in the
extracted RootTemplates/_merged.lsf, whose Stats attribute names the donor.
The potion template's OnUsePeaceActions consumes status POTION_OF_HEALING
(Status_BOOST.txt), so the kombucha template restates that action with its own
status; that is the only template override.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

GRANT_LEVEL = 6          # one of the base levels (6, 10, 12) with only a single HC spell grant; earliest of the tie

WEAPON = "HC_WPN_CaltransDetourSign"
BOOTS = "HC_ARM_DuctTapedHighTops"
DRINK = "HC_OBJ_LukewarmKombucha"
VISOR = "HC_ARM_TinfoilSunVisor"
DRINK_STATUS = "HC_POTION_KOMBUCHA"
BUZZ_STATUS = "HC_KOMBUCHA_BUZZ"
SPELL = "HC_Shout_CurbAlert"

# (name, stat type, donor stat, donor root template id, donor icon, rarity, title, description, extra stat lines)
ITEMS = (
    (WEAPON, "Weapon", "WPN_Greatclub", "19ce6720-03b6-4d22-bf35-4963b510d1da",
     "Item_WPN_HUM_Greatclub_A_0", "Common", "Caltrans Detour Sign",
     "A two-handed road sign of unknown jurisdiction. It detours your enemies, mostly into the ground.",
     ()),
    (BOOTS, "Armor", "ARM_Boots_Leather", "969bab00-b269-46a5-a7e9-dd4887814719",
     "Item_ARM_Boots_Leather_2", "Common", "Duct-Taped High-Tops",
     "Held together by tape and conviction. Slightly faster, mostly out of fear of the sole detaching.",
     (("Boosts", "ActionResource(Movement,1.5,0)"),)),
    (DRINK, "Object", "OBJ_Potion_Healing", "d47006e9-8a51-453d-b200-9e0d42e9bbab",
     "Item_CONS_Potion_Healing_A", "Common", "Lukewarm Gas Station Kombucha",
     "Fermented near a hot pump. Restores hit points, then leaves you buzzing and unable to sit still.",
     ()),
    (VISOR, "Armor", "ARM_Helmet_Leather", "c58a1f91-ec1b-49c8-96ab-d94d4be4b584",
     "Item_ARM_Helmet_Leather", "Uncommon", "Tin-Foil Sun Visor",
     "Blocks the sun, the signals, and most of what people say to you. You have advantage on Wisdom saving throws.",
     (("Boosts", "Advantage(SavingThrow,Wisdom)"),)),
)


def _stat_file(entries):
    return "\n".join(entries)


def generate_junk_items(public_dir, add_loca, get_guid):
    """Write HC-only items, statuses and the granting shout; return the spell name."""
    public = Path(public_dir)
    stats = public / "Stats" / "Generated" / "Data"
    roots = public / "RootTemplates"
    stats.mkdir(parents=True, exist_ok=True)
    roots.mkdir(parents=True, exist_ok=True)

    save = ET.Element("save")
    ET.SubElement(save, "version", major="4", minor="0", revision="9", build="0")
    region = ET.SubElement(save, "region", id="Templates")
    templates = ET.SubElement(region, "node", id="Templates")
    children = ET.SubElement(templates, "children")
    blocks = {"Weapon": [], "Armor": [], "Object": []}
    summoned = []

    for name, kind, base_stat, parent, icon, rarity, title, description, extra in ITEMS:
        template_id = get_guid(name + "_RootTemplate")
        title_handle = add_loca(name + "_Name", title)
        description_handle = add_loca(name + "_Description", description)
        obj = ET.SubElement(children, "node", id="GameObjects")
        for attr, attr_type, value in (
            ("MapKey", "FixedString", template_id),
            ("Name", "LSString", name),
            ("ParentTemplateId", "FixedString", parent),
            ("Stats", "FixedString", name),
            ("Type", "FixedString", "item"),
            ("Icon", "FixedString", icon),
        ):
            ET.SubElement(obj, "attribute", id=attr, type=attr_type, value=value)
        for attr, handle in (("DisplayName", title_handle), ("Description", description_handle)):
            ET.SubElement(obj, "attribute", id=attr, type="TranslatedString", handle=handle, version="1")
        if name == DRINK:
            technical = add_loca(name + "_TechnicalDescription",
                                 "Restores 2d4+2 hit points and grants 3 m of extra movement for 2 turns.")
            ET.SubElement(obj, "attribute", id="TechnicalDescription", type="TranslatedString",
                          handle=technical, version="1")
            # The vanilla potion template consumes POTION_OF_HEALING. Restate that
            # one action pointing at the kombucha status; nothing else is overridden.
            node_children = ET.SubElement(obj, "children")
            use = ET.SubElement(node_children, "node", id="OnUsePeaceActions")
            use_children = ET.SubElement(use, "children")
            action = ET.SubElement(use_children, "node", id="Action")
            ET.SubElement(action, "attribute", id="ActionType", type="int32", value="7")
            action_children = ET.SubElement(action, "children")
            attrs = ET.SubElement(action_children, "node", id="Attributes")
            for attr, attr_type, value in (
                ("Animation", "FixedString", "895ce382-397d-4b9a-9e8f-6ee3b1ff3a13"),
                ("Conditions", "LSString", ""),
                ("Consume", "bool", "True"),
                ("StatsId", "FixedString", DRINK_STATUS),
                ("StatusDuration", "int32", "0"),
            ):
                ET.SubElement(attrs, "attribute", id=attr, type=attr_type, value=value)

        lines = [f'new entry "{name}"', f'type "{kind}"', f'using "{base_stat}"',
                 f'data "RootTemplate" "{template_id}"', f'data "Rarity" "{rarity}"',
                 'data "ValueOverride" "0"']
        lines += [f'data "{key}" "{value}"' for key, value in extra]
        blocks[kind].append("\n".join(lines) + "\n")
        summoned.append(f"SummonInInventory({template_id},-1,1,false,false,false)")

    ET.indent(save, space="    ")
    ET.ElementTree(save).write(roots / "HC_JunkItems.lsf.lsx", encoding="utf-8", xml_declaration=True)
    (stats / "HC_Weapon_JunkItems.txt").write_text(_stat_file(blocks["Weapon"]), encoding="utf-8")
    (stats / "HC_Armor_JunkItems.txt").write_text(_stat_file(blocks["Armor"]), encoding="utf-8")
    (stats / "HC_Object_JunkItems.txt").write_text(_stat_file(blocks["Object"]), encoding="utf-8")

    # ---------------------------------------------------------------- statuses
    # Statuses are not translated through the template, so they carry their own loca.
    drink_title = add_loca(DRINK_STATUS + "_Name", "Lukewarm Gas Station Kombucha")
    buzz_title = add_loca(BUZZ_STATUS + "_Name", "Kombucha Buzz")
    buzz_description = add_loca(BUZZ_STATUS + "_Description",
                                "Fermentation is a journey. Your movement speed increases by 3 m.")
    (stats / "HC_Status_JunkItems.txt").write_text(f'''new entry "{DRINK_STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{drink_title};1"
data "Icon" "Item_CONS_Potion_Healing_A"
data "HitAnimationType" "MagicalNonDamage"
data "StackId" "{DRINK_STATUS}"
data "StatusPropertyFlags" "DisableOverhead;DisableCombatlog;DisablePortraitIndicator"
data "OnApplyFunctors" "RegainHitPoints(2d4+2);ApplyStatus({BUZZ_STATUS},100,2)"
data "ApplyEffect" "89f2d0ac-9295-4657-bfa6-fb6d61adf59c"

new entry "{BUZZ_STATUS}"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{buzz_title};1"
data "Description" "{buzz_description};1"
data "Icon" "Item_CONS_Potion_Speed"
data "StackId" "{BUZZ_STATUS}"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "ActionResource(Movement,3,0)"
''', encoding="utf-8")

    # ------------------------------------------------------------------ spell
    from hc_icon_keys import icon_for_spell
    icon = icon_for_spell(SPELL, 'Spell_Transmutation_Goodberry')
    spell_title = add_loca(SPELL + "_Name", "Curb Alert")
    spell_description = add_loca(
        SPELL + "_Description",
        "Put a sign that says FREE on a pile of someone's stuff. Find a Caltrans Detour Sign, "
        "Duct-Taped High-Tops, a Lukewarm Gas Station Kombucha and a Tin-Foil Sun Visor. "
        "Added to your inventory; equip them yourself.")
    (stats / "HC_Spell_Shout_CurbAlert.txt").write_text(f'''new entry "{SPELL}"
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
data "Icon" "{icon}"
data "DisplayName" "{spell_title};1"
data "Description" "{spell_description};1"
data "Cooldown" "OncePerRest"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "IgnoreSilence;UnavailableInDialogs"
data "TargetRadius" "0"
''', encoding="utf-8")
    return SPELL
