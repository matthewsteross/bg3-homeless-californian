# Baldur's Gate 3 - Homeless Californian Class Mod

A custom class mod for **Baldur's Gate 3** introducing the **Homeless Californian** class.

---

## 🌟 Class Overview

Tempered by the unforgiving sidewalks of San Francisco and Los Angeles, the **Homeless Californian** brings makeshift bio-chemical warfare, erratic street fury, and the gravity-defying equilibrium of the legendary **Fent Lean** into Faerûn.

- **Primary Ability**: Constitution (Cast DC & Toughness) & Dexterity (Tossing accuracy & Reflexes)
- **Hit Die**: d12 (12 Base HP, +7 per level)
- **Saving Throws**: Constitution & Strength
- **Proficiencies**: Simple Weapons, Improvised Weapons, Clubs, Daggers, Shields
- **Armor Defense**: **Street Grit Defense** (Unarmored Defense: Add both Constitution & Dexterity modifiers to Armor Class when not wearing armor)

---

## 💥 Signature Abilities & Mechanics

### 💩 1. Sling Poop
*Hurl a handful of raw biological waste at a target.*
- **Action Type**: Action (Unlimited use / Cantrip style)
- **Range**: 18m
- **Damage**: `1d6 + CON Bludgeoning` + `1d4 Poison`
- **Effect**: Creates a biohazard puddle on impact and afflicts the target with **Fecal Stench** for 2 turns (-3m Movement Speed, Disadvantage on Attack Rolls and Ability Checks).
- **Level 5 Upgrade - Sling Chunky Poop**: Upgrades to `2d6 + CON Bludgeoning` + `2d4 Poison` and expands the splash radius to 2.5m.

### 💊 2. Sling Fentanyl
*Launch a concentrated dose of chemical contraband.*
- **Action Type**: Action (Recharges on Short Rest)
- **Range**: 18m
- **Damage**: `1d4 + CON Psychic`
- **Effect**: Spawns a toxic narcotic haze and forces a DC Constitution Saving Throw. On failure, inflicts **Fent Stupor** for 2 turns: target is **Incapacitated** (cannot take actions or reactions) with 0 Movement Speed.
- **Level 9 Upgrade - Mass Fentanyl Contraband**: 4m explosive AoE narcotic cloud dealing `3d6 + CON Psychic` damage and subjecting all enemies in the area to **Fent Stupor**.

### 🧘 3. Power Move: Fent Lean
*Assume the ultimate posture of street invulnerability: rigidly fold forward at a perfect 90-degree waist angle.*
- **Action Type**: Bonus Action (Recharges on Short Rest, lasts 3 turns)
- **Effects While Leaning**:
  - **Invulnerability**: Resistance to **ALL damage types** (Bludgeoning, Slashing, Piercing, Fire, Cold, Lightning, Acid, Poison, Force, Necrotic, Radiant).
  - **Immovable Stance**: Immune to Knockdown, Prone, Shove, and forced displacement.
  - **Detached Mind**: Complete immunity to Psychic damage, Frightened, Charmed, and Stunned.
  - **Bewildering Silhouette**: +3 Armor Class; attackers have Disadvantage against you.
  - **Trade-off**: Movement speed reduced by 100% (locked in place).
- **Snap Out of Lean**: Bonus action to cancel early and regain mobility.
- **Level 6 Upgrade - Restorative Stupor**: Passively regenerates `2d6 Hit Points` at the start of each turn while leaning.
- **Level 11 Upgrade - Baffling Retaliation**: Melee attackers striking you during Fent Lean suffer `1d10 Psychic damage` from sheer cognitive dissonance.

### 🏃 4. Additional Class Features
- **Sidewalk Scramble** (Level 1): Bonus Action to dash +4.5m while ignoring difficult terrain (broken glass, mud, grease).
- **Aggressive Panhandling** (Level 2): Action shout within 9m. Forces enemies to make a DC Wisdom Save or drop their guard and become **Frightened** for 2 turns.
- **Feral Screech** (Level 7): 9m AoE 3 AM sidewalk wail dealing `3d6 + CON Psychic` damage, Deafening and Frightening enemies.
- **Tent City Sanctuary** (Level 9): Deploys an emergency tarp perimeter granting 15 Temporary HP and Sanctuary protection.

---

## 🏙️ Subclasses (Level 3)

1. **Tenderloin Biohazard (Alchemist / Shaman)**
   - Specializes in expanded toxic surfaces, biohazard cloud proliferation, and the **Biohazard Bomb** (explosive feces & chemical payload).
2. **Venice Boardwalk Brawler (Martial Pugilist)**
   - Specializes in brutal close-quarters combat: **Broken Bottle Shank** (1d8 piercing + bleeding) and **Shopping Cart Charge** (9m rush that knocks enemies Prone).
3. **BART Platform Menace (Street Rogue)**
   - Specializes in urban dimensional evasion: **Turnstile Hop** (Bonus Action 12m teleport) and unshakeable street paranoia.

---

## 🛠️ Project Structure & Build Tool

```
Baldurs Gate 3 Homeless Californian Class/
├── generate_mod.py              # Generates all LSX, XML, and txt data with deterministic GUIDs
├── build.py                     # Pipeline: compiles loca, packs .pak, installs & activates
├── dist/
│   └── HomelessCalifornian.pak  # The packaged mod ready for BG3
├── src/HomelessCalifornian/      # Full unpacked mod source tree
│   ├── Mods/HomelessCalifornian/meta.lsx
│   └── Public/HomelessCalifornian/...
└── tools/Packed/Tools/Divine.exe# LSLib Divine tool used for packing and localization
```

### CLI Commands:
- `python build.py` - Recompiles localization and generates `dist/HomelessCalifornian.pak`.
- `python build.py --install` - Copies the `.pak` directly into your BG3 Mods folder.
- `python build.py --activate` - Activates the mod in `modsettings.lsx`.
- `python build.py --status` - Verifies current mod installation and load order status.
