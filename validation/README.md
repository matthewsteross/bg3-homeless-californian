# Local preinstall checks

Run from the Homeless Californian project directory:

```powershell
py -3 -m unittest discover -s validation -p test_validate.py -v
py -3 validation/validate.py --pak dist/HomelessCalifornian.pak
```

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
