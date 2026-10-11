"""
Complete Generator Script for Baldur's Gate 3 Homeless Californian Class Mod.
Generates all LSX files, Stats/Data txt files, and Localization XML.
"""

import os
import uuid
import xml.etree.ElementTree as ET

# Deterministic namespace for reproducible GUIDs
NAMESPACE = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

def get_guid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))

def get_handle(name: str) -> str:
    u = uuid.uuid5(NAMESPACE, f"handle_{name}")
    h = u.hex
    return f"h{h[:8]}g{h[8:12]}g{h[12:16]}g{h[16:20]}g{h[20:32]}"

# Core GUIDs
MOD_UUID = get_guid("HomelessCalifornian_Mod")
CLASS_UUID = get_guid("HomelessCalifornian_Class")
PROG_TABLE_UUID = get_guid("HomelessCalifornian_ProgTable")

# Subclass GUIDs
SUBCLASS_TENDERLOIN_UUID = get_guid("Subclass_Tenderloin")
SUBCLASS_TENDERLOIN_TABLE_UUID = get_guid("Subclass_Tenderloin_Table")

SUBCLASS_VENICE_UUID = get_guid("Subclass_Venice")
SUBCLASS_VENICE_TABLE_UUID = get_guid("Subclass_Venice_Table")

SUBCLASS_BART_UUID = get_guid("Subclass_BART")
SUBCLASS_BART_TABLE_UUID = get_guid("Subclass_BART_Table")

# Spell Lists
SPELLLIST_LVL1 = get_guid("SpellList_Lvl1")
SPELLLIST_LVL2 = get_guid("SpellList_Lvl2")
SPELLLIST_LVL5 = get_guid("SpellList_Lvl5")
SPELLLIST_LVL7 = get_guid("SpellList_Lvl7")
SPELLLIST_LVL9 = get_guid("SpellList_Lvl9")

SPELLLIST_TENDERLOIN_L3 = get_guid("SpellList_Tenderloin_L3")
SPELLLIST_VENICE_L3 = get_guid("SpellList_Venice_L3")
SPELLLIST_BART_L3 = get_guid("SpellList_BART_L3")

# Presets and Lists
ABILITY_DISTRIB_UUID = get_guid("AbilityDistrib_Homeless")
SKILLLIST_UUID = get_guid("SkillList_Homeless")
DEFAULT_ABILITY_UUID = get_guid("DefaultAbility_Homeless")
DEFAULT_SKILL_UUID = get_guid("DefaultSkill_Homeless")

# Base directories
MOD_NAME = "HomelessCalifornian"
ROOT_DIR = os.getcwd()
SRC_DIR = os.path.join(ROOT_DIR, "src", MOD_NAME)
MODS_DIR = os.path.join(SRC_DIR, "Mods", MOD_NAME)
PUBLIC_DIR = os.path.join(SRC_DIR, "Public", MOD_NAME)

# Dictionary of localization entries: {handle: text}
LOCA_ENTRIES = {}

def add_loca(key: str, text: str) -> str:
    handle = get_handle(key)
    LOCA_ENTRIES[handle] = text
    return handle

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

# -------------------------------------------------------------
# 1. Localization Strings Setup
# -------------------------------------------------------------
# Class & Subclass Display Names & Descriptions
h_class_name = add_loca("class_name", "Homeless Californian")
h_class_desc = add_loca("class_desc", "Hardened by the concrete jungles of San Francisco and Los Angeles, the Homeless Californian channels makeshift biological warfare, erratic street fury, and the gravity-defying equilibrium of the legendary Fent Lean.")

h_sub_tenderloin_name = add_loca("sub_tenderloin_name", "Tenderloin Biohazard")
h_sub_tenderloin_desc = add_loca("sub_tenderloin_desc", "Master of chemical concoctions and sidewalk biohazards. Amplifies the potency of toxic clouds, explosive biological payloads, and turns environmental hazards into personal restoration.")

h_sub_venice_name = add_loca("sub_venice_name", "Venice Boardwalk Brawler")
h_sub_venice_desc = add_loca("sub_venice_desc", "A ferocious close-quarters pugilist specializing in improvised shivs, reckless flurries, and chaotic shopping cart charges.")

h_sub_bart_name = add_loca("sub_bart_name", "BART Platform Menace")
h_sub_bart_desc = add_loca("sub_bart_desc", "An erratic street phantom who slips through turnstiles and spatial dimensions, unleashing ear-piercing 3 AM screeches to disorient and terrorize foes.")

# Spells & Actions
h_sling_poop_name = add_loca("sling_poop_name", "Sling Poop")
h_sling_poop_desc = add_loca("sling_poop_desc", "Hurl a handful of raw biological waste at a target. Deals 1d6 Bludgeoning + 1d4 Poison damage, coats the ground in a repulsive slick, and inflicts Fecal Stench.")

h_sling_poop_chunky_name = add_loca("sling_poop_chunky_name", "Sling Chunky Poop")
h_sling_poop_chunky_desc = add_loca("sling_poop_chunky_desc", "Hurl a dense, fermented biological projectile with devastating force. Deals 2d6 Bludgeoning + 2d6 Poison damage, spreading an expanded slick and inflicting severe Fecal Stench.")

h_sling_fent_name = add_loca("sling_fent_name", "Sling Fentanyl")
h_sling_fent_desc = add_loca("sling_fent_desc", "Launch a concentrated chemical dose at an enemy. Deals 1d4 Psychic damage, spawns a toxic narcotic haze, and forces a DC Constitution Saving Throw or the target is paralyzed in Fent Stupor.")

h_sling_fent_cloud_name = add_loca("sling_fent_cloud_name", "Mass Fentanyl Contraband")
h_sling_fent_cloud_desc = add_loca("sling_fent_cloud_desc", "Scatter an entire contraband brick across a wide area. Creates an expansive narcotic fog that numbs, slows, and incapacitates all caught within.")

h_fent_lean_name = add_loca("fent_lean_name", "Fent Lean")
h_fent_lean_desc = add_loca("fent_lean_desc", "Assume the ultimate posture of street invulnerability: rigidly fold forward at a perfect 90-degree waist angle. Gain resistance to ALL damage, complete immunity to Knockdown, Prone, Shove, and Psychic effects, and +3 AC due to your bewildering center of gravity. Your movement speed is reduced to 0.")

h_fent_lean_end_name = add_loca("fent_lean_end_name", "Snap Out of Lean")
h_fent_lean_end_desc = add_loca("fent_lean_end_desc", "Forcefully snap your spine back into vertical alignment, regaining normal mobility.")

h_sidewalk_scramble_name = add_loca("sidewalk_scramble_name", "Sidewalk Scramble")
h_sidewalk_scramble_desc = add_loca("sidewalk_scramble_desc", "Sprint across the battlefield with reckless street urgency, ignoring difficult terrain such as broken glass, grease, and mud.")

h_panhandling_name = add_loca("panhandling_name", "Aggressive Panhandling")
h_panhandling_desc = add_loca("panhandling_desc", "Corner an enemy and aggressively demand spare coin or life essence. The target must succeed on a Wisdom Saving Throw or drop their weapons in terror and become Frightened for 2 turns.")

h_feral_screech_name = add_loca("feral_screech_name", "Feral Screech")
h_feral_screech_desc = add_loca("feral_screech_desc", "Unleash an unhinged, high-decibel 3 AM sidewalk wail. Foes within 9m take 3d6 Psychic damage and become Deafened and Frightened.")

h_tent_encampment_name = add_loca("tent_encampment_name", "Tent City Sanctuary")
h_tent_encampment_desc = add_loca("tent_encampment_desc", "Erect an impromptu tarp shelter perimeter. Allies within the encampment gain 15 Temporary Hit Points and cannot be targeted by ranged attacks for 3 turns.")

# Subclass abilities
h_bottle_shank_name = add_loca("bottle_shank_name", "Broken Bottle Shank")
h_bottle_shank_desc = add_loca("bottle_shank_desc", "Viciously stab an adjacent target with a jagged glass bottle. Deals 1d8 Piercing damage and inflicts heavy Bleeding.")

h_cart_charge_name = add_loca("cart_charge_name", "Shopping Cart Charge")
h_cart_charge_desc = add_loca("cart_charge_desc", "Barreling forward behind a squeaky shopping cart, rush up to 9m and slam into a target, dealing 2d6 Bludgeoning damage and knocking them Prone.")

h_turnstile_hop_name = add_loca("turnstile_hop_name", "Turnstile Hop")
h_turnstile_hop_desc = add_loca("turnstile_hop_desc", "Effortlessly hurdle through urban dimensional barriers, teleporting up to 12m as a Bonus Action.")

# Statuses
h_status_fent_lean_name = add_loca("status_fent_lean_name", "Fent Lean")
h_status_fent_lean_desc = add_loca("status_fent_lean_desc", "Locked in the legendary 90-degree fold. Immune to Knockdown, Prone, and Psychic damage. Resistant to ALL damage. +3 AC. Movement speed is 0.")

h_status_fecal_stench_name = add_loca("status_fecal_stench_name", "Fecal Stench")
h_status_fecal_stench_desc = add_loca("status_fecal_stench_desc", "Coated in raw, rank bio-waste. Sickened by the odor, suffering Disadvantage on Attack Rolls and -3m Movement Speed.")

h_status_fent_stupor_name = add_loca("status_fent_stupor_name", "Fent Stupor")
h_status_fent_stupor_desc = add_loca("status_fent_stupor_desc", "Severe narcotic stupor and respiratory depression. Incapacitated, unable to take actions or reactions, and movement speed reduced to 0.")

h_status_scramble_name = add_loca("status_scramble_name", "Sidewalk Scramble")
h_status_scramble_desc = add_loca("status_scramble_desc", "Movement speed increased by 4.5m and immune to difficult terrain.")

h_status_panhandled_name = add_loca("status_panhandled_name", "Panhandled Terror")
h_status_panhandled_desc = add_loca("status_panhandled_desc", "Terrified by aggressive personal space violations. Frightened and suffering Disadvantage on Attack Rolls.")

# Passives
h_passive_unarmored_name = add_loca("passive_unarmored_name", "Street Grit Defense")
h_passive_unarmored_desc = add_loca("passive_unarmored_desc", "While not wearing armor, your tough skin and street instincts add both your Constitution and Dexterity modifiers to your Armor Class.")

h_passive_immunity_name = add_loca("passive_immunity_name", "Sidewalk Immunity")
h_passive_immunity_desc = add_loca("passive_immunity_desc", "Years of dumpster exposure have forged an impenetrable immune system. Immune to Disease and Poisoned, and resistant to Poison damage.")

h_passive_lean_heal_name = add_loca("passive_lean_heal_name", "Restorative Stupor")
h_passive_lean_heal_desc = add_loca("passive_lean_heal_desc", "While locked in the Fent Lean, your slowed metabolic rate knits wounds back together, restoring 2d6 Hit Points at the start of every turn.")

h_passive_lean_reflect_name = add_loca("passive_lean_reflect_name", "Baffling Retaliation")
h_passive_lean_reflect_desc = add_loca("passive_lean_reflect_desc", "While in Fent Lean, melee attackers attempting to strike your bewildering posture strike bone-jarring equilibrium, suffering 1d10 Psychic damage.")


# -------------------------------------------------------------
# 2. Generate meta.lsx
# -------------------------------------------------------------
def generate_meta_lsx():
    path = os.path.join(MODS_DIR, "meta.lsx")
    ensure_dir(os.path.dirname(path))
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="Config">
        <node id="root">
            <children>
                <node id="Conflicts"/>
                <node id="Dependencies">
                    <children>
                        <node id="ModuleShortDesc">
                            <attribute id="Folder" type="LSString" value="GustavDev"/>
                            <attribute id="MD5" type="LSString" value="c360fcf32ac7d77e2ba190ccb102c94d"/>
                            <attribute id="Name" type="LSString" value="GustavDev"/>
                            <attribute id="PublishHandle" type="uint64" value="0"/>
                            <attribute id="UUID" type="guid" value="28ac9ce2-2aba-8cda-b3b5-6e922f71b6b8"/>
                            <attribute id="Version64" type="int64" value="145241130939120737"/>
                        </node>
                    </children>
                </node>
                <node id="ModuleInfo">
                    <attribute id="Author" type="LSString" value="Matthew"/>
                    <attribute id="CharacterCreationLevelName" type="FixedString" value=""/>
                    <attribute id="Description" type="LSString" value="Introduces the Homeless Californian class to Baldur's Gate 3. Sling poop, fling fentanyl, and master the legendary Fent Lean!"/>
                    <attribute id="FileSize" type="uint64" value="0"/>
                    <attribute id="Folder" type="LSString" value="{MOD_NAME}"/>
                    <attribute id="LobbyLevelName" type="FixedString" value=""/>
                    <attribute id="MD5" type="LSString" value=""/>
                    <attribute id="MenuLevelName" type="FixedString" value=""/>
                    <attribute id="Name" type="LSString" value="Homeless Californian Class"/>
                    <attribute id="NumPlayers" type="uint8" value="4"/>
                    <attribute id="PhotoBooth" type="FixedString" value=""/>
                    <attribute id="PublishHandle" type="uint64" value="0"/>
                    <attribute id="StartupLevelName" type="FixedString" value=""/>
                    <attribute id="UUID" type="FixedString" value="{MOD_UUID}"/>
                    <attribute id="Version64" type="int64" value="36028797018963968"/>
                    <children>
                        <node id="PublishVersion">
                            <attribute id="Version64" type="int64" value="36028797018963968"/>
                        </node>
                    </children>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")


# -------------------------------------------------------------
# 3. Generate ClassDescriptions.lsx
# -------------------------------------------------------------
def generate_class_descriptions_lsx():
    path = os.path.join(PUBLIC_DIR, "ClassDescriptions", "ClassDescriptions.lsx")
    ensure_dir(os.path.dirname(path))
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="ClassDescriptions">
        <node id="root">
            <children>
                <!-- Main Class: Homeless Californian -->
                <node id="ClassDescription">
                    <attribute id="BaseHp" type="int32" value="12"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_class_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_class_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="7"/>
                    <attribute id="ItemsHotbarColumns" type="int32" value="2"/>
                    <attribute id="LearningStrategy" type="uint8" value="1"/>
                    <attribute id="MulticlassSpellcasterModifier" type="double" value="0"/>
                    <attribute id="MustPrepareSpells" type="bool" value="false"/>
                    <attribute id="Name" type="FixedString" value="HomelessCalifornian"/>
                    <attribute id="PrimaryAbility" type="uint8" value="3"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="SoundClassType" type="FixedString" value="Barbarian"/>
                    <attribute id="SpellCastingAbility" type="uint8" value="3"/>
                    <attribute id="UUID" type="guid" value="{CLASS_UUID}"/>
                    <children>
                        <node id="Tags">
                            <!-- Barbarian class dialogue tag for gritty raw tone -->
                            <attribute id="Object" type="guid" value="d82370fb-caf8-4da2-bd26-e16180c14b88"/>
                        </node>
                    </children>
                </node>

                <!-- Subclass 1: Tenderloin Biohazard -->
                <node id="ClassDescription">
                    <attribute id="BaseHp" type="int32" value="12"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_sub_tenderloin_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_sub_tenderloin_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="7"/>
                    <attribute id="ItemsHotbarColumns" type="int32" value="2"/>
                    <attribute id="LearningStrategy" type="uint8" value="1"/>
                    <attribute id="MulticlassSpellcasterModifier" type="double" value="0"/>
                    <attribute id="MustPrepareSpells" type="bool" value="false"/>
                    <attribute id="Name" type="FixedString" value="TenderloinBiohazard"/>
                    <attribute id="ParentGuid" type="guid" value="{CLASS_UUID}"/>
                    <attribute id="PrimaryAbility" type="uint8" value="3"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{SUBCLASS_TENDERLOIN_TABLE_UUID}"/>
                    <attribute id="SpellCastingAbility" type="uint8" value="3"/>
                    <attribute id="UUID" type="guid" value="{SUBCLASS_TENDERLOIN_UUID}"/>
                </node>

                <!-- Subclass 2: Venice Boardwalk Brawler -->
                <node id="ClassDescription">
                    <attribute id="BaseHp" type="int32" value="12"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_sub_venice_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_sub_venice_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="7"/>
                    <attribute id="ItemsHotbarColumns" type="int32" value="2"/>
                    <attribute id="LearningStrategy" type="uint8" value="1"/>
                    <attribute id="MulticlassSpellcasterModifier" type="double" value="0"/>
                    <attribute id="MustPrepareSpells" type="bool" value="false"/>
                    <attribute id="Name" type="FixedString" value="VeniceBoardwalkBrawler"/>
                    <attribute id="ParentGuid" type="guid" value="{CLASS_UUID}"/>
                    <attribute id="PrimaryAbility" type="uint8" value="3"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{SUBCLASS_VENICE_TABLE_UUID}"/>
                    <attribute id="SpellCastingAbility" type="uint8" value="3"/>
                    <attribute id="UUID" type="guid" value="{SUBCLASS_VENICE_UUID}"/>
                </node>

                <!-- Subclass 3: BART Platform Menace -->
                <node id="ClassDescription">
                    <attribute id="BaseHp" type="int32" value="12"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_sub_bart_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_sub_bart_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="7"/>
                    <attribute id="ItemsHotbarColumns" type="int32" value="2"/>
                    <attribute id="LearningStrategy" type="uint8" value="1"/>
                    <attribute id="MulticlassSpellcasterModifier" type="double" value="0"/>
                    <attribute id="MustPrepareSpells" type="bool" value="false"/>
                    <attribute id="Name" type="FixedString" value="BARTPlatformMenace"/>
                    <attribute id="ParentGuid" type="guid" value="{CLASS_UUID}"/>
                    <attribute id="PrimaryAbility" type="uint8" value="3"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{SUBCLASS_BART_TABLE_UUID}"/>
                    <attribute id="SpellCastingAbility" type="uint8" value="3"/>
                    <attribute id="UUID" type="guid" value="{SUBCLASS_BART_UUID}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")


# -------------------------------------------------------------
# 4. Generate Lists/SpellLists.lsx and Lists/SkillLists.lsx
# -------------------------------------------------------------
def generate_lists_lsx():
    # SpellLists.lsx
    spell_path = os.path.join(PUBLIC_DIR, "Lists", "SpellLists.lsx")
    ensure_dir(os.path.dirname(spell_path))
    spell_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="SpellLists">
        <node id="root">
            <children>
                <!-- Level 1: Poop, Fentanyl, Fent Lean, Scramble -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_SlingPoop;Projectile_SlingFentanyl;Shout_FentLean;Shout_FentLean_End;Shout_SidewalkScramble"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL1}"/>
                </node>

                <!-- Level 2: Aggressive Panhandling -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_AggressivePanhandling"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL2}"/>
                </node>

                <!-- Level 5: Chunky Poop upgrade -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_SlingPoop_Chunky"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL5}"/>
                </node>

                <!-- Level 7: Feral Screech -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_FeralScreech"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL7}"/>
                </node>

                <!-- Level 9: Mass Fentanyl Cloud & Tent Encampment -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_SlingFentanyl_Mass;Shout_TentEncampment"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL9}"/>
                </node>

                <!-- Subclass Tenderloin Spells -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_BiohazardBomb"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_TENDERLOIN_L3}"/>
                </node>

                <!-- Subclass Venice Brawler Spells -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Target_BrokenBottleShank;Shout_ShoppingCartCharge"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_VENICE_L3}"/>
                </node>

                <!-- Subclass BART Menace Spells -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_TurnstileHop"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_BART_L3}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(spell_path, "w", encoding="utf-8") as f:
        f.write(spell_content)
    print(f"Generated: {spell_path}")

    # SkillLists.lsx
    skill_path = os.path.join(PUBLIC_DIR, "Lists", "SkillLists.lsx")
    skill_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="SkillLists">
        <node id="root">
            <children>
                <node id="SkillList">
                    <attribute id="Skills" type="LSString" value="Athletics,Acrobatics,SleightOfHand,Stealth,Survival,Intimidation,Perception"/>
                    <attribute id="UUID" type="guid" value="{SKILLLIST_UUID}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_content)
    print(f"Generated: {skill_path}")


# -------------------------------------------------------------
# 5. Generate Progressions/Progressions.lsx
# -------------------------------------------------------------
def generate_progressions_lsx():
    path = os.path.join(PUBLIC_DIR, "Progressions", "Progressions.lsx")
    ensure_dir(os.path.dirname(path))

    # Base proficiencies: Simple Weapons, Improvised Weapons, Clubs, Daggers, Shields
    boosts_lvl1 = "ProficiencyBonus(SavingThrow,Constitution);ProficiencyBonus(SavingThrow,Strength);Proficiency(SimpleWeapons);Proficiency(ImprovisedWeapons);Proficiency(Daggers);Proficiency(Clubs);Proficiency(Shields)"
    passives_lvl1 = "StreetHardiness;StreetImmunity"

    # We will generate Level 1 to 12
    nodes = []

    # Level 1
    u_l1 = get_guid("Prog_Homeless_Lvl1")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Boosts" type="LSString" value="{boosts_lvl1}"/>
                    <attribute id="Level" type="uint8" value="1"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="{passives_lvl1}"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL1});SelectSkills({SKILLLIST_UUID},2);SelectAbilityBonus(b9149c8e-52c8-46e5-9cb6-fc39301c05fe,AbilityBonus,2,1)"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l1}"/>
                </node>""")

    # Level 2
    u_l2 = get_guid("Prog_Homeless_Lvl2")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="2"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL2})"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l2}"/>
                </node>""")

    # Level 3 (Subclasses)
    u_l3 = get_guid("Prog_Homeless_Lvl3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l3}"/>
                    <children>
                        <node id="SubClasses">
                            <children>
                                <node id="SubClass">
                                    <attribute id="Object" type="guid" value="{SUBCLASS_TENDERLOIN_UUID}"/>
                                </node>
                                <node id="SubClass">
                                    <attribute id="Object" type="guid" value="{SUBCLASS_VENICE_UUID}"/>
                                </node>
                                <node id="SubClass">
                                    <attribute id="Object" type="guid" value="{SUBCLASS_BART_UUID}"/>
                                </node>
                            </children>
                        </node>
                    </children>
                </node>""")

    # Level 4 (Feat)
    u_l4 = get_guid("Prog_Homeless_Lvl4")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="true"/>
                    <attribute id="Level" type="uint8" value="4"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l4}"/>
                </node>""")

    # Level 5 (Extra Attack + Chunky Poop)
    u_l5 = get_guid("Prog_Homeless_Lvl5")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="5"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="ExtraAttack"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL5})"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l5}"/>
                </node>""")

    # Level 6 (Restorative Stupor in Lean)
    u_l6 = get_guid("Prog_Homeless_Lvl6")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="6"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="RestorativeLean"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l6}"/>
                </node>""")

    # Level 7 (Feral Screech)
    u_l7 = get_guid("Prog_Homeless_Lvl7")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="7"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL7})"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l7}"/>
                </node>""")

    # Level 8 (Feat)
    u_l8 = get_guid("Prog_Homeless_Lvl8")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="true"/>
                    <attribute id="Level" type="uint8" value="8"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l8}"/>
                </node>""")

    # Level 9 (Mass Fent & Tent Encampment)
    u_l9 = get_guid("Prog_Homeless_Lvl9")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="9"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL9})"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l9}"/>
                </node>""")

    # Level 10
    u_l10 = get_guid("Prog_Homeless_Lvl10")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="10"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l10}"/>
                </node>""")

    # Level 11 (Lean Retaliation)
    u_l11 = get_guid("Prog_Homeless_Lvl11")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="11"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="LeanDamageReflect"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l11}"/>
                </node>""")

    # Level 12 (Feat)
    u_l12 = get_guid("Prog_Homeless_Lvl12")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="true"/>
                    <attribute id="Level" type="uint8" value="12"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l12}"/>
                </node>""")

    # Subclass Progressions (ProgressionType 1)
    # Tenderloin
    u_tend_l3 = get_guid("Prog_Tend_L3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="TenderloinBiohazard"/>
                    <attribute id="ProgressionType" type="uint8" value="1"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_TENDERLOIN_L3})"/>
                    <attribute id="TableUUID" type="guid" value="{SUBCLASS_TENDERLOIN_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_tend_l3}"/>
                </node>""")

    # Venice Brawler
    u_ven_l3 = get_guid("Prog_Ven_L3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="VeniceBoardwalkBrawler"/>
                    <attribute id="ProgressionType" type="uint8" value="1"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_VENICE_L3})"/>
                    <attribute id="TableUUID" type="guid" value="{SUBCLASS_VENICE_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_ven_l3}"/>
                </node>""")

    # BART Menace
    u_bart_l3 = get_guid("Prog_Bart_L3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="BARTPlatformMenace"/>
                    <attribute id="ProgressionType" type="uint8" value="1"/>
                    <attribute id="PassivesAdded" type="LSString" value="ReliableTalent"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_BART_L3})"/>
                    <attribute id="TableUUID" type="guid" value="{SUBCLASS_BART_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_bart_l3}"/>
                </node>""")

    joined_nodes = "".join(nodes)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="Progressions">
        <node id="root">
            <children>{joined_nodes}
            </children>
        </node>
    </region>
</save>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")


# -------------------------------------------------------------
# 6. Generate Character Creation Presets
# -------------------------------------------------------------
def generate_presets_lsx():
    path = os.path.join(PUBLIC_DIR, "CharacterCreationPresets", "AbilityDistributionPresets.lsx")
    ensure_dir(os.path.dirname(path))
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="AbilityDistributionPresets">
        <node id="root">
            <children>
                <node id="AbilityDistributionPreset">
                    <attribute id="Charisma" type="int32" value="10"/>
                    <attribute id="ClassUUID" type="guid" value="{CLASS_UUID}"/>
                    <attribute id="Constitution" type="int32" value="15"/>
                    <attribute id="Dexterity" type="int32" value="14"/>
                    <attribute id="Intelligence" type="int32" value="8"/>
                    <attribute id="Strength" type="int32" value="13"/>
                    <attribute id="UUID" type="guid" value="{ABILITY_DISTRIB_UUID}"/>
                    <attribute id="Wisdom" type="int32" value="12"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")

    # DefaultValues/Abilities.lsx
    ab_path = os.path.join(PUBLIC_DIR, "DefaultValues", "Abilities.lsx")
    ensure_dir(os.path.dirname(ab_path))
    ab_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="DefaultValues">
        <node id="root">
            <children>
                <node id="DefaultValue">
                    <attribute id="Add" type="LSString" value="Constitution;Dexterity"/>
                    <attribute id="Level" type="int32" value="1"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{DEFAULT_ABILITY_UUID}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(ab_path, "w", encoding="utf-8") as f:
        f.write(ab_content)
    print(f"Generated: {ab_path}")

    # DefaultValues/Skills.lsx
    sk_path = os.path.join(PUBLIC_DIR, "DefaultValues", "Skills.lsx")
    ensure_dir(os.path.dirname(sk_path))
    sk_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="DefaultValues">
        <node id="root">
            <children>
                <node id="DefaultValue">
                    <attribute id="Add" type="LSString" value="Survival;Athletics"/>
                    <attribute id="Level" type="int32" value="1"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{DEFAULT_SKILL_UUID}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(sk_path, "w", encoding="utf-8") as f:
        f.write(sk_content)
    print(f"Generated: {sk_path}")


# -------------------------------------------------------------
# 7. Generate Stats/Generated/Data TXT files
# -------------------------------------------------------------
def generate_stats_txt():
    stats_dir = os.path.join(PUBLIC_DIR, "Stats", "Generated", "Data")
    ensure_dir(stats_dir)

    # Spell_Projectile.txt
    proj_content = f"""new entry "Projectile_SlingPoop"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "SpellProperties" "GROUND:CreateSurface(1.5,,SurfacePoison);ApplyStatus(FECAL_STENCH,100,2)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "Attack(AttackType.RangedSpellAttack)"
data "SpellSuccess" "DealDamage(1d6+CON,Bludgeoning);DealDamage(1d4,Poison);ApplyStatus(FECAL_STENCH,100,2)"
data "TargetConditions" "not Dead()"
data "ProjectileCount" "1"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_Transmutation_RayOfSickness"
data "DisplayName" "{h_sling_poop_name};1"
data "Description" "{h_sling_poop_desc};1"
data "TooltipDamageList" "DealDamage(1d6+CON,Bludgeoning);DealDamage(1d4,Poison)"
data "TooltipAttackSave" "RangedSpellAttack"
data "CastSound" "Spell_Cast_Damage_Acid_ChromaticOrbAcid_L1to3"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Damage"
data "SpellFlags" "HasSomaticComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
data "DamageType" "Bludgeoning"

new entry "Projectile_SlingPoop_Chunky"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "SpellProperties" "GROUND:CreateSurface(2.5,,SurfacePoison);ApplyStatus(FECAL_STENCH,100,3)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "Attack(AttackType.RangedSpellAttack)"
data "SpellSuccess" "DealDamage(2d6+CON,Bludgeoning);DealDamage(2d4,Poison);ApplyStatus(FECAL_STENCH,100,3)"
data "TargetConditions" "not Dead()"
data "ProjectileCount" "1"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_Evocation_Grease"
data "DisplayName" "{h_sling_poop_chunky_name};1"
data "Description" "{h_sling_poop_chunky_desc};1"
data "TooltipDamageList" "DealDamage(2d6+CON,Bludgeoning);DealDamage(2d4,Poison)"
data "TooltipAttackSave" "RangedSpellAttack"
data "CastSound" "Spell_Cast_Damage_Acid_ChromaticOrbAcid_L1to3"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Damage"
data "SpellFlags" "HasSomaticComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
data "DamageType" "Bludgeoning"

new entry "Projectile_SlingFentanyl"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "1"
data "SpellSchool" "Necromancy"
data "CooldownType" "OncePerShortRest"
data "SpellProperties" "GROUND:CreateCloud(2,,SurfaceCloudPoison)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(1d4,Psychic);ApplyStatus(FENT_STUPOR,100,1)"
data "SpellFail" "DealDamage(1d4+CON,Psychic);ApplyStatus(FENT_STUPOR,100,2)"
data "TargetConditions" "not Dead()"
data "ProjectileCount" "1"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_Illusion_Sleep"
data "DisplayName" "{h_sling_fent_name};1"
data "Description" "{h_sling_fent_desc};1"
data "TooltipDamageList" "DealDamage(1d4+CON,Psychic)"
data "TooltipAttackSave" "Constitution"
data "CastSound" "Spell_Cast_Buff_PoisonSpray"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
data "DamageType" "Psychic"

new entry "Projectile_SlingFentanyl_Mass"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "5"
data "SpellSchool" "Necromancy"
data "CooldownType" "OncePerShortRest"
data "SpellProperties" "GROUND:CreateCloud(4,,SurfaceCloudPoison);ApplyStatus(FENT_STUPOR,100,2)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(2d4,Psychic);ApplyStatus(FENT_STUPOR,100,1)"
data "SpellFail" "DealDamage(3d6+CON,Psychic);ApplyStatus(FENT_STUPOR,100,2)"
data "TargetConditions" "not Dead()"
data "ExplodeRadius" "4"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_Necromancy_Contagion"
data "DisplayName" "{h_sling_fent_cloud_name};1"
data "Description" "{h_sling_fent_cloud_desc};1"
data "TooltipDamageList" "DealDamage(3d6+CON,Psychic)"
data "TooltipAttackSave" "Constitution"
data "CastSound" "Spell_Cast_Buff_PoisonSpray"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "HasSomaticComponent;IsSpell;IsHarmful"
data "DamageType" "Psychic"

new entry "Projectile_BiohazardBomb"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "2"
data "SpellSchool" "Evocation"
data "CooldownType" "OncePerShortRest"
data "SpellProperties" "GROUND:CreateSurface(3,,SurfacePoison);GROUND:CreateCloud(3,,SurfaceCloudPoison);ApplyStatus(FECAL_STENCH,100,3)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "ExplodeRadius" "3"
data "SpellRoll" "Attack(AttackType.RangedSpellAttack)"
data "SpellSuccess" "DealDamage(3d6+CON,Acid);DealDamage(2d6,Poison);ApplyStatus(FECAL_STENCH,100,3)"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_Evocation_StinkingCloud"
data "DisplayName" "Biohazard Bomb;1"
data "Description" "Hurl a supercharged chemical-biological payload that detonates in a 3m toxic inferno.;1"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "HasSomaticComponent;IsSpell;IsHarmful"
data "DamageType" "Acid"
"""
    with open(os.path.join(stats_dir, "Spell_Projectile.txt"), "w", encoding="utf-8") as f:
        f.write(proj_content)

    # Spell_Shout.txt
    shout_content = f"""new entry "Shout_FentLean"
type "SpellData"
data "SpellType" "Shout"
data "Level" "1"
data "CooldownType" "OncePerShortRest"
data "SpellProperties" "ApplyStatus(SELF,FENT_LEAN,100,3)"
data "TargetConditions" "Self()"
data "Icon" "Spell_Buff_Rage"
data "DisplayName" "{h_fent_lean_name};1"
data "Description" "{h_fent_lean_desc};1"
data "CastSound" "Spell_Cast_Shout_Rage"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "d2a09b40-9a2c-47bc-bb37-c62d0891d451,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "SpellFlags" "IsSpell"

new entry "Shout_FentLean_End"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellProperties" "RemoveStatus(SELF,FENT_LEAN)"
data "TargetConditions" "Self()"
data "Icon" "Spell_Abjuration_Sanctuary"
data "DisplayName" "{h_fent_lean_end_name};1"
data "Description" "{h_fent_lean_end_desc};1"
data "UseCosts" "BonusActionPoint:1"
data "SpellFlags" "IsSpell"

new entry "Shout_SidewalkScramble"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "CooldownType" "OncePerTurn"
data "SpellProperties" "ApplyStatus(SELF,SIDEWALK_SCRAMBLE,100,1)"
data "TargetConditions" "Self()"
data "Icon" "Spell_Transmutation_Longstrider"
data "DisplayName" "{h_sidewalk_scramble_name};1"
data "Description" "{h_sidewalk_scramble_desc};1"
data "UseCosts" "BonusActionPoint:1"
data "SpellFlags" "IsSpell"

new entry "Shout_AggressivePanhandling"
type "SpellData"
data "SpellType" "Shout"
data "Level" "1"
data "CooldownType" "OncePerShortRest"
data "SpellProperties" "ApplyStatus(PANHANDLED_TERROR,100,2)"
data "AreaRadius" "9"
data "SpellRoll" "SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellFail" "ApplyStatus(PANHANDLED_TERROR,100,2)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Enchantment_DissonantWhispers"
data "DisplayName" "{h_panhandling_name};1"
data "Description" "{h_panhandling_desc};1"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "HasVerbalComponent;IsSpell;IsHarmful"

new entry "Shout_FeralScreech"
type "SpellData"
data "SpellType" "Shout"
data "Level" "4"
data "CooldownType" "OncePerShortRest"
data "SpellRoll" "SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(1d6,Psychic)"
data "SpellFail" "DealDamage(3d6+CON,Psychic);ApplyStatus(FRIGHTENED,100,2);ApplyStatus(DEAFENED,100,2)"
data "AreaRadius" "9"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Enchantment_HideousLaughter"
data "DisplayName" "{h_feral_screech_name};1"
data "Description" "{h_feral_screech_desc};1"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "HasVerbalComponent;IsSpell;IsHarmful"
data "DamageType" "Psychic"

new entry "Shout_ShoppingCartCharge"
type "SpellData"
data "SpellType" "Rush"
data "Level" "1"
data "CooldownType" "OncePerShortRest"
data "SpellProperties" "ApplyStatus(PRONE,100,1)"
data "TargetRadius" "9"
data "SpellRoll" "Attack(AttackType.MeleeWeaponAttack)"
data "SpellSuccess" "DealDamage(2d6+STR,Bludgeoning);ApplyStatus(PRONE,100,1)"
data "Icon" "Spell_Transmutation_ExpeditiousRetreat"
data "DisplayName" "{h_cart_charge_name};1"
data "Description" "{h_cart_charge_desc};1"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "IsHarmful"

new entry "Shout_TurnstileHop"
type "SpellData"
data "SpellType" "Teleportation"
data "Level" "2"
data "CooldownType" "OncePerShortRest"
data "TargetRadius" "12"
data "TargetConditions" "CanMove()"
data "Icon" "Spell_Conjuration_MistyStep"
data "DisplayName" "{h_turnstile_hop_name};1"
data "Description" "{h_turnstile_hop_desc};1"
data "UseCosts" "BonusActionPoint:1"
data "SpellFlags" "IsSpell"

new entry "Shout_TentEncampment"
type "SpellData"
data "SpellType" "Shout"
data "Level" "5"
data "CooldownType" "OncePerLongRest"
data "SpellProperties" "ApplyStatus(SELF,SANCTUARY,100,3);ApplyStatus(AID_5,100,3)"
data "TargetConditions" "Self()"
data "Icon" "Spell_Abjuration_Sanctuary"
data "DisplayName" "{h_tent_encampment_name};1"
data "Description" "{h_tent_encampment_desc};1"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "IsSpell"
"""
    with open(os.path.join(stats_dir, "Spell_Shout.txt"), "w", encoding="utf-8") as f:
        f.write(shout_content)

    # Spell_Target.txt
    target_content = f"""new entry "Target_BrokenBottleShank"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "TargetRadius" "1.5"
data "SpellRoll" "Attack(AttackType.MeleeWeaponAttack)"
data "SpellSuccess" "DealDamage(1d8+DEX,Piercing);ApplyStatus(BLEEDING,100,2)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Necromancy_InflictWounds"
data "DisplayName" "{h_bottle_shank_name};1"
data "Description" "{h_bottle_shank_desc};1"
data "UseCosts" "ActionPoint:1"
data "SpellFlags" "IsHarmful"
data "DamageType" "Piercing"
"""
    with open(os.path.join(stats_dir, "Spell_Target.txt"), "w", encoding="utf-8") as f:
        f.write(target_content)

    # Status_BOOST.txt
    status_content = f"""new entry "FENT_LEAN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_fent_lean_name};1"
data "Description" "{h_status_fent_lean_desc};1"
data "Icon" "Status_Heroism"
data "Boosts" "Resistance(All, Resistant);Immunity(Knockdown);Immunity(Prone);Immunity(Psychic);StatusImmunity(FRIGHTENED);StatusImmunity(CHARMED);StatusImmunity(STUNNED);AC(3);MovementSpeed(-100%);Disadvantage(AttackTarget)"
data "TickType" "EndTurn"

new entry "FECAL_STENCH"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_fecal_stench_name};1"
data "Description" "{h_status_fecal_stench_desc};1"
data "Icon" "Status_Nauseated"
data "Boosts" "Disadvantage(AttackRoll);Disadvantage(Ability);MovementSpeed(-3m)"
data "TickType" "EndTurn"

new entry "FENT_STUPOR"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_fent_stupor_name};1"
data "Description" "{h_status_fent_stupor_desc};1"
data "Icon" "Status_Lethargic"
data "Boosts" "Incapacitated();MovementSpeed(-9m);Disadvantage(SavingThrow, Dexterity)"
data "TickType" "EndTurn"

new entry "SIDEWALK_SCRAMBLE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_scramble_name};1"
data "Description" "{h_status_scramble_desc};1"
data "Icon" "Status_Longstrider"
data "Boosts" "MovementSpeed(4.5m);GameplayLight(None);Immunity(DifficultTerrain)"
data "TickType" "EndTurn"

new entry "PANHANDLED_TERROR"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_panhandled_name};1"
data "Description" "{h_status_panhandled_desc};1"
data "Icon" "Status_Fear"
data "Boosts" "Disadvantage(AttackRoll);Disadvantage(Ability);MovementSpeed(-4.5m)"
data "TickType" "EndTurn"
"""
    with open(os.path.join(stats_dir, "Status_BOOST.txt"), "w", encoding="utf-8") as f:
        f.write(status_content)

    # Passive.txt
    passive_content = f"""new entry "StreetHardiness"
type "PassiveData"
data "DisplayName" "{h_passive_unarmored_name};1"
data "Description" "{h_passive_unarmored_desc};1"
data "Icon" "PassiveFeature_UnarmoredDefense_Barbarian"
data "Properties" "Highlighted"
data "Boosts" "AC(ConstitutionModifier);AC(DexterityModifier)"
data "Conditions" "not WieldingArmor() and not WieldingShield()"

new entry "StreetImmunity"
type "PassiveData"
data "DisplayName" "{h_passive_immunity_name};1"
data "Description" "{h_passive_immunity_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Boosts" "Resistance(Poison, Resistant);StatusImmunity(POISONED)"

new entry "RestorativeLean"
type "PassiveData"
data "DisplayName" "{h_passive_lean_heal_name};1"
data "Description" "{h_passive_lean_heal_desc};1"
data "Icon" "PassiveFeature_SecondWind"
data "StatsFunctorContext" "OnTurn"
data "Conditions" "HasStatus('FENT_LEAN')"
data "StatsFunctors" "RegainHitPoints(2d6)"

new entry "LeanDamageReflect"
type "PassiveData"
data "DisplayName" "{h_passive_lean_reflect_name};1"
data "Description" "{h_passive_lean_reflect_desc};1"
data "Icon" "PassiveFeature_Retaliation"
data "StatsFunctorContext" "OnAttacked"
data "Conditions" "HasStatus('FENT_LEAN') and IsMeleeAttack()"
data "StatsFunctors" "DealDamage(1d10, Psychic)"
"""
    with open(os.path.join(stats_dir, "Passive.txt"), "w", encoding="utf-8") as f:
        f.write(passive_content)

    print(f"Generated Stats data in: {stats_dir}")


# -------------------------------------------------------------
# 8. Generate Localization Files
# -------------------------------------------------------------
def generate_localization():
    # Write to both Mods/HomelessCalifornian/Localization/English and Public/...
    loca_dirs = [
        os.path.join(MODS_DIR, "Localization", "English"),
        os.path.join(PUBLIC_DIR, "Localization", "English")
    ]
    for d in loca_dirs:
        ensure_dir(d)
        xml_path = os.path.join(d, "HomelessCalifornian.loca.xml")
        lines = ['<?xml version="1.0" encoding="utf-8"?>', '<contentList>']
        for handle, text in LOCA_ENTRIES.items():
            safe_text = (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            lines.append(f'    <content contentuid="{handle}" version="1">{safe_text}</content>')
        lines.append('</contentList>')
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Generated: {xml_path}")


def main():
    print("Generating Baldur's Gate 3 Homeless Californian Class Mod...")
    generate_meta_lsx()
    generate_class_descriptions_lsx()
    generate_lists_lsx()
    generate_progressions_lsx()
    generate_presets_lsx()
    generate_stats_txt()
    generate_localization()
    print("Mod source files generated successfully!")


if __name__ == "__main__":
    main()
