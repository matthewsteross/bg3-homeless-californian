# Local preinstall checks

Run from the Homeless Californian project directory:

```powershell
python -m unittest discover -s validation -q
py -3 validation/validate.py --pak dist/HomelessCalifornian.pak
```

The suite has **322 tests** in 26 files (counted by `def test_` per file; 110 of them were the suite shipped in v0.4.0, and the other 207 are
the source-only rounds 4-10 and the nine source-only props: barricade, tent, scooter graveyard, robotaxi, porta-potty, and the four round 10 props: spike bench, utility pole, spin bike and cooler bonfire). The first four files held 39 tests at the v0.3.0 release; the next five cover the additions in v0.4.0; the last
sixteen cover the source-only additions and are **not part of the public v0.4.0 download**. The list-count and level-grant assertions in `test_expansion.py`, `test_overpass.py` and `test_junk_items.py` were adjusted for rounds 8 and 9 (their test counts did not change).

| File | Tests | Covers |
|---|---:|---|
| `test_validate.py` | 12 | The validator itself, including deliberately corrupt fixtures |
| `test_cart.py` | 6 | The Abandoned Cart spell, template and model assets |
| `test_expansion.py` | 3 | The October 12 Junk toolkit lists and grants |
| `test_spell_rules.py` | 18 | Spell syntax rules against vanilla data |
| `test_overpass.py` | 21 | The Overpass Riverbed Dweller subclass |
| `test_kit_additions.py` | 11 | Squeegee Technician, Cardboard Insulator and NIMBY Zoning Defense |
| `test_round2.py` | 21 | Sprinkler Violation, Catalytic Converter Sawzall, One-Star Citation, HOV Lane, Bakersfield Tule Fog, the Decatted Exhaust status, the Notary Street Trade and the Tinfoil Deflector Junk Doctrine |
| `test_tarp.py` | 8 | The blue tarp lean-to prop (assets, visual resource, root template and Object stat) |
| `test_junk_items.py` | 10 | The Curb Alert spell and the four junk items it grants (Caltrans Detour Sign, Duct-Taped High-Tops, Lukewarm Gas Station Kombucha, Tin-Foil Sun Visor) |
| `test_round4.py` | 23 | Source-only. Freeway Directions (no Prone, copied Hold Person save fields and laughter audio/animation), Weather Complaint (cosmetic lines, triggers, lock ordering, reset), Permit Pending (three stages, Bane roll penalties replaced, one-turn Slow approval, 100-HP threshold), donors and vanilla evidence across the five stat layers, icon fallbacks |
| `test_round5.py` | 5 | Source-only. The 10 round 5 spells and 7 statuses: unique `HC_` names, donors, base/subclass/racial grants, mechanics and surfaces, localization and icon registration |
| `test_round6.py` | 6 | Source-only. Round 6: unique names and donors (including the item templates), the Flea Market summons all four items and the Rhino shot's consume status, base/subclass/subrace grants, the two new Street Trades and two new Junk Doctrines, localization and icons |
| `test_round7.py` | 5 | Source-only. The 11 round 7 spells and 8 statuses: unique names, donors, base/subclass/subrace grants, mechanics and surfaces, localization and icon registration |
| `test_round8.py` | 15 | Source-only. The 10 round 8 spells and 9 statuses: unique `HC_` names, donors, base/subclass/racial grants, mechanics and surfaces, failed-save-only enemy effects, vanilla precedent for every boost and functor, localization and icon registration |
| `test_barricade.py` | 10 | Source-only. The Caltrans 'Lane Closed Ahead' barricade prop and spell (model round trip through Divine, visual resource, root template and Object stat, spawn spell and costs, the +2 AC status, grant level, GUID uniqueness) |
| `test_tent.py` | 12 | Source-only. The Pop-Up Encampment Tent prop and spell (model round trip through Divine, 1024 px texture, visual resource, root template and Object stat, spawn spell and costs, the 8 temporary hit points status, grant level, GUID uniqueness) |
| `test_round9.py` | 18 | Source-only. The 10 round 9 spells and 4 statuses: unique `HC_` names that do not override vanilla, donors (none overridden in Honour), grant levels, costs and cooldowns (racial spells cost no Junk, class spells at most one), enemy-only targeting and failed-save-only enemy effects, the status and spell mechanics, exact vanilla precedent for every boost, functor and damage form, localization and descriptions |
| `test_scooters.py` | 12 | Source-only. The Dockless Scooter Graveyard prop and spell (model round trip through Divine, 1024 px texture, visual resource, root template and Object stat, spawn spell and costs, the Lightning-damage and movement status, Beachborn level-5 grant, GUID uniqueness) |
| `test_robotaxi.py` | 12 | Source-only. The Broken-Down Robotaxi prop and spell (same model, template and spawn-spell checks, the movement and Dexterity-save-advantage status, Siliconite level-5 grant, GUID uniqueness) |
| `test_portapotty.py` | 12 | Source-only. The Tipped-Over Festival Porta-Potty prop and spell (same model, template and spawn-spell checks, the Poisoned-immunity and +1d4 saves status, Inland Emperor level-5 grant, GUID uniqueness) |
| `test_round10.py` | 24 | Source-only. The 9 round 10 spells, the Caltrans Safety Vest (rare light armour, inherited AC and Dexterity, Hi-Vis Authority equip passive), the Rent-Stabilized Grit passive (HP-gated boost passive at base level 9) and 5 statuses: unique `HC_` names, donors (none overridden in Honour), grant levels, costs and cooldowns, enemy-only targeting, failed-save-only enemy effects, vanilla precedent for every boost and functor, localization and a check for foreign-mod references in generated text |
| `test_bench.py` | 13 | Source-only. The Hostile Architecture Spike Bench prop and spell (model round trip through Divine, 1024 px texture, visual resource, root template and Object stat, spawn spell and costs, the resistance and Prone-immunity status, base level-10 grant, GUID uniqueness) |
| `test_utilitypole.py` | 13 | Source-only. The Sparking Utility Pole prop and spell (same model, template and spawn-spell checks, the Lightning-resistance and small flat-bonus status, base level-11 grant, GUID uniqueness) |
| `test_spinbike.py` | 14 | Source-only. The Evicted Studio Spin Bike prop and spell (same model, template and spawn-spell checks, the Athletics, Intimidation and Constitution advantage status, base level-6 grant, GUID uniqueness) |
| `test_coolerfire.py` | 13 | Source-only. The Sidewalk Cooler Bonfire prop and spell (same model, template and spawn-spell checks, the Cold-resistance and +1d4 Fire status, base level-4 grant, GUID uniqueness) |
| `test_sounds.py` | 5 | Source-only. The meme-sound map `hc_sound_map.json`: every event name is a real vanilla CastSound/TargetSound/PrepareSound value, only HC spells are touched, applying twice gives the same result |
| **Total** | **322** | |

Like everything else here, these are file-level checks: they do not show that any of it works in game. In particular, none of the round 4-10 or nine-prop
tests play a spell; `test_round4.py` says in its own test name that its status chain check is "smoke only, not engine execution".

The validator returns exit code **1** on a finding. It does not install, regenerate,
edit source, modify game configuration, or contact GitHub. `--pak` extracts into a
temporary folder under `work/local_validation`, compares files, then removes that
temporary folder. The package reader is the shared repository's independent
stdlib `tools/lspk_list.py`; it is run as a subprocess and is never edited.

Checks cover local stat duplicates and types, `using` targets and cycles, common
status/passive/spell functor references, passive grants, spell containers and lists,
selector UUIDs, localization handles, icons and game-facing icon files, well-formed
XML, action resource definitions and cost/boost names, cooldowns, and surface names
with evidence from vanilla `CreateSurface` calls. Every local stat is checked,
irrespective of its naming prefix. Vanilla status groups are indexed from vanilla
declarations rather than treated as missing StatusData entries.

Reference data is expected in the local `temp_race` extraction with all five
layers: Shared, SharedDev, Gustav, GustavDev, and Honour. Missing layers fail the
check; game data is not copied into the repository. Vanilla handles and icons can
be proved by their occurrence in vanilla resources even where the extraction
does not contain the vanilla localization or texture files.

The tests deliberately create corrupt temporary fixtures, including missing
references without an HC prefix, wrong donor types, cyclic inheritance, invalid
XML, dangling selector UUIDs, missing art/text/resource names, unsupported surface
names, incomplete vanilla references, and package/source disagreement.

## Limits

This is **file-level verification**, not a gameplay test or a complete parser of
BG3's functor language. It does not prove animation/effect UUID validity, texture
appearance, body fitting, action economy, equipment behavior, balance, or saved
game compatibility. A surface name occurring in vanilla demonstrates spelling,
not whether a particular spell should create that surface.

Package comparison is byte-for-byte for shipped source files. A compiled
`.lsf` counterpart may satisfy an omitted `.lsf.lsx` authoring file; the tool does
not equate those formats or prove the conversion is semantically current. It
checks compiled localization files exist and match the package bytes, but does
not decode them to compare text to authoring XML. Human playtesting remains the
release gate.

## Live in-game testing

A Script Extender (BG3SE v33) harness exists for dev-only test builds. The harness is never shipped
in the released package. See `HANDOFF.md`. On 2026-10-15 it was used for an in-game data check of the v0.4.0 content (everything loads, Curb Alert grants its items, the tarp spawns, four ground effects appear); it does not test damage, saves or balance. Anything it touches stays "not yet verified in game"
until Matthew confirms it by playing. That check predates rounds 4-10 and the nine source-only props (barricade, tent, scooter graveyard, robotaxi, porta-potty and the four round 10 props), so nothing from them has been seen in game.
