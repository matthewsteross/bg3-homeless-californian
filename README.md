# Baldur's Gate 3 - Homeless Californian Class Mod

## Public playtest

[Download the playtest (October 15 build, v0.4.0)](https://github.com/matthewsteross/bg3-homeless-californian/releases/tag/playtest-2026-10-15-v0.4.0) · [Nexus Mods page](https://www.nexusmods.com/baldursgate3/mods/25761) · [Report a bug](https://github.com/matthewsteross/bg3-homeless-californian/issues/new/choose)

**Throw bricks. Weaponise furniture. Make public transit everybody else's problem.**

Looking for PC testers for a ridiculous Constitution-based class with four
subclasses: Tenderloin poison, Venice furniture melee, BART repositioning, and Overpass Riverbed Dweller flood control
(the Overpass subclass is new in v0.4.0; see
[the v0.4.0 section](#additions-in-v040-not-yet-play-tested)).
Try one subclass for ten minutes and tell us one thing that broke—or one thing
that worked. [Start the short tester checklist](TESTING.md).

**Which version is which:** the public download (release `playtest-2026-10-15-v0.4.0`, also the Nexus file, version 0.4.0) is
**v0.4.0**: v0.3.0 plus the Overpass Riverbed Dweller subclass, round 2 spells, new Street Trade and Junk Doctrine options,
NIMBY Zoning Defense, Bakersfield Tule Fog, a blue tarp prop, Curb Alert with four junk items, and more custom icons (listed in
[the v0.4.0 section](#additions-in-v040-not-yet-play-tested)). v0.3.0 (release `playtest-2026-10-15`) and the older October 12 and 13 builds
remain on their own release pages. **Honest status:** file-level checks pass (110 validation tests, validator PASS), and an in-game
data check on 2026-10-15 confirmed that every spell, status and passive loads, the new items and props resolve, Curb Alert grants its
four items, Blue Tarp Lean-To spawns one tarp at the caster's feet, and Storm Drain Flash Flood, Sprinkler Violation, Drainage Ditch
Dig-In and Bakersfield Tule Fog create their ground effects. Playing it is still mostly untested: damage, saves, Junk costs, level-up
grants on a real Homeless Californian character, tarp facing and collision, the Kombucha override and balance have not been checked.
Only level 12 and the cart had been confirmed by hand earlier. The Nexus page is live; the in-game (mod.io)
listing is still pending approval, so the mod is not yet confirmed in the in-game mod menu.

**Newer than the download:** the repository is ahead of v0.4.0. Rounds 4 to 10 (50 spells in rounds 4 to 9, 2 Street Trades, 2 Junk Doctrines,
4 contraband items and a pile of statuses; round 10 adds 9 spells, a rare armour item and a passive), plus nine custom 3D props (a Caltrans "Lane Closed Ahead" barricade, a Pop-Up Encampment Tent, a Dockless Scooter Graveyard,
a Broken-Down Robotaxi, a Tipped-Over Festival Porta-Potty, and four round 10 props: a Hostile Architecture Spike Bench, a Sparking Utility Pole, an Evicted Studio Spin Bike and a Sidewalk Cooler Bonfire, each with its own spell), are **source-only: in the repo and the local pak, not in the v0.4.0 download, and not
play-tested**. They are listed in [their own section](#source-only-rounds-4-10-not-in-the-v040-download-not-play-tested). Nothing in the
public download or on Nexus has changed.

Intentionally overpowered: this is a ridiculous class with actions, saves,
Junk costs and rest cooldowns, rather than an attempt at vanilla balance.
The starting-area test confirmed icons after a reload and castability of
available spells. Full effect, progression and compatibility testing continues.
The human (Matthew, @themadhattermsr) directs the design; Claude, Codex, Antigravity/Gemini, and the local model (Qwen) assisted with code, architecture, testing and ideation. Gemini generated the custom icons and banners, and the shopping cart model is also AI-generated (the blue tarp model is too, and so are the five older source-only props, the barricade, the tent, the scooter graveyard, the robotaxi and the porta-potty (the four round 10 props are Blender-built); see [Contributors](#-contributors--ai-pair-programming-team)). Nothing here is hand-made by a human artist.

This download is the manual PC package. It is not yet a mod.io/in-game or
console release. Use a separate test save; respec or start a new character if
new progression grants are missing. Keep the mod installed on saves that use it.

## Capstone, Street Trade, Doctrines and the Hustle kit (v0.2.0 and later; mostly NOT yet play-tested)

The October 13 build (v0.2.0) and later builds contain a much larger kit than the October 12
playtest ZIP: the level-12 **Squatter's Rights** capstone, a **Street Trade** selector, **Junk Doctrines**, and the
**Hustle kit** (Guilt Trip, Beg, Public Scene, Trapped in the Invisible Box, Bucket Drum Solo, Compassion Burnout,
Punctured Lithium Cell, Sublet, Everybody Knows This Guy, plus the Homeless Fatigue and Breadcrumbed statuses).
**Honest status:** file-level checks and 39 validation tests passed at the v0.3.0 release (v0.4.0 has 110, see the v0.4.0 section). In game, only "a character can reach level 12 without a catastrophic failure" has been
confirmed; individual abilities have not been tested, and **Beg** (gold from non-hostile NPCs) is the most experimental.
Guilt Trip, Public Scene and Compassion Burnout now work on any enemy and add a bonus when the target is Socially
Shamed or Homeless Fatigued (fixed since v0.2.1; the old v0.2.0 download requires the status and can show "Invalid Target"). Use a new character or a respec for new grants. Test routes for the new
abilities are at the bottom of [TESTING.md](TESTING.md).

## October 12 Codex expansion — gameplay review in progress

This build keeps the original class, race, UUID, and existing abilities, and adds a
scavenged **Junk** supply shared by a new toolkit. File checks are required
before installation; this section is not an in-game success claim.

| Unlock | Addition | Intended behavior |
|---|---|---|
| Class 1 | Junk | 3 charges, replenished on short rest; 5 at class level 5, 7 at 9 |
| Class 1 | Emotional Support Brick | Action + 1 Junk; ranged attack, 2d6 + CON Bludgeoning; failed CON save causes Dazed for 1 turn |
| Class 1 | Bag of Other Bags | Action + 1 Junk; 2.5 m Web surface for 3 turns, concentration; affects allies too |
| Class 1 | Load-Bearing Lawn Chair | Bonus action + 1 Junk; +2 AC, advantage on STR saves, Prone immunity for 2 turns |
| Class 1 | Unclaimed Wardrobe | Action, once per long rest; optional ruined robe and cloak placed in inventory |
| Class 2 | Dumpster Dive | Action outside combat, once per short rest; restores 2 Junk, up to capacity |
| Tenderloin 3 | Pigeon Witness Protection | Action + 1 Junk, once per short rest; summons a vanilla raven familiar |
| Venice 3 | Heirloom Furniture | Action + 1 Junk; melee hit for 3d6 + CON Bludgeoning, failed STR save knocks Prone; hit prepares a follow-up shiv |
| Venice follow-up | Chair-Leg Shiv | Bonus-action melee attack for 2d6 + CON Piercing; consumes the temporary unlock |
| BART 6 | Wrong Platform | Action + 1 Junk, once per short rest; failed WIS save swaps your position with an enemy |
| Class 7 | Moving Day | While leaning: free, once per short rest; ends Lean, +6 m movement and difficult-terrain immunity for 1 turn, and scatters a 2.5 m ring of rubbish (difficult terrain, 2 turns) where you stood (ring not yet verified in game) |

All ten local expansion abilities now have custom Gemini-generated icons,
including matching icons for the Chair, Moving Day, and ready-Shiv statuses.
The atlas grows automatically as new art is added. The abilities still use
existing animations. The chair
abilities do not display a new chair mesh. The "pigeon" is visibly a raven, and
the wardrobe uses existing robe/cloak visuals, not a custom safety vest. Guns are future work. There are exactly two custom meshes: the
Abandoned Cart (added in v0.3.0, see the v0.3.0 additions below) and the blue tarp lean-to (added in v0.4.0; it spawns in game but its look has not been checked; see the v0.4.0 section below). The chair, guns, pigeon and junk items are still not custom meshes. The level-12
Squatter's Rights capstone, Street Trade and Junk Doctrines are described in the
section above.

**Honest status (October 12 build):** source and package checks and 14 validation tests passed at the time.
Matthew confirmed starting-area icons after reload and castability of available
spells; individual effects still need testing. Wrong Platform's enemy swap is
the most experimental addition. The installed/published icon build is
14,932,869 bytes, SHA256
`552ae557a794eb7a0a9799dfb2ca37421548f58bf5587533f7853d93263d63fc`
(the October 12 build).

For existing characters, respec into the class or start a new test character
to receive new progression grants. Confirm the UI and grants in-game; do not
assume updating a package retroactively reapplies already-earned levels.

Build-only: `python build.py`. The build now runs the local validator before
an optional install. Run the full suite with `python -m unittest discover -s validation -q`
(110 tests in v0.4.0, including the deliberate-corruption checks; 39 at the v0.3.0 release; 322 on the current source, which includes the source-only rounds 4-10 and the nine source-only props). The saved original
package can restore the previous build with BG3 closed. Keep the candidate
out of co-op until both players intentionally use the same package.

A custom class and race mod for **Baldur's Gate 3** introducing the **Homeless Californian** class (levels 1-12; four subclasses) and the **Californian** race (three subraces, a California identity / gender selector, and a restricted garish look).

---

## Additions in v0.3.0 (after v0.2.0; NOT yet verified in game)

These are in the public v0.3.0 download but not in the older v0.2.0 download. Everything
below is **not yet verified in game**; numbers are copied from the generated game data.

| Unlock | Addition | Intended behavior |
|---|---|---|
| Class 7 | I Was Here First | Action + 1 Junk, once per short rest; 2 turns of +2 AC, advantage on Constitution saves and Prone immunity, and a 2.5 m ring of rubbish (difficult terrain) around you |
| Class 7 | Moving Day (updated) | Leaving Fent Lean now also scatters a 2.5 m ring of rubbish (difficult terrain) where you stood |
| Tenderloin 3 | Pigeon Lunch Rush | Granted to the summoned raven: 1 Action, once per short rest, 4 m radius; failed Dexterity save gives Disadvantage on attack rolls and Dexterity saves for 1 turn |
| Class 2 | Dumpster Dive (updated) | As before (restores 2 Junk), plus pulls a piece of cheese and a half-eaten apple into your inventory |
| Street Trade (class 2) | Busker, Can Collector | Busker: advantage on Performance and Insight. Can Collector: advantage on Athletics and Sleight of Hand (alongside Scrounger, Fixer, Lookout) |
| Junk Doctrine (class 4) | Twitchy | +3 Initiative (alongside Hoarder, Fortifier, Runner) |
| BART 6 | Fare Evasion Audit | Action + 1 Junk, once per short rest, 9 m; failed Wisdom save leaves the target Fined for 2 turns (-3 m movement, no Reactions) |
| Venice 6 | Sublet | Action + 1 Junk; an ally within 9 m gets the Lawn Chair buff (+2 AC, advantage on Strength saves, Prone immunity) for 2 turns |
| Class 4 | Coat-Hanger Slim Jim | Action + 1 Junk, 1.5 m; unlocks a door or container (not magical locks) |
| Tenderloin 6 | Curbside Needle Exchange | Action + 1 Junk, once per short rest, 1.5 m; a living ally is cured of Poisoned, Disease, Blinded and Paralysed and regains `2d6 + CON` HP |
| Venice 3 | Abandoned Cart | Bonus action + 1 Junk, once per short rest, 6 m; spawns a shopping-cart prop on the ground (see below) |
| Venice 10 | Chair Check | Action + 1 Junk, once per short rest; melee weapon attack for weapon damage plus 2d8 Bludgeoning; failed Strength save knocks the target Prone |

**Abandoned Cart** (`HC_Target_AbandonedCart`): the cart model is an AI-generated asset. A Claude Sonnet agent wrote procedural Python
geometry scripts (`assets/models/HC_ShoppingCart/`; Blender is used only for previews), and the result was converted with LSLib Divine.
It was the only custom mesh in v0.3.0 (v0.4.0 adds a second, the blue tarp; see below). What was verified live in game on 2026-10-14, and only this: the stat, template and
localization resolve, the cart spawns and is visible, and casting it spawns exactly one cart. **Not verified:** facing,
collision, the Junk cost on a real Homeless Californian character, and how it looks in good light.

The Californian race also gained racial progression (levels 1, 3 and 5); see [the race section](#-californian-race).
At the v0.3.0 release the repository had 39 passing validation tests (file-level checks only); v0.4.0 has 110 (see below).

---

## Additions in v0.4.0 (NOT yet play-tested)

Everything in this section is new in the public v0.4.0 download (and the Nexus file), and was not in v0.3.0. It has passed file-level
checks (110 validation tests, 39 of them from before these additions, validator PASS) and an in-game **data** check on 2026-10-15,
which confirmed that all spells, statuses and passives load with their text, that the new items and the blue tarp prop resolve, that
Curb Alert grants its four items, that Blue Tarp Lean-To spawns one tarp at the caster's feet, and that Storm Drain Flash Flood,
Sprinkler Violation, Drainage Ditch Dig-In and Bakersfield Tule Fog create their ground effects. Nobody has played it: damage and save
outcomes, Junk costs, level-up grants on a real Homeless Californian character, tarp facing, collision and look, the Kombucha heal
override, item equip and visuals, and balance are all untested. Numbers are copied from the generated game data and the
localization text. A new character or respec is needed to receive the grants.

**Fourth subclass: Overpass Riverbed Dweller** (internal name `OverpassRiverbedDweller`). The level 12 capstone is included.

| Unlock | Addition | Intended behavior |
|---|---|---|
| Overpass 3 | Concrete Bank Traction | Passive: immune to difficult terrain (mud, webs, vines) |
| Overpass 3 | Storm Drain Flash Flood | Action + 1 Junk, once per short rest, 9 m line; creatures that are not allies make a Strength save, taking `2d8 + CON` Bludgeoning and falling Prone for 1 turn on a failure, or half damage on a success; leaves standing water for 2 turns. The line shape is borrowed from Thunderwave and is not verified |
| Overpass 3 | Blue Tarp Lean-To | Bonus action + 1 Junk, once per short rest, 3 m radius; you and allies get Blue Tarp Cover (+1 AC, advantage on Dexterity saves) for 2 turns, and fire on the ground is doused. It also spawns a custom blue tarp lean-to prop (see below) |
| Overpass 6 | Culvert Siphon | Action + 1 Junk, once per short rest, 9 m; you or an ally (not undead or construct) regain `2d6 + CON` HP and stop Burning, and the ground is doused |
| Overpass 6 | Underpass Climate Control | Passive: Resistance to Lightning and Cold damage |
| Overpass 10 | Rebar Anchor | Passive: +1 AC and advantage on Strength saving throws |
| Overpass 10 | Drainage Ditch Dig-In | Action + 1 Junk, once per short rest, 9 m, 3 m radius: turns the ground into Mud for 3 turns (difficult terrain for everyone but you, thanks to Concrete Bank Traction) |
| Overpass 12 | Squatter's Rights: Spillway Sovereignty | Bonus action, once per long rest; restores all Junk; lasts 3 turns: +2 AC and +3 m movement, and the ground within 4 m turns to mud (difficult terrain) for 3 turns |

**New choices and a racial passive:**

| Unlock | Addition | Intended behavior |
|---|---|---|
| Street Trade (class 2) | Squeegee Technician | Advantage on Intimidation and Insight ability checks (a sixth option beside Scrounger, Fixer, Lookout, Can Collector, Busker) |
| Street Trade (class 2) | Notary | Advantage on Investigation and Persuasion ability checks (a seventh option; Street Trade now has 7 in source) |
| Junk Doctrine (class 4) | Cardboard Insulator | Resistance to Cold damage (a fifth option beside Hoarder, Fortifier, Runner, Twitchy) |
| Junk Doctrine (class 4) | Tinfoil Deflector | Resistance to Psychic damage (a sixth option; Junk Doctrines now number 6 in source) |
| Californian race 1 | NIMBY Zoning Defense | Passive: advantage on saving throws against being Charmed (granted through the `CHARMED_ADV` tag; the tag's in-game behavior is not verified) |

**Round 2: five spells and one status** (generated by `hc_round2.py`). Numbers are copied from
`HC_Spells_Round2.txt`, `HC_Status_Round2.txt` and the localization text. Four are base-class spells (at most one new spell per
class level); Bakersfield Tule Fog is a racial spell. All of them have custom Gemini-generated icons.

| Unlock | Addition | Intended behavior |
|---|---|---|
| Class 2 | Sprinkler Violation | Bonus action + 1 Junk, once per short rest, 9 m; a 2 m radius water surface lasts 2 turns and creatures in it become Wet for 3 turns. Donor: Create Water |
| Class 4 | Catalytic Converter Sawzall | Action + 1 Junk, once per short rest, 1.5 m; melee spell attack for `3d8` Slashing, and a hit applies Decatted Exhaust for 2 turns. Donor: Inflict Wounds |
| Class 8 | One-Star Citation | Action + 1 Junk, no cooldown, 9 m; the target takes `2d8` Psychic damage, and a failed Wisdom save leaves it Baned for 2 turns. The damage is written to apply whether or not the save succeeds (not verified). Donor: Vicious Mockery |
| Class 11 | HOV Lane | Bonus action + 1 Junk, once per short rest; teleport up to 12 m to a place you can see. Donor: Misty Step. It does not leave mud where you stood: that was left out because no vanilla spell places a surface at the teleport source |
| Californian race, Inland Emperor 3 | Bakersfield Tule Fog | Action (no Junk), once per short rest, 9 m; a 4.5 m radius fog cloud lasts up to 10 turns and needs concentration (same mechanics as vanilla Fog Cloud; an earlier 2-turn, no-concentration version showed no fog in game). Donor: Fog Cloud |
| Status (from Sawzall) | Decatted Exhaust | -2 AC and no Reactions for 2 turns as applied by Sawzall; flagged to initiate combat |

**Round 3: a custom blue tarp prop and four junk items** (generated by `hc_tarp.py` and `hc_junk_items.py`). The tarp spawn and the
item grant were confirmed by the 2026-10-15 data check; how they look and behave has not been seen.

**Blue tarp lean-to prop** (`HC_OBJ_BlueTarp`, spawned by Blue Tarp Lean-To): a blue plastic tarp over a ridge pole on two rebar uprights, with
grommets, rope guy lines, stakes and bricks, about 2.46 m wide and 1.4 m tall (2,544 triangles, 512 px base colour texture). It is the second custom
mesh in the mod after the cart, and, like the cart, it is an AI-generated asset: a Claude agent wrote the procedural Python geometry and the procedural
texture painting (`assets/models/HC_BlueTarp/`; Blender is used only for previews), and the result was converted with LSLib Divine and conformed to a
vanilla skeleton. It reuses the cart's pipeline (visual resource, root template, Object stat, and a `GROUND:Spawn` on a spell). The tarp is a static prop that cannot be moved or picked up.
The cart's spell is a ground-target spell, whereas this one is a self-centred Shout. The 2026-10-15 data check confirmed that casting it spawns
exactly one tarp prop, at the caster's feet, and applies Blue Tarp Cover. **Still unverified:** its facing, its collision bounds, its scale and how the texture looks.

**Curb Alert and four junk items:** Curb Alert (`HC_Shout_CurbAlert`) is a base-class spell granted at class level 6, alongside Public Scene (it is the only new spell added at that level in v0.4.0). Action, once per long rest, no Junk cost, self only; it puts one each of the four items below into your
inventory, and you equip or use them yourself. It has a custom Gemini-generated icon. Each item is an HC-only stat that inherits a vanilla stat and
vanilla root template, so meshes and textures are borrowed from the donor and no custom art is involved. All four have a gold value of 0.

| Item | Donor | Rarity | Intended behavior |
|---|---|---|---|
| Caltrans Detour Sign | Greatclub | Common | A plain renamed Greatclub with the donor's numbers; no extra effect |
| Duct-Taped High-Tops | Leather Boots | Common | +1.5 m movement while worn |
| Lukewarm Gas Station Kombucha | Potion of Healing | Common | Drink to heal `2d4 + 2` HP and gain Kombucha Buzz (+3 m movement) for 2 turns |
| Tin-Foil Sun Visor | Leather Helmet | Uncommon | Advantage on Wisdom saving throws while worn |

The 2026-10-15 data check confirmed that the four items resolve and that Curb Alert puts all four in the caster's inventory. What is least certain about the items: whether the Kombucha's replacement of the donor potion's use action works (the template restates that one action so the potion applies
its own status), whether the items equip correctly, and whether the donors' icons, names and tooltips show up as intended. The boots and
visor are donor armour, so their armour class and proficiency requirements are inherited and were not checked in game.

**What is least certain:** the damage and Prone outcome of the Storm Drain Flash Flood zone (its water surface was seen along the whole 2-8 m line in the data check);
whether the Mud surface from Spillway Sovereignty slows enemies without trapping you; and the NIMBY tag. The Culvert Siphon
borrows the cast animation of vanilla Healing Word so a 9 m cast is not a touch spell, which is also untested in game.
Of the round 2 additions, the donors' animations and sound/visual effects are inherited unchanged: Sawzall keeps Inflict Wounds' necrotic cast and hit effects, and whether Sprinkler Violation's Wet reaches only creatures inside the 2 m radius is untested. The four new Overpass spells (Storm Drain Flash Flood, Blue Tarp Lean-To, Culvert Siphon and the Spillway Sovereignty capstone) have custom Gemini-generated icons; the Overpass subclass reuses the shared class crest, the Cardboard Insulator reuses the Cardboard Insulation icon, and the other new passives use vanilla icons. Drainage Ditch Dig-In, Curb Alert and the round 2 spells also have custom Gemini-generated icons; the junk items use their donors' vanilla icons.

---

## Source-only rounds 4-10 (not in the v0.4.0 download, not play-tested)

**Read this first:** everything in this section is in the repository and in the locally built `dist/HomelessCalifornian.pak`, and it is
**not** in the public v0.4.0 download or the Nexus file. You cannot get it by downloading the release. **Nobody has played any of it.**
The only checking so far is file-level: 848 unit tests and the pak validator pass on the current source, which proves the
files agree with each other and with vanilla data, not that a single spell does what it says. Numbers are copied from the generated game
data and the localization text.

Two honesty notes. First, the 28 spells from rounds 5, 6 and 7, the 10 round 8 spells, the 10 round 9 spells, the nine round 10 spells, the four round 10 prop spells and the five earlier prop spells (barricade, tent, scooters, robotaxi and porta-potty) currently use **placeholder vanilla icons** (the Gemini art for them has not
been generated yet; the icon keys are registered, so the art will be picked up when it exists); only Freeway Directions and Permit Pending from round 4 have custom icons. Second, most of these are written as
"failed save = full damage plus the nasty status, successful save = half damage", and the status duration, surface and Prone behaviour is
untested. Expect a few to be wrong the first time they meet an actual goblin.

Most need a **new character or a respec** to receive the grants. All are once per short rest unless the table says otherwise, and "1 Junk" is
the class resource.

### Spells (50 in rounds 4-9, plus nine in round 10; the prop spells are in the props section below)

| Spell | Where granted | Intended behaviour |
|---|---|---|
| **Round 4** | | |
| Freeway Directions | Californian race, level 1 | Action, 9 m. Wisdom save or Incapacitated for 1 turn, without Prone. "Trust the 101. There is no 101 at this hour." |
| Permit Pending | Class 5 | Action + 1 Junk, 18 m. Wisdom save or a 3-stack countdown (no Bonus Action, -3 m movement); each successful end-of-turn save removes a stack and the last gives 1 turn of Slow. Targets above 100 current HP have advantage on the saves |
| Weather Complaint (passive) | Californian race, level 1 | Purely cosmetic: when you become Wet, Chilled, or step on ice, you complain overhead ("Is this a storm??", "It's literally 60 degrees.", "I didn't bring a jacket."), once per weather type per rest |
| **Round 5** | | |
| 3 AM Sidewalk Lawnmower Disassembly | Class 6 | Bonus action + 1 Junk. 2 turns of +4.5 m movement, +2 AC, advantage on Dexterity saves and Sleight of Hand, Sleep immunity |
| Live Copper Wire Harvest | Class 7 | Action + 1 Junk. Melee spell attack at 1.5 m: `3d8` Lightning + `1d8` Slashing, -2 AC and no Reactions for 2 turns, electrified puddle |
| Prop 47 '$949' Calculator | Class 9 | Action + 1 Junk, 9 m. You pocket 5 gold and get +3 m movement and Prone immunity for 1 turn; target makes a Wisdom save or takes `3d8` Psychic and is Dazed for 2 turns (half on a success) |
| Jailbroken E-Scooter Hit-and-Run | Class 10 | Action + 1 Junk, 9 m by 3 m rectangle ahead of you. You get +3 m movement for 1 turn; Dexterity save or `3d8 + CON` Bludgeoning + `1d8` Thunder and Prone (half on a success) |
| Tin-Foil Bus Shelter Hotbox | Tenderloin 6 | Action + **2 Junk**, 3 m radius. Constitution save or `3d8` Poison + `2d6` Psychic and Fent Stupor for 1 turn (half on a success); leaves fog for 2 turns |
| Aggressive Mixtape & Sunset Bongos | Venice 6 | Action + 1 Junk, 9 m. Wisdom save or `2d8` Thunder + `2d8` Psychic and Socially Shamed for 2 turns, and you collect 5 gold (half on a success) |
| Damp Cloth BART Seat Mystery Stain | BART 6 | Action + 1 Junk, 9 m. Constitution save or `3d8` Poison + `1d8` Acid and Fecal Stench for 2 turns (half on a success) |
| Stolen Propane Tank Overpass Cookout | Overpass 6 | Bonus action + 1 Junk. Regain `1d8 + CON` HP; 2 turns of Cold resistance and `+1d6` Fire weapon damage; a 2 m patch of fire around you for 2 turns (you stand in it too) |
| 'Actually, The Term Is Unhoused Neighbor' | Californian race, level 1 | Action (no Junk), 9 m. Wisdom save or `2d6` Psychic and Cancelled for 2 turns (disadvantage on attack rolls, no Reactions); `1d6` on a success |
| $24 Erewhon Sea-Moss & Ozempic Glaze | Californian race, level 1 | Bonus action (no Junk), **once per long rest**. Regain `1d8 +` spellcasting modifier HP; 2 turns of +2 AC, +3 m movement and advantage on Constitution saves |
| **Round 6** | | |
| Fake Lease & Sovereign Citizen Lien | Class 5 | Action + 1 Junk, 9 m. Wisdom save or `2d8` Psychic and cannot move, with disadvantage on attack rolls, for 2 turns (half on a success) |
| Oakland Flea Market Stolen Tool Table | Class 8 | Action (no Junk), **once per long rest**. Puts four items in your inventory (below) |
| Six-Foot CVS Receipt Ward | Class 11 | Bonus action + 1 Junk. 2 turns of +2 AC and resistance to Slashing and Piercing |
| 3 AM Oakland Intersection Sideshow | BART 6 | Action + 1 Junk, 9 m. Dexterity save or `3d8` Bludgeoning + `1d8` Fire and Prone (half on a success); 2.5 m tire-smoke cloud for 2 turns |
| Malibu Trust-Fund Surfboard Localism | Beachborn 3 | Action, melee spell attack at 1.5 m: `2d8` Bludgeoning + `1d6` Cold, shoves the target 4 m, disadvantage on its attack rolls for 2 turns |
| 9 AM Zoom All-Hands 15% Layoff | Siliconite 3 | Action, **once per long rest**, 6 m. You get +2 AC and advantage on Wisdom saves for 2 turns; enemies make a Wisdom save or take `2d8` Psychic and lose 3 m movement and Reactions for 2 turns (half on a success) |
| Hemet Garage 2-Liter Shake-and-Bake Rupture | Inland Emperor 5 | Action, **once per long rest**, 3 m radius. Dexterity save or `3d8` Fire + `2d8` Poison and Burning for 2 turns (half on a success); fire on the ground |
| **Round 7** | | |
| Unsolicited Red-Light Dirty Squeegee | Class 1 | Action + 1 Junk. Melee spell attack at 1.5 m: `2d6` Acid + `1d6` Bludgeoning and Blinded for 1 turn. "That will be five dollars, cash or Venmo." |
| Amazon Fake Service-Animal Vest | Class 2 | Bonus action + 1 Junk. 2 turns of +2 AC and advantage on Deception and Intimidation |
| Fermented Trucker 'Way of the Road' Gallon Jug | Class 7 | Action + 1 Junk, 3 m radius. Constitution save or `3d8` Acid + `2d6` Poison and Fecal Stench for 2 turns (half on a success); Acid surface |
| Election-Year VIP Street-Sweep Photo Op | Class 12 | Bonus action (costs nothing and no longer restores Junk), **once per long rest**, 6 m. You get +2 AC and +3 m movement for 2 turns; enemies make a Wisdom save or take `4d8` Psychic and are Socially Shamed for 2 turns (half on a success) |
| Secondhand Foil-Trail Exhale | Tenderloin 3 | Action + 1 Junk, 3 m. Constitution save or `2d8` Poison + `2d8` Psychic, halved movement and disadvantage on attack rolls for 2 turns (half on a success) |
| Bootleg Streetlight 220V Power Tap | Overpass 3 | Action + 1 Junk, 9 m. Dexterity save or `3d8` Lightning + `1d8` Fire, no Reactions and disadvantage on Dexterity saves for 2 turns (half on a success); electrified puddle |
| Expired Trenbolone & Raw Liver Tantrum | Venice 10 | Bonus action + 1 Junk. 2 turns of `+1d8` Force weapon damage, +3 m movement and advantage on attack rolls |
| Emergency Exit Gate Alarm & JBL Speaker | BART 10 | Action + 1 Junk, 6 m. You get +3 m movement for 1 turn; enemies make a Constitution save or take `3d8` Thunder + `1d8` Psychic and are Dazed for 2 turns (half on a success) |
| Beverly Hills Emergency Botox & Lip-Filler Freeze | Beachborn 5 | Action, **once per long rest**, 9 m. Constitution save or `3d8` Poison, no Bonus Actions or Reactions and disadvantage on Constitution saves for 2 turns (half on a success) |
| Bay Area 9-Person Polycule Google Calendar Invite | Siliconite 5 | Action, **once per long rest**, 6 m. Wisdom save or `3d8` Psychic, halved movement and disadvantage on attack rolls for 2 turns (half on a success) |
| 2 AM Straight-Piped Nissan Altima Rev | Inland Emperor 1 | Action, 9 m. Constitution save or `2d8` Thunder, -2 AC and disadvantage on Wisdom saves for 2 turns (half on a success) |
| **Round 8** | | |
| Unrepaired Pothole Since 2014 Ankle-Breaker | Class 4 | Action + 1 Junk, 9 m. Dexterity save or `2d8` Bludgeoning, Prone, and Class-Action Metatarsal Fracture (halved movement, disadvantage on Dexterity saves) for 2 turns (half damage on a success) |
| NIMBY Three-Minute Public Comment Period | Class 6 | Action + **2 Junk**, **once per long rest**, 6 m radius. Enemies make a Wisdom save or take `2d6` Psychic and cannot move or take actions, bonus actions or reactions for 1 turn (Speaker Forty-One of Forty-Four); half damage on a success |
| Department of Unfinished Business Red-Tag Notice | Class 10 | Action + 1 Junk, 12 m. Wisdom save or `3d10` Force and Red-Tagged for 2 turns (attack rolls against it have advantage, disadvantage on its Wisdom saves); half damage on a success |
| Municipal Budget Hearing & Consent Calendar | Class 11 | Bonus action + 1 Junk, **once per long rest**. 3 turns of `+1d4` to attack rolls, `+1d4` to saving throws and +1 AC |
| Unlicensed Sidewalk Chiropractic Cervical Adjustment | Tenderloin 10 | Action + 1 Junk, ally within 1.5 m. Heals `4d8` and gives advantage on Strength and Dexterity saves for 3 turns, but knocks the ally Prone for 1 turn |
| PG&E Public Safety Power Shutoff Rolling Blackout | Overpass 10 | Action + 1 Junk, **once per long rest**, 4 m radius. Dexterity save or `3d8` Lightning and Blinded for 1 turn (half damage on a success); a 4 m darkness cloud for 3 turns |
| Emergency Ten-Dollar Boardwalk Sunglasses | Venice 12 | Bonus action (**no Junk cost**), **once per long rest**. 3 turns of immunity to Blinded, `+1d4` to attack rolls and advantage on Intimidation |
| Hayward Fault Transbay Seismic Retrofit (Delayed Until 2041) | BART 12 | Action + 1 Junk, **once per long rest**, 6 m radius. Enemies make a Dexterity save or take `4d8` Bludgeoning and fall Prone (half damage on a success); you get +2 AC and Prone immunity for 2 turns |
| Whole Foods Pay-By-Weight Hot Bar Heist | Californian race, level 1 | Bonus action (no Junk). Regain `1d8 +` Constitution modifier HP and advantage on Constitution saves for 2 turns, at -3 m movement |
| This Meeting Could Have Been a Scroll | Siliconite 1 | Bonus action (no Junk), 9 m. You or an ally get `+1d4` to attack rolls and `+1d4` to ability checks for 2 turns |
| **Round 9** | | |
| Costco Sample Cart Parked Sideways in the Aisle | Class 8 | Action + 1 Junk, 6 m. Strength save or `2d6` Bludgeoning and Cube-Denied (-3 m movement) for 2 turns; half damage on a success |
| DMV Ticket B047 Called at the Far Window | Class 8 | Action + 1 Junk, 12 m. Wisdom save or `2d8` Psychic and Dazed for 1 turn; half damage on a success |
| Self-Checkout: Unexpected Item in the Bagging Area | Class 8 | Action + 1 Junk, 9 m. Wisdom save or `2d8` Psychic and Unexpected Item Lockout for 2 turns (no Bonus Actions, disadvantage on attack rolls); half damage on a success. This no longer applies Dazed |
| Prop 13 Grandfathered Assessment Smirk | Class 12 | Bonus action + 1 Junk, **once per long rest**. Regain `1d8 + CON` HP and gain Grandfathered In (+2 AC) for 2 turns. It shares the `HC_CHAIR_BRACED` stack group, so it replaces (does not add to) the other braced +2 AC buffs |
| Double-Decker Tech Shuttle Idling in the Bike Lane | BART 3 | Action + 1 Junk, 9 m rectangle ahead of you (3 m wide), enemies only. Dexterity save or `3d8` Bludgeoning and Prone; half damage on a success |
| Raccoon Tribunal Behind the Green Compost Bins | Tenderloin 12 | Action + 1 Junk, **once per long rest**, 3 m. Constitution save or `2d6` Piercing + `1d8` Poison and Frightened for 1 turn; half damage on a success |
| PurpleAir Wildfire Refresh at 2:14 PM | Overpass 12 | Action + 1 Junk, **once per long rest**, 6 m. Constitution save or `2d6` Poison and Blinded for 1 turn; half damage on a success |
| Series-B Offsite Trust Fall Onto Asphalt | Siliconite 3 | Action (no Junk), melee spell attack at 1.5 m: `2d8` Bludgeoning and Prone. You get Offsite Bounce-Back (advantage on attack rolls) for 2 turns; it is written as a cast-time effect on you, so it may apply even if the attack misses (unchecked) |
| HOA Architectural Committee Beige-Paint Denial | Inland Emperor 3 | Action (no Junk), 9 m. Wisdom save or `2d8` Psychic and Frightened for 2 turns; half damage on a success |
| Nextdoor Lost-Coyote Thread, 214 Comments Deep | Beachborn 1 | Action (no Junk), 6 m radius around you, enemies only. Wisdom save or `2d8` Psychic and Frightened for 1 turn; half damage on a success |
| **Round 10** | | |
| In-N-Out Animal-Style Argument | Class 5 | Bonus action + 1 Junk, once per short rest. Regain `1d8 + CON` HP and gain Animal-Style Energy (advantage on attack rolls) for 2 turns |
| Caltrans Cone Labyrinth | Class 9 | Action + 1 Junk, once per short rest, 9 m. Dexterity save or `2d8` Bludgeoning and Prone for 1 turn (half on a success); you gain Detour Dash (+3 m movement) for 1 turn either way |
| Caltrain Horn at the Grade Crossing | Class 10 | Action + 1 Junk, **once per long rest**, 12 m. Constitution save or `3d8` Thunder and Dazed for 1 turn (half on a success) |
| Caltrans Truck-Bed Vest Requisition | Class 11 | Action (no Junk), **once per long rest**. Places a Caltrans Safety Vest in your inventory: rare light armour (AC 12 plus Dexterity, +1 Deception) that gives Hi-Vis Authority when worn (advantage on Intimidation, disadvantage on Stealth) |
| Sixty-Day Rent Increase Notice | Class 12 | Action + 1 Junk, **once per long rest**, 9 m. Wisdom save or `3d8` Psychic and Frightened for 2 turns (half on a success) |
| Rent-Stabilized Grit (passive) | Class 9 | Below 50% HP: +2 AC, immunity to being knocked Prone, and advantage on Strength saving throws |
| Laminated Pool-Hours Sign | Venice Boardwalk Brawler 6 | Action + 1 Junk, once per short rest, 9 m. Wisdom save or `2d6` Psychic and Dazed for 1 turn (half on a success) |
| Street-Sweep Citation at 2:01 | BART Platform Menace 10 | Action + 1 Junk, once per short rest. Melee spell attack within 1.5 m: `1d6` Slashing and `2d8` Psychic on a hit, and Citation Filed (disadvantage on Dexterity saves) for 2 turns |
| Farmers' Market Peach Parking Denial | Beachborn 3 | Bonus action (no Junk), once per short rest, 9 m. Dexterity save or `2d6` Bludgeoning and Prone for 1 turn (half on a success); you gain Validation Sprint (+3 m movement) for 1 turn either way |
| Seven-Dollar Oat-Milk Line | Siliconite 1 | Action (no Junk), once per short rest, 6 m. Wisdom save or `2d8` Psychic and Stuck in the Oat-Milk Line (disadvantage on attack rolls) for 2 turns (half on a success) |

The three fear spells in round 9 (Raccoon Tribunal, HOA Beige-Paint Denial and Nextdoor Lost-Coyote Thread) now use the vanilla fear-advantage tags (`AdvantageOnFrightened` and
`DisadvantageOnFrightened`) on their saves. Round 9 cooldowns: once per short rest for Costco, DMV, Self-Checkout, Tech Shuttle, Trust Fall, HOA and Nextdoor; once per long rest for Prop 13, Raccoon Tribunal and PurpleAir.

"Class N" means Homeless Californian class level N. "Beachborn / Siliconite / Inland Emperor N" is the subrace spell list at that character level,
the same way the v0.3.0 subrace abilities work. Every grant level above was checked against the generated spell lists and progressions in the
source, not in game.

### New Street Trades, Junk Doctrines and contraband items (round 6)

| Addition | Where granted | Intended behaviour |
|---|---|---|
| Bankruptcy Mattress Sign Spinner (Street Trade) | Class 2 choice | Advantage on Athletics and Performance checks (ninth Street Trade) |
| Unleashed 'Service Pitbull' Handler (Street Trade) | Class 2 choice | Advantage on Intimidation and Deception checks (the pitbull is called Princess) |
| Prop 65 Carcinogen Tolerance (Junk Doctrine) | Class 4 choice | Resistance to Acid damage (eighth Junk Doctrine) |
| Locked-Wheel Cart Drift (Junk Doctrine) | Class 4 choice | Advantage on Dexterity saving throws |
| Sharpened Interstate-880 Rebar (Uncommon, donor: Mace) | Oakland Flea Market | Weapon attacks deal an extra `1d4` Piercing |
| Shoplifted Finance-Bro Patagonia Vest (Uncommon, donor: Destroyed Robe) | Oakland Flea Market | +1 AC and advantage on Persuasion checks |
| Foil-Wrapped GPS Ankle Monitor & Jail Slides (Uncommon, donor: Shoes) | Oakland Flea Market | +1 to saving throws and Prone immunity |
| Bodega Counter 'Rhino 69K & Kratom' Shot (Uncommon, donor: Healing Potion) | Oakland Flea Market | Drink to heal `2d4 + 2` HP and gain Gas Station Rhino Rush (`+1d6` weapon damage, advantage on Strength checks and saves) for 2 turns. Like the v0.4.0 Kombucha, whether the drink action works is unverified |

The four Flea Market items borrow their donors' meshes and icons, so they look like a mace, a robe, shoes and a healing potion.

### Nine custom props (barricade, tent, scooter graveyard, robotaxi, porta-potty and four round 10 props)

The first five are 3D props like the shopping cart and the blue tarp: **AI-generated procedural meshes**. A Claude agent wrote the Python geometry and the
procedural texture painting; Blender is used only for previews. The GR2 files were converted with LSLib Divine and conformed to a vanilla
skeleton, using the same pipeline as the cart and tarp (visual resource, root template, Object stat, and a `GROUND:Spawn` on a spell). Each is a static
prop that cannot be moved or picked up. None has ever been spawned in game, so facing, collision, scale and how the texture looks are all unchecked, and the
spell icons are placeholders. The three newest spells (scooters, robotaxi, porta-potty) also add a self status next to the ground spawn on the same projectile-type donor, and
whether that extra self status still applies alongside `GROUND:Spawn` is unverified, as with the barricade. None of the three has an emissive map, so glowing parts are only bright colours.

The four round 10 props (`hc_bench.py`, `hc_utilitypole.py`, `hc_spinbike.py` and `hc_coolerfire.py`) are Blender-built, use the same `GROUND:Spawn` pattern with a 9 m ground target, and give their buff for 3 turns. None has been spawned in game.

| Spell | Where granted | Intended behaviour |
|---|---|---|
| Caltrans 'Lane Closed Ahead' Barricade (`HC_Target_CaltransLaneClosure`; model in `assets/models/HC_Barricade/`, code in `hc_barricade.py`) | Class 9 | Bonus action + 1 Junk, once per short rest, ground target within 9 m. Spawns an orange-and-white barricade with two reflective cones, sandbags and an amber lamp, and gives you Cones of Untouchable Authority (+2 AC) for 2 turns. Open question: whether the AC status still applies next to the prop spawn on this projectile-type donor |
| Pop-Up Tent City Encampment (Permit Pending) (`HC_Shout_PopUpTentEncampment`; model in `assets/models/HC_PopUpTent/`, code in `hc_tent.py`) | Class 7 | Action + 1 Junk, once per long rest, self-centred. Spawns a two-person dome tent (teal and orange, with duct tape, string lights, a milk-crate side table and a pigeon in sunglasses) at your feet and gives you Illegally Cozy: 8 temporary hit points for 3 turns. It uses vanilla's shared `TEMPORARY_HP` stack, so it does not stack with other temporary HP (Rally, for example). Open question: whether the spawn resolves once at the caster's feet for a self-centred shout (the same open question the blue tarp had before the 2026-10-15 data check) |
| Dockless Scooter Graveyard (Please Do Not Block the Sidewalk) (`HC_Target_ScooterGraveyard`; model in `assets/models/HC_ScooterGraveyard/`, code in `hc_scooters.py`) | Beachborn 5 | Action, **no Junk cost**, once per long rest, ground target within 9 m. Spawns a heap of six abandoned rental e-scooters (lime, cyan and white) against a chain-link panel with a stray traffic cone on top, and gives you Static Charge From the Pile for 3 turns: `+1d8` Lightning weapon damage and +3 m movement |
| Autonomous Robotaxi Has Seen a Traffic Cone (`HC_Target_RobotaxiBreakdown`; model in `assets/models/HC_Robotaxi/`, code in `hc_robotaxi.py`) | Siliconite 5 | Action, **no Junk cost**, once per long rest, ground target within 9 m. Spawns a white driverless crossover with a LiDAR dome, hazard lamps, a flat tyre and one cone wedged under the bumper, and gives you Your Driver Is Arriving In 0 Minutes for 3 turns: +3 m movement and advantage on Dexterity saving throws |
| Caltrans Festival Honey Bucket Tip-Over (`HC_Target_PortaPottyTipOver`; model in `assets/models/HC_PortaPotty/`, code in `hc_portapotty.py`) | Inland Emperor 5 | Action, **no Junk cost**, once per long rest, ground target within 9 m. Spawns a turquoise porta-potty lying on its side with a glowing puddle, loose toilet paper and an out-of-order sign, and gives you Nothing Left to Fear for 3 turns: immunity to Poisoned and `+1d4` to saving throws |
| Hostile Architecture Spike Bench (`HC_Target_HostileArchitectureBench`; `hc_bench.py`) | Base class 10 | Action (no Junk), once per long rest, ground target within 9 m. Spawns the spike bench prop and gives you Certified Bench Sleeper for 3 turns: Piercing and Bludgeoning resistance and immunity to being knocked Prone |
| Deferred Maintenance Pole Drop (`HC_Target_SparkingUtilityPole`; `hc_utilitypole.py`) | Base class 11 | Action + **2 Junk**, once per long rest, ground target within 9 m. Spawns the sparking utility pole prop (made-up utility: Pacific Grid & Excuse) and gives you Grid Safety Fee for 3 turns: Lightning resistance, +1 to attack rolls and +1 to your spell save DC |
| Studio Cycle Eviction Notice (`HC_Target_EvictedSpinBike`; `hc_spinbike.py`) | Base class 6 | Action + 1 Junk, once per long rest, ground target within 9 m. Spawns the evicted spin bike prop (made-up brand: SoulCyclone) and gives you Motivational Energy for 3 turns: advantage on Athletics and Intimidation checks and on Constitution saves |
| Illegal Sidewalk Cookout (`HC_Target_SidewalkCoolerBonfire`; `hc_coolerfire.py`) | Base class 4 | Action + 1 Junk, once per short rest, ground target within 9 m. Spawns the sidewalk cooler bonfire prop and gives you Parking Lot Warmth for 3 turns: Cold resistance and `+1d4` Fire weapon damage |

### Shared +2 AC stack

Four of the new buffs share one stacking group, `HC_CHAIR_BRACED`, which is also the group used by the Chair-Braced status: 3 AM Tweaker Hyperfocus (from 3 AM Sidewalk Lawnmower Disassembly),
the Six-Foot CVS Receipt Ward, the Amazon Fake Service-Animal Vest and Grandfathered In (from Prop 13 Grandfathered Assessment Smirk). They **overwrite each other**, so using a second one while the first is running replaces it rather than stacking to +4 AC.
Other +2 AC buffs (for example the Zoom layoff shield, the Seismic Retrofit and the barricade's cones) have their own groups. This is intended, not yet checked in game.

### Statuses

Round 4 adds 11 statuses (Freeway Directions, the three Weather Complaint lines with their cooldown locks, the three Permit
Pending stages and the one-turn "Approved, pending review." Slow), round 5 adds 7, round 6 adds 7 (including the Rhino shot's drink status), round 7 adds 8, round 8 adds 9 and round 9 adds 4 (Cube-Denied, Unexpected Item Lockout, Grandfathered In, Offsite Bounce-Back), round 10 adds 5 (Detour Dash, Animal-Style Energy, Citation Filed at 2:01, Validation Sprint, Stuck in the Oat-Milk Line);
the barricade (Cones of Untouchable Authority), the tent (Illegally Cozy), the scooters (Static Charge From the Pile), the robotaxi (Your Driver Is Arriving In 0 Minutes) and the porta-potty (Nothing Left to Fear) add one each, and the four round 10 props add one each (Certified Bench Sleeper, Grid Safety Fee, Motivational Energy, Parking Lot Warmth). They are the
conditions the spells above apply, such as Stripped Copper & Live Sparks, Cancelled & Tone-Policed, Impacted by Macroeconomic Headwinds,
Involuntary Sidewalk Nod, Speaker Forty-One of Forty-Four and Red-Tagged: Unpermitted Everything.

### What is checked, and what is not

- **Checked at file level:** every stat starts with `HC_`, every donor exists in the vanilla extraction and is not overridden in Honour, the spell
  lists and progressions grant each spell at the level shown above, mechanics tokens and surfaces appear in vanilla data, and the localization
  and icon registrations resolve. See [validation/README.md](validation/README.md) for the per-file breakdown.
- **Current numbers:** the validator reports 317 stat entries, 94 icons and 659 localization handles; 848 unit tests (counted per file with `def test_`,
  and passing per `HANDOFF.md`), and `validate.py --pak` passing per `HANDOFF.md`.
- **Not checked:** everything about play. Nothing from rounds 4-10 or the nine source-only props has been played, and none of the props has been spawned in game: damage, saves, Junk costs, durations, the Permit Pending
  stack countdown, the Weather Complaint triggers, surface effects, the Flea Market item grants and the Rhino shot's use action, level-up
  grants on a real character, and balance.

---

## 🌟 Class Overview

Hardened by the concrete jungles of San Francisco and Los Angeles, the **Homeless Californian** channels makeshift biological warfare, erratic street fury, and the gravity-defying equilibrium of the legendary **Fent Lean**.

- **Primary Ability**: Constitution (also the spellcasting ability for DCs and damage)
- **Hit Points**: 14 base HP, +8 per level above 1
- **Saving Throws**: Constitution & Dexterity
- **Armor & Weapons**: Light Armor, Medium Armor, Shields, Simple Weapons, Martial Weapons (Venice Boardwalk Brawler also gains Heavy Armor)
- **Skills**: choose 3 from Athletics, Acrobatics, Sleight of Hand, Stealth, Survival, Intimidation, Deception
- **Level 1 ability bonus**: +2 / +1 to your choice of scores
- **Ability Improvements**: levels 4, 8 and 12
- **Level cap**: 12 (multiclassing in is supported)
- **Recommended array**: STR 13, DEX 14, CON 15, INT 8, WIS 12, CHA 10

---

## 📈 Level Progression

| Level | Class features gained |
|------:|-----------------------|
| 1 | Street Grit Defence, Sidewalk Immunity, Proposition 47, Sling Poop, Sling Fentanyl, Fent Lean, Narcan, Sidewalk Scramble, Junk, Emotional Support Brick, Bag of Other Bags, Load-Bearing Lawn Chair, Unclaimed Wardrobe, 3 skills, +2/+1 ability bonus |
| 2 | Aggressive Panhandling, Pocket Lint Buffet, Street Hustle, Dumpster Dive, Street Trade choice (Scrounger / Fixer / Lookout / Can Collector / Busker; Squeegee Technician and Notary are new in v0.4.0), Sprinkler Violation (new in v0.4.0) |
| 3 | **Subclass choice** (subclass features below; Overpass Riverbed Dweller is new in v0.4.0) |
| 4 | Eviction Notice, Coat-Hanger Slim Jim, Junk Doctrine choice (Hoarder / Fortifier / Runner / Twitchy; Cardboard Insulator and Tinfoil Deflector are new in v0.4.0), Catalytic Converter Sawzall (new in v0.4.0), Ability Improvement |
| 5 | Extra Attack, Sling Chunky Poop; Sling Poop damage steps up; Guilt Trip, Beg |
| 6 | Restorative Stupor, Unkillable Vagrant; Public Scene; Curb Alert (new in v0.4.0); subclass feature |
| 7 | Feral Screech, Moving Day, I Was Here First |
| 8 | Ability Improvement, Trapped in the Invisible Box, One-Star Citation (new in v0.4.0) |
| 9 | Mass Fentanyl Contraband, Pitch Tent Encampment, Bucket Drum Solo |
| 10 | Encampment Sweep Survival Instinct; subclass feature; Sling Poop damage steps up; Compassion Burnout |
| 11 | Extra Attack (2 extra attacks), Baffling Retaliation, Punctured Lithium Cell, HOV Lane (new in v0.4.0) |
| 12 | Call 311 (On Hold), Ability Improvement, subclass Squatter's Rights capstone (details in the subclass sections; the Overpass version is new in v0.4.0) |

---

## 💥 Class Abilities

### 💩 Sling Poop & Sling Chunky Poop
*Hurl a handful of raw biological waste at a target.*
- **Action Type**: Action, unlimited use (cantrip)
- **Attack**: Ranged spell attack
- **Damage**: `1d10 + CON Bludgeoning` (2d10 at level 5, 3d10 at level 10) and `1d6 Poison`
- **Effect**: Leaves a puddle of filth and inflicts **Fecal Stench** for 2 turns.
- **Level 5 - Sling Chunky Poop**: Extra `1d10` Bludgeoning on top of Sling Poop, `2d6 Poison`, a wider puddle, and Fecal Stench for 3 turns.

### 💊 Sling Fentanyl & Mass Fentanyl Contraband
*Launch a concentrated dose of chemical contraband.*
- **Sling Fentanyl**: Action, recharges on Short Rest. Deals `2d6 Psychic`; on a failed Constitution save the target falls into **Fent Stupor** for 2 turns.
- **Level 9 - Mass Fentanyl Contraband**: Action, recharges on Short Rest. 4m area, `5d6 Psychic` to everyone caught (half on a successful save); failed Constitution save means **Fent Stupor** until the end of their next turn.

### 🧘 Fent Lean & Narcan
*Fold forward at a perfect, gravity-defying 90-degree angle (and slump while doing it).*
- **Fent Lean**: Bonus Action, recharges on Short Rest, lasts 3 turns. Resistance to all damage, +3 Armor Class, Advantage on Constitution and Dexterity saving throws, immune to Prone, but you cannot move.
- **Narcan**: Free action that ends Fent Lean early. Jam a dose of Narcan up your nose and snap your spine back upright.
- **Level 6 - Restorative Stupor**: While leaning, regain `2d6 + CON` Hit Points at the start of each of your turns.
- **Level 11 - Baffling Retaliation**: Creatures that hit you with a melee attack while you lean take `2d10 Psychic` damage.

### 🏃 Other Spells & Actions
- **Sidewalk Scramble** (Level 1): Bonus Action Dash with +3m movement, immune to difficult terrain and Prone until the end of your next turn.
- **Aggressive Panhandling** (Level 2): Action, 6m, Short Rest. Enemies make a Wisdom save or become **Socially Shamed** for 2 turns (Disadvantage on attack rolls, no Reactions).
- **Eviction Notice** (Level 4): Bonus Action, Short Rest. On a failed Wisdom save the target takes `3d6 Psychic` and suffers **Rent Hike** for 3 turns (-2 AC, -3m movement, `2d6 Psychic` at the start of each of its turns).
- **Feral Screech** (Level 7): Action, 9m, Short Rest. `6d6 Thunder` (half on a successful save); failed Wisdom save also leaves enemies **Frightened** for 2 turns.
- **Pitch Tent Encampment** (Level 9): Action, 5m, Long Rest. You and allies in range gain 15 Temporary HP, Resistance to Bludgeoning/Piercing/Slashing for 3 turns, and Sanctuary for 1 turn.
- **Call 311 (On Hold)** (Level 12): Bonus Action, 9m, Short Rest. On a failed Wisdom save enemies are **On Hold** for 3 turns (no Bonus Actions or Reactions, halved movement).

### 🎭 Hustle Kit (levels 5-11) - not yet verified in game
Phase 4 abilities; all but Beg cost 1 Junk. The Junk toolkit above is documented in the expansion tables near the top.
- **Guilt Trip** (5): Bonus Action, 9 m. `1d6 + CON Psychic`; if the target is Socially Shamed, an extra `2d6 Psychic` and the shame is spent.
- **Beg** (5): Action, once per short rest, no Junk. Non-hostile target makes a Wisdom save; on a failure you receive 5 gold. Either way they gain Homeless Fatigue. The most experimental ability.
- **Public Scene** (6): Action, 9 m. Wisdom save or Frightened for 1 turn (2 turns and shame spent if Socially Shamed).
- **Trapped in the Invisible Box** (8): Action, once per short rest. Wisdom save or the target cannot move for 1 turn.
- **Bucket Drum Solo** (9): Action, cone. Constitution save: `2d6 Thunder` and pushed back on a failure (half damage on a success); failures gain Homeless Fatigue for 3 turns.
- **Compassion Burnout** (10): Bonus Action, 9 m. `2d6 Psychic`; if the target has Homeless Fatigue, an extra `2d6 Psychic` and the fatigue ends.
- **Punctured Lithium Cell** (11): Action, ranged spell attack for `2d6 Lightning` + `2d6 Fire`; ignites the ground. Mind your friends indoors.
- **Everybody Knows This Guy** (Tenderloin 10): Action, 9 m. Wisdom save or Breadcrumbed for 2 turns.
- **Sublet** (Venice 6), **Fare Evasion Audit** (BART 6): see the subclass sections.
- **Statuses**: Fined (-3 m movement, no Reactions; from Fare Evasion Audit), Homeless Fatigue (attack rolls against the target have advantage), Trapped in the Invisible Box (cannot move), Breadcrumbed (attacks against it have advantage; its own attacks have disadvantage).

### 🛡️ Passive Features
- **Street Grit Defence** (1): Unarmored AC = 10 + Dexterity + Constitution modifiers; shields still allowed.
- **Sidewalk Immunity** (1): Immune to Poisoned and Disease, Resistance to Poison damage.
- **Proposition 47** (1): Hitting an enemy with a melee attack grants a **Stolen Patagonia Vest** for 2 turns (+1 AC, +1d4 Bludgeoning on weapon attacks).
- **Pocket Lint Buffet** (2): Once per turn, damaging a creature afflicted with Fecal Stench grants Temporary HP equal to your CON modifier + 2.
- **Street Hustle** (2): +3m movement and +3 Initiative.
- **Extra Attack** (5), upgraded to **Extra Attack (2)** at level 11.
- **Unkillable Vagrant** (6): Resistance to Bludgeoning, Piercing and Slashing damage; Advantage on saves against Frightened and Charmed.
- **Encampment Sweep Survival Instinct** (10): The first time each combat you drop below half HP, you collapse into Fent Lean for 2 turns and gain 20 Temporary HP.

### 🧪 Statuses
- **Fecal Stench**: Disadvantage on attack rolls and `1d4 Poison` at the end of each turn.
- **Fent Stupor**: Incapacitated and unable to move; damage does not wake them.

---

## 🏙️ Subclasses (Level 3)

Four subclasses are in the public v0.4.0 download. The fourth, Overpass Riverbed Dweller, is new in v0.4.0 (last entry below).

### Tenderloin Biohazard
*Master of chemical concoctions and sidewalk biohazards.*
- **L3 - Tenderloin Biohazard Aura**: 3m miasma that afflicts nearby enemies with Fecal Stench.
- **L3 - Biohazard Bomb**: Action, Short Rest. 4m explosion for `6d6 Poison` + `3d6 Acid` (half on a successful Dexterity save), inflicts Fecal Stench, leaves a lingering poison cloud.
- **L6 - Toxic Adaptation**: Poison damage ignores Resistance; weapon attacks deal an extra `1d6 Poison`.
- **L10 - Patient Zero**: Weapon attacks deal a further `2d6 Poison`; you are immune to Poison damage.
- **L3 - Pigeon Witness Protection** *(not yet verified in game)*: Action + 1 Junk, once per short rest; summons a vanilla raven familiar.
- **L3 - Pigeon Lunch Rush** *(not yet verified in game)*: granted to the raven; 1 Action, once per short rest, 4 m radius; failed Dexterity save gives Disadvantage on attack rolls and Dexterity saves for 1 turn.
- **L6 - Curbside Needle Exchange** *(not yet verified in game)*: Action + 1 Junk, once per short rest, 1.5 m; cures Poisoned, Disease, Blinded and Paralysed on a living ally and heals `2d6 + CON`.
- **L10 - Everybody Knows This Guy** *(not yet verified in game)*: Action + 1 Junk, 9 m; Wisdom save or Breadcrumbed for 2 turns.
- **L12 - Squatter's Rights: Condemned Block** *(not yet verified in game)*: Bonus Action, once per long rest; restores all Junk and lasts 3 turns. Unlocks Condemn Block (`3d8 Poison`, Constitution save for half, 2 Junk), enemies within 6 m get Fecal Stench, and you have advantage on concentration checks.

### Venice Boardwalk Brawler
*A close-quarters pugilist with shivs, flurries and shopping carts.*
- **L3 - Heavy Armor proficiency**
- **L3 - Broken 40oz Shank**: Bonus Action melee attack, `2d6 + CON Piercing` + `1d6 Slashing`, Bleeding for 2 turns.
- **L3 - Shopping Cart Charge**: Action, 9m rush, Short Rest. `4d8 + CON Bludgeoning` to the first creature hit; failed Strength save knocks it Prone.
- **L6 - Muscle Beach Juice**: Weapon attacks deal an extra `1d8 Bludgeoning`; +2 AC.
- **L10 - King of the Boardwalk**: Critical hits on 18-20; heal `1d8` HP whenever you hit with a melee attack.
- **L3 - Heirloom Furniture** *(not yet verified in game)*: Action + 1 Junk; melee hit for `3d6 + CON Bludgeoning`, failed Strength save knocks Prone; a hit prepares a Chair-Leg Shiv.
- **L3 - Chair-Leg Shiv** *(not yet verified in game)*: Bonus-action melee attack for `2d6 + CON Piercing`; consumes the temporary unlock.
- **L3 - Abandoned Cart**: Bonus action + 1 Junk, once per short rest, 6 m; spawns a shopping-cart prop. Partly verified live on 2026-10-14 (see the v0.3.0 additions above); facing, collision, Junk cost and look are not verified.
- **L6 - Sublet** *(not yet verified in game)*: Action + 1 Junk; an ally within 9 m gets the Lawn Chair buff (+2 AC, advantage on Strength saves, Prone immunity) for 2 turns.
- **L10 - Chair Check** *(not yet verified in game)*: Action + 1 Junk, once per short rest; weapon attack for weapon damage plus `2d8 Bludgeoning`, failed Strength save knocks Prone.
- **L12 - Squatter's Rights: Eviction Defense** *(not yet verified in game)*: Bonus Action, once per long rest; restores all Junk and lasts 3 turns. Action Surge, advantage on attack rolls, and an Emergency Chair-Leg Shiv.

### BART Platform Menace
*An erratic street phantom who slips through turnstiles and spatial dimensions.*
- **L3 - Reliable Talent** (vanilla)
- **L3 - Turnstile Hop**: Bonus Action teleport up to 18m, once per turn.
- **L6 - Evasion** and **Uncanny Dodge** (vanilla)
- **L10 - Last Train Phantom**: +4.5m movement, immune to difficult terrain.
- **L10 - Express Hop**: Free teleport up to 9m, once per turn.
- **L6 - Wrong Platform** *(not yet verified in game)*: Action + 1 Junk, once per short rest; failed Wisdom save swaps your position with an enemy.
- **L6 - Fare Evasion Audit** *(not yet verified in game)*: Action + 1 Junk, once per short rest, 9 m; failed Wisdom save leaves the target Fined for 2 turns (-3 m movement, no Reactions).
- **L12 - Squatter's Rights: Last Train Out** *(not yet verified in game)*: Bonus Action, once per long rest; restores all Junk and lasts 3 turns. +1 Reaction, +4.5 m movement, and unlocks Platform Rescue and Wrong Platform Express.

### Overpass Riverbed Dweller *(new in v0.4.0; NOT yet play-tested)*
*A survivalist who keeps house in concrete flood channels and under freeway overpasses. The ground is always doing something. You are used to it.*
- **L3 - Concrete Bank Traction**: Immune to difficult terrain (mud, webs, vines).
- **L3 - Storm Drain Flash Flood**: Action + 1 Junk, once per short rest; 9 m line. Strength save: `2d8 + CON Bludgeoning` and Prone for 1 turn on a failure, half damage on a success; leaves standing water for 2 turns.
- **L3 - Blue Tarp Lean-To**: Bonus Action + 1 Junk, once per short rest, 3 m radius; you and allies get +1 AC and advantage on Dexterity saves for 2 turns, and fire on the ground is doused. It also spawns a custom blue tarp lean-to prop on the ground (AI-generated model; the data check confirmed one spawns at your feet, but its look and collision are unchecked).
- **L6 - Culvert Siphon**: Action + 1 Junk, once per short rest, 9 m; you or an ally regain `2d6 + CON` HP and stop Burning, and the ground is doused.
- **L6 - Underpass Climate Control**: Resistance to Lightning and Cold damage.
- **L10 - Rebar Anchor**: +1 AC and advantage on Strength saving throws.
- **L10 - Drainage Ditch Dig-In**: Action + 1 Junk, once per short rest, 9 m range, 3 m radius; creates Mud for 3 turns. Technically a flood-control project.
- **L12 - Squatter's Rights: Spillway Sovereignty**: Bonus Action, once per long rest; restores all Junk and lasts 3 turns. +2 AC, +3 m movement, and the ground within 4 m turns to mud (difficult terrain) for 3 turns.

---

## 🌴 Californian Race

Hailing from the Golden State, **Californians** are a human-bodied race (standard human body types, camera poses and appearance options) with uncanny resilience shaped by natural disasters, gridlock traffic and perpetual microclimates.

**Base traits**
- Resistance to Fire damage
- **Earthquake Sense**: cannot be knocked Prone
- **405 Commute Veteran**: cannot be Slowed or Restrained
- **Touch Grass**: Action, Short Rest. Melee spell attack for `1d8 Psychic`, ends Rage, and inflicts Existential Daze (Disadvantage on attack rolls) for 2 turns.
- **Avocado Toast**: Bonus Action, Short Rest. Regain `1d6 + CON` HP and gain 5 Temporary HP.
- **Runyon Canyon Glutes** (new, not yet verified in game): +50% jump distance and +25% carrying capacity.
- **NIMBY Zoning Defense** (new in v0.4.0, not yet play-tested): advantage on saving throws against being Charmed.
- **Emotional Support Hydroflask** (new, not yet verified in game): Bonus Action, Short Rest. Regain `1d8 + CON` HP, remove Poisoned, douse the surface beneath you and leave a puddle of clean water.
- Racial spells use Charisma as their spellcasting ability.

### Subraces
Each subrace gets abilities at race levels 1, 3 and 5 (character level). **None of the subrace abilities below are verified in game yet.** Levels 3 and 5 are new in v0.3.0 (Bakersfield Tule Fog is new in v0.4.0).

| Subrace | Level 1 | Level 3 | Level 5 |
|---------|---------|---------|---------|
| **Beachborn (SoCal)** | Resistance to Radiant damage; **Hang Ten** (Bonus Action, Short Rest): +3m movement and immunity to difficult terrain and Prone for 2 turns | **Rip Current** (Action, 9m, Short Rest): melee spell attack for `2d6 Cold`, pulls the target 4.5m toward you, Prone on a failed Strength save, leaves a puddle of seawater | **Golden Hour** (Action, 6m radius, Long Rest): enemies make a Constitution save or are Blinded for 2 turns; you gain +3m movement and `+1d4 Radiant` weapon damage for 2 turns |
| **Siliconite (NorCal)** | **Siliconite Synergy**: once per turn, weapon damage deals an extra `1d4 Psychic`; **Vibe Check** (Action, 18m, Short Rest): failed Wisdom save breaks concentration and applies Vibe Checked (no Bonus Actions or Reactions, halved movement) | **Disruptive Pivot** (Bonus Action, 9m, Long Rest): teleport to an unoccupied space and gain Advantage on your next attack roll | **Non-Disclosure Agreement** (Action, 9m, Long Rest): `2d8 Psychic`; failed Wisdom save also Silences the target for 2 turns |
| **Inland Emperor (The Valley)** | Resistance to Poison damage; **Smog Lungs** (Advantage vs Poisoned, immune to Disease); **Heat Index Mastery** (immune to Burning); **Dust Devil** (Bonus Action, 3m radius, Short Rest): you gain Blur for 1 turn, enemies make a Constitution save or are Blinded for 1 turn | **Overpass Exhaust** (6m cone, Long Rest): `2d8 Poison` + `1d8 Fire`, Constitution save for half | **Heatstroke** (Action, 9m, Long Rest): `3d8 Fire` (half on a save); failed Constitution save inflicts Heatstroke for 2 turns (reduced movement, Disadvantage on attack rolls and physical saves) |

### California Identity & Gender Expression
At character creation, every Californian picks one identity / pronoun archetype, each with its own perk:
- **Dude** (Dude / Dude / Dudeself): +2 Persuasion, Advantage on saves against Frightened
- **Founder** (Founder / Disrupter / Unicorn): +2 Initiative, Advantage on Deception
- **Oat** (Oat / Almond / Lactose-Free): immune to Poisoned
- **Self-Actualized** (Aura / High-Frequency / Elevated): 5 Temporary HP at the start of combat
- **The Algorithm** (Optimized / Scaled / Series-A): +1 to all saving throws

### The Californian Look
Character creation hair and makeup choices are locked to a garish palette:
- Hair colors: pink, blue or aqua only (highlights: pink or blue)
- Makeup: pink, blue, aqua, teal, purple or black
- Lipstick: pink, blue or black

---

## 🛠️ Project Structure & Build Tool

```
Baldurs Gate 3 Homeless Californian Class/
├── generate_mod.py              # Generates all LSX, XML, and txt data with deterministic GUIDs
├── build.py                     # Pipeline: generate, build icons, compile loca, pack .pak, install & activate
├── build_icons.py               # Packs icons into the texture atlas and builds Content/GUI + race icon resources
├── hc_choices.py                # Street Trade selector (includes Squeegee Technician and Notary, new in v0.4.0)
├── hc_doctrines.py              # Junk Doctrine passives (includes Cardboard Insulator and Tinfoil Deflector, new in v0.4.0)
├── hc_expansion.py              # Junk toolkit, race progression and other expansion abilities
├── hc_hustle.py                 # Hustle kit (Guilt Trip, Beg, Sublet, ...)
├── hc_capstone.py               # Squatter's Rights level-12 capstones (all four subclasses)
├── hc_utility.py                # Coat-Hanger Slim Jim, Curbside Needle Exchange
├── hc_overpass.py               # Overpass Riverbed Dweller subclass (new in v0.4.0)
├── hc_round2.py                 # Round 2 spells and Decatted Exhaust status (new in v0.4.0)
├── hc_tarp.py                   # Blue tarp lean-to prop: visual resource, template and Object stat (new in v0.4.0)
├── hc_junk_items.py             # Curb Alert and its four junk items, Kombucha statuses (new in v0.4.0)
├── hc_round4.py                 # Round 4: Freeway Directions, Weather Complaint, Permit Pending (source-only)
├── hc_round5.py                 # Round 5: 10 stereotype/street comedy spells and 7 statuses (source-only)
├── hc_round6.py                 # Round 6: Oakland Flea Market items and 6 more spells (source-only; also adds trades/doctrines via the two files above)
├── hc_round7.py                 # Round 7: 11 spells and 8 statuses (source-only)
├── hc_round8.py                 # Round 8: 10 bureaucracy/infrastructure/wellness spells and 9 statuses (source-only)
├── hc_barricade.py              # Caltrans 'Lane Closed Ahead' barricade prop and spell (source-only)
├── hc_tent.py                   # Pop-Up Encampment Tent prop and spell (source-only)
├── hc_round9.py                 # Round 9: 10 grocery/DMV/HOA/tech comedy spells and 4 statuses (source-only)
├── hc_scooters.py               # Dockless Scooter Graveyard prop and spell (source-only)
├── hc_robotaxi.py               # Broken-Down Robotaxi prop and spell (source-only)
├── hc_portapotty.py             # Tipped-Over Festival Porta-Potty prop and spell (source-only)
├── hc_round10.py                # Round 10: 9 spells, Caltrans Safety Vest and Rent-Stabilized Grit passive (source-only)
├── hc_bench.py                  # Hostile Architecture Spike Bench prop and spell (source-only)
├── hc_utilitypole.py            # Sparking Utility Pole prop and spell (source-only)
├── hc_spinbike.py               # Evicted Studio Spin Bike prop and spell (source-only)
├── hc_coolerfire.py             # Sidewalk Cooler Bonfire prop and spell (source-only)
├── hc_cart.py                   # Abandoned Cart spell and template
├── hc_outfit.py                 # Outfit / wardrobe items
├── hc_icon_keys.py              # Maps spells to icon keys
├── validation/                  # Local validator and unit tests (see validation/README.md)
├── archive/                     # Old handoffs, notes, review and AI prompts (moved here 2026-10-14)
├── assets/
│   ├── icons/                   # Custom spell/class/race art (<MapKey>.png) picked up by build_icons.py
│   ├── models/                  # AI-generated model scripts and converted files
│   │   ├── HC_ShoppingCart/     # Shopping cart (added in v0.3.0)
│   │   ├── HC_BlueTarp/         # Blue tarp lean-to (added in v0.4.0)
│   │   ├── HC_Barricade/        # Caltrans barricade (source-only; AI-generated, Blender for previews)
│   │   ├── HC_PopUpTent/        # Pop-up encampment tent (source-only; AI-generated, Blender for previews)
│   ├── HC_ScooterGraveyard/ # Dockless scooter graveyard (source-only; AI-generated, Blender for previews)
│   ├── HC_Robotaxi/         # Broken-down robotaxi (source-only; AI-generated, Blender for previews)
│   └── HC_PortaPotty/       # Tipped-over festival porta-potty (source-only; AI-generated, Blender for previews)
│   ├── human_race_children.xml  # Human race appearance data reused (and look-restricted) for the Californian race
│   ├── human_cc_appearance_visuals.xml  # Human character creation visuals cloned for the Californian race
│   └── cc_color_names.json      # Colour names used to enforce the Californian look lock
├── dist/
│   └── HomelessCalifornian.pak  # The packaged mod ready for BG3
├── src/HomelessCalifornian/     # Full unpacked mod source tree
│   ├── Mods/HomelessCalifornian/meta.lsx
│   └── Public/HomelessCalifornian/...
└── tools/Packed/Tools/Divine.exe # LSLib Divine (NOT in git)
```

`tools/` is not in git. Supply `Divine.exe` and `granny2.dll` yourself (see the LSLib ExportTool); they are needed for packing, localization and the cart, tarp, barricade, tent, scooter graveyard, robotaxi, porta-potty and round 10 prop model conversion.

### CLI Commands:
- `python build.py` - Regenerates the source tree, builds icons, recompiles localization and generates `dist/HomelessCalifornian.pak`.
- `python build.py --install` - Also copies the `.pak` into your BG3 Mods folder.
- `python build.py --activate` - Also installs and activates the mod in `modsettings.lsx`.
- `python -m unittest discover -s validation -q` - Runs the full validation suite (110 tests in v0.4.0; 322 on the current source).
- `python build.py --status` - Verifies current mod installation and load order status.
- `python generate_mod.py` - Regenerates only the source tree (no icons or packing).
- `python build_icons.py` - Rebuilds only the icon atlas and GUI resources.

---

## 👥 Contributors & AI Pair Programming Team

- **Matthew (@themadhattermsr)** — Creator, Project Director, Gameplay Design & Live In-Game Playtester.
- **Claude (Anthropic)** — Initial Architecture, Handoff Lead, Generator Engineering & Lore QA, and directing and testing the AI-generated shopping cart and blue tarp lean-to, and the source-only barricade, tent, scooter graveyard, robotaxi and porta-potty (Claude agents wrote the procedural model scripts; Blender was used only for previews), and the four round 10 props (spike bench, utility pole, spin bike, cooler bonfire) are Blender-built.
- **Codex (OpenAI)** — BG3 Mechanics Audits, Engine Functors, Subclass Balance & Donor Specialist.
- **Antigravity / Gemini (Google DeepMind)** — Lead Orchestrator, Generator Pipeline, Test Suite & Validation, and Visual Artist (custom spell icons, class crests, status art, and Nexus banners). The shopping cart, blue tarp, barricade, tent, scooter graveyard, robotaxi and porta-potty models are AI-generated, not made by Gemini or a human artist.
- **Local Model (Qwen / Ollama)** — Offline Flavor Text Ideation, Creative Brainstorming & Dialogue Concepts.

