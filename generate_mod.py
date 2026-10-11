"""
Complete Generator Script for Baldur's Gate 3 Homeless Californian Mod.
Generates all LSX files, Stats/Data txt files, and Localization XML
for both the Homeless Californian Class and the Californian Race.
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

# -------------------------------------------------------------
# GUIDs - Class & Subclasses
# -------------------------------------------------------------
MOD_UUID = get_guid("HomelessCalifornian_Mod")
CLASS_UUID = get_guid("HomelessCalifornian_Class")
PROG_TABLE_UUID = get_guid("HomelessCalifornian_ProgTable")

SUBCLASS_TENDERLOIN_UUID = get_guid("Subclass_Tenderloin")
SUBCLASS_TENDERLOIN_TABLE_UUID = get_guid("Subclass_Tenderloin_Table")

SUBCLASS_VENICE_UUID = get_guid("Subclass_Venice")
SUBCLASS_VENICE_TABLE_UUID = get_guid("Subclass_Venice_Table")

SUBCLASS_BART_UUID = get_guid("Subclass_BART")
SUBCLASS_BART_TABLE_UUID = get_guid("Subclass_BART_Table")

# Class Spell Lists
SPELLLIST_LVL1 = get_guid("SpellList_Lvl1")
SPELLLIST_LVL2 = get_guid("SpellList_Lvl2")
SPELLLIST_LVL4 = get_guid("SpellList_Lvl4")
SPELLLIST_LVL5 = get_guid("SpellList_Lvl5")
SPELLLIST_LVL7 = get_guid("SpellList_Lvl7")
SPELLLIST_LVL9 = get_guid("SpellList_Lvl9")
SPELLLIST_LVL12 = get_guid("SpellList_Lvl12")

SPELLLIST_TENDERLOIN_L3 = get_guid("SpellList_Tenderloin_L3")
SPELLLIST_VENICE_L3 = get_guid("SpellList_Venice_L3")
SPELLLIST_BART_L3 = get_guid("SpellList_BART_L3")

# Class Presets and Lists
ABILITY_DISTRIB_UUID = get_guid("AbilityDistrib_Homeless")
SKILLLIST_UUID = get_guid("SkillList_Homeless")
DEFAULT_ABILITY_UUID = get_guid("DefaultAbility_Homeless")
DEFAULT_SKILL_UUID = get_guid("DefaultSkill_Homeless")

# -------------------------------------------------------------
# GUIDs - Race, Subraces & Identity
# -------------------------------------------------------------
RACE_CALIFORNIAN_UUID = get_guid("Race_Californian")
RACE_BEACHBORN_UUID = get_guid("Race_Californian_Beachborn")
RACE_SILICONITE_UUID = get_guid("Race_Californian_Siliconite")
RACE_INLANDEMPEROR_UUID = get_guid("Race_Californian_InlandEmperor")

PROG_TABLE_RACE_CALIFORNIAN = get_guid("ProgTable_Race_Californian")
PROG_TABLE_RACE_BEACHBORN = get_guid("ProgTable_Race_Beachborn")
PROG_TABLE_RACE_SILICONITE = get_guid("ProgTable_Race_Siliconite")
PROG_TABLE_RACE_INLANDEMPEROR = get_guid("ProgTable_Race_InlandEmperor")

PASSIVELIST_CALIFORNIA_IDENTITY = get_guid("PassiveList_CaliforniaIdentity")
PROG_DESC_CALIFORNIA_IDENTITY = get_guid("ProgDesc_CaliforniaIdentity")

SPELLLIST_CALIFORNIAN_L1 = get_guid("SpellList_Californian_L1")
SPELLLIST_BEACHBORN_L1 = get_guid("SpellList_Beachborn_L1")
SPELLLIST_SILICONITE_L1 = get_guid("SpellList_Siliconite_L1")

# Base directories
MOD_NAME = "HomelessCalifornian"
ROOT_DIR = os.getcwd()
SRC_DIR = os.path.join(ROOT_DIR, "src", MOD_NAME)
MODS_DIR = os.path.join(SRC_DIR, "Mods", MOD_NAME)
PUBLIC_DIR = os.path.join(SRC_DIR, "Public", MOD_NAME)
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

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

# Spells & Actions - Class
h_sling_poop_name = add_loca("sling_poop_name", "Sling Poop")
h_sling_poop_desc = add_loca("sling_poop_desc", "Hurl a handful of raw biological waste at a target. Deals 1d6 Bludgeoning + 1d4 Poison damage, coats the ground in a repulsive slick, and inflicts Fecal Stench.")

h_sling_poop_chunky_name = add_loca("sling_poop_chunky_name", "Sling Chunky Poop")
h_sling_poop_chunky_desc = add_loca("sling_poop_chunky_desc", "Hurl a dense, fermented biological projectile with devastating force. Deals 2d6 Bludgeoning + 2d6 Poison damage, spreading an expanded slick and inflicting severe Fecal Stench.")

h_sling_fent_name = add_loca("sling_fent_name", "Sling Fentanyl")
h_sling_fent_desc = add_loca("sling_fent_desc", "Launch a concentrated chemical dose at an enemy. Deals 1d4 Psychic damage, spawns a toxic narcotic haze, and forces a DC Constitution Saving Throw or the target is paralyzed in Fent Stupor.")

h_sling_fent_cloud_name = add_loca("sling_fent_cloud_name", "Mass Fentanyl Contraband")
h_sling_fent_cloud_desc = add_loca("sling_fent_cloud_desc", "Scatter an entire contraband brick across a wide area. Creates an expansive narcotic fog that numbs, slows, and incapacitates all caught within.")

h_fent_lean_name = add_loca("fent_lean_name", "Fent Lean")
h_fent_lean_desc = add_loca("fent_lean_desc", "Enter a state of gravity-defying postural transcendence. You bend backward at an impossible 45-degree angle. While leaning, you gain Resistance to all damage types, Advantage on Constitution and Dexterity saving throws, and +2 Armour Class, but your movement speed is reduced to zero. Can snap out at any time as a Free Action.")

h_snap_out_name = add_loca("snap_out_name", "Snap Out of Lean")
h_snap_out_desc = add_loca("snap_out_desc", "Instantly snap your spine back upright with a terrifying pop. Restores your mobility immediately. Costs no Action or Bonus Action.")

h_scramble_name = add_loca("scramble_name", "Sidewalk Scramble")
h_scramble_desc = add_loca("scramble_desc", "Scurry frantically across broken glass and hazardous surfaces as a Bonus Action. Increases movement speed, stacks with Dash, and grants immunity to difficult terrain and slipping for 2 turns.")

h_panhandling_name = add_loca("panhandling_name", "Aggressive Panhandling")
h_panhandling_desc = add_loca("panhandling_desc", "Shake a rusty cup aggressively at all nearby enemies within 6m. Forces a DC Wisdom Saving Throw: failing creatures must drop 2d6 gold on the ground and suffer Disadvantage on Attack Rolls for 2 turns from sheer awkwardness.")

h_screech_name = add_loca("screech_name", "Feral Screech")
h_screech_desc = add_loca("screech_desc", "Unleash an unhinged, ear-splitting 3 AM psychotic shriek. All enemies within a 9m cone suffer 3d6 Thunder damage and must make a Wisdom Saving Throw or become Frightened for 2 turns.")

h_tent_encampment_name = add_loca("tent_encampment_name", "Pitch Tent Encampment")
h_tent_encampment_desc = add_loca("tent_encampment_desc", "Erect a fortified, tarp-and-shopping-cart shantytown bunker on the battlefield. Provides Half-Cover (+2 AC and saving throws) to all allies inside and generates an aura of biological discouragement.")

h_biohazard_bomb_name = add_loca("biohazard_bomb_name", "Biohazard Bomb")
h_biohazard_bomb_desc = add_loca("biohazard_bomb_desc", "Lob a pressurized five-gallon bucket of aged, fermented street slop. Explodes in a 5m radius dealing 4d6 Poison + 2d6 Acid damage and creating persistent toxic fumes.")

h_bottle_shank_name = add_loca("bottle_shank_name", "Broken 40oz Shank")
h_bottle_shank_desc = add_loca("bottle_shank_desc", "Drive a jagged malt liquor bottleneck into vital organs. Deals 2d4 Piercing + 1d6 Slashing damage and inflicts deep Bleeding.")

h_cart_charge_name = add_loca("cart_charge_name", "Shopping Cart Charge")
h_cart_charge_desc = add_loca("cart_charge_desc", "Mount a rattling grocery cart packed with scrap metal and careen headfirst into enemy ranks. Deals 3d6 Bludgeoning damage, knocks all creatures in your path Prone, and travels up to 9 meters.")

h_turnstile_hop_name = add_loca("turnstile_hop_name", "Turnstile Hop")
h_turnstile_hop_desc = add_loca("turnstile_hop_desc", "Slip between the spatial fabric of reality just like hopping a transit barrier. Teleport up to 18 meters as a Bonus Action, leaving behind a brief burst of confusing screeching.")

# Statuses - Class
h_status_stench_name = add_loca("status_stench_name", "Fecal Stench")
h_status_stench_desc = add_loca("status_stench_desc", "Overwhelmed by nauseating biological stench. Suffers Disadvantage on Attack Rolls and takes 1d4 Poison damage per turn.")

h_status_stupor_name = add_loca("status_stupor_name", "Fent Stupor")
h_status_stupor_desc = add_loca("status_stupor_desc", "Incapacitated and paralyzed in an unresponsive narcotic daze. Cannot move or take actions.")

h_status_lean_name = add_loca("status_lean_name", "Fent Lean")
h_status_lean_desc = add_loca("status_lean_desc", "Locked in supreme postural equilibrium. Resistant to all damage, +2 AC, Advantage on DEX and CON saves, but Movement Speed is 0.")

h_status_scramble_name = add_loca("status_scramble_name", "Sidewalk Scramble")
h_status_scramble_desc = add_loca("status_scramble_desc", "Movement speed increased by 3m. Immune to difficult terrain, grease, and surface slipping.")

h_status_panhandling_name = add_loca("status_panhandling_name", "Socially Shamed")
h_status_panhandling_desc = add_loca("status_panhandling_desc", "Deeply rattled by persistent street solicitation. Suffers Disadvantage on Attack Rolls.")

# Passives - Class
h_passive_immunity_name = add_loca("passive_immunity_name", "Sidewalk Immunity")
h_passive_immunity_desc = add_loca("passive_immunity_desc", "Years of dumpster exposure have forged an impenetrable immune system. Immune to Disease and Poisoned, and resistant to Poison damage.")

h_passive_lean_heal_name = add_loca("passive_lean_heal_name", "Restorative Stupor")
h_passive_lean_heal_desc = add_loca("passive_lean_heal_desc", "While locked in the Fent Lean, your slowed metabolic rate knits wounds back together, restoring 2d6 Hit Points at the start of every turn.")

h_passive_lean_reflect_name = add_loca("passive_lean_reflect_name", "Baffling Retaliation")
h_passive_lean_reflect_desc = add_loca("passive_lean_reflect_desc", "While in Fent Lean, melee attackers attempting to strike your bewildering posture strike bone-jarring equilibrium, suffering 1d10 Psychic damage.")

h_prop47_name = add_loca("prop47_name", "Proposition 47")
h_prop47_desc = add_loca("prop47_desc", "Petty theft under 950 gold is completely decriminalized. Whenever you strike an enemy with a melee attack, you snatch a Stolen Patagonia Vest (+1 AC, +1d4 damage) for 2 turns. Authorities will apologize for profiling you.")

h_status_patagonia_name = add_loca("status_patagonia_name", "Stolen Patagonia Vest")
h_status_patagonia_desc = add_loca("status_patagonia_desc", "Warm, fleece-lined, and acquired without prosecution. Grants +1 Armour Class and adds 1d4 Bludgeoning damage to weapon strikes.")

h_pocket_lint_name = add_loca("pocket_lint_name", "Pocket Lint Buffet")
h_pocket_lint_desc = add_loca("pocket_lint_desc", "Rummaging through the coats of foes marinating in your biological weaponry grants sustenance. Dealing damage to a creature afflicted with Fecal Stench restores 1d6 Temporary Hit Points.")

h_eviction_name = add_loca("eviction_name", "Eviction Notice")
h_eviction_desc = add_loca("eviction_desc", "Serve a foe with an immediate lease termination. The target must make a Wisdom Saving Throw or fall into crushing financial ruin with Rent Hike: losing -2 AC (cannot afford armor), -3m Movement, and taking 2d4 Psychic damage at the start of each turn from Bay Area cost of living.")

h_status_rent_hike_name = add_loca("status_rent_hike_name", "Rent Hike")
h_status_rent_hike_desc = add_loca("status_rent_hike_desc", "Crushed by runaway housing costs. Suffers -2 AC, -3m Movement, and takes 2d4 Psychic damage at the start of each turn.")

h_biohazard_aura_name = add_loca("biohazard_aura_name", "Tenderloin Biohazard Aura")
h_biohazard_aura_desc = add_loca("biohazard_aura_desc", "An unbearable 3-meter miasma radiating from your person. Enemies entering or starting their turn within range must make a Constitution save or contract Fecal Stench.")

h_encampment_sweep_name = add_loca("encampment_sweep_name", "Encampment Sweep Survival Instinct")
h_encampment_sweep_desc = add_loca("encampment_sweep_desc", "When the municipal cleanup crew drops you below 50% Hit Points, your body reflexively collapses into Fent Lean as an emergency damage-resistant bunker once per combat.")

h_sweep_cd_name = add_loca("sweep_cd_name", "Sweep Fatigue")
h_sweep_cd_desc = add_loca("sweep_cd_desc", "Your survival reflexes need time to reset.")

h_call311_name = add_loca("call311_name", "Call 311 (On Hold)")
h_call311_desc = add_loca("call311_desc", "Subject all enemies in a 9m radius to the agonizing purgatory of municipal hold music. Enemies lose their Reaction and Bonus Action, and have their movement halved for 3 turns.")

h_status_hold_music_name = add_loca("status_hold_music_name", "On Hold (311)")
h_status_hold_music_desc = add_loca("status_hold_music_desc", "Your call is important to us. Please continue to hold. Cannot take Bonus Actions or Reactions, and Movement Speed is halved.")

# -------------------------------------------------------------
# Localization Strings - Race & Subraces
# -------------------------------------------------------------
h_race_californian_name = add_loca("race_californian_name", "Californian")
h_race_californian_desc = add_loca("race_californian_desc", "Hailing from the Golden State, Californians possess an uncanny resilience shaped by natural disasters, gridlock traffic, and perpetual microclimates. Whether meditating on a Malibu beach or pitching a seed-stage venture in a coffee shop, they navigate Faerûn with effortless chill and passive aggression.")

h_subrace_beachborn_name = add_loca("subrace_beachborn_name", "Beachborn (SoCal)")
h_subrace_beachborn_desc = add_loca("subrace_beachborn_desc", "Sun-drenched coastal dwellers who surf metaphysical waves. Radiant resistance, supreme mobility, and the innate ability to 'Hang Ten' across treacherous surfaces.")

h_subrace_siliconite_name = add_loca("subrace_siliconite_name", "Siliconite (NorCal)")
h_subrace_siliconite_desc = add_loca("subrace_siliconite_desc", "Disruptive visionaries fortified by microdosed mushroom tea and quarterly pitch decks. Channels psychic energy to disrupt hostile thought patterns and optimize output.")

h_subrace_inland_name = add_loca("subrace_inland_name", "Inland Emperor (The Valley)")
h_subrace_inland_desc = add_loca("subrace_inland_desc", "Forged in extreme heatwaves, agricultural dust, and unending highway commutes. Virtually immune to toxic air, burning conditions, and high-temperature environments.")

# Identity & 3rd Gender Selector
h_prog_desc_identity_name = add_loca("prog_desc_identity_name", "California Identity & Gender Expression")
h_prog_desc_identity_desc = add_loca("prog_desc_identity_desc", "Select your spiritual California identity and pronoun archetype. Each comes with bespoke perks, cultural flair, and cosmic validation.")

h_id_dude_name = add_loca("id_dude_name", "Dude (Dude / Dude / Dudeself)")
h_id_dude_desc = add_loca("id_dude_desc", "A timeless, universal California vibration. You greet gods, goblins, and dragons alike as 'dude'. You gain +1 to Persuasion checks, and have Advantage on Saving Throws against intoxication, fear, and exhaustion.")

h_id_founder_name = add_loca("id_founder_name", "Founder (Founder / Disrupter / Unicorn)")
h_id_founder_desc = add_loca("id_founder_desc", "You operate in perpetual stealth mode. Treating every battle as a Series-A pitch, you gain +2 to Initiative and Advantage on Deception checks when bluffing.")

h_id_oat_name = add_loca("id_oat_name", "Oat (Oat / Almond / Lactose-Free)")
h_id_oat_desc = add_loca("id_oat_desc", "Completely organic, non-GMO, and free of inflammatory systemic toxins. You are completely immune to the Poisoned condition.")

h_id_self_name = add_loca("id_self_name", "Self-Actualized (Aura / High-Frequency / Elevated)")
h_id_self_desc = add_loca("id_self_desc", "Your chakras are aligned to the exact resonant frequency of Sedona crystals. At the start of combat, you automatically manifest 5 Temporary Hit Points.")

h_id_algo_name = add_loca("id_algo_name", "The Algorithm (Optimized / Scaled / Series-A)")
h_id_algo_desc = add_loca("id_algo_desc", "You have surrendered all bodily autonomy to predictive machine learning models. You gain a +1 bonus to all Saving Throws as incoming attacks are forecasted in real-time.")

# Racial Spells & Passives
h_touch_grass_name = add_loca("touch_grass_name", "Touch Grass")
h_touch_grass_desc = add_loca("touch_grass_desc", "Touch a foe and force them to disconnect from online discourse. Deals 1d8 Psychic damage, immediately terminates any active Rage, Frenzy, or Enraged condition, and inflicts Existential Daze (Disadvantage on Attack Rolls for 2 turns).")

h_avocado_toast_name = add_loca("avocado_toast_name", "Avocado Toast")
h_avocado_toast_desc = add_loca("avocado_toast_desc", "Nourish yourself with artisanal sourdough topped with mashed Hass avocado and flaky sea salt. Restores 1d6 + CON modifier Hit Points and grants 5 Temporary Hit Points.")

h_hang_ten_name = add_loca("hang_ten_name", "Hang Ten")
h_hang_ten_desc = add_loca("hang_ten_desc", "Catch the cosmic Pacific swell. Increases movement speed by 3m and grants immunity to difficult terrain and slipping on ice or grease for 2 turns.")

h_vibe_check_name = add_loca("vibe_check_name", "Vibe Check")
h_vibe_check_desc = add_loca("vibe_check_desc", "Subject a target's consciousness to a brutal seed-stage vibe check. Target must succeed a DC Wisdom saving throw or break concentration and suffer Existential Dread.")

h_earthquake_name = add_loca("earthquake_name", "Earthquake Sense")
h_earthquake_desc = add_loca("earthquake_desc", "Born on the San Andreas Fault, you possess impeccable footing. Advantage on Saving Throws against falling Prone or knockdowns.")

h_veteran405_name = add_loca("veteran405_name", "405 Commute Veteran")
h_veteran405_desc = add_loca("veteran405_desc", "Decades spent idling on the I-405 freeway have made you immune to gridlock. You cannot be Slowed or Restrained.")

h_smog_lungs_name = add_loca("smog_lungs_name", "Smog Lungs")
h_smog_lungs_desc = add_loca("smog_lungs_desc", "Central Valley dust and Los Angeles smog have turned your respiratory system into an industrial air filter. Advantage on saving throws against Poison and Disease.")

h_heat_index_name = add_loca("heat_index_name", "Heat Index Mastery")
h_heat_index_desc = add_loca("heat_index_desc", "Triple-digit Palm Springs heat is merely room temperature to you. Immune to Burning condition.")

h_synergy_name = add_loca("synergy_name", "Siliconite Synergy")
h_synergy_desc = add_loca("synergy_desc", "Cross-functional synergy allows you to optimize output. Once per turn, dealing weapon damage deals an additional 1d4 Psychic damage.")

h_status_daze_name = add_loca("status_daze_name", "Existential Daze")
h_status_daze_desc = add_loca("status_daze_desc", "Disconnected from rage by reality. Suffers Disadvantage on Attack Rolls.")

h_status_avocado_name = add_loca("status_avocado_name", "Avocado Bliss")
h_status_avocado_desc = add_loca("status_avocado_desc", "Fortified by artisanal healthy fats. Grants Temporary Hit Points.")

h_status_hangten_name = add_loca("status_hangten_name", "Hang Ten")
h_status_hangten_desc = add_loca("status_hangten_desc", "Surfing metaphysical waves. +3m Movement Speed and immune to slipping or difficult terrain.")

h_status_vibe_name = add_loca("status_vibe_name", "Vibe Checked")
h_status_vibe_desc = add_loca("status_vibe_desc", "Concentration broken and mind disrupted by venture capital reality.")


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
                    <attribute id="Description" type="LSString" value="Introduces the Homeless Californian class and Californian race to Baldur's Gate 3."/>
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
# 4. Generate Lists/SpellLists.lsx, SkillLists.lsx, PassiveLists.lsx
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
                <!-- Class Level 1: Poop, Fentanyl, Fent Lean, Scramble -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_SlingPoop;Projectile_SlingFentanyl;Shout_FentLean;Shout_FentLean_End;Shout_SidewalkScramble"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL1}"/>
                </node>

                <!-- Class Level 2: Aggressive Panhandling -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_AggressivePanhandling"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL2}"/>
                </node>

                <!-- Class Level 4: Eviction Notice (Rent Hike) -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Target_EvictionNotice"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL4}"/>
                </node>

                <!-- Class Level 5: Chunky Poop upgrade -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_SlingPoop_Chunky"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL5}"/>
                </node>

                <!-- Class Level 7: Feral Screech -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_FeralScreech"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL7}"/>
                </node>

                <!-- Class Level 9: Mass Fentanyl Cloud & Tent Encampment -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Projectile_SlingFentanyl_Mass;Shout_TentEncampment"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL9}"/>
                </node>

                <!-- Class Level 12: Call 311 (On Hold) -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_Call311"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_LVL12}"/>
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

                <!-- Racial Californian Spells: Touch Grass & Avocado Toast -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Target_TouchGrass;Shout_AvocadoToast"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_CALIFORNIAN_L1}"/>
                </node>

                <!-- Racial Beachborn Spells: Hang Ten -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Shout_HangTen"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_BEACHBORN_L1}"/>
                </node>

                <!-- Racial Siliconite Spells: Vibe Check -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Target_VibeCheck"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_SILICONITE_L1}"/>
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
                    <attribute id="Skills" type="LSString" value="Athletics,Acrobatics,SleightOfHand,Stealth,Survival,Intimidation,Deception"/>
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

    # PassiveLists.lsx
    passive_path = os.path.join(PUBLIC_DIR, "Lists", "PassiveLists.lsx")
    passive_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="PassiveLists">
        <node id="root">
            <children>
                <node id="PassiveList">
                    <attribute id="Name" type="FixedString" value="California Identity and Gender Expression"/>
                    <attribute id="Passives" type="LSString" value="CaliforniaIdentity_Dude,CaliforniaIdentity_Founder,CaliforniaIdentity_Oat,CaliforniaIdentity_SelfActualized,CaliforniaIdentity_Algorithm"/>
                    <attribute id="UUID" type="guid" value="{PASSIVELIST_CALIFORNIA_IDENTITY}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(passive_path, "w", encoding="utf-8") as f:
        f.write(passive_content)
    print(f"Generated: {passive_path}")


# -------------------------------------------------------------
# 5. Generate Progressions/Progressions.lsx & ProgressionDescriptions.lsx
# -------------------------------------------------------------
def generate_progressions_lsx():
    path = os.path.join(PUBLIC_DIR, "Progressions", "Progressions.lsx")
    ensure_dir(os.path.dirname(path))

    nodes = []

    # --- CLASS PROGRESSIONS (Type 0) ---
    # Level 1
    u_l1 = get_guid("Prog_Homeless_Lvl1")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="false"/>
                    <attribute id="Boosts" type="ls::Guid" value="ProficiencyBonus(SavingThrow,Constitution);ProficiencyBonus(SavingThrow,Dexterity);Proficiency(LightArmor);Proficiency(MediumArmor);Proficiency(Shields);Proficiency(SimpleWeapons);Proficiency(MartialWeapons)"/>
                    <attribute id="Level" type="uint8" value="1"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="SidewalkImmunity;Proposition47"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="SelectSkills({SKILLLIST_UUID},2);AddSpells({SPELLLIST_LVL1})"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l1}"/>
                </node>""")

    # Level 2
    u_l2 = get_guid("Prog_Homeless_Lvl2")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="2"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="PocketLintBuffet"/>
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

    # Level 4 (Feat + Eviction Notice)
    u_l4 = get_guid("Prog_Homeless_Lvl4")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="true"/>
                    <attribute id="Level" type="uint8" value="4"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL4})"/>
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

    # Level 10 (Encampment Sweep Instinct)
    u_l10 = get_guid("Prog_Homeless_Lvl10")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="10"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="PassivesAdded" type="LSString" value="EncampmentSweepInstinct"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l10}"/>
                </node>""")

    # Level 11 (Retaliation Lean)
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

    # Level 12 (Feat + Call 311)
    u_l12 = get_guid("Prog_Homeless_Lvl12")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="true"/>
                    <attribute id="Level" type="uint8" value="12"/>
                    <attribute id="Name" type="LSString" value="HomelessCalifornian"/>
                    <attribute id="ProgressionType" type="uint8" value="0"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_LVL12})"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_l12}"/>
                </node>""")

    # Subclass Progressions (Type 1)
    u_tend_l3 = get_guid("Prog_Tenderloin_L3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="TenderloinBiohazard"/>
                    <attribute id="PassivesAdded" type="LSString" value="BiohazardStench"/>
                    <attribute id="ProgressionType" type="uint8" value="1"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_TENDERLOIN_L3})"/>
                    <attribute id="TableUUID" type="guid" value="{SUBCLASS_TENDERLOIN_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_tend_l3}"/>
                </node>""")

    u_ven_l3 = get_guid("Prog_Venice_L3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="VeniceBoardwalkBrawler"/>
                    <attribute id="PassivesAdded" type="LSString" value="UnarmoredDefense_Barbarian"/>
                    <attribute id="ProgressionType" type="uint8" value="1"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_VENICE_L3})"/>
                    <attribute id="TableUUID" type="guid" value="{SUBCLASS_VENICE_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_ven_l3}"/>
                </node>""")

    u_bart_l3 = get_guid("Prog_BART_L3")
    nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="3"/>
                    <attribute id="Name" type="LSString" value="BARTPlatformMenace"/>
                    <attribute id="PassivesAdded" type="LSString" value="ReliableTalent"/>
                    <attribute id="ProgressionType" type="uint8" value="1"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_BART_L3})"/>
                    <attribute id="TableUUID" type="guid" value="{SUBCLASS_BART_TABLE_UUID}"/>
                    <attribute id="UUID" type="guid" value="{u_bart_l3}"/>
                </node>""")

    # --- RACIAL PROGRESSIONS (Type 2) ---
    # Californian Base Race Progression (Levels 1 - 12)
    for lvl in range(1, 13):
        u_race = get_guid(f"Prog_Californian_Lvl{lvl}")
        if lvl == 1:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="false"/>
                    <attribute id="Boosts" type="ls::Guid" value="ActionResource(Movement,9,0);Resistance(Fire,Resistant)"/>
                    <attribute id="Level" type="uint8" value="1"/>
                    <attribute id="Name" type="LSString" value="Californian"/>
                    <attribute id="PassivesAdded" type="LSString" value="EarthquakeSense;Veteran405"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="Selectors" type="LSString" value="SelectPassives({PASSIVELIST_CALIFORNIA_IDENTITY},1,CaliforniaIdentity);AddSpells({SPELLLIST_CALIFORNIAN_L1},,Charisma,,AlwaysPrepared)"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_CALIFORNIAN}"/>
                    <attribute id="UUID" type="guid" value="{u_race}"/>
                </node>""")
        else:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="{lvl}"/>
                    <attribute id="Name" type="LSString" value="Californian"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_CALIFORNIAN}"/>
                    <attribute id="UUID" type="guid" value="{u_race}"/>
                </node>""")

    # Beachborn Subrace Progression (Levels 1 - 12)
    for lvl in range(1, 13):
        u_beach = get_guid(f"Prog_Beachborn_Lvl{lvl}")
        if lvl == 1:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Boosts" type="ls::Guid" value="Resistance(Radiant,Resistant)"/>
                    <attribute id="Level" type="uint8" value="1"/>
                    <attribute id="Name" type="LSString" value="Beachborn"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_BEACHBORN_L1},,Charisma,,AlwaysPrepared)"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_BEACHBORN}"/>
                    <attribute id="UUID" type="guid" value="{u_beach}"/>
                </node>""")
        else:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="{lvl}"/>
                    <attribute id="Name" type="LSString" value="Beachborn"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_BEACHBORN}"/>
                    <attribute id="UUID" type="guid" value="{u_beach}"/>
                </node>""")

    # Siliconite Subrace Progression (Levels 1 - 12)
    for lvl in range(1, 13):
        u_silicon = get_guid(f"Prog_Siliconite_Lvl{lvl}")
        if lvl == 1:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="1"/>
                    <attribute id="Name" type="LSString" value="Siliconite"/>
                    <attribute id="PassivesAdded" type="LSString" value="Passive_SiliconiteSynergy"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="Selectors" type="LSString" value="AddSpells({SPELLLIST_SILICONITE_L1},,Charisma,,AlwaysPrepared)"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_SILICONITE}"/>
                    <attribute id="UUID" type="guid" value="{u_silicon}"/>
                </node>""")
        else:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="{lvl}"/>
                    <attribute id="Name" type="LSString" value="Siliconite"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_SILICONITE}"/>
                    <attribute id="UUID" type="guid" value="{u_silicon}"/>
                </node>""")

    # Inland Emperor Subrace Progression (Levels 1 - 12)
    for lvl in range(1, 13):
        u_inland = get_guid(f"Prog_InlandEmperor_Lvl{lvl}")
        if lvl == 1:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Boosts" type="ls::Guid" value="Resistance(Poison,Resistant);Advantage(SavingThrow,Poison)"/>
                    <attribute id="Level" type="uint8" value="1"/>
                    <attribute id="Name" type="LSString" value="InlandEmperor"/>
                    <attribute id="PassivesAdded" type="LSString" value="Passive_SmogLungs;Passive_HeatIndexMastery"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_INLANDEMPEROR}"/>
                    <attribute id="UUID" type="guid" value="{u_inland}"/>
                </node>""")
        else:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="Level" type="uint8" value="{lvl}"/>
                    <attribute id="Name" type="LSString" value="InlandEmperor"/>
                    <attribute id="ProgressionType" type="uint8" value="2"/>
                    <attribute id="TableUUID" type="guid" value="{PROG_TABLE_RACE_INLANDEMPEROR}"/>
                    <attribute id="UUID" type="guid" value="{u_inland}"/>
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

    # ProgressionDescriptions.lsx
    pdesc_path = os.path.join(PUBLIC_DIR, "Progressions", "ProgressionDescriptions.lsx")
    pdesc_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="ProgressionDescriptions">
        <node id="root">
            <children>
                <node id="ProgressionDescription">
                    <attribute id="Description" type="TranslatedString" handle="{h_prog_desc_identity_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_prog_desc_identity_name}" version="1"/>
                    <attribute id="SelectorId" type="FixedString" value="CaliforniaIdentity"/>
                    <attribute id="UUID" type="guid" value="{PROG_DESC_CALIFORNIA_IDENTITY}"/>
                </node>
            </children>
        </node>
    </region>
</save>
"""
    with open(pdesc_path, "w", encoding="utf-8") as f:
        f.write(pdesc_content)
    print(f"Generated: {pdesc_path}")


# -------------------------------------------------------------
# 6. Generate Character Creation Presets & Default Values
# -------------------------------------------------------------
def generate_presets_lsx():
    # AbilityDistributionPresets.lsx
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
# 7. Generate Races/Races.lsx
# -------------------------------------------------------------
def generate_races_lsx():
    path = os.path.join(PUBLIC_DIR, "Races", "Races.lsx")
    ensure_dir(os.path.dirname(path))

    # Read extracted human children
    human_children_path = os.path.join(ASSETS_DIR, "human_race_children.xml")
    human_children_xml = ""
    if os.path.exists(human_children_path):
        with open(human_children_path, "r", encoding="utf-8") as f:
            human_children_xml = f.read()

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="Races">
        <node id="root">
            <children>
                <!-- Main Race: Californian -->
                <node id="Race">
                    <attribute id="Description" type="TranslatedString" handle="{h_race_californian_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_race_californian_name}" version="1"/>
                    <attribute id="DisplayTypeUUID" type="guid" value="899d275e-9893-490a-9cd5-be856794929f"/>
                    <attribute id="Name" type="FixedString" value="Californian"/>
                    <attribute id="ParentGuid" type="guid" value="899d275e-9893-490a-9cd5-be856794929f"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{PROG_TABLE_RACE_CALIFORNIAN}"/>
                    <attribute id="RaceEquipment" type="FixedString" value="EQ_Underwear_Humans"/>
                    <attribute id="RaceSoundSwitch" type="FixedString" value="Human"/>
                    <attribute id="UUID" type="guid" value="{RACE_CALIFORNIAN_UUID}"/>
                    {human_children_xml}
                </node>

                <!-- Subrace: Beachborn (SoCal) -->
                <node id="Race">
                    <attribute id="Description" type="TranslatedString" handle="{h_subrace_beachborn_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_subrace_beachborn_name}" version="1"/>
                    <attribute id="DisplayTypeUUID" type="guid" value="899d275e-9893-490a-9cd5-be856794929f"/>
                    <attribute id="Name" type="FixedString" value="Californian_Beachborn"/>
                    <attribute id="ParentGuid" type="guid" value="{RACE_CALIFORNIAN_UUID}"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{PROG_TABLE_RACE_BEACHBORN}"/>
                    <attribute id="RaceEquipment" type="FixedString" value="EQ_Underwear_Humans"/>
                    <attribute id="RaceSoundSwitch" type="FixedString" value="Human"/>
                    <attribute id="UUID" type="guid" value="{RACE_BEACHBORN_UUID}"/>
                    {human_children_xml}
                </node>

                <!-- Subrace: Siliconite (NorCal) -->
                <node id="Race">
                    <attribute id="Description" type="TranslatedString" handle="{h_subrace_siliconite_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_subrace_siliconite_name}" version="1"/>
                    <attribute id="DisplayTypeUUID" type="guid" value="899d275e-9893-490a-9cd5-be856794929f"/>
                    <attribute id="Name" type="FixedString" value="Californian_Siliconite"/>
                    <attribute id="ParentGuid" type="guid" value="{RACE_CALIFORNIAN_UUID}"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{PROG_TABLE_RACE_SILICONITE}"/>
                    <attribute id="RaceEquipment" type="FixedString" value="EQ_Underwear_Humans"/>
                    <attribute id="RaceSoundSwitch" type="FixedString" value="Human"/>
                    <attribute id="UUID" type="guid" value="{RACE_SILICONITE_UUID}"/>
                    {human_children_xml}
                </node>

                <!-- Subrace: Inland Emperor (The Valley) -->
                <node id="Race">
                    <attribute id="Description" type="TranslatedString" handle="{h_subrace_inland_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_subrace_inland_name}" version="1"/>
                    <attribute id="DisplayTypeUUID" type="guid" value="899d275e-9893-490a-9cd5-be856794929f"/>
                    <attribute id="Name" type="FixedString" value="Californian_InlandEmperor"/>
                    <attribute id="ParentGuid" type="guid" value="{RACE_CALIFORNIAN_UUID}"/>
                    <attribute id="ProgressionTableUUID" type="guid" value="{PROG_TABLE_RACE_INLANDEMPEROR}"/>
                    <attribute id="RaceEquipment" type="FixedString" value="EQ_Underwear_Humans"/>
                    <attribute id="RaceSoundSwitch" type="FixedString" value="Human"/>
                    <attribute id="UUID" type="guid" value="{RACE_INLANDEMPEROR_UUID}"/>
                    {human_children_xml}
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
# 8. Generate Character Creation Appearance Visuals
# -------------------------------------------------------------
def generate_cc_appearance_visuals_lsx():
    path = os.path.join(PUBLIC_DIR, "CharacterCreation", "CharacterCreationAppearanceVisuals.lsx")
    ensure_dir(os.path.dirname(path))

    visuals_asset = os.path.join(ASSETS_DIR, "human_cc_appearance_visuals.xml")
    tree = ET.parse(visuals_asset)
    nodes = []

    for node in tree.getroot():
        if node.tag == "node" or node.attrib.get("id") == "CharacterCreationAppearanceVisual":
            # Clone and rewrite RaceUUID & UUID
            new_node = ET.fromstring(ET.tostring(node, encoding="utf-8"))
            old_uuid = ""
            for attr in new_node.findall("attribute"):
                aid = attr.attrib.get("id")
                if aid == "UUID":
                    old_uuid = attr.attrib.get("value")
                    attr.set("value", get_guid(f"CC_Vis_{old_uuid}"))
                elif aid == "RaceUUID":
                    attr.set("value", RACE_CALIFORNIAN_UUID)
            nodes.append(ET.tostring(new_node, encoding="unicode"))

    joined = "\n".join(nodes)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="CharacterCreationAppearanceVisuals">
        <node id="root">
            <children>
{joined}
            </children>
        </node>
    </region>
</save>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")


# -------------------------------------------------------------
# 9. Generate CharacterCreationPresets.lsx
# -------------------------------------------------------------
def generate_cc_presets_lsx():
    path = os.path.join(PUBLIC_DIR, "CharacterCreationPresets", "CharacterCreationPresets.lsx")
    ensure_dir(os.path.dirname(path))

    # 4 Human player body setups
    body_configs = [
        {"shape": "0", "btype": "0", "root": "80d0ef19-f11e-482f-96ab-f184a9460b8e", "ov": "HUM_M_Camera_Overview_A", "ca": "HUM_M_Camera_Closeup_A", "cb": "HUM_M_Camera_Closeup_B"},
        {"shape": "1", "btype": "0", "root": "056fffd0-9009-4627-84c2-f0a22e311ec7", "ov": "HUM_MB_Camera_Overview_A", "ca": "HUM_MB_Camera_Closeup_A", "cb": "HUM_MB_Camera_Closeup_B"},
        {"shape": "0", "btype": "1", "root": "e3c07ecd-d3f7-4661-b029-18dee1f3114e", "ov": "HUM_F_Camera_Overview_A", "ca": "HUM_F_Camera_Closeup_A", "cb": "HUM_F_Camera_Closeup_B"},
        {"shape": "1", "btype": "1", "root": "3303e8f6-a7e4-4b24-b64c-d64bbc152803", "ov": "HUM_FB_Camera_Overview_A", "ca": "HUM_FB_Camera_Closeup_A", "cb": "HUM_FB_Camera_Closeup_B"},
    ]

    races = [
        ("Base", "00000000-0000-0000-0000-000000000000"),
        ("Beachborn", RACE_BEACHBORN_UUID),
        ("Siliconite", RACE_SILICONITE_UUID),
        ("InlandEmperor", RACE_INLANDEMPEROR_UUID)
    ]

    nodes = []
    for rname, sub_uuid in races:
        for cfg in body_configs:
            u_preset = get_guid(f"CC_Preset_{rname}_{cfg['shape']}_{cfg['btype']}")
            nodes.append(f"""
                <node id="CharacterCreationPreset">
                    <attribute id="BodyShape" type="uint8" value="{cfg['shape']}"/>
                    <attribute id="BodyType" type="uint8" value="{cfg['btype']}"/>
                    <attribute id="CloseUpA" type="FixedString" value="{cfg['ca']}"/>
                    <attribute id="CloseUpB" type="FixedString" value="{cfg['cb']}"/>
                    <attribute id="Overview" type="FixedString" value="{cfg['ov']}"/>
                    <attribute id="RaceUUID" type="guid" value="{RACE_CALIFORNIAN_UUID}"/>
                    <attribute id="RootTemplate" type="guid" value="{cfg['root']}"/>
                    <attribute id="SubRaceUUID" type="guid" value="{sub_uuid}"/>
                    <attribute id="UUID" type="guid" value="{u_preset}"/>
                    <attribute id="VOLinesTableUUID" type="guid" value="14df8f45-90af-4bd0-8024-42624da9976e"/>
                </node>""")

    joined = "".join(nodes)
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<save>
    <version major="4" minor="8" revision="0" build="10"/>
    <region id="CharacterCreationPresets">
        <node id="root">
            <children>{joined}
            </children>
        </node>
    </region>
</save>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {path}")


# -------------------------------------------------------------
# 10. Generate Stats/Generated/Data TXT files
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
data "Icon" "Spell_SlingPoop"
data "DisplayName" "{h_sling_poop_name};1"
data "Description" "{h_sling_poop_desc};1"
data "TooltipDamageList" "DealDamage(1d6+CON,Bludgeoning);DealDamage(1d4,Poison)"
data "TooltipAttackSave" "RangedSpellAttack"
data "CastSound" "Spell_Cast_Damage_Acid_ChromaticOrbAcid_L1to3"
data "TargetSound" "Spell_Impact_Damage_Acid_ChromaticOrbAcid_L1to3"
data "VocalComponentSound" "Vocal_Component_Disadvantage"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Damage"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
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
data "Icon" "Spell_SlingPoop"
data "DisplayName" "{h_sling_poop_chunky_name};1"
data "Description" "{h_sling_poop_chunky_desc};1"
data "TooltipDamageList" "DealDamage(2d6+CON,Bludgeoning);DealDamage(2d4,Poison)"
data "TooltipAttackSave" "RangedSpellAttack"
data "CastSound" "Spell_Cast_Damage_Acid_ChromaticOrbAcid_L1to3"
data "TargetSound" "Spell_Impact_Damage_Acid_ChromaticOrbAcid_L1to3"
data "VocalComponentSound" "Vocal_Component_Disadvantage"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Damage"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
data "DamageType" "Bludgeoning"

new entry "Projectile_SlingFentanyl"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "SpellProperties" "GROUND:CreateSurface(1.5,,SurfacePoison);ApplyStatus(FENT_STUPOR,100,1)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(1d4,Psychic);ApplyStatus(FENT_STUPOR,100,1)"
data "SpellFail" "DealDamage(1d4,Psychic)"
data "TargetConditions" "Character() and not Dead()"
data "ProjectileCount" "1"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_SlingFentanyl"
data "DisplayName" "{h_sling_fent_name};1"
data "Description" "{h_sling_fent_desc};1"
data "TooltipDamageList" "DealDamage(1d4,Psychic)"
data "TooltipAttackSave" "Constitution"
data "CastSound" "Spell_Cast_Control_Blindness_L1to3"
data "TargetSound" "Spell_Impact_Control_Blindness_L1to3"
data "VocalComponentSound" "Vocal_Component_Enchantment"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
data "DamageType" "Psychic"

new entry "Projectile_SlingFentanyl_Mass"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "5"
data "SpellSchool" "Enchantment"
data "SpellProperties" "GROUND:CreateSurface(4.0,,SurfacePoison);ApplyStatus(FENT_STUPOR,100,2)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(3d6,Psychic);ApplyStatus(FENT_STUPOR,100,2)"
data "SpellFail" "DealDamage(3d6/2,Psychic)"
data "TargetConditions" "Character() and not Dead()"
data "ProjectileCount" "1"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_SlingFentanyl"
data "DisplayName" "{h_sling_fent_cloud_name};1"
data "Description" "{h_sling_fent_cloud_desc};1"
data "TooltipDamageList" "DealDamage(3d6,Psychic)"
data "TooltipAttackSave" "Constitution"
data "CastSound" "Spell_Cast_Control_Blindness_L1to3"
data "TargetSound" "Spell_Impact_Control_Blindness_L1to3"
data "VocalComponentSound" "Vocal_Component_Enchantment"
data "PreviewCursor" "Cast"
data "CastTextEvent" "Cast"
data "CycleConditions" "Enemy() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold;IsHarmful"
data "DamageType" "Psychic"

new entry "Projectile_BiohazardBomb"
type "SpellData"
data "SpellType" "Projectile"
data "Level" "3"
data "SpellSchool" "Evocation"
data "SpellProperties" "GROUND:CreateSurface(5.0,,SurfacePoison);ApplyStatus(FECAL_STENCH,100,3)"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Dexterity, SourceSpellDC())"
data "SpellSuccess" "DealDamage(4d6,Poison);DealDamage(2d6,Acid)"
data "SpellFail" "DealDamage(2d6,Poison);DealDamage(1d6,Acid)"
data "TargetConditions" "not Dead()"
data "Trajectories" "792ba497-a6ea-46bc-81cb-deb78e4dd9d3"
data "Icon" "Spell_SlingPoop"
data "DisplayName" "{h_biohazard_bomb_name};1"
data "Description" "{h_biohazard_bomb_desc};1"
data "TooltipDamageList" "DealDamage(4d6,Poison);DealDamage(2d6,Acid)"
data "TooltipAttackSave" "Dexterity"
data "CastSound" "Spell_Cast_Damage_Acid_ChromaticOrbAcid_L1to3"
data "TargetSound" "Spell_Impact_Damage_Acid_ChromaticOrbAcid_L1to3"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"
"""
    with open(os.path.join(stats_dir, "Spell_Projectile.txt"), "w", encoding="utf-8") as f:
        f.write(proj_content)

    # Spell_Shout.txt
    shout_content = f"""new entry "Shout_FentLean"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "SpellProperties" "ApplyStatus(FENT_LEAN,100,-1)"
data "TargetConditions" "Self()"
data "Icon" "Spell_FentLean"
data "DisplayName" "{h_fent_lean_name};1"
data "Description" "{h_fent_lean_desc};1"
data "CastSound" "Spell_Cast_Buff_Stoneskin_L4to6"
data "TargetSound" "Spell_Impact_Buff_Stoneskin_L4to6"
data "VocalComponentSound" "Vocal_Component_Buff"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "d0f854a2-113e-43bd-9d41-eeef34b12c8a,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "VerbalIntent" "Buff"
data "SpellFlags" "HasSomaticComponent;IsSpell"

new entry "Shout_FentLean_End"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "SpellProperties" "RemoveStatus(FENT_LEAN)"
data "TargetConditions" "Self()"
data "Icon" "Spell_SnapOutLean"
data "DisplayName" "{h_snap_out_name};1"
data "Description" "{h_snap_out_desc};1"
data "CastSound" "Spell_Impact_BodyFall_Stone"
data "TargetSound" "Spell_Impact_BodyFall_Stone"
data "SpellAnimation" "d0f854a2-113e-43bd-9d41-eeef34b12c8a,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "VerbalIntent" "Buff"
data "SpellFlags" "IsSpell"

new entry "Shout_SidewalkScramble"
type "SpellData"
data "SpellType" "Shout"
using "Shout_Dash_BonusAction"
data "SpellProperties" "ApplyStatus(SIDEWALK_SCRAMBLE,100,2);IF(HasStatus('DASH_STACKED')):ApplyStatus(DASH_STACKED_2,100,1);IF(not HasStatus('DASH_STACKED_2') and HasStatus('DASH')):ApplyStatus(DASH_STACKED,100,1);IF(not HasStatus('DASH_STACKED_2') and not HasStatus('DASH_STACKED') and not HasStatus('DASH')):ApplyStatus(DASH,100,1)"
data "TargetConditions" "Self()"
data "UseCosts" "BonusActionPoint:1"
data "Icon" "Spell_SnapOutLean"
data "DisplayName" "{h_scramble_name};1"
data "Description" "{h_scramble_desc};1"
data "CastSound" "Action_Sprint"
data "TargetSound" "Action_Sprint"

new entry "Shout_AggressivePanhandling"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "AreaRadius" "6"
data "SpellRoll" "SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "ApplyStatus(PANHANDLING_SHAME,100,2);DropGold(2d6)"
data "SpellFail" "ApplyStatus(PANHANDLING_SHAME,100,1)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Panhandling"
data "DisplayName" "{h_panhandling_name};1"
data "Description" "{h_panhandling_desc};1"
data "CastSound" "Spell_Cast_Control_DissonantWhispers_L1to3"
data "TargetSound" "Spell_Impact_Control_DissonantWhispers_L1to3"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"

new entry "Shout_FeralScreech"
type "SpellData"
data "SpellType" "Shout"
data "Level" "3"
data "SpellSchool" "Evocation"
data "AreaRadius" "9"
data "SpellRoll" "SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "DealDamage(3d6,Thunder);ApplyStatus(FEARED,100,2)"
data "SpellFail" "DealDamage(3d6/2,Thunder)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Panhandling"
data "DisplayName" "{h_screech_name};1"
data "Description" "{h_screech_desc};1"
data "TooltipDamageList" "DealDamage(3d6,Thunder)"
data "CastSound" "Spell_Cast_Damage_Thunder_Thunderwave_L1to3"
data "TargetSound" "Spell_Impact_Damage_Thunder_Thunderwave_L1to3"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"

new entry "Shout_TentEncampment"
type "SpellData"
data "SpellType" "Shout"
data "Level" "4"
data "SpellSchool" "Abjuration"
data "AreaRadius" "5"
data "SpellProperties" "ApplyStatus(BLADE_WARD,100,3);ApplyStatus(SANCTUARY,100,1)"
data "TargetConditions" "Ally() and not Dead()"
data "Icon" "Spell_FentLean"
data "DisplayName" "{h_tent_encampment_name};1"
data "Description" "{h_tent_encampment_desc};1"
data "CastSound" "Spell_Cast_Buff_Stoneskin_L4to6"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "d0f854a2-113e-43bd-9d41-eeef34b12c8a,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;IsSpell"

new entry "Shout_ShoppingCartCharge"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "AreaRadius" "9"
data "SpellSuccess" "DealDamage(3d6,Bludgeoning);ApplyStatus(PRONE,100,1)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_SnapOutLean"
data "DisplayName" "{h_cart_charge_name};1"
data "Description" "{h_cart_charge_desc};1"
data "UseCosts" "ActionPoint:1;BonusActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;IsSpell;IsHarmful"

new entry "Shout_TurnstileHop"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Conjuration"
data "TargetConditions" "Self()"
data "Icon" "Spell_SnapOutLean"
data "DisplayName" "{h_turnstile_hop_name};1"
data "Description" "{h_turnstile_hop_desc};1"
data "UseCosts" "BonusActionPoint:1"
data "SpellProperties" "Teleport(18)"
data "SpellAnimation" "d0f854a2-113e-43bd-9d41-eeef34b12c8a,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;IsSpell"

new entry "Shout_Call311"
type "SpellData"
data "SpellType" "Shout"
data "Level" "5"
data "SpellSchool" "Enchantment"
data "AreaRadius" "9"
data "SpellProperties" "ApplyStatus(HOLD_MUSIC_311,100,3)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Panhandling"
data "DisplayName" "{h_call311_name};1"
data "Description" "{h_call311_desc};1"
data "CastSound" "Spell_Cast_Control_Silence_L1to3"
data "TargetSound" "Spell_Impact_Control_Silence_L1to3"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"

# Racial Shouts
new entry "Shout_AvocadoToast"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Evocation"
data "SpellProperties" "RegainHitPoints(1d6+CON);ApplyStatus(AVOCADO_BLISS,100,3)"
data "TargetConditions" "Self()"
data "Icon" "Spell_AvocadoToast"
data "DisplayName" "{h_avocado_toast_name};1"
data "Description" "{h_avocado_toast_desc};1"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "d0f854a2-113e-43bd-9d41-eeef34b12c8a,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "VerbalIntent" "Buff"
data "SpellFlags" "HasSomaticComponent;IsSpell"

new entry "Shout_HangTen"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "SpellProperties" "ApplyStatus(HANG_TEN,100,2)"
data "TargetConditions" "Self()"
data "Icon" "Spell_Transmutation_Longstrider"
data "DisplayName" "{h_hang_ten_name};1"
data "Description" "{h_hang_ten_desc};1"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "d0f854a2-113e-43bd-9d41-eeef34b12c8a,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "VerbalIntent" "Buff"
data "SpellFlags" "HasSomaticComponent;IsSpell"
"""
    with open(os.path.join(stats_dir, "Spell_Shout.txt"), "w", encoding="utf-8") as f:
        f.write(shout_content)

    # Spell_Target.txt
    target_content = f"""new entry "Target_BrokenBottleShank"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "TargetFloor" "-1"
data "TargetRadius" "2"
data "SpellRoll" "Attack(AttackType.MeleeWeaponAttack)"
data "SpellSuccess" "DealDamage(2d4+STR,Piercing);DealDamage(1d6,Slashing);ApplyStatus(BLEEDING,100,2)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_SnapOutLean"
data "DisplayName" "{h_bottle_shank_name};1"
data "Description" "{h_bottle_shank_desc};1"
data "TooltipDamageList" "DealDamage(2d4+STR,Piercing);DealDamage(1d6,Slashing)"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "7a372138-b0a1-432d-9442-83b631f41756,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;IsSpell;IsHarmful"

new entry "Target_EvictionNotice"
type "SpellData"
data "SpellType" "Target"
data "Level" "2"
data "SpellSchool" "Enchantment"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "ApplyStatus(RENT_HIKE,100,3)"
data "TargetConditions" "Enemy() and not Dead()"
data "Icon" "Spell_Panhandling"
data "DisplayName" "{h_eviction_name};1"
data "Description" "{h_eviction_desc};1"
data "CastSound" "Spell_Cast_Control_CrownOfMadness_L1to3"
data "TargetSound" "Spell_Impact_Control_CrownOfMadness_L1to3"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"

# Racial Targets
new entry "Target_TouchGrass"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "TargetFloor" "-1"
data "TargetRadius" "2"
data "SpellRoll" "Attack(AttackType.MeleeSpellAttack)"
data "SpellSuccess" "DealDamage(1d8,Psychic);RemoveStatus(RAGE);RemoveStatus(FRENZY);RemoveStatus(BARBARIAN_RAGE);ApplyStatus(EXISTENTIAL_DAZE,100,2)"
data "TargetConditions" "Character() and not Dead()"
data "Icon" "Spell_Enchantment_CalmEmotions"
data "DisplayName" "{h_touch_grass_name};1"
data "Description" "{h_touch_grass_desc};1"
data "TooltipDamageList" "DealDamage(1d8,Psychic)"
data "CastSound" "Spell_Cast_Buff_Bless_L1to3"
data "TargetSound" "Spell_Impact_Buff_Bless_L1to3"
data "VocalComponentSound" "Vocal_Component_Disadvantage"
data "PreviewCursor" "Melee"
data "CastTextEvent" "Cast"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "7a372138-b0a1-432d-9442-83b631f41756,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"

new entry "Target_VibeCheck"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "TargetFloor" "-1"
data "TargetRadius" "18"
data "SpellRoll" "SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "BreakConcentration();ApplyStatus(VIBE_CHECKED,100,1)"
data "TargetConditions" "Character() and not Dead()"
data "Icon" "Spell_Enchantment_TashasHideousLaughter"
data "DisplayName" "{h_vibe_check_name};1"
data "Description" "{h_vibe_check_desc};1"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;,,;,,;,,;,,;,,;,,;,,"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"
"""
    with open(os.path.join(stats_dir, "Spell_Target.txt"), "w", encoding="utf-8") as f:
        f.write(target_content)

    # Status_BOOST.txt
    status_content = f"""new entry "FECAL_STENCH"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_stench_name};1"
data "Description" "{h_status_stench_desc};1"
data "Icon" "Spell_SlingPoop"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "Disadvantage(AttackRoll)"
data "TickFunctors" "DealDamage(1d4,Poison)"

new entry "FENT_STUPOR"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_stupor_name};1"
data "Description" "{h_status_stupor_desc};1"
data "Icon" "Spell_SlingFentanyl"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "BlockRegainBonusAction();BlockRegainReaction();ActionResourceMultiplier(Movement,0,0)"

new entry "FENT_LEAN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_lean_name};1"
data "Description" "{h_status_lean_desc};1"
data "Icon" "Spell_FentLean"
data "FormatColor" "Purple"
data "StackType" "Overwrite"
data "Boosts" "AC(2);Resistance(All, Resistant);Advantage(SavingThrow, Constitution);Advantage(SavingThrow, Dexterity);ActionResourceMultiplier(Movement,0,0)"

new entry "SIDEWALK_SCRAMBLE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_scramble_name};1"
data "Description" "{h_status_scramble_desc};1"
data "Icon" "Spell_SnapOutLean"
data "FormatColor" "Green"
data "StackType" "Overwrite"
data "Boosts" "ActionResource(Movement,3,0);StatusImmunity(PRONE);StatusImmunity(SG_DifficultTerrain)"

new entry "PANHANDLING_SHAME"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_panhandling_name};1"
data "Description" "{h_status_panhandling_desc};1"
data "Icon" "Spell_Panhandling"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "Disadvantage(AttackRoll)"

new entry "STOLEN_PATAGONIA"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_patagonia_name};1"
data "Description" "{h_status_patagonia_desc};1"
data "Icon" "Item_ARM_Robes_A"
data "FormatColor" "Green"
data "StackType" "Overwrite"
data "Boosts" "AC(1);DamageBonus(1d4, Bludgeoning)"

new entry "RENT_HIKE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_rent_hike_name};1"
data "Description" "{h_status_rent_hike_desc};1"
data "Icon" "Spell_Evocation_Fireball"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "AC(-2);ActionResource(Movement,-3,0)"
data "TickFunctors" "DealDamage(2d4, Psychic)"

new entry "HOLD_MUSIC_311"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_hold_music_name};1"
data "Description" "{h_status_hold_music_desc};1"
data "Icon" "Spell_Enchantment_Bane"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "BlockRegainBonusAction();BlockRegainReaction();ActionResourceMultiplier(Movement,0.5,0)"

new entry "SWEEP_COOLDOWN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_sweep_cd_name};1"
data "Description" "{h_sweep_cd_desc};1"
data "Icon" "PassiveFeature_SecondWind"
data "FormatColor" "Grey"
data "StackType" "Overwrite"

# Racial Statuses
new entry "EXISTENTIAL_DAZE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_daze_name};1"
data "Description" "{h_status_daze_desc};1"
data "Icon" "Spell_Enchantment_CalmEmotions"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "Disadvantage(AttackRoll)"

new entry "AVOCADO_BLISS"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_avocado_name};1"
data "Description" "{h_status_avocado_desc};1"
data "Icon" "Spell_AvocadoToast"
data "FormatColor" "Green"
data "StackType" "Overwrite"
data "Boosts" "TemporaryHP(5)"

new entry "HANG_TEN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_hangten_name};1"
data "Description" "{h_status_hangten_desc};1"
data "Icon" "Spell_Transmutation_Longstrider"
data "FormatColor" "Cyan"
data "StackType" "Overwrite"
data "Boosts" "ActionResource(Movement,3,0);StatusImmunity(PRONE);StatusImmunity(SG_DifficultTerrain)"

new entry "VIBE_CHECKED"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_vibe_name};1"
data "Description" "{h_status_vibe_desc};1"
data "Icon" "Spell_Enchantment_TashasHideousLaughter"
data "FormatColor" "Red"
data "StackType" "Overwrite"
data "Boosts" "BlockRegainBonusAction();BlockRegainReaction();ActionResourceMultiplier(Movement,0.5,0)"

new entry "SYNERGY_COOLDOWN"
type "StatusData"
data "StatusType" "BOOST"
data "Icon" "Spell_Enchantment_DissonantWhispers"
data "FormatColor" "Grey"
data "StackType" "Overwrite"
"""
    with open(os.path.join(stats_dir, "Status_BOOST.txt"), "w", encoding="utf-8") as f:
        f.write(status_content)

    # Passive.txt
    passive_content = f"""new entry "SidewalkImmunity"
type "PassiveData"
data "DisplayName" "{h_passive_immunity_name};1"
data "Description" "{h_passive_immunity_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Properties" "Highlighted"
data "Boosts" "StatusImmunity(POISONED);StatusImmunity(DISEASE);Resistance(Poison, Resistant)"

new entry "Proposition47"
type "PassiveData"
data "DisplayName" "{h_prop47_name};1"
data "Description" "{h_prop47_desc};1"
data "Icon" "PassiveFeature_SneakAttack"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "IsMeleeAttack()"
data "StatsFunctors" "SELF:ApplyStatus(STOLEN_PATAGONIA,100,2)"

new entry "PocketLintBuffet"
type "PassiveData"
data "DisplayName" "{h_pocket_lint_name};1"
data "Description" "{h_pocket_lint_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "HasStatus('FECAL_STENCH',context.Target)"
data "StatsFunctors" "SELF:RegainTemporaryHitPoints(1d6)"

new entry "RestorativeLean"
type "PassiveData"
data "DisplayName" "{h_passive_lean_heal_name};1"
data "Description" "{h_passive_lean_heal_desc};1"
data "Icon" "PassiveFeature_SecondWind"
data "StatsFunctorContext" "OnTurn"
data "Conditions" "HasStatus('FENT_LEAN')"
data "StatsFunctors" "RegainHitPoints(2d6)"

new entry "BiohazardStench"
type "PassiveData"
data "DisplayName" "{h_biohazard_aura_name};1"
data "Description" "{h_biohazard_aura_desc};1"
data "Icon" "Spell_Evocation_CloudOfDaggers"
data "Properties" "Highlighted"
data "Boosts" "Aura(FECAL_STENCH,3,Enemy and not Dead(),,Poison)"

new entry "EncampmentSweepInstinct"
type "PassiveData"
data "DisplayName" "{h_encampment_sweep_name};1"
data "Description" "{h_encampment_sweep_desc};1"
data "Icon" "PassiveFeature_SecondWind"
data "StatsFunctorContext" "OnDamaged"
data "Conditions" "HasHPPercentageLessThan(50) and not HasStatus('FENT_LEAN') and not HasStatus('SWEEP_COOLDOWN')"
data "StatsFunctors" "SELF:ApplyStatus(FENT_LEAN,100,2);SELF:ApplyStatus(SWEEP_COOLDOWN,100,10)"

new entry "LeanDamageReflect"
type "PassiveData"
data "DisplayName" "{h_passive_lean_reflect_name};1"
data "Description" "{h_passive_lean_reflect_desc};1"
data "Icon" "PassiveFeature_Retaliation"
data "StatsFunctorContext" "OnAttacked"
data "Conditions" "HasStatus('FENT_LEAN') and IsMeleeAttack()"
data "StatsFunctors" "DealDamage(1d10, Psychic)"

# Racial Passives
new entry "EarthquakeSense"
type "PassiveData"
data "DisplayName" "{h_earthquake_name};1"
data "Description" "{h_earthquake_desc};1"
data "Icon" "PassiveFeature_SureFooted"
data "Boosts" "Advantage(SavingThrow, KnockedDown)"

new entry "Veteran405"
type "PassiveData"
data "DisplayName" "{h_veteran405_name};1"
data "Description" "{h_veteran405_desc};1"
data "Icon" "PassiveFeature_FreedomOfMovement"
data "Boosts" "StatusImmunity(SG_Slowed);StatusImmunity(SG_Restrained)"

new entry "Passive_SiliconiteSynergy"
type "PassiveData"
data "DisplayName" "{h_synergy_name};1"
data "Description" "{h_synergy_desc};1"
data "Icon" "Spell_Enchantment_DissonantWhispers"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "IsWeaponAttack() and not HasStatus('SYNERGY_COOLDOWN')"
data "StatsFunctors" "DealDamage(1d4, Psychic);SELF:ApplyStatus(SYNERGY_COOLDOWN,100,1)"

new entry "Passive_SmogLungs"
type "PassiveData"
data "DisplayName" "{h_smog_lungs_name};1"
data "Description" "{h_smog_lungs_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Boosts" "Advantage(SavingThrow, Poison);Advantage(SavingThrow, Disease)"

new entry "Passive_HeatIndexMastery"
type "PassiveData"
data "DisplayName" "{h_heat_index_name};1"
data "Description" "{h_heat_index_desc};1"
data "Icon" "PassiveFeature_FireResistance"
data "Boosts" "StatusImmunity(BURNING)"

# 3rd Gender / California Identity Passives
new entry "CaliforniaIdentity_Dude"
type "PassiveData"
data "DisplayName" "{h_id_dude_name};1"
data "Description" "{h_id_dude_desc};1"
data "Icon" "PassiveFeature_Actor"
data "Boosts" "Skill(Persuasion, 1);Advantage(SavingThrow, Fear);Advantage(SavingThrow, Exhaustion)"

new entry "CaliforniaIdentity_Founder"
type "PassiveData"
data "DisplayName" "{h_id_founder_name};1"
data "Description" "{h_id_founder_desc};1"
data "Icon" "PassiveFeature_Alert"
data "Boosts" "Initiative(2);Advantage(Skill, Deception)"

new entry "CaliforniaIdentity_Oat"
type "PassiveData"
data "DisplayName" "{h_id_oat_name};1"
data "Description" "{h_id_oat_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Boosts" "StatusImmunity(SG_Poisoned)"

new entry "CaliforniaIdentity_SelfActualized"
type "PassiveData"
data "DisplayName" "{h_id_self_name};1"
data "Description" "{h_id_self_desc};1"
data "Icon" "Spell_Abjuration_Aid"
data "StatsFunctorContext" "OnCombatEntered"
data "StatsFunctors" "SELF:RegainTemporaryHitPoints(5)"

new entry "CaliforniaIdentity_Algorithm"
type "PassiveData"
data "DisplayName" "{h_id_algo_name};1"
data "Description" "{h_id_algo_desc};1"
data "Icon" "PassiveFeature_ReliableTalent"
data "Boosts" "SavingThrow(All, 1)"
"""
    with open(os.path.join(stats_dir, "Passive.txt"), "w", encoding="utf-8") as f:
        f.write(passive_content)

    print(f"Generated Stats data in: {stats_dir}")


# -------------------------------------------------------------
# 11. Generate Localization Files
# -------------------------------------------------------------
def generate_localization():
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
    print("Generating Baldur's Gate 3 Homeless Californian Class & Race Mod...")
    generate_meta_lsx()
    generate_class_descriptions_lsx()
    generate_lists_lsx()
    generate_progressions_lsx()
    generate_presets_lsx()
    generate_races_lsx()
    generate_cc_appearance_visuals_lsx()
    generate_cc_presets_lsx()
    generate_stats_txt()
    generate_localization()
    print("Mod source files generated successfully!")


if __name__ == "__main__":
    main()
