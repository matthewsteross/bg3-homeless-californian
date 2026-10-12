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
SPELLLIST_BART_L10 = get_guid("SpellList_BART_L10")

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


# Custom spell art lives in assets/icons/<MapKey>.png and is packed into the atlas by
# build_icons.py. Until a piece of art exists, fall back to an existing icon (or, for
# spells built on a vanilla spell, inherit its icon by omitting the line).
NEW_SPELL_ICONS = [
    "Spell_SidewalkScramble", "Spell_FeralScreech", "Spell_EvictionNotice", "Spell_TentEncampment",
    "Spell_Call311", "Spell_BiohazardBomb", "Spell_BottleShank", "Spell_CartCharge", "Spell_TurnstileHop",
]


def icon_line(map_key: str, fallback: str = "") -> str:
    if os.path.exists(os.path.join(ASSETS_DIR, "icons", f"{map_key}.png")):
        return f'data "Icon" "{map_key}"'
    return f'data "Icon" "{fallback}"' if fallback else ""

# -------------------------------------------------------------
# 1. Localization Strings Setup
# -------------------------------------------------------------
# Class & Subclass Display Names & Descriptions
h_class_name = add_loca("class_name", "Homeless Californian")
h_class_desc = add_loca("class_desc", "Hardened by the concrete jungles of San Francisco and Los Angeles, the Homeless Californian channels makeshift biological warfare, erratic street fury, and the gravity-defying equilibrium of the legendary Fent Lean.")

h_sub_tenderloin_name = add_loca("sub_tenderloin_name", "Tenderloin Biohazard")
h_sub_tenderloin_desc = add_loca("sub_tenderloin_desc", "Master of chemical concoctions and sidewalk biohazards. Amplifies the potency of toxic clouds and explosive biological payloads, until every strike drips with poison.")

h_sub_venice_name = add_loca("sub_venice_name", "Venice Boardwalk Brawler")
h_sub_venice_desc = add_loca("sub_venice_desc", "A ferocious close-quarters pugilist specializing in improvised shivs, reckless flurries, and chaotic shopping cart charges.")

h_sub_bart_name = add_loca("sub_bart_name", "BART Platform Menace")
h_sub_bart_desc = add_loca("sub_bart_desc", "An erratic street phantom who slips through turnstiles and spatial dimensions, never quite where the enemy expects.")

# Spells & Actions - Class
h_sling_poop_name = add_loca("sling_poop_name", "Sling Poop")
h_sling_poop_desc = add_loca("sling_poop_desc", "Hurl a handful of raw biological waste at a target. On a hit, deals 1d10 + Constitution Bludgeoning (2d10 at level 5, 3d10 at level 10) and 1d6 Poison damage, leaves a puddle of filth, and inflicts Fecal Stench for 2 turns. Can be used as often as you like.")

h_sling_poop_chunky_name = add_loca("sling_poop_chunky_name", "Sling Chunky Poop")
h_sling_poop_chunky_desc = add_loca("sling_poop_chunky_desc", "Hurl a dense, fermented payload with devastating force. On a hit, deals an extra 1d10 Bludgeoning on top of Sling Poop (3d10 + Constitution at level 5, 4d10 at level 10) and 2d6 Poison damage, leaves a wider puddle of filth, and inflicts Fecal Stench for 3 turns. Can be used as often as you like.")

h_sling_fent_name = add_loca("sling_fent_name", "Sling Fentanyl")
h_sling_fent_desc = add_loca("sling_fent_desc", "Flick a concentrated dose at an enemy. Deals 2d6 Psychic damage. On a failed Constitution saving throw the target falls into Fent Stupor for 2 turns. Recharges on a Short Rest.")

h_sling_fent_cloud_name = add_loca("sling_fent_cloud_name", "Mass Fentanyl Contraband")
h_sling_fent_cloud_desc = add_loca("sling_fent_cloud_desc", "Scatter an entire contraband brick across a 4m area. Every creature caught takes 5d6 Psychic damage and must make a Constitution saving throw or fall into Fent Stupor until the end of its next turn; on a success, half damage. Recharges on a Short Rest.")

h_fent_lean_name = add_loca("fent_lean_name", "Fent Lean")
h_fent_lean_desc = add_loca("fent_lean_desc", "Fold forward at a perfect, gravity-defying 90-degree angle as a Bonus Action. For 3 turns you have Resistance to all damage, +3 Armour Class, Advantage on Constitution and Dexterity saving throws, and cannot be knocked Prone, but you cannot move. Narcan ends it for free. Recharges on a Short Rest.")

h_snap_out_name = add_loca("snap_out_name", "Narcan")
h_snap_out_desc = add_loca("snap_out_desc", "Jam a dose of Narcan up your nose and snap your spine back upright with a terrifying pop, ending Fent Lean. Costs nothing.")

h_scramble_name = add_loca("scramble_name", "Sidewalk Scramble")
h_scramble_desc = add_loca("scramble_desc", "Scurry frantically across broken glass and hazardous surfaces. As a Bonus Action, Dash and gain +3m movement and immunity to difficult terrain and being knocked Prone until the end of your next turn.")

h_panhandling_name = add_loca("panhandling_name", "Aggressive Panhandling")
h_panhandling_desc = add_loca("panhandling_desc", "Shake a rusty cup aggressively at every enemy within 6m. Each must make a Wisdom saving throw or become Socially Shamed for 2 turns (Disadvantage on Attack Rolls and they cannot take Reactions). Recharges on a Short Rest.")

h_screech_name = add_loca("screech_name", "Feral Screech")
h_screech_desc = add_loca("screech_desc", "Unleash an unhinged, ear-splitting 3 AM shriek. Every enemy within 9m takes 6d6 Thunder damage and must make a Wisdom saving throw or become Frightened for 2 turns; on a success, half damage and no fear. Recharges on a Short Rest.")

h_tent_encampment_name = add_loca("tent_encampment_name", "Pitch Tent Encampment")
h_tent_encampment_desc = add_loca("tent_encampment_desc", "Throw up a tarp-and-shopping-cart bunker. You and every ally within 5m gain 15 Temporary Hit Points, Resistance to Bludgeoning, Piercing and Slashing damage for 3 turns, and Sanctuary for 1 turn. Recharges on a Long Rest.")

h_biohazard_bomb_name = add_loca("biohazard_bomb_name", "Biohazard Bomb")
h_biohazard_bomb_desc = add_loca("biohazard_bomb_desc", "Lob a pressurised five-gallon bucket of aged street slop. Explodes in a 4m radius dealing 6d6 Poison and 3d6 Acid damage (half on a successful Dexterity saving throw), inflicts Fecal Stench on anyone who fails, and leaves a lingering poison cloud. Recharges on a Short Rest.")

h_bottle_shank_name = add_loca("bottle_shank_name", "Broken 40oz Shank")
h_bottle_shank_desc = add_loca("bottle_shank_desc", "As a Bonus Action, drive a jagged malt liquor bottleneck into a vital organ. Deals 2d6 + Constitution Piercing and 1d6 Slashing damage and inflicts Bleeding for 2 turns.")

h_cart_charge_name = add_loca("cart_charge_name", "Shopping Cart Charge")
h_cart_charge_desc = add_loca("cart_charge_desc", "Shove a rattling grocery cart packed with scrap metal up to 9m into the enemy ranks, hitting the first creature in your path for 4d8 + Constitution Bludgeoning damage. On a failed Strength saving throw, the target is knocked Prone. Recharges on a Short Rest.")

h_turnstile_hop_name = add_loca("turnstile_hop_name", "Turnstile Hop")
h_turnstile_hop_desc = add_loca("turnstile_hop_desc", "Slip through the fabric of reality like hopping a transit barrier. Teleport up to 18m as a Bonus Action. Once per turn.")

# Statuses - Class
h_status_stench_name = add_loca("status_stench_name", "Fecal Stench")
h_status_stench_desc = add_loca("status_stench_desc", "Overwhelmed by nauseating biological stench. Disadvantage on Attack Rolls, and takes 1d4 Poison damage at the end of each turn.")

h_status_stupor_name = add_loca("status_stupor_name", "Fent Stupor")
h_status_stupor_desc = add_loca("status_stupor_desc", "Slumped in an unresponsive narcotic daze. Incapacitated: cannot move, act or react. Taking damage does not wake them.")

h_status_lean_name = add_loca("status_lean_name", "Fent Lean")
h_status_lean_desc = add_loca("status_lean_desc", "Locked in supreme postural equilibrium. Resistant to all damage, +3 AC, Advantage on Dexterity and Constitution saving throws, immune to Prone, but cannot move.")

h_status_scramble_name = add_loca("status_scramble_name", "Sidewalk Scramble")
h_status_scramble_desc = add_loca("status_scramble_desc", "+3m movement. Immune to difficult terrain and being knocked Prone.")

h_status_panhandling_name = add_loca("status_panhandling_name", "Socially Shamed")
h_status_panhandling_desc = add_loca("status_panhandling_desc", "Deeply rattled by persistent street solicitation. Disadvantage on Attack Rolls and cannot take Reactions.")

# Passives - Class
h_passive_immunity_name = add_loca("passive_immunity_name", "Sidewalk Immunity")
h_passive_immunity_desc = add_loca("passive_immunity_desc", "Years of dumpster exposure have forged an impenetrable immune system. Immune to Poisoned and Disease, and Resistant to Poison damage.")

h_street_grit_name = add_loca("street_grit_name", "Street Grit Defence")
h_street_grit_desc = add_loca("street_grit_desc", "While not wearing armour, your Armour Class equals 10 + Dexterity modifier + Constitution modifier. You can still use a shield.")

h_passive_lean_heal_name = add_loca("passive_lean_heal_name", "Restorative Stupor")
h_passive_lean_heal_desc = add_loca("passive_lean_heal_desc", "While in Fent Lean, your slowed metabolism knits wounds back together, restoring 2d6 + Constitution Hit Points at the start of each of your turns.")

h_passive_lean_reflect_name = add_loca("passive_lean_reflect_name", "Baffling Retaliation")
h_passive_lean_reflect_desc = add_loca("passive_lean_reflect_desc", "While in Fent Lean, any creature that hits you with a melee attack takes 2d10 Psychic damage from sheer cognitive dissonance.")

h_prop47_name = add_loca("prop47_name", "Proposition 47")
h_prop47_desc = add_loca("prop47_desc", "Petty theft under 950 gold is decriminalised. Whenever you hit an enemy with a melee attack, you snatch a Stolen Patagonia Vest (+1 AC, +1d4 damage on weapon attacks) for 2 turns. Authorities will apologise for profiling you.")

h_status_patagonia_name = add_loca("status_patagonia_name", "Stolen Patagonia Vest")
h_status_patagonia_desc = add_loca("status_patagonia_desc", "Warm, fleece-lined, and acquired without prosecution. +1 Armour Class and +1d4 Bludgeoning damage on weapon attacks.")

h_pocket_lint_name = add_loca("pocket_lint_name", "Pocket Lint Buffet")
h_pocket_lint_desc = add_loca("pocket_lint_desc", "Rummaging through the coats of foes marinating in your biological weaponry is sustenance. Once per turn, when you damage a creature that has Fecal Stench, you gain Temporary Hit Points equal to your Constitution modifier + 2 (minimum 3).")

h_status_pocket_lint_name = add_loca("status_pocket_lint_name", "Pocket Lint Snack")
h_status_pocket_lint_desc = add_loca("status_pocket_lint_desc", "Fortified by whatever was in that coat. Grants Temporary Hit Points.")

h_eviction_name = add_loca("eviction_name", "Eviction Notice")
h_eviction_desc = add_loca("eviction_desc", "As a Bonus Action, serve a foe with an immediate lease termination. On a failed Wisdom saving throw the target takes 3d6 Psychic damage and suffers Rent Hike for 3 turns: -2 AC, -3m movement, and 2d6 Psychic damage at the start of each of its turns from Bay Area cost of living. Recharges on a Short Rest.")

h_status_rent_hike_name = add_loca("status_rent_hike_name", "Rent Hike")
h_status_rent_hike_desc = add_loca("status_rent_hike_desc", "Crushed by runaway housing costs. -2 AC, -3m movement, and takes 2d6 Psychic damage at the start of each turn.")

h_biohazard_aura_name = add_loca("biohazard_aura_name", "Tenderloin Biohazard Aura")
h_biohazard_aura_desc = add_loca("biohazard_aura_desc", "An unbearable 3m miasma radiates from you. Enemies within it reek of Fecal Stench.")

h_status_miasma_name = add_loca("status_miasma_name", "Tenderloin Miasma")
h_status_miasma_desc = add_loca("status_miasma_desc", "Radiating an unbearable 3m stench. Nearby enemies are afflicted with Fecal Stench.")

h_encampment_sweep_name = add_loca("encampment_sweep_name", "Encampment Sweep Survival Instinct")
h_encampment_sweep_desc = add_loca("encampment_sweep_desc", "The first time each combat that the municipal cleanup crew drops you below half Hit Points, you reflexively collapse into Fent Lean for 2 turns and gain 20 Temporary Hit Points.")

h_sweep_cd_name = add_loca("sweep_cd_name", "Sweep Fatigue")
h_sweep_cd_desc = add_loca("sweep_cd_desc", "Your survival reflexes need time to reset.")

h_call311_name = add_loca("call311_name", "Call 311 (On Hold)")
h_call311_desc = add_loca("call311_desc", "Subject every enemy within 9m to the purgatory of municipal hold music. On a failed Wisdom saving throw, for 3 turns they cannot take Bonus Actions or Reactions and their movement is halved. Costs only a Bonus Action. Recharges on a Short Rest.")

h_status_hold_music_name = add_loca("status_hold_music_name", "On Hold (311)")
h_status_hold_music_desc = add_loca("status_hold_music_desc", "Your call is important to us. Please continue to hold. Cannot take Bonus Actions or Reactions, and movement is halved.")

# New features (rebalance)
h_hustle_name = add_loca("hustle_name", "Street Hustle")
h_hustle_desc = add_loca("hustle_desc", "Survival on the block keeps you moving. +3m movement and +3 to Initiative.")

h_unkillable_name = add_loca("unkillable_name", "Unkillable Vagrant")
h_unkillable_desc = add_loca("unkillable_desc", "You have survived things that would kill a dragon. Resistance to Bludgeoning, Piercing and Slashing damage, and Advantage on saving throws against being Frightened or Charmed.")

h_status_boardwalk_heal_name = add_loca("status_boardwalk_heal_name", "Protein Shake")
h_status_boardwalk_heal_desc = add_loca("status_boardwalk_heal_desc", "Restores Hit Points.")

h_status_selfact_name = add_loca("status_selfact_name", "Aligned Chakras")
h_status_selfact_desc = add_loca("status_selfact_desc", "Grants Temporary Hit Points.")

h_status_sweep_shelter_name = add_loca("status_sweep_shelter_name", "Emergency Shelter")
h_status_sweep_shelter_desc = add_loca("status_sweep_shelter_desc", "Your body found a doorway to curl up in. Grants Temporary Hit Points.")

h_status_tent_name = add_loca("status_tent_name", "Tent City")
h_status_tent_desc = add_loca("status_tent_desc", "Huddled under a tarp bunker. Temporary Hit Points and Resistance to Bludgeoning, Piercing and Slashing damage.")

# Subclass features (levels 6 and 10)
h_toxic_name = add_loca("toxic_name", "Toxic Adaptation")
h_toxic_desc = add_loca("toxic_desc", "Your poison damage ignores Resistance, and your weapon attacks deal an extra 1d6 Poison damage.")

h_patient_zero_name = add_loca("patient_zero_name", "Patient Zero")
h_patient_zero_desc = add_loca("patient_zero_desc", "Your body is a walking public-health emergency. Your weapon attacks deal a further 2d6 Poison damage, and you are immune to Poison damage.")

h_juiced_name = add_loca("juiced_name", "Muscle Beach Juice")
h_juiced_desc = add_loca("juiced_desc", "Venice gym regulars taught you everything. Your weapon attacks deal an extra 1d8 Bludgeoning damage, and you gain +2 Armour Class.")

h_boardwalk_king_name = add_loca("boardwalk_king_name", "King of the Boardwalk")
h_boardwalk_king_desc = add_loca("boardwalk_king_desc", "Nothing on the boardwalk scares you anymore. You score critical hits on a roll of 18-20, and you heal 1d8 Hit Points whenever you hit with a melee attack.")


h_last_train_name = add_loca("last_train_name", "Last Train Phantom")
h_last_train_desc = add_loca("last_train_desc", "You are never where they expect. +4.5m movement, immunity to difficult terrain, and you learn Express Hop.")

h_express_hop_name = add_loca("express_hop_name", "Express Hop")
h_express_hop_desc = add_loca("express_hop_desc", "No fare, no wait, no action. Teleport up to 9m for free. Once per turn.")

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
h_id_dude_desc = add_loca("id_dude_desc", "A timeless, universal California vibration. You greet gods, goblins, and dragons alike as 'dude'. You gain +2 to Persuasion checks and Advantage on saving throws against being Frightened.")

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
h_earthquake_desc = add_loca("earthquake_desc", "Born on the San Andreas Fault, you possess impeccable footing. You cannot be knocked Prone.")

h_veteran405_name = add_loca("veteran405_name", "405 Commute Veteran")
h_veteran405_desc = add_loca("veteran405_desc", "Decades spent idling on the I-405 freeway have made you immune to gridlock. You cannot be Slowed or Restrained.")

h_smog_lungs_name = add_loca("smog_lungs_name", "Smog Lungs")
h_smog_lungs_desc = add_loca("smog_lungs_desc", "Central Valley dust and Los Angeles smog have turned your respiratory system into an industrial air filter. Advantage on saving throws against being Poisoned, and immune to Disease.")

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
                    <attribute id="BaseHp" type="int32" value="14"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_class_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_class_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="8"/>
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
                    <attribute id="BaseHp" type="int32" value="14"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_sub_tenderloin_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_sub_tenderloin_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="8"/>
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
                    <attribute id="BaseHp" type="int32" value="14"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_sub_venice_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_sub_venice_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="8"/>
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
                    <attribute id="BaseHp" type="int32" value="14"/>
                    <attribute id="CanLearnSpells" type="bool" value="false"/>
                    <attribute id="CharacterCreationPose" type="guid" value="0f07ec6e-4ef0-434e-9a51-1353260ccff8"/>
                    <attribute id="ClassEquipment" type="FixedString" value="EQP_CC_Barbarian"/>
                    <attribute id="ClassHotbarColumns" type="int32" value="5"/>
                    <attribute id="CommonHotbarColumns" type="int32" value="9"/>
                    <attribute id="Description" type="TranslatedString" handle="{h_sub_bart_desc}" version="1"/>
                    <attribute id="DisplayName" type="TranslatedString" handle="{h_sub_bart_name}" version="1"/>
                    <attribute id="HpPerLevel" type="int32" value="8"/>
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
                    <attribute id="Spells" type="LSString" value="Target_BrokenBottleShank;Rush_ShoppingCartCharge"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_VENICE_L3}"/>
                </node>

                <!-- Subclass BART Menace Spells -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Target_TurnstileHop"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_BART_L3}"/>
                </node>

                <!-- Subclass BART Menace Level 10: Express Hop -->
                <node id="SpellList">
                    <attribute id="Spells" type="LSString" value="Target_ExpressHop"/>
                    <attribute id="UUID" type="guid" value="{SPELLLIST_BART_L10}"/>
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
    # Boosts/Selectors/Passives are plain LSString in vanilla (Shared/Progressions.lsx).
    def prog(key, name, level, table, ptype=0, boosts="", passives="", passives_removed="",
             selectors="", improvement=None, multiclass=False, children=""):
        attrs = []
        if improvement is not None:
            attrs.append(f'<attribute id="AllowImprovement" type="bool" value="{str(improvement).lower()}"/>')
        if boosts:
            attrs.append(f'<attribute id="Boosts" type="LSString" value="{boosts}"/>')
        if multiclass:
            attrs.append('<attribute id="IsMulticlass" type="bool" value="true"/>')
        attrs.append(f'<attribute id="Level" type="uint8" value="{level}"/>')
        attrs.append(f'<attribute id="Name" type="LSString" value="{name}"/>')
        if passives:
            attrs.append(f'<attribute id="PassivesAdded" type="LSString" value="{passives}"/>')
        if passives_removed:
            attrs.append(f'<attribute id="PassivesRemoved" type="LSString" value="{passives_removed}"/>')
        attrs.append(f'<attribute id="ProgressionType" type="uint8" value="{ptype}"/>')
        if selectors:
            attrs.append(f'<attribute id="Selectors" type="LSString" value="{selectors}"/>')
        attrs.append(f'<attribute id="TableUUID" type="guid" value="{table}"/>')
        attrs.append(f'<attribute id="UUID" type="guid" value="{get_guid(key)}"/>')
        body = "\n                    ".join(attrs)
        kids = f"\n                    <children>{children}\n                    </children>" if children else ""
        nodes.append(f"""
                <node id="Progression">
                    {body}{kids}
                </node>""")

    CLS = "HomelessCalifornian"
    T = PROG_TABLE_UUID
    ABILITY_BONUS = "SelectAbilityBonus(b9149c8e-52c8-46e5-9cb6-fc39301c05fe,AbilityBonus,2,1)"
    PROFS = "Proficiency(LightArmor);Proficiency(MediumArmor);Proficiency(Shields);Proficiency(SimpleWeapons);Proficiency(MartialWeapons)"
    L1_PASSIVES = "StreetGritDefence;SidewalkImmunity;Proposition47"

    prog("Prog_Homeless_Lvl1", CLS, 1, T, improvement=False,
         boosts="ProficiencyBonus(SavingThrow,Constitution);ProficiencyBonus(SavingThrow,Dexterity);" + PROFS,
         passives=L1_PASSIVES,
         selectors=f"SelectSkills({SKILLLIST_UUID},3);AddSpells({SPELLLIST_LVL1});{ABILITY_BONUS}")
    # Multiclassing in: same kit minus saving throws and skills (vanilla pattern)
    prog("Prog_Homeless_Lvl1_Multiclass", CLS, 1, T, improvement=False, multiclass=True,
         boosts=PROFS, passives=L1_PASSIVES, selectors=f"AddSpells({SPELLLIST_LVL1})")
    prog("Prog_Homeless_Lvl2", CLS, 2, T, passives="PocketLintBuffet;StreetHustle",
         selectors=f"AddSpells({SPELLLIST_LVL2})")
    prog("Prog_Homeless_Lvl3", CLS, 3, T, children=f"""
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
                        </node>""")
    prog("Prog_Homeless_Lvl4", CLS, 4, T, improvement=True, selectors=f"AddSpells({SPELLLIST_LVL4})")
    prog("Prog_Homeless_Lvl5", CLS, 5, T, passives="ExtraAttack", selectors=f"AddSpells({SPELLLIST_LVL5})")
    prog("Prog_Homeless_Lvl6", CLS, 6, T, passives="RestorativeLean;UnkillableVagrant")
    prog("Prog_Homeless_Lvl7", CLS, 7, T, selectors=f"AddSpells({SPELLLIST_LVL7})")
    prog("Prog_Homeless_Lvl8", CLS, 8, T, improvement=True)
    prog("Prog_Homeless_Lvl9", CLS, 9, T, selectors=f"AddSpells({SPELLLIST_LVL9})")
    prog("Prog_Homeless_Lvl10", CLS, 10, T, passives="EncampmentSweepInstinct")
    prog("Prog_Homeless_Lvl11", CLS, 11, T, passives="ExtraAttack_2;LeanDamageReflect", passives_removed="ExtraAttack")
    prog("Prog_Homeless_Lvl12", CLS, 12, T, improvement=True, selectors=f"AddSpells({SPELLLIST_LVL12})")

    # --- SUBCLASS PROGRESSIONS (Type 1) ---
    prog("Prog_Tenderloin_L3", "TenderloinBiohazard", 3, SUBCLASS_TENDERLOIN_TABLE_UUID, ptype=1,
         passives="BiohazardStench", selectors=f"AddSpells({SPELLLIST_TENDERLOIN_L3})")
    prog("Prog_Tenderloin_L6", "TenderloinBiohazard", 6, SUBCLASS_TENDERLOIN_TABLE_UUID, ptype=1,
         passives="ToxicAdaptation")
    prog("Prog_Tenderloin_L10", "TenderloinBiohazard", 10, SUBCLASS_TENDERLOIN_TABLE_UUID, ptype=1,
         passives="PatientZero")

    prog("Prog_Venice_L3", "VeniceBoardwalkBrawler", 3, SUBCLASS_VENICE_TABLE_UUID, ptype=1,
         boosts="Proficiency(HeavyArmor)", selectors=f"AddSpells({SPELLLIST_VENICE_L3})")
    prog("Prog_Venice_L6", "VeniceBoardwalkBrawler", 6, SUBCLASS_VENICE_TABLE_UUID, ptype=1,
         passives="MuscleBeachJuice")
    prog("Prog_Venice_L10", "VeniceBoardwalkBrawler", 10, SUBCLASS_VENICE_TABLE_UUID, ptype=1,
         passives="KingOfTheBoardwalk")

    prog("Prog_BART_L3", "BARTPlatformMenace", 3, SUBCLASS_BART_TABLE_UUID, ptype=1,
         passives="ReliableTalent", selectors=f"AddSpells({SPELLLIST_BART_L3})")
    prog("Prog_BART_L6", "BARTPlatformMenace", 6, SUBCLASS_BART_TABLE_UUID, ptype=1,
         passives="Evasion;UncannyDodge")
    prog("Prog_BART_L10", "BARTPlatformMenace", 10, SUBCLASS_BART_TABLE_UUID, ptype=1,
         passives="LastTrainPhantom", selectors=f"AddSpells({SPELLLIST_BART_L10})")

    # --- RACIAL PROGRESSIONS (Type 2) ---
    # Californian Base Race Progression (Levels 1 - 12)
    for lvl in range(1, 13):
        u_race = get_guid(f"Prog_Californian_Lvl{lvl}")
        if lvl == 1:
            nodes.append(f"""
                <node id="Progression">
                    <attribute id="AllowImprovement" type="bool" value="false"/>
                    <attribute id="Boosts" type="LSString" value="ActionResource(Movement,9,0);Resistance(Fire,Resistant)"/>
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
                    <attribute id="Boosts" type="LSString" value="Resistance(Radiant,Resistant)"/>
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
                    <attribute id="Boosts" type="LSString" value="Resistance(Poison,Resistant)"/>
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
                    <attribute id="Add" type="LSString" value="Survival;Athletics;Stealth;Intimidation;Acrobatics"/>
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
def _hue_class(hex_argb):
    """'pink', 'blue', 'black' or None for a '#AARRGGBB' colour."""
    import colorsys
    h = hex_argb.lstrip("#")[-6:]
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, light, sat = colorsys.rgb_to_hls(r, g, b)
    hue *= 360
    if light < 0.12:
        return "black"
    if sat < 0.30 or light > 0.92:
        return None
    if hue >= 285 or hue < 10:
        return "pink"
    if 170 <= hue < 250:
        return "blue"
    return None


def restrict_californian_look(children_xml: str) -> str:
    import json
    colours = json.load(open(os.path.join(ASSETS_DIR, "cc_color_names.json"), encoding="utf-8"))
    hair_ok = ("HAIR_Color_Pink_", "HAIR_Color_Blue_", "HAIR_Color_Aqua_")
    makeup_ok = ("Makeup_Pink", "Makeup_Blue", "Makeup_Aqua", "Makeup_Teal", "Makeup_Purple", "Makeup_Black")

    def keep(group, uuid):
        c = colours.get(uuid)
        if c is None:
            return True
        if group == "HairColors":
            return c["name"].startswith(hair_ok)
        if group == "HairHighlightColors":
            return _hue_class(c["color"]) in ("pink", "blue")
        if group == "MakeupColors":
            return c["name"].startswith(makeup_ok)
        if group == "LipsMakeupColors":
            return _hue_class(c["color"]) in ("pink", "blue", "black")
        return True

    root = ET.fromstring(children_xml.split("?>", 1)[-1].strip())
    for node in list(root):
        group = node.get("id")
        if group in ("HairColors", "HairHighlightColors", "MakeupColors", "LipsMakeupColors"):
            for attr in node.findall("attribute"):
                if attr.get("id") == "Object" and not keep(group, attr.get("value")):
                    root.remove(node)
                    break
    return ET.tostring(root, encoding="unicode")


def generate_races_lsx():
    path = os.path.join(PUBLIC_DIR, "Races", "Races.lsx")
    ensure_dir(os.path.dirname(path))

    # Read extracted human children, then restrict the Californian look:
    # hair/highlights only bright pink, blue or aqua; makeup and lipstick only garish shades.
    human_children_path = os.path.join(ASSETS_DIR, "human_race_children.xml")
    # Fail loudly: without this file the race silently ships with no hair/skin/eye options
    with open(human_children_path, "r", encoding="utf-8") as f:
        human_children_xml = restrict_californian_look(f.read())

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
    # Syntax notes (checked against vanilla Shared/Gustav stats):
    #  - save spells roll "not SavingThrow(...)": SpellSuccess = target FAILED the save
    #  - "ApplyStatus(SELF,X,...)" targets the caster from a passive/spell
    #  - ActionResourceMultiplier is a percentage (200 = double, 50 = half)
    #  - spells built on a vanilla spell with `using` inherit its visuals/targeting;
    #    `using` must come right after `type`
    stats_dir = os.path.join(PUBLIC_DIR, "Stats", "Generated", "Data")
    ensure_dir(stats_dir)
    ANIM_CAST = "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;38cdb41c-2eec-4e03-bb31-83cff0346c35,,;85414f5f-b448-4dda-9370-1b6c4b38b561,,;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;,,;,,"
    # Animation/effect IDs below are copied from vanilla spells (an unknown ID makes the cast silently do nothing)
    ANIM_SELF = "9122eb08-93f1-4010-a275-f5ae3ec7c76e,,;,,;9fb11cca-02d4-4d2f-955f-2826c0553b17,,;5103d398-d8de-4aa4-9633-db2e1b7f6254,,;5301d674-b7da-47b6-b4cf-2802ba33a9e9,,;,,;86b3cf93-21fb-4a3d-bed9-97d0a567d084,,;,,;,,"  # Shout_SecondWind
    FX_SELF = 'data "PrepareEffect" "bd833cb2-2d28-4533-bfdf-67e4f77dd10f"\ndata "CastEffect" "bc392fbd-4ca6-4066-954b-169eb0b963e0"'
    ANIM_MELEE = "8b8bb757-21ce-4e02-a2f3-97d55cf2f90b,,;6606c30b-be1c-4f17-ae6b-1a591c80b18c,366693ee-d97f-4294-a4dd-a2145ddc4e6a,9f2d32b9-529a-4b75-b3df-6e1ae1395280;f4ac302b-1569-404f-bd52-1fe443e265df,479ee5da-2967-41e1-b7d1-a94e864a5f25,79323098-edb3-4993-ba50-9b5f705e9878;e8a5c57f-855b-4227-acaa-11e8ce8d7d64,b5cb923d-0c08-4c20-89a9-44b9bf98c6cb,6282d127-0c06-4365-9d53-6f32ef350127;7bb52cd4-0b1c-4926-9165-fa92b75876a3,,;2b81c18b-9698-4262-a623-932c2bb1296d,ecbf9949-3b33-432c-b735-e47aaed0924a,e71a7c08-fdc1-4a0b-9a90-1c793c58553c;0b07883a-08b8-43b6-ac18-84dc9e84ff50,,;,,;,,"  # Target_MainHandAttack
    ANIM_TOUCH = "3ff87abf-1ea1-4c32-aadf-c822d74c7dc0,,;,,;c17a3562-3758-4c4a-96e8-790cebed1df4,a1227ad0-1db2-4941-836b-0a8d85b87a0b,aef20313-abe9-4abb-8ecf-65c22d25ea80;a8012b19-b279-45ec-89b0-86a1b73ad584,92b2bf7e-5fd5-4016-acb9-dae833b7c2e2,a6874259-8dd1-46fa-99f8-6a19ebb19087;d8925ce4-d6d9-400c-92f5-ad772ef7f178,,;,,;eadedcce-d01b-4fbb-a1ae-d218f13aa5d6,,;efbf3ee5-7340-4b29-8ab5-113b004a8e7b,,;95c387b6-3756-4bb5-accf-75a117eefb5f,,"  # Target_ShockingGrasp

    # Spell_Projectile.txt
    proj_content = f"""new entry "Projectile_SlingPoop"
type "SpellData"
data "SpellType" "Projectile"
using "Projectile_RayOfSickness"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "SpellRoll" "Attack(AttackType.RangedSpellAttack)"
data "SpellSuccess" "DealDamage(LevelMapValue(D10Cantrip)+ConstitutionModifier,Bludgeoning,Magical);DealDamage(1d6,Poison,Magical);ApplyStatus(FECAL_STENCH,100,2)"
data "SpellProperties" "GROUND:CreateSurface(1.5,2,Mud)"
data "TargetConditions" "not Self() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "Icon" "Spell_SlingPoop"
data "DisplayName" "{h_sling_poop_name};1"
data "Description" "{h_sling_poop_desc};1"
data "TooltipDamageList" "DealDamage(LevelMapValue(D10Cantrip)+ConstitutionModifier,Bludgeoning);DealDamage(1d6,Poison)"
data "TooltipAttackSave" "RangedSpellAttack"
data "TooltipStatusApply" "ApplyStatus(FECAL_STENCH,100,2)"
data "TooltipUpcastDescription" ""
data "DamageType" "Bludgeoning"

new entry "Projectile_SlingPoop_Chunky"
type "SpellData"
data "SpellType" "Projectile"
using "Projectile_SlingPoop"
data "SpellSuccess" "DealDamage(LevelMapValue(D10Cantrip)+1d10+ConstitutionModifier,Bludgeoning,Magical);DealDamage(2d6,Poison,Magical);ApplyStatus(FECAL_STENCH,100,3)"
data "SpellProperties" "GROUND:CreateSurface(2.5,3,Mud)"
data "DisplayName" "{h_sling_poop_chunky_name};1"
data "Description" "{h_sling_poop_chunky_desc};1"
data "TooltipDamageList" "DealDamage(LevelMapValue(D10Cantrip)+1d10+ConstitutionModifier,Bludgeoning);DealDamage(2d6,Poison)"
data "TooltipStatusApply" "ApplyStatus(FECAL_STENCH,100,3)"

new entry "Projectile_SlingFentanyl"
type "SpellData"
data "SpellType" "Projectile"
using "Projectile_RayOfSickness"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "Cooldown" "OncePerShortRest"
data "SpellRoll" "not SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(2d6,Psychic,Magical);ApplyStatus(FENT_STUPOR,100,2)"
data "SpellFail" "DealDamage(2d6,Psychic,Magical)"
data "TargetConditions" "not Self() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "Icon" "Spell_SlingFentanyl"
data "DisplayName" "{h_sling_fent_name};1"
data "Description" "{h_sling_fent_desc};1"
data "TooltipDamageList" "DealDamage(2d6,Psychic)"
data "TooltipAttackSave" "Constitution"
data "TooltipStatusApply" "ApplyStatus(FENT_STUPOR,100,2)"
data "TooltipUpcastDescription" ""
data "DamageType" "Psychic"

new entry "Projectile_SlingFentanyl_Mass"
type "SpellData"
data "SpellType" "Projectile"
using "Projectile_AcidSplash"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "Cooldown" "OncePerShortRest"
data "AreaRadius" "4"
data "ExplodeRadius" "4"
data "SpellRoll" "not SavingThrow(Ability.Constitution, SourceSpellDC())"
data "SpellSuccess" "DealDamage(5d6,Psychic,Magical);ApplyStatus(FENT_STUPOR,100,1)"
data "SpellFail" "DealDamage(5d6/2,Psychic,Magical)"
data "UseCosts" "ActionPoint:1"
data "Icon" "Spell_SlingFentanyl"
data "DisplayName" "{h_sling_fent_cloud_name};1"
data "Description" "{h_sling_fent_cloud_desc};1"
data "TooltipDamageList" "DealDamage(5d6,Psychic)"
data "TooltipAttackSave" "Constitution"
data "TooltipStatusApply" "ApplyStatus(FENT_STUPOR,100,1)"
data "DamageType" "Psychic"

new entry "Projectile_BiohazardBomb"
type "SpellData"
data "SpellType" "Projectile"
using "Projectile_AcidSplash"
data "Level" "0"
data "SpellSchool" "Evocation"
data "Cooldown" "OncePerShortRest"
data "AreaRadius" "4"
data "ExplodeRadius" "4"
data "SpellRoll" "not SavingThrow(Ability.Dexterity, SourceSpellDC())"
data "SpellSuccess" "DealDamage(6d6,Poison,Magical);DealDamage(3d6,Acid,Magical);ApplyStatus(FECAL_STENCH,100,3)"
data "SpellFail" "DealDamage(6d6/2,Poison,Magical);DealDamage(3d6/2,Acid,Magical)"
data "SpellProperties" "GROUND:CreateSurface(4,3,PoisonCloud)"
data "UseCosts" "ActionPoint:1"
{icon_line("Spell_BiohazardBomb", "Spell_SlingPoop")}
data "DisplayName" "{h_biohazard_bomb_name};1"
data "Description" "{h_biohazard_bomb_desc};1"
data "TooltipDamageList" "DealDamage(6d6,Poison);DealDamage(3d6,Acid)"
data "TooltipAttackSave" "Dexterity"
data "TooltipStatusApply" "ApplyStatus(FECAL_STENCH,100,3)"
data "DamageType" "Poison"
"""
    with open(os.path.join(stats_dir, "Spell_Projectile.txt"), "w", encoding="utf-8") as f:
        f.write(proj_content)

    # Spell_Shout.txt
    shout_content = f"""new entry "Shout_FentLean"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "Cooldown" "OncePerShortRest"
data "SpellProperties" "ApplyStatus(FENT_LEAN,100,3)"
data "TargetConditions" "Self()"
data "Icon" "Spell_FentLean"
data "DisplayName" "{h_fent_lean_name};1"
data "Description" "{h_fent_lean_desc};1"
data "TooltipStatusApply" "ApplyStatus(FENT_LEAN,100,3)"
data "CastSound" "Spell_Cast_Buff_Stoneskin_L4to6"
data "TargetSound" "Spell_Impact_Buff_Stoneskin_L4to6"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "{ANIM_SELF}"
{FX_SELF}
data "CastTextEvent" "Cast"
data "VerbalIntent" "Buff"
data "SpellFlags" "IgnoreSilence"

new entry "Shout_FentLean_End"
type "SpellData"
data "SpellType" "Shout"
data "SpellProperties" "RemoveStatus(FENT_LEAN)"
data "TargetConditions" "Self()"
data "Requirements" ""
data "Icon" "Spell_SnapOutLean"
data "DisplayName" "{h_snap_out_name};1"
data "Description" "{h_snap_out_desc};1"
data "SpellAnimation" "d7745165-66e4-41c4-9e42-d09d95a29491,,;,,;fd5e6365-f314-42e8-a39b-a041dc56b0e7,,;721abca5-2d52-4317-82a3-2a2e970a7a16,,;ce773016-6fb4-44fe-84db-e037aaa22041,,;,,;,,;,,;,,"
data "VerbalIntent" "Utility"
data "CastTextEvent" "Cast"
data "SpellActionType" "Dismiss"
data "SpellAnimationIntentType" "Peaceful"
data "SpellFlags" "IgnoreSilence"

new entry "Shout_SidewalkScramble"
type "SpellData"
data "SpellType" "Shout"
using "Shout_Dash_BonusAction"
data "SpellProperties" "ApplyStatus(SIDEWALK_SCRAMBLE,100,2);IF(HasStatus('DASH_STACKED')):ApplyStatus(DASH_STACKED_2,100,1);IF(not HasStatus('DASH_STACKED_2') and HasStatus('DASH')):ApplyStatus(DASH_STACKED,100,1);IF(not HasStatus('DASH_STACKED_2') and not HasStatus('DASH_STACKED') and not HasStatus('DASH')):ApplyStatus(DASH,100,1)"
data "UseCosts" "BonusActionPoint:1"
data "DisplayName" "{h_scramble_name};1"
data "Description" "{h_scramble_desc};1"
{icon_line("Spell_SidewalkScramble")}
data "TooltipStatusApply" "ApplyStatus(SIDEWALK_SCRAMBLE,100,2)"

new entry "Shout_AggressivePanhandling"
type "SpellData"
data "SpellType" "Shout"
using "Shout_FeyPresence"
data "SpellContainerID" ""
data "Level" "0"
data "SpellSchool" "Enchantment"
data "Cooldown" "OncePerShortRest"
data "AreaRadius" "6"
data "SpellRoll" "not SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "ApplyStatus(PANHANDLING_SHAME,100,2)"
data "SpellFail" "ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL, 100, 0)"
data "TargetConditions" "not Self() and not Ally() and not Dead()"
data "UseCosts" "ActionPoint:1"
data "Icon" "Spell_Panhandling"
data "DisplayName" "{h_panhandling_name};1"
data "Description" "{h_panhandling_desc};1"
data "TooltipAttackSave" "Wisdom"
data "TooltipStatusApply" "ApplyStatus(PANHANDLING_SHAME,100,2)"

new entry "Shout_FeralScreech"
type "SpellData"
data "SpellType" "Shout"
using "Shout_MAG_Thunder_ThunderClap"
data "Level" "0"
data "Cooldown" "OncePerShortRest"
data "AreaRadius" "9"
data "SpellRoll" "not SavingThrow(Ability.Wisdom, SourceSpellDC(), AdvantageOnFrightened(), DisadvantageOnFrightened())"
data "SpellSuccess" "DealDamage(6d6,Thunder,Magical);ApplyStatus(FRIGHTENED,100,2)"
data "SpellFail" "DealDamage(6d6/2,Thunder,Magical)"
data "UseCosts" "ActionPoint:1"
data "DisplayName" "{h_screech_name};1"
data "Description" "{h_screech_desc};1"
{icon_line("Spell_FeralScreech")}
data "TooltipDamageList" "DealDamage(6d6,Thunder)"
data "TooltipAttackSave" "Wisdom"
data "TooltipStatusApply" "ApplyStatus(FRIGHTENED,100,2)"

new entry "Shout_TentEncampment"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Abjuration"
data "Cooldown" "OncePerRest"
data "AreaRadius" "5"
data "SpellProperties" "ApplyStatus(TENT_CITY,100,3);ApplyStatus(SANCTUARY,100,1)"
data "TargetConditions" "(Ally() or Self()) and not Dead()"
{icon_line("Spell_TentEncampment", "Spell_FentLean")}
data "DisplayName" "{h_tent_encampment_name};1"
data "Description" "{h_tent_encampment_desc};1"
data "TooltipStatusApply" "ApplyStatus(TENT_CITY,100,3)"
data "CastSound" "Spell_Cast_Buff_Stoneskin_L4to6"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "{ANIM_SELF}"
{FX_SELF}
data "CastTextEvent" "Cast"
data "VerbalIntent" "Buff"
data "SpellFlags" "IgnoreSilence"

new entry "Shout_Call311"
type "SpellData"
data "SpellType" "Shout"
using "Shout_FeyPresence"
data "SpellContainerID" ""
data "Level" "0"
data "SpellSchool" "Enchantment"
data "Cooldown" "OncePerShortRest"
data "AreaRadius" "9"
data "SpellRoll" "not SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "ApplyStatus(HOLD_MUSIC_311,100,3)"
data "SpellFail" "ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL, 100, 0)"
data "TargetConditions" "not Self() and not Ally() and not Dead()"
data "UseCosts" "BonusActionPoint:1"
{icon_line("Spell_Call311", "Spell_Panhandling")}
data "DisplayName" "{h_call311_name};1"
data "Description" "{h_call311_desc};1"
data "TooltipAttackSave" "Wisdom"
data "TooltipStatusApply" "ApplyStatus(HOLD_MUSIC_311,100,3)"

# Racial Shouts
new entry "Shout_AvocadoToast"
type "SpellData"
data "SpellType" "Shout"
data "Level" "0"
data "SpellSchool" "Evocation"
data "SpellProperties" "RegainHitPoints(1d6+ConstitutionModifier);ApplyStatus(AVOCADO_BLISS,100,3)"
data "TargetConditions" "Self()"
data "Icon" "Spell_AvocadoToast"
data "DisplayName" "{h_avocado_toast_name};1"
data "Description" "{h_avocado_toast_desc};1"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "{ANIM_SELF}"
{FX_SELF}
data "CastTextEvent" "Cast"
data "VerbalIntent" "Healing"
data "SpellFlags" "IgnoreSilence"

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
data "SpellAnimation" "{ANIM_SELF}"
{FX_SELF}
data "CastTextEvent" "Cast"
data "VerbalIntent" "Buff"
data "SpellFlags" "IgnoreSilence"
"""
    with open(os.path.join(stats_dir, "Spell_Shout.txt"), "w", encoding="utf-8") as f:
        f.write(shout_content)

    # Spell_Target.txt
    target_content = f"""new entry "Target_BrokenBottleShank"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Transmutation"
data "TargetRadius" "1.5"
data "SpellRoll" "Attack(AttackType.MeleeWeaponAttack)"
data "SpellSuccess" "DealDamage(2d6+ConstitutionModifier,Piercing);DealDamage(1d6,Slashing);ApplyStatus(BLEEDING,100,2)"
data "TargetConditions" "not Self() and not Dead()"
{icon_line("Spell_BottleShank", "Spell_SnapOutLean")}
data "DisplayName" "{h_bottle_shank_name};1"
data "Description" "{h_bottle_shank_desc};1"
data "TooltipDamageList" "DealDamage(2d6+ConstitutionModifier,Piercing);DealDamage(1d6,Slashing)"
data "TooltipAttackSave" "MeleeWeaponAttack"
data "TooltipStatusApply" "ApplyStatus(BLEEDING,100,2)"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "{ANIM_MELEE}"
data "HitAnimationType" "PhysicalDamage"
data "SpellAnimationIntentType" "Aggressive"
data "CastEffect" "8682067a-e523-40fb-b705-3112083b6b05"
data "Sheathing" "Melee"
data "CastTextEvent" "Cast"
data "VerbalIntent" "Damage"
data "SpellFlags" "IsHarmful;IsMelee"
data "DamageType" "Piercing"

new entry "Target_EvictionNotice"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "Cooldown" "OncePerShortRest"
data "TargetRadius" "18"
data "SpellRoll" "not SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "DealDamage(3d6,Psychic,Magical);ApplyStatus(RENT_HIKE,100,3)"
data "SpellFail" "ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL, 100, 0)"
data "TargetConditions" "not Self() and not Dead()"
{icon_line("Spell_EvictionNotice", "Spell_Panhandling")}
data "DisplayName" "{h_eviction_name};1"
data "Description" "{h_eviction_desc};1"
data "TooltipAttackSave" "Wisdom"
data "TooltipStatusApply" "ApplyStatus(RENT_HIKE,100,3)"
data "CastSound" "Spell_Cast_Control_CrownOfMadness_L1to3"
data "TargetSound" "Spell_Impact_Control_CrownOfMadness_L1to3"
data "TooltipDamageList" "DealDamage(3d6,Psychic)"
data "UseCosts" "BonusActionPoint:1"
data "SpellAnimation" "{ANIM_CAST}"
data "CastTextEvent" "Cast"
data "VerbalIntent" "Control"
data "SpellFlags" "HasVerbalComponent;HasSomaticComponent;IsSpell;IsHarmful"

new entry "Target_TurnstileHop"
type "SpellData"
data "SpellType" "Target"
using "Target_MistyStep"
data "Level" "0"
data "Cooldown" "OncePerTurn"
data "UseCosts" "BonusActionPoint:1"
data "DisplayName" "{h_turnstile_hop_name};1"
data "Description" "{h_turnstile_hop_desc};1"
{icon_line("Spell_TurnstileHop")}
data "TooltipUpcastDescription" ""
data "SpellFlags" "IgnoreSilence;HasHighGroundRangeExtension;RangeIgnoreVerticalThreshold"

new entry "Target_ExpressHop"
type "SpellData"
data "SpellType" "Target"
using "Target_TurnstileHop"
data "TargetRadius" "9"
data "UseCosts" ""
data "DisplayName" "{h_express_hop_name};1"
data "Description" "{h_express_hop_desc};1"

# Racial Targets
new entry "Target_TouchGrass"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "TargetRadius" "1.5"
data "SpellRoll" "Attack(AttackType.MeleeSpellAttack)"
data "SpellSuccess" "DealDamage(1d8,Psychic,Magical);RemoveStatus(SG_Rage);ApplyStatus(EXISTENTIAL_DAZE,100,2)"
data "TargetConditions" "Character() and not Self() and not Dead()"
data "Icon" "Spell_Enchantment_CalmEmotions"
data "DisplayName" "{h_touch_grass_name};1"
data "Description" "{h_touch_grass_desc};1"
data "TooltipDamageList" "DealDamage(1d8,Psychic)"
data "TooltipAttackSave" "MeleeSpellAttack"
data "CastSound" "Spell_Cast_Buff_Bless_L1to3"
data "TargetSound" "Spell_Impact_Buff_Bless_L1to3"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "{ANIM_TOUCH}"
data "CastTextEvent" "Cast"
data "HitAnimationType" "MagicalDamage_Psychic"
data "PrepareEffect" "77241e8c-ae8d-4402-92d8-a871ce64d86f"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;IsSpell;IsHarmful"
data "DamageType" "Psychic"

new entry "Target_VibeCheck"
type "SpellData"
data "SpellType" "Target"
data "Level" "0"
data "SpellSchool" "Enchantment"
data "TargetRadius" "18"
data "SpellRoll" "not SavingThrow(Ability.Wisdom, SourceSpellDC())"
data "SpellSuccess" "BreakConcentration();ApplyStatus(VIBE_CHECKED,100,1)"
data "SpellFail" "ApplyStatus(SAVED_AGAINST_HOSTILE_SPELL, 100, 0)"
data "TargetConditions" "Character() and not Self() and not Dead()"
data "Icon" "Spell_Enchantment_Tasha'sHideousLaughter"
data "DisplayName" "{h_vibe_check_name};1"
data "Description" "{h_vibe_check_desc};1"
data "TooltipAttackSave" "Wisdom"
data "Cooldown" "OncePerShortRest"
data "UseCosts" "ActionPoint:1"
data "SpellAnimation" "{ANIM_CAST}"
data "CastTextEvent" "Cast"
data "VerbalIntent" "Control"
data "SpellFlags" "HasSomaticComponent;HasVerbalComponent;IsSpell;IsHarmful"
"""
    with open(os.path.join(stats_dir, "Spell_Target.txt"), "w", encoding="utf-8") as f:
        f.write(target_content)

    # Spell_Rush.txt
    rush_content = f"""new entry "Rush_ShoppingCartCharge"
type "SpellData"
data "SpellType" "Rush"
using "Rush_SpringAttack"
data "Cooldown" "OncePerShortRest"
data "SpellSuccess" "DealDamage(4d8+ConstitutionModifier,Bludgeoning);IF(Character() and not SavingThrow(Ability.Strength, SourceSpellDC())):ApplyStatus(PRONE,100,1)"
data "TargetConditions" "(Character() and not Ally() and not Dead()) or Item()"
data "UseCosts" "ActionPoint:1"
data "RequirementConditions" ""
data "WeaponTypes" ""
data "RechargeValues" ""
data "SpellFlags" "IsHarmful"
{icon_line("Spell_CartCharge")}
data "DisplayName" "{h_cart_charge_name};1"
data "Description" "{h_cart_charge_desc};1"
data "TooltipDamageList" "DealDamage(4d8+ConstitutionModifier,Bludgeoning)"
data "TooltipAttackSave" "MeleeWeaponAttack"
data "TooltipStatusApply" "ApplyStatus(PRONE,100,1)"
data "DamageType" "Bludgeoning"
"""
    with open(os.path.join(stats_dir, "Spell_Rush.txt"), "w", encoding="utf-8") as f:
        f.write(rush_content)

    # Status_BOOST.txt
    status_content = f"""new entry "FECAL_STENCH"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_stench_name};1"
data "Description" "{h_status_stench_desc};1"
data "Icon" "Spell_SlingPoop"
data "StackId" "FECAL_STENCH"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "Disadvantage(AttackRoll)"
data "TickFunctors" "DealDamage(1d4,Poison)"
data "StatusPropertyFlags" "InitiateCombat"

new entry "FECAL_STENCH_AURA"
type "StatusData"
data "StatusType" "BOOST"
using "FECAL_STENCH"
data "StackId" "FECAL_STENCH_AURA"

new entry "TENDERLOIN_MIASMA"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_miasma_name};1"
data "Description" "{h_status_miasma_desc};1"
data "Icon" "Spell_SlingPoop"
data "StackId" "TENDERLOIN_MIASMA"
data "AuraRadius" "3"
data "AuraStatuses" "TARGET:IF(Character() and Enemy() and not Dead()):ApplyStatus(FECAL_STENCH_AURA)"
data "StatusPropertyFlags" "IgnoreResting;DisableOverhead;DisableCombatlog;DisablePortraitIndicator"

new entry "FENT_STUPOR"
type "StatusData"
data "StatusType" "INCAPACITATED"
using "STUNNED"
data "DisplayName" "{h_status_stupor_name};1"
data "Description" "{h_status_stupor_desc};1"
data "Icon" "Spell_SlingFentanyl"
data "StackId" "FENT_STUPOR"

new entry "FENT_LEAN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_lean_name};1"
data "Description" "{h_status_lean_desc};1"
data "Icon" "Spell_FentLean"
data "StillAnimationType" "Weakened"
data "StillAnimationPriority" "Weakened"
data "StackId" "FENT_LEAN"
data "StackType" "Overwrite"
data "TickType" "StartTurn"
data "Boosts" "AC(3);Resistance(All,Resistant);Advantage(SavingThrow,Constitution);Advantage(SavingThrow,Dexterity);StatusImmunity(PRONE);StatusImmunity(SG_Prone);ActionResourceMultiplier(Movement,0,0)"
data "TickFunctors" "IF(HasPassive('RestorativeLean',context.Source)):RegainHitPoints(2d6+ConstitutionModifier)"

new entry "SIDEWALK_SCRAMBLE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_scramble_name};1"
data "Description" "{h_status_scramble_desc};1"
data "Icon" "Action_Dash_Bonus"
data "StackId" "SIDEWALK_SCRAMBLE"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "ActionResource(Movement,3,0);StatusImmunity(SG_DifficultTerrain);StatusImmunity(SG_Prone)"

new entry "PANHANDLING_SHAME"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_panhandling_name};1"
data "Description" "{h_status_panhandling_desc};1"
data "Icon" "Spell_Panhandling"
data "StackId" "PANHANDLING_SHAME"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "Disadvantage(AttackRoll);ActionResourceBlock(ReactionActionPoint)"
data "StatusPropertyFlags" "InitiateCombat"

new entry "STOLEN_PATAGONIA"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_patagonia_name};1"
data "Description" "{h_status_patagonia_desc};1"
data "Icon" "PassiveFeature_Tough"
data "StackId" "STOLEN_PATAGONIA"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "AC(1);CharacterWeaponDamage(1d4,Bludgeoning)"

new entry "POCKET_LINT_SNACK"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_pocket_lint_name};1"
data "Description" "{h_status_pocket_lint_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "StackId" "POCKET_LINT_SNACK"
data "StackType" "Overwrite"
data "Boosts" "TemporaryHP(max(1,ConstitutionModifier)+2)"
data "RemoveConditions" "not HasTemporaryHP()"
data "RemoveEvents" "OnStatusApplied"
data "StatusPropertyFlags" "IgnoreResting"

new entry "RENT_HIKE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_rent_hike_name};1"
data "Description" "{h_status_rent_hike_desc};1"
data "Icon" "Spell_Evocation_Fireball"
data "StackId" "RENT_HIKE"
data "StackType" "Overwrite"
data "TickType" "StartTurn"
data "Boosts" "AC(-2);ActionResource(Movement,-3,0)"
data "TickFunctors" "DealDamage(2d6,Psychic)"
data "StatusPropertyFlags" "InitiateCombat"

new entry "HOLD_MUSIC_311"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_hold_music_name};1"
data "Description" "{h_status_hold_music_desc};1"
data "Icon" "Spell_Enchantment_Bane"
data "StackId" "HOLD_MUSIC_311"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "ActionResourceBlock(BonusActionPoint);ActionResourceBlock(ReactionActionPoint);ActionResourceMultiplier(Movement,50,0)"
data "StatusPropertyFlags" "InitiateCombat"

new entry "TENT_CITY"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_tent_name};1"
data "Description" "{h_status_tent_desc};1"
data "Icon" "Spell_FentLean"
data "StackId" "TENT_CITY"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "TemporaryHP(15);Resistance(Bludgeoning,Resistant);Resistance(Piercing,Resistant);Resistance(Slashing,Resistant)"

new entry "SWEEP_SHELTER"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_sweep_shelter_name};1"
data "Description" "{h_status_sweep_shelter_desc};1"
data "Icon" "Skill_Fighter_SecondWind"
data "StackId" "SWEEP_SHELTER"
data "StackType" "Overwrite"
data "Boosts" "TemporaryHP(20)"
data "RemoveConditions" "not HasTemporaryHP()"
data "RemoveEvents" "OnStatusApplied"

new entry "SWEEP_COOLDOWN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_sweep_cd_name};1"
data "Description" "{h_sweep_cd_desc};1"
data "Icon" "Skill_Fighter_SecondWind"
data "StackId" "SWEEP_COOLDOWN"
data "StackType" "Overwrite"
data "RemoveEvents" "OnCombatEnded"
data "StatusPropertyFlags" "DisableOverhead"

new entry "BOARDWALK_HEAL"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_boardwalk_heal_name};1"
data "Description" "{h_status_boardwalk_heal_desc};1"
data "Icon" "Skill_Fighter_SecondWind"
data "StackId" "BOARDWALK_HEAL"
data "OnApplyFunctors" "RegainHitPoints(1d8)"
data "StatusPropertyFlags" "DisableOverhead;DisableCombatlog;DisablePortraitIndicator"

# Racial Statuses
new entry "EXISTENTIAL_DAZE"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_daze_name};1"
data "Description" "{h_status_daze_desc};1"
data "Icon" "Spell_Enchantment_CalmEmotions"
data "StackId" "EXISTENTIAL_DAZE"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "Disadvantage(AttackRoll)"

new entry "AVOCADO_BLISS"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_avocado_name};1"
data "Description" "{h_status_avocado_desc};1"
data "Icon" "Spell_AvocadoToast"
data "StackId" "AVOCADO_BLISS"
data "StackType" "Overwrite"
data "Boosts" "TemporaryHP(5)"
data "RemoveConditions" "not HasTemporaryHP()"
data "RemoveEvents" "OnStatusApplied"

new entry "SELF_ACTUALIZED"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_selfact_name};1"
data "Description" "{h_status_selfact_desc};1"
data "Icon" "Spell_Abjuration_Aid"
data "StackId" "SELF_ACTUALIZED"
data "StackType" "Overwrite"
data "Boosts" "TemporaryHP(5)"
data "RemoveConditions" "not HasTemporaryHP()"
data "RemoveEvents" "OnStatusApplied"

new entry "HANG_TEN"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_hangten_name};1"
data "Description" "{h_status_hangten_desc};1"
data "Icon" "Spell_Transmutation_Longstrider"
data "StackId" "HANG_TEN"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "ActionResource(Movement,3,0);StatusImmunity(SG_Prone);StatusImmunity(SG_DifficultTerrain)"

new entry "VIBE_CHECKED"
type "StatusData"
data "StatusType" "BOOST"
data "DisplayName" "{h_status_vibe_name};1"
data "Description" "{h_status_vibe_desc};1"
data "Icon" "Spell_Enchantment_Tasha'sHideousLaughter"
data "StackId" "VIBE_CHECKED"
data "StackType" "Overwrite"
data "TickType" "EndTurn"
data "Boosts" "ActionResourceBlock(BonusActionPoint);ActionResourceBlock(ReactionActionPoint);ActionResourceMultiplier(Movement,50,0)"
"""
    with open(os.path.join(stats_dir, "Status_BOOST.txt"), "w", encoding="utf-8") as f:
        f.write(status_content)

    # Passive.txt
    passive_content = f"""new entry "StreetGritDefence"
type "PassiveData"
using "UnarmouredDefence_Barbarian"
data "DisplayName" "{h_street_grit_name};1"
data "Description" "{h_street_grit_desc};1"
data "ExtraDescription" ""

new entry "SidewalkImmunity"
type "PassiveData"
data "DisplayName" "{h_passive_immunity_name};1"
data "Description" "{h_passive_immunity_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Properties" "Highlighted"
data "Boosts" "StatusImmunity(SG_Poisoned);StatusImmunity(SG_Disease);Resistance(Poison,Resistant)"

new entry "Proposition47"
type "PassiveData"
data "DisplayName" "{h_prop47_name};1"
data "Description" "{h_prop47_desc};1"
data "Icon" "Action_SneakAttack_Melee"
data "Properties" "Highlighted"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "IsMeleeAttack()"
data "StatsFunctors" "ApplyStatus(SELF,STOLEN_PATAGONIA,100,2)"

new entry "PocketLintBuffet"
type "PassiveData"
data "DisplayName" "{h_pocket_lint_name};1"
data "Description" "{h_pocket_lint_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Properties" "Highlighted;OncePerTurn"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "HasStatus('FECAL_STENCH',context.Target) or HasStatus('FECAL_STENCH_AURA',context.Target)"
data "StatsFunctors" "ApplyStatus(SELF,POCKET_LINT_SNACK,100,-1)"

new entry "StreetHustle"
type "PassiveData"
data "DisplayName" "{h_hustle_name};1"
data "Description" "{h_hustle_desc};1"
data "Icon" "PassiveFeature_FastMovement"
data "Properties" "Highlighted"
data "Boosts" "ActionResource(Movement,3,0);Initiative(3)"

new entry "RestorativeLean"
type "PassiveData"
data "DisplayName" "{h_passive_lean_heal_name};1"
data "Description" "{h_passive_lean_heal_desc};1"
data "Icon" "Skill_Fighter_SecondWind"
data "Properties" "Highlighted"

new entry "UnkillableVagrant"
type "PassiveData"
data "DisplayName" "{h_unkillable_name};1"
data "Description" "{h_unkillable_desc};1"
data "Icon" "PassiveFeature_Tough"
data "Properties" "Highlighted"
data "Boosts" "Resistance(Bludgeoning,Resistant);Resistance(Piercing,Resistant);Resistance(Slashing,Resistant);Tag(FRIGHTENED_ADV);Tag(CHARMED_ADV)"

new entry "EncampmentSweepInstinct"
type "PassiveData"
data "DisplayName" "{h_encampment_sweep_name};1"
data "Description" "{h_encampment_sweep_desc};1"
data "Icon" "Skill_Fighter_SecondWind"
data "Properties" "Highlighted"
data "StatsFunctorContext" "OnDamaged"
data "Conditions" "Combat() and HasHPPercentageLessThan(50) and not HasStatus('SWEEP_COOLDOWN') and not HasStatus('FENT_LEAN')"
data "StatsFunctors" "ApplyStatus(SELF,FENT_LEAN,100,2);ApplyStatus(SELF,SWEEP_SHELTER,100,-1);ApplyStatus(SELF,SWEEP_COOLDOWN,100,-1)"

new entry "LeanDamageReflect"
type "PassiveData"
data "DisplayName" "{h_passive_lean_reflect_name};1"
data "Description" "{h_passive_lean_reflect_desc};1"
data "Icon" "Spell_Enchantment_DissonantWhispers"
data "Properties" "Highlighted"
data "StatsFunctorContext" "OnAttacked"
data "Conditions" "IsMeleeAttack() and HasDamageEffectFlag(DamageFlags.Hit) and HasStatus('FENT_LEAN',context.Target)"
data "StatsFunctors" "DealDamage(SWAP,2d10,Psychic,Magical)"

# Subclass passives
new entry "BiohazardStench"
type "PassiveData"
data "DisplayName" "{h_biohazard_aura_name};1"
data "Description" "{h_biohazard_aura_desc};1"
data "Icon" "Spell_Conjuration_StinkingCloud"
data "Properties" "Highlighted"
data "StatsFunctorContext" "OnCreate;OnCombatStarted;OnTurn;OnShortRest;OnLongRest"
data "StatsFunctors" "ApplyStatus(SELF,TENDERLOIN_MIASMA,100,-1)"

new entry "ToxicAdaptation"
type "PassiveData"
data "DisplayName" "{h_toxic_name};1"
data "Description" "{h_toxic_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Properties" "Highlighted"
data "Boosts" "IgnoreResistance(Poison,Resistant);CharacterWeaponDamage(1d6,Poison)"

new entry "PatientZero"
type "PassiveData"
data "DisplayName" "{h_patient_zero_name};1"
data "Description" "{h_patient_zero_desc};1"
data "Icon" "Spell_Conjuration_StinkingCloud"
data "Properties" "Highlighted"
data "Boosts" "CharacterWeaponDamage(2d6,Poison);Resistance(Poison,Immune)"

new entry "MuscleBeachJuice"
type "PassiveData"
data "DisplayName" "{h_juiced_name};1"
data "Description" "{h_juiced_desc};1"
data "Icon" "PassiveFeature_Tough"
data "Properties" "Highlighted"
data "Boosts" "CharacterWeaponDamage(1d8,Bludgeoning);AC(2)"

new entry "KingOfTheBoardwalk"
type "PassiveData"
data "DisplayName" "{h_boardwalk_king_name};1"
data "Description" "{h_boardwalk_king_desc};1"
data "Icon" "PassiveFeature_ImprovedCritical"
data "Properties" "Highlighted"
data "Boosts" "ReduceCriticalAttackThreshold(2)"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "IsMeleeAttack() and Enemy() and Character()"
data "StatsFunctors" "ApplyStatus(SELF,BOARDWALK_HEAL,100,0)"

new entry "LastTrainPhantom"
type "PassiveData"
data "DisplayName" "{h_last_train_name};1"
data "Description" "{h_last_train_desc};1"
data "Icon" "PassiveFeature_FastMovement"
data "Properties" "Highlighted"
data "Boosts" "ActionResource(Movement,4.5,0);StatusImmunity(SG_DifficultTerrain)"

# Racial Passives
new entry "EarthquakeSense"
type "PassiveData"
data "DisplayName" "{h_earthquake_name};1"
data "Description" "{h_earthquake_desc};1"
data "Icon" "PassiveFeature_Mobile_DashAcrossDifficultTerrain"
data "Properties" "Highlighted"
data "Boosts" "StatusImmunity(SG_Prone)"

new entry "Veteran405"
type "PassiveData"
data "DisplayName" "{h_veteran405_name};1"
data "Description" "{h_veteran405_desc};1"
data "Icon" "Spell_Abjuration_FreedomOfMovement"
data "Properties" "Highlighted"
data "Boosts" "StatusImmunity(SLOW);StatusImmunity(SG_Restrained)"

new entry "Passive_SiliconiteSynergy"
type "PassiveData"
data "DisplayName" "{h_synergy_name};1"
data "Description" "{h_synergy_desc};1"
data "Icon" "Spell_Enchantment_DissonantWhispers"
data "Properties" "Highlighted;OncePerTurn"
data "StatsFunctorContext" "OnDamage"
data "Conditions" "IsWeaponAttack()"
data "StatsFunctors" "DealDamage(1d4,Psychic)"

new entry "Passive_SmogLungs"
type "PassiveData"
data "DisplayName" "{h_smog_lungs_name};1"
data "Description" "{h_smog_lungs_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Properties" "Highlighted"
data "Boosts" "Tag(POISONED_ADV);StatusImmunity(SG_Disease)"

new entry "Passive_HeatIndexMastery"
type "PassiveData"
data "DisplayName" "{h_heat_index_name};1"
data "Description" "{h_heat_index_desc};1"
data "Icon" "Item_CONS_Potion_Fire_Resistance_2"
data "Properties" "Highlighted"
data "Boosts" "StatusImmunity(BURNING)"

# 3rd Gender / California Identity Passives
new entry "CaliforniaIdentity_Dude"
type "PassiveData"
data "DisplayName" "{h_id_dude_name};1"
data "Description" "{h_id_dude_desc};1"
data "Icon" "Spell_Enchantment_CalmEmotions"
data "Properties" "Highlighted"
data "Boosts" "Skill(Persuasion,2);Tag(FRIGHTENED_ADV)"

new entry "CaliforniaIdentity_Founder"
type "PassiveData"
data "DisplayName" "{h_id_founder_name};1"
data "Description" "{h_id_founder_desc};1"
data "Icon" "PassiveFeature_FastMovement"
data "Properties" "Highlighted"
data "Boosts" "Initiative(2);Advantage(Skill,Deception)"

new entry "CaliforniaIdentity_Oat"
type "PassiveData"
data "DisplayName" "{h_id_oat_name};1"
data "Description" "{h_id_oat_desc};1"
data "Icon" "PassiveFeature_PurityOfBody"
data "Properties" "Highlighted"
data "Boosts" "StatusImmunity(SG_Poisoned)"

new entry "CaliforniaIdentity_SelfActualized"
type "PassiveData"
data "DisplayName" "{h_id_self_name};1"
data "Description" "{h_id_self_desc};1"
data "Icon" "Spell_Abjuration_Aid"
data "Properties" "Highlighted"
data "StatsFunctorContext" "OnCombatStarted"
data "StatsFunctors" "ApplyStatus(SELF,SELF_ACTUALIZED,100,-1)"

new entry "CaliforniaIdentity_Algorithm"
type "PassiveData"
data "DisplayName" "{h_id_algo_name};1"
data "Description" "{h_id_algo_desc};1"
data "Icon" "PassiveFeature_ReliableTalent"
data "Properties" "Highlighted"
data "Boosts" "RollBonus(SavingThrow,1)"
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
