# Baldur's Gate 3 - Homeless Californian Class Mod

## Public playtest

[Download the playtest (Oct 13 build)](https://github.com/matthewsteross/bg3-homeless-californian/releases/tag/playtest-2026-10-13) · [Nexus Mods page](https://www.nexusmods.com/baldursgate3/mods/25761) · [Report a bug](https://github.com/matthewsteross/bg3-homeless-californian/issues/new/choose)

**Throw bricks. Weaponise furniture. Make public transit everybody else's problem.**

Looking for PC testers for a ridiculous Constitution-based class with three
subclasses: Tenderloin poison, Venice furniture melee, and BART repositioning.
Try one subclass for ten minutes and tell us one thing that broke—or one thing
that worked. [Start the short tester checklist](TESTING.md).

**Which version is which:** the public download (release `playtest-2026-10-13`, also the Nexus file) is
**v0.2.0 (untested in game)**. The source in this repository is newer: it is v0.2.1 plus later additions
(race abilities, I Was Here First, Pigeon Lunch Rush and more, listed below). Those fixes and additions are **not
released yet** and have **not been tested in game**. The older October 12 build is still on its own release page.
Use the release ZIP for playtesting. The Nexus page is live; the in-game (mod.io) listing is still pending
approval, so the mod is not yet confirmed in the in-game mod menu.

Intentionally overpowered: this is a ridiculous class with actions, saves,
Junk costs and rest cooldowns, rather than an attempt at vanilla balance.
The starting-area test confirmed icons after a reload and castability of
available spells. Full effect, progression and compatibility testing continues.
The human (Matthew, @themadhattermsr) directs the design; Claude, Codex, Antigravity/Gemini, and the local model (Qwen) assisted with code, architecture, testing and ideation. Gemini generated the custom icons and banners, and the shopping cart model is also AI-generated (see [Contributors](#-contributors--ai-pair-programming-team)). Nothing here is hand-made by a human artist.

This download is the manual PC package. It is not yet a mod.io/in-game or
console release. Use a separate test save; respec or start a new character if
new progression grants are missing. Keep the mod installed on saves that use it.

## Capstone, Street Trade, Doctrines and the Hustle kit (in v0.2.0; NOT yet play-tested)

The October 13 build (v0.2.0) contains a much larger build than the October 12
playtest ZIP: the level-12 **Squatter's Rights** capstone, a **Street Trade** selector, **Junk Doctrines**, and the
**Hustle kit** (Guilt Trip, Beg, Public Scene, Trapped in the Invisible Box, Bucket Drum Solo, Compassion Burnout,
Punctured Lithium Cell, Sublet, Everybody Knows This Guy, plus the Homeless Fatigue and Breadcrumbed statuses).
**Honest status:** file-level checks and 39 validation tests pass (on the current repository source, which is newer
than the downloadable v0.2.0). In game, only "a character can reach level 12 without a catastrophic failure" has been
confirmed; individual abilities have not been tested, and **Beg** (gold from non-hostile NPCs) is the most experimental.
Guilt Trip, Public Scene and Compassion Burnout now work on any enemy and add a bonus when the target is Socially
Shamed or Homeless Fatigued (repository source only; the v0.2.0 download requires the status and can show "Invalid Target"). Use a new character or a respec for new grants. Test routes for the new
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
the wardrobe uses existing robe/cloak visuals, not a custom safety vest or
blue tarp model. Guns are future work. There is now exactly one custom mesh, the
Abandoned Cart (see the unreleased additions below); the chair, tarp, guns and pigeon are still not custom. The level-12
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
(39 tests, including the deliberate-corruption checks). The saved original
package can restore the previous build with BG3 closed. Keep the candidate
out of co-op until both players intentionally use the same package.

A custom class and race mod for **Baldur's Gate 3** introducing the **Homeless Californian** class (levels 1-12, three subclasses) and the **Californian** race (three subraces, a California identity / gender selector, and a restricted garish look).

---

## Unreleased repository additions (after v0.2.0; NOT yet verified in game)

These exist in the source and a locally built pak only. They are not in the public v0.2.0 download. Everything
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
It is the only custom mesh in the mod. What was verified live in game on 2026-10-14, and only this: the stat, template and
localization resolve, the cart spawns and is visible, and casting it spawns exactly one cart. **Not verified:** facing,
collision, the Junk cost on a real Homeless Californian character, and how it looks in good light.

The Californian race also gained racial progression (levels 1, 3 and 5); see [the race section](#-californian-race).
The repository has 39 passing validation tests (file-level checks only).

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
| 2 | Aggressive Panhandling, Pocket Lint Buffet, Street Hustle, Dumpster Dive, Street Trade choice (Scrounger / Fixer / Lookout / Can Collector / Busker) |
| 3 | **Subclass choice** (subclass features below) |
| 4 | Eviction Notice, Coat-Hanger Slim Jim, Junk Doctrine choice (Hoarder / Fortifier / Runner / Twitchy), Ability Improvement |
| 5 | Extra Attack, Sling Chunky Poop; Sling Poop damage steps up; Guilt Trip, Beg |
| 6 | Restorative Stupor, Unkillable Vagrant; Public Scene; subclass feature |
| 7 | Feral Screech, Moving Day, I Was Here First |
| 8 | Ability Improvement, Trapped in the Invisible Box |
| 9 | Mass Fentanyl Contraband, Pitch Tent Encampment, Bucket Drum Solo |
| 10 | Encampment Sweep Survival Instinct; subclass feature; Sling Poop damage steps up; Compassion Burnout |
| 11 | Extra Attack (2 extra attacks), Baffling Retaliation, Punctured Lithium Cell |
| 12 | Call 311 (On Hold), Ability Improvement, subclass Squatter's Rights capstone (details in the subclass sections) |

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
- **L3 - Abandoned Cart**: Bonus action + 1 Junk, once per short rest, 6 m; spawns a shopping-cart prop. Partly verified live on 2026-10-14 (see unreleased additions above); facing, collision, Junk cost and look are not verified.
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
- **Emotional Support Hydroflask** (new, not yet verified in game): Bonus Action, Short Rest. Regain `1d8 + CON` HP, remove Poisoned, douse the surface beneath you and leave a puddle of clean water.
- Racial spells use Charisma as their spellcasting ability.

### Subraces
Each subrace gets abilities at race levels 1, 3 and 5 (character level). **None of the subrace abilities below are verified in game yet.** Levels 3 and 5 are new in the unreleased repository source.

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
├── hc_choices.py                # Street Trade and Junk Doctrine selectors
├── hc_doctrines.py              # Junk Doctrine passives
├── hc_expansion.py              # Junk toolkit, race progression and other expansion abilities
├── hc_hustle.py                 # Hustle kit (Guilt Trip, Beg, Sublet, ...)
├── hc_capstone.py               # Squatter's Rights level-12 capstone
├── hc_utility.py                # Coat-Hanger Slim Jim, Curbside Needle Exchange
├── hc_cart.py                   # Abandoned Cart spell and template
├── hc_outfit.py                 # Outfit / wardrobe items
├── hc_icon_keys.py              # Maps spells to icon keys
├── validation/                  # Local validator and unit tests (see validation/README.md)
├── archive/                     # Old handoffs, notes, review and AI prompts (moved here 2026-10-14)
├── assets/
│   ├── icons/                   # Custom spell/class/race art (<MapKey>.png) picked up by build_icons.py
│   ├── models/                  # AI-generated shopping cart model scripts and converted files
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

`tools/` is not in git. Supply `Divine.exe` and `granny2.dll` yourself (see the LSLib ExportTool); they are needed for packing, localization and the cart model conversion.

### CLI Commands:
- `python build.py` - Regenerates the source tree, builds icons, recompiles localization and generates `dist/HomelessCalifornian.pak`.
- `python build.py --install` - Also copies the `.pak` into your BG3 Mods folder.
- `python build.py --activate` - Also installs and activates the mod in `modsettings.lsx`.
- `python -m unittest discover -s validation -q` - Runs the full validation suite (39 tests).
- `python build.py --status` - Verifies current mod installation and load order status.
- `python generate_mod.py` - Regenerates only the source tree (no icons or packing).
- `python build_icons.py` - Rebuilds only the icon atlas and GUI resources.

---

## 👥 Contributors & AI Pair Programming Team

- **Matthew (@themadhattermsr)** — Creator, Project Director, Gameplay Design & Live In-Game Playtester.
- **Claude (Anthropic)** — Initial Architecture, Handoff Lead, Generator Engineering & Lore QA, and directing and testing the AI-generated shopping cart (a Claude Sonnet agent wrote the procedural model scripts).
- **Codex (OpenAI)** — BG3 Mechanics Audits, Engine Functors, Subclass Balance & Donor Specialist.
- **Antigravity / Gemini (Google DeepMind)** — Lead Orchestrator, Generator Pipeline, Test Suite & Validation, and Visual Artist (custom spell icons, class crests, status art, and Nexus banners). The shopping cart model is AI-generated, not made by Gemini or a human artist.
- **Local Model (Qwen / Ollama)** — Offline Flavor Text Ideation, Creative Brainstorming & Dialogue Concepts.

