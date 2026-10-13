# Baldur's Gate 3 - Homeless Californian Class Mod

## Public playtest

[Download the playtest (Oct 13 build)](https://github.com/matthewsteross/bg3-homeless-californian/releases/tag/playtest-2026-10-13) · [Nexus Mods page](https://www.nexusmods.com/baldursgate3/mods/25761) · [Report a bug](https://github.com/matthewsteross/bg3-homeless-californian/issues/new/choose)

**Throw bricks. Weaponise furniture. Make public transit everybody else's problem.**

Looking for PC testers for a ridiculous Constitution-based class with three
subclasses: Tenderloin poison, Venice furniture melee, and BART repositioning.
Try one subclass for ten minutes and tell us one thing that broke—or one thing
that worked. [Start the short tester checklist](TESTING.md).

The downloadable build is the October 13 playtest build (v0.2.0); the older
October 12 build is still available on its own release page. Use the release ZIP
for playtesting. The Toolkit upload is pending account resolution and publication;
it is not confirmed available in the in-game menu.

Intentionally overpowered: this is a ridiculous class with actions, saves,
Junk costs and rest cooldowns, rather than an attempt at vanilla balance.
The starting-area test confirmed icons after a reload and castability of
available spells. Full effect, progression and compatibility testing continues.
The human directs the design; Claude, Gemini and Codex helped with code, and
the custom icons were generated with Gemini.

This download is the manual PC package. It is not yet a mod.io/in-game or
console release. Use a separate test save; respec or start a new character if
new progression grants are missing. Keep the mod installed on saves that use it.

## October 13 build - capstone, Street Trade, Doctrines and the Hustle kit (NOT yet play-tested)

The repository source and `dist/HomelessCalifornian.pak` now contain a much larger build than the October 12
playtest ZIP: the level-12 **Squatter's Rights** capstone, a **Street Trade** selector, **Junk Doctrines**, and the
**Hustle kit** (Guilt Trip, Beg, Public Scene, Trapped in the Invisible Box, Bucket Drum Solo, Compassion Burnout,
Punctured Lithium Cell, Sublet, Everybody Knows This Guy, plus the Homeless Fatigue and Breadcrumbed statuses).
**Honest status:** file-level checks and 14 validation tests pass. In game, only "a character can reach level 12
without a catastrophic failure" has been confirmed; individual abilities have not been tested, and **Beg** (gold from
non-hostile NPCs) is the most experimental. Use a new character or a respec for new grants. Test routes for the new
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
| Class 7 | Moving Day | While leaning: free, once per short rest; ends Lean, +6 m movement and difficult-terrain immunity for 1 turn |

All ten local expansion abilities now have custom Gemini-generated icons,
including matching icons for the Chair, Moving Day, and ready-Shiv statuses.
The atlas grows automatically as new art is added. The abilities still use
existing animations. The chair
abilities do not display a new chair mesh. The "pigeon" is visibly a raven, and
the wardrobe uses existing robe/cloak visuals, not a custom safety vest or
blue tarp model. Guns and custom meshes are future work. The level-12
Squatter's Rights capstone and Phase 2 class-depth choices remain design drafts;
they are not included in this package.

**Honest status:** source and package checks and 14 validation tests pass.
Matthew confirmed starting-area icons after reload and castability of available
spells; individual effects still need testing. Wrong Platform's enemy swap is
the most experimental addition. The installed/published icon build is
14,932,869 bytes, SHA256
`552ae557a794eb7a0a9799dfb2ca37421548f58bf5587533f7853d93263d63fc`.

For existing characters, respec into the class or start a new test character
to receive new progression grants. Confirm the UI and grants in-game; do not
assume updating a package retroactively reapplies already-earned levels.

Build-only: `python build.py`. The build now runs the local validator before
an optional install. Run `py -3 -m unittest discover -s validation -p
test_validate.py -v` for the deliberate-corruption checks. The saved original
package can restore the previous build with BG3 closed. Keep the candidate
out of co-op until both players intentionally use the same package.

A custom class and race mod for **Baldur's Gate 3** introducing the **Homeless Californian** class (levels 1-12, three subclasses) and the **Californian** race (three subraces, a California identity / gender selector, and a restricted garish look).

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
| 1 | Street Grit Defence, Sidewalk Immunity, Proposition 47, Sling Poop, Sling Fentanyl, Fent Lean, Narcan, Sidewalk Scramble, 3 skills, +2/+1 ability bonus |
| 2 | Aggressive Panhandling, Pocket Lint Buffet, Street Hustle |
| 3 | **Subclass choice** (subclass features below) |
| 4 | Eviction Notice, Ability Improvement |
| 5 | Extra Attack, Sling Chunky Poop; Sling Poop damage steps up |
| 6 | Restorative Stupor, Unkillable Vagrant; subclass feature |
| 7 | Feral Screech |
| 8 | Ability Improvement |
| 9 | Mass Fentanyl Contraband, Pitch Tent Encampment |
| 10 | Encampment Sweep Survival Instinct; subclass feature; Sling Poop damage steps up |
| 11 | Extra Attack (2 extra attacks), Baffling Retaliation |
| 12 | Call 311 (On Hold), Ability Improvement |

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

### 🛡️ Passive Features
- **Street Grit Defence** (1): Unarmored AC = 10 + Dexterity + Constitution modifiers; shields still allowed.
- **Sidewalk Immunity** (1): Immune to Poisoned and Disease, Resistance to Poison damage.
- **Proposition 47** (1): Hitting an enemy with a melee attack grants a **Stolen Patagonia Vest** for 2 turns (+1 AC, +1d4 Bludgeoning on weapon attacks).
- **Pocket Lint Buffet** (2): Once per turn, damaging a creature afflicted with Fecal Stench grants Temporary HP equal to your CON modifier + 2 (minimum 3).
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

### Venice Boardwalk Brawler
*A close-quarters pugilist with shivs, flurries and shopping carts.*
- **L3 - Heavy Armor proficiency**
- **L3 - Broken 40oz Shank**: Bonus Action melee attack, `2d6 + CON Piercing` + `1d6 Slashing`, Bleeding for 2 turns.
- **L3 - Shopping Cart Charge**: Action, 9m rush, Short Rest. `4d8 + CON Bludgeoning` to the first creature hit; failed Strength save knocks it Prone.
- **L6 - Muscle Beach Juice**: Weapon attacks deal an extra `1d8 Bludgeoning`; +2 AC.
- **L10 - King of the Boardwalk**: Critical hits on 18-20; heal `1d8` HP whenever you hit with a melee attack.

### BART Platform Menace
*An erratic street phantom who slips through turnstiles and spatial dimensions.*
- **L3 - Reliable Talent** (vanilla)
- **L3 - Turnstile Hop**: Bonus Action teleport up to 18m, once per turn.
- **L6 - Evasion** and **Uncanny Dodge** (vanilla)
- **L10 - Last Train Phantom**: +4.5m movement, immune to difficult terrain.
- **L10 - Express Hop**: Free teleport up to 9m, once per turn.

---

## 🌴 Californian Race

Hailing from the Golden State, **Californians** are a human-bodied race (standard human body types, camera poses and appearance options) with uncanny resilience shaped by natural disasters, gridlock traffic and perpetual microclimates.

**Base traits**
- Resistance to Fire damage
- **Earthquake Sense**: cannot be knocked Prone
- **405 Commute Veteran**: cannot be Slowed or Restrained
- **Touch Grass**: Action, Short Rest. Melee spell attack for `1d8 Psychic`, ends Rage, and inflicts Existential Daze (Disadvantage on attack rolls) for 2 turns.
- **Avocado Toast**: Bonus Action, Short Rest. Regain `1d6 + CON` HP and gain 5 Temporary HP.
- Racial spells use Charisma as their spellcasting ability.

### Subraces
| Subrace | Traits |
|---------|--------|
| **Beachborn (SoCal)** | Resistance to Radiant damage; **Hang Ten** (Bonus Action, Short Rest): +3m movement and immunity to difficult terrain and Prone for 2 turns |
| **Siliconite (NorCal)** | **Siliconite Synergy**: once per turn, weapon damage deals an extra `1d4 Psychic`; **Vibe Check** (Action, 18m, Short Rest): failed Wisdom save breaks concentration and applies Vibe Checked (no Bonus Actions or Reactions, halved movement) |
| **Inland Emperor (The Valley)** | Resistance to Poison damage; **Smog Lungs** (Advantage vs Poisoned, immune to Disease); **Heat Index Mastery** (immune to Burning) |

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
├── assets/
│   ├── icons/                   # Custom spell/class/race art (<MapKey>.png) picked up by build_icons.py
│   ├── human_race_children.xml  # Human race appearance data reused (and look-restricted) for the Californian race
│   ├── human_cc_appearance_visuals.xml  # Human character creation visuals cloned for the Californian race
│   └── cc_color_names.json      # Colour names used to enforce the Californian look lock
├── dist/
│   └── HomelessCalifornian.pak  # The packaged mod ready for BG3
├── src/HomelessCalifornian/     # Full unpacked mod source tree
│   ├── Mods/HomelessCalifornian/meta.lsx
│   └── Public/HomelessCalifornian/...
└── tools/Packed/Tools/Divine.exe # LSLib Divine tool used for packing and localization
```

### CLI Commands:
- `python build.py` - Regenerates the source tree, builds icons, recompiles localization and generates `dist/HomelessCalifornian.pak`.
- `python build.py --install` - Also copies the `.pak` into your BG3 Mods folder.
- `python build.py --activate` - Also installs and activates the mod in `modsettings.lsx`.
- `python build.py --status` - Verifies current mod installation and load order status.
- `python generate_mod.py` - Regenerates only the source tree (no icons or packing).
- `python build_icons.py` - Rebuilds only the icon atlas and GUI resources.
