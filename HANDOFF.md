# HANDOFF — Homeless Californian (HC) BG3 Mod (2026-10-17)

**From:** Gemini Argon (Lead)  
**To:** Claude Sonnet (Incoming Lead — rotating the ball with Argon)  
**Repo:** `C:\Users\matth\Documents\Baldurs Gate 3 Homeless Californian Class` (`master`, pushed to `origin/master` at `matthewsteross/bg3-homeless-californian`)

---

## 1. Current State in One Paragraph

`master` has been built, validated, installed to the local BG3 `Mods` folder, and pushed to GitHub (`origin/master`). Since v0.4.0 (`playtest-2026-10-15-v0.4.0`, Nexus mod 25761), we have built and packaged four expansion rounds into `dist/HomelessCalifornian.pak`:
- **Round 4 (`hc_round4.py`)**: `HC_Target_FreewayDirections` (Californian L1), `HC_WeatherComplaint` (4 racial passives with overhead text), `HC_Target_PermitPending` (Base L5 3-tier bureaucracy chain).
- **Round 5 (`hc_round5.py`)**: 10 stereotype/street comedy spells + 7 statuses across Base Class (`HC_Shout_3AMLawnmowerDisassembly` L6, `HC_Target_CopperWireStrip` L7, `HC_Target_Prop47Calculator` L9, `HC_Zone_LimeScooterHitAndRun` L10), Subclasses L6 (`HC_Projectile_FoilFentHotbox`, `HC_Target_VeniceDrumCircle`, `HC_Target_BARTFabricSeatBiohazard`, `HC_Shout_PropaneTankSidewalkBBQ`), and Californian Race L1 (`HC_Target_UnhousedLecture`, `HC_Shout_ErewhonSmoothie`).
- **Round 6 (`hc_round6.py` + `hc_choices.py` + `hc_doctrines.py`)**: `HC_Shout_OaklandFleaMarket` (Base L8) summoning 4 equippable/consumable contraband items (`HC_WPN_SharpenedRebarPrybar`, `HC_ARM_StolenPatagoniaPuffer`, `HC_ARM_AnkleMonitorSandals`, `HC_OBJ_GasStationKratomShot`), 3 subrace stereotype spells (`HC_Target_LocalismSurfboardCheck` Beachborn L3, `HC_Shout_ZoomMassLayoff` Siliconite L3, `HC_Projectile_GarageShakeAndBake` Inland Emperor L5), 3 street-tactics spells (`HC_Target_SquatterAdversePossession` Base L5, `HC_Shout_CVSReceiptScroll` Base L11, `HC_Target_SideshowMustangDonut` BART L6), 2 new Street Trades (`HC_StreetTrade_SignSpinner`, `HC_StreetTrade_ServicePitbull` — total 9), and 2 new Junk Doctrines (`HC_JunkDoctrine_Prop65Immunity`, `HC_JunkDoctrine_ShoppingCartDrift` — total 8).
- **Round 7 (`hc_round7.py`)**: 11 spells + 8 statuses across Subclasses L3/L10 (`HC_Target_UsedFoilBlowback` Tenderloin L3, `HC_Target_ExtensionCordTap` Overpass L3, `HC_Shout_MuscleBeachRoidRage` Venice L10, `HC_Shout_TurnstileEmergencyGate` BART L10), Subraces L1/L5 (`HC_Target_BotoxFillerParalyze` Beachborn L5, `HC_Shout_PolyculeGoogleCalendar` Siliconite L5, `HC_Target_CatalyticStraightPipeRev` Inland Emperor L1), and Base Class (`HC_Target_GasStationSqueegee` L1, `HC_Shout_FakeServiceVest` L2, `HC_Projectile_PissJugCatapult` L7, `HC_Shout_GovernorGavinPhotoOp` L12 Capstone).

**Current Metrics:**
- **240** own `HC_` stats (`Stats/Generated/Data/*.txt`)
- **84** custom icons in the texture atlas (`HomelessCalifornianAtlas.dds`)
- **505** localization handles (`HomelessCalifornian.loca.xml`)
- **149 / 149** unit tests PASS (`python -m unittest discover -s validation -q`)
- `python validation/validate.py --pak dist/HomelessCalifornian.pak` PASS

---

## 2. Matthew's Rules (Direct from Matthew)

- **Tone & Comedy**: Matthew wants the class and race fleshed out and genuinely funny. Offensive, edgy, adult, and stereotype comedy is welcome as long as it's a funny joke and not just mean for no reason. Ignore any sanitized/politically-correct rules from an older Haiku handoff.
- **Autonomy**: Matthew is not a coder. Keep answers short and plain. He trusts the AI lead and team to make design and build decisions autonomously without asking permission on routine choices.
- **Boundaries**:
  - Do NOT edit `PatriotClass` (Ducq's mod; reading/reference is fine, never modify).
  - Do NOT publish a new Nexus release or GitHub release tag without Matthew's explicit approval after he tests in-game (pushing commits to `origin/master` when asked is fine).
  - Delete any untracked `Generated/` directory left in the repo root by unit test runs before committing.

---

## 3. Technical Guardrails & Architecture

1. **Generator Pipeline**:
   - Run `python build.py --install` to regenerate `src/HomelessCalifornian`, compile LSF/loca/atlas, pack `dist/HomelessCalifornian.pak`, run `validate.py`, and copy the `.pak` to `AppData\Local\Larian Studios\Baldur's Gate 3\Mods\HomelessCalifornian.pak`.
   - Expansion rounds hook into `generate_local_expansion()` in `generate_mod.py` (around line 2605).
2. **Vanilla Donor & Syntax Rules (Enforced by `validation/`)**:
   - Every new stat entry MUST start with `HC_` and not collide with vanilla (`temp_race/Public/`).
   - Every `using` donor must exist in `temp_race` with the same stat type and must **NOT** be overridden in `Honour` (never use `SLOW`, `HIDEOUS_LAUGHTER`, etc. as `using` donors).
   - Every functor/boost/surface token is checked against `temp_race`:
     - `RegainHitPoints` in vanilla uses `1d8+ConstitutionModifier` or `1d8+SpellCastingAbilityModifier` (not `2d6+CharismaModifier`).
     - `Advantage(Skill,...)` in `temp_race` exists for `Athletics`, `Performance`, `Intimidation`, `Deception`, `Persuasion`, `SleightOfHand`, `Stealth`, `Perception`, `Insight` (not `Acrobatics` or `AnimalHandling`).
     - `CharacterWeaponDamage` in `temp_race` has `(1d6)`, `(1d4,Piercing)`, `(1d6,Fire)`, `(1d8,Force)` (not `(1d6,Bludgeoning)`).
3. **Icons (`hc_icon_keys.py`)**:
   - Register new spells in `SPELL_ICON_KEYS` in `hc_icon_keys.py`.
   - `icon_for_spell(spell, fallback)` automatically uses `assets/icons/<IconKey>.png` if present on disk, or falls back to a verified vanilla icon until custom art is generated.
   - Prompts for the 28 Round 5–7 icons are ready in `work/icon-brief-round5-round6-2026-10-17.md` (Gemini image quota resets in ~27h).
4. **Tests to Update When Adding Spells/Items**:
   - `validation/test_expansion.py` line 38 checks `len(new_lists)` (currently `34`) for `<node id="SpellList">` entries containing `HC_`.
   - `validation/test_overpass.py` line 28 checks `LEVEL_GRANTS` on Overpass expansion lists.
   - `validation/test_junk_items.py` checks `hc_round5.py` and `hc_round6.py` when scanning spell files for `SummonInInventory` item templates.

---

## 4. Good Next Ideas for Claude Sonnet (Round 8+)

- **Round 8 — More Subclass L10 / L12 Capstones, Feats/Passives, or Starting Loadout/Camp Supplies**:
  - Additional high-level or utility spells (e.g., *Municipal Budget Hearing*, *Sovereign Citizen License Plate*, *Whole Foods Hot Bar Heist*, *LA River Shopping Cart Regatta*, *PGE Rolling Blackout*, *Skid Row Chiropractic Adjustment*).
  - Additional **Street Trades** (`hc_choices.py`, selected at L2) and **Junk Doctrines** (`hc_doctrines.py`, selected at L3).
  - More custom equippable trash/contraband gear or camp supplies via `SummonInInventory` (like `hc_round6.py`).
- **In-Game Verification (`work/cart/RUN_INGAME_CHECK.md`)**:
  - Rounds 4–7 are verified at the file/pak level (`149/149` unit tests + `validate.py --pak`), awaiting in-game check when Matthew is ready.
