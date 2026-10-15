# Local preinstall checks

Run from the Homeless Californian project directory:

```powershell
python -m unittest discover -s validation -q
py -3 validation/validate.py --pak dist/HomelessCalifornian.pak
```

The suite (110 tests on the current source) lives in `test_validate.py` (12), `test_cart.py` (6), `test_expansion.py` (3),
`test_spell_rules.py` (18), `test_overpass.py` (21), `test_kit_additions.py` (11), `test_round2.py` (21), `test_tarp.py` (8) and
`test_junk_items.py` (10). The first four files held
39 tests at the v0.3.0 release. `test_overpass.py` covers the source-only Overpass Riverbed Dweller subclass, `test_kit_additions.py`
covers the source-only Squeegee Technician, Cardboard Insulator and NIMBY Zoning Defense, and `test_round2.py` covers the source-only
round 2 additions (Sprinkler Violation, Catalytic Converter Sawzall, One-Star Citation, HOV Lane, Bakersfield Tule Fog, the Decatted
Exhaust status, the Notary Street Trade and the Tinfoil Deflector Junk Doctrine), `test_tarp.py` covers the source-only blue tarp lean-to
prop (its assets, visual resource, root template and Object stat), and `test_junk_items.py` covers the source-only Curb Alert spell and the four junk
items it grants (Caltrans Detour Sign, Duct-Taped High-Tops, Lukewarm Gas Station Kombucha and Tin-Foil Sun Visor). Like everything else here, these are file-level
checks: they do not show that any of it works in game.

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
in the released package. See `HANDOFF-2026-10-14.md`. Anything it touches stays "not yet verified in game"
until Matthew confirms it by playing.
