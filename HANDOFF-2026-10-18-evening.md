# Handoff, 2026-10-18 evening (Claude, lead) — read this first, then HANDOFF.md for older history

Project: BG3 mod "Homeless Californian" (HC). Folder `C:\Users\matth\Documents\Baldurs Gate 3 Homeless Californian Class`, git master (personal repo `matthewsteross/bg3-homeless-californian`, MANY local commits ahead, not pushed). Shared repo with Ducq is `ZellisE82/bg3-meme-mods` (HC lives in `mods/HomelessCalifornian/`). **Never read, edit, build or copy Patriot-named paths (Ducq's).** Reading Ducq's repo is fine; never edit his stuff.

## Matthew's standing orders
- "Biggest, most amazing, artful update yet." Keep fleshing out the class: spells at every level, subclasses with something at every level, funny/edgy/cool (aim at institutions, transit, housing, tech, wellness, bureaucracy, Caltrans; no slurs, no sexual content, don't mock real people's suffering).
- Keep making Meshy (3D) + Blender assets tied to spells/skills and to items the character uses (props and objects ONLY, no player-model/body work). Example he gave: Unclaimed Wardrobe (done, see below).
- Use the AI team (Solo project 2): Codex builders, Gemini Flash/Argon, Grok. Do not spin up more Sonnet/Opus sub-agents. He verifies everything in one BG3 run later; **do NOT install the pak into BG3 or push to the shared repo until he says so** (BG3 must be closed to install; back up the old pak first into `work/installed-backups/`).
- Matthew said to stop the GitHub issue #1 watcher (co-op fix is done; Ducq just hasn't closed it). Cron removed.
- He says "don't whine"; act, do not ask him to do things.

## State right now (all committed locally except the last build output)
- `python build.py` OK (pak about 57 MB). `python -m unittest discover -s validation -q`: **562 tests pass**.
- Added this session (all local, all UNVERIFIED in game):
  - Caltrans punchline jokes pass; dumpster has a "WASTE MISMANAGEMENT" WM-lookalike decal (`MIRROR_DECAL` in hc_dumpster.py if the game mirrors it).
  - Sound map `hc_sound_map.json` now 125 spells (vanilla sound events only; test_sounds enforces they exist and no event used more than 5 times). Custom meme audio is PARKED (needs Script Extender plus an in-game test).
  - 8+ new Meshy props wired into generate_mod.py (each patches an existing spell with a timed `GROUND:Spawn(<guid>, ,HC_PROP_LIFETIME_10T)`): condemned mattress (Squatter's Rights Tenderloin), therapy couch, propane BBQ, hot bar, plexiglass aisle, receipt scroll, retrofit scaffold, animal-style tray (In-N-Out), unclaimed wardrobe prop (`hc_wardrobeprop.py`, uses assets/meshy/wardrobe3), council podium (assets/meshy/podium2). Earlier props: dumpster, lawn chair, curb pile, trash bags.
  - **Sunglasses stall** (assets/meshy/sunglasses3): Codex #80 was building `hc_sunglasses.py` + `validation/test_sunglasses.py` + `work/sunglasses-report.md`. The module files exist; check the report says PASS, then wire it (`from hc_sunglasses import generate_sunglasses; generate_sunglasses(PUBLIC_DIR, add_loca, get_guid)` after the other generators in generate_mod.py main, next to generate_podium). If it was rejected or unfinished, skip it.
  - Subclass round 2: `hc_sub_round2.py` adds 12 spells (L5, L8, L11 for Venice, Tenderloin, Overpass, BART) + 7 statuses, wired in generate_mod.py next to hc_sub_others. Icon keys for them are registered in hc_icon_keys.py (PNG missing, so they fall back to vanilla icons until art exists).
  - Subclass levels 4-11 plumbing (`hc_subclass_levels.py`), BART 12 features (`hc_sub_bart.py`), Venice/Tenderloin/Overpass 18 features (`hc_sub_others.py`), Round 10 and 11 content: all wired earlier.
- Test-fixing pattern for prop modules: tests that read the built `src/.../Stats/...` spell text must wrap it with `validation/prop_patch_helper.unpatched(...)` because the build already contains the spawn patch.

## Meshy (credits about 2,900 left; each prop about 30 credits)
- Client: `python meshy_client.py text3d "<prompt>" --name <n> --polycount 8000 --no-pose --refine --texture-prompt "<t>" --yes` (dry run without `--yes`). Key in git-ignored `.env`; never print or read it. Task log `work/meshy/tasks.jsonl`. Batch scripts in `work/meshy/batch*.sh`.
- **Batch 7 was just launched** (`work/meshy/batch7.sh`, done marker `work/meshy/batch7.done`): `dumbbells` (outdoor weight rack, for Venice L11 Muscle Beach Bro Spotter, spell HC_Shout_MuscleBeachBroSpotter), `hazmatsign` (A-frame biohazard sign, for HC_Shout_FederalHazmatDeclaration), `palletwall` (pallets + corrugated tin, for HC_Shout_PalletAndTinArmor). Look at `assets/meshy/<name>/thumbnail.png`; reject models with floating parts or open/missing geometry (Codex QA does this too).
- Converting a Meshy model to a prop: give a Codex builder `work/brief-meshy-batch2-common-2026-10-18.md` and add an assignment line to `work/brief-meshy-batch2-assign-2026-10-18.md` (prop name, spell to patch, target height, source folder). Each builder writes `hc_<prop>.py` (generate_<prop>), `validation/test_<prop>.py`, `assets/models/HC_<Prop>/`, `work/<prop>-report.md`. The lead then wires the generator into generate_mod.py, rebuilds, runs tests.
- Props only attach to existing spells with a self-cast Shout (confirmed in game for the tarp). Target-type spells with ground spawn are untested.

**Icon run result (15:36 on 2026-10-18):** Gemini image quota is STILL exhausted (429 RESOURCE_EXHAUSTED, resets about 14:30 on 2026-10-19). Zero icons were made; `assets/icons` still has 49 PNGs. Process 77 is idle. Retry after the reset with the same prompt (the one-shot cron is spent). The list is 81 icons now (includes the 12 round-2 spells).

**Codex can make icons (Matthew approved):** Codex #20 was switched to GPT-6-Luna low (/model) and its built-in image tool works (images land in C:/Users/matth/.codex/generated_images/<id>/exec-*.png; the tool prints 'Saved to: file:///...' which IS the image). Brief: `work/solo-brief-codex-icons-2026-10-18.md` (12 per run). Each icon is saved with `python work/save_icon.py <png> <IconName> "Codex image"`. Status lines go to work/codex-icon-status.md. Luna low sometimes misreports; check the file. Row 1 (Spell_CurbsideClinic) was saved by the lead.

**Matthew's newest directives:** (1) subclasses must share a common core of spells with only mild differences: `hc_sub_round2.py` now grants all 12 round-2 spells plus the new L7 `HC_Shout_OversizedSharpsDisposal` to ALL four subclasses (he plays BART); keep this principle for future subclass content (shared base, small flavour differences). (2) A "stupid large" used-needle Meshy prop (assets/meshy/needle2, about 4 m, `hc_giantneedle.py` by Codex #80, assignment K) spawned by that spell. (3) Codex may be used for icons (see above).

## Solo agents (project 2; use mcp__solo__send_input; every message to Codex needs a following [13] Enter ONLY if it did not submit; never send text while an agent sits at an approval prompt, it cancels the command)
- 20 Codex (BG3 Modding), 80 Codex (Subclass Builder), 81 Codex (Subclass Builder 2). Codex 5h limit is about 30% left: go easy on Codex.
- 21 Gemini Argon, 78 Gemini Flash Writers Room, 77 Flash Icon Art, 79 Grok. Gemini agents ask "Allow creation of this file?" for files my briefs told them to write: approve with [13]. Grok uses a numbered menu (type 3, Enter).
- Cron `4792e49b` (one-shot 15:36) tells the lead to run the Flash icon job: brief `work/solo-brief-flash-icons-2026-10-18.md`, list `work/icons-missing-2026-10-18.tsv` (81 icons, at most 25 per run, quota check first with ONE icon; approve only the `work/save_icon.py` command). Process 77 does it. If the quota is still exhausted, record it and try again later. Icons land in `assets/icons/`; `hc_icon_keys.py` makes the build use them only once the PNG exists.

## Still to do (suggested order)
1. Check batch 7 models, send the good ones to a Codex builder (80 or 81, whichever has budget), wire, rebuild, test, commit.
2. Wire sunglasses if Codex's report passed.
3. Icon runs (see above); rebuild after each batch; commit.
4. Round 12 ideas if wanted: more base-class spells at lean levels (base L2 has 4, L3 has none by design), Caltrans spell ideas in `work/caltrans-grok.md` (Phase Two, In Transition, Transfer at the Cone, It's Just a Phase), extend `hc_sound_map.json` to the 12 round-2 spells and the Round 10/11 spells not yet mapped (Flash, text-only job; keep the 5-use cap per event).
5. Docs refresh (README.md, TESTING.md, validation/README.md, HANDOFF.md still say 317-411 tests; truth is 562+) and a Nexus changelog draft for the next version (Haiku or Flash can draft; the existing text is `work/public-playtest/nexus-update-0.4.5.md`).
6. Release gate: Matthew verifies in game (props spawn, despawn after about 60 s, dumpster decal, subclass spells, co-op). Then: back up and install the pak (`python build.py --install`, BG3 closed), sync to the shared repo (fresh shallow clone, `tools/verify.py`, remove duplicate `.lsf` where a `.lsf.lsx` exists, README, commit with the shared-repo trailer), and push the personal repo. Not before.

## Known unknowns (honest)
Nothing from this session has been run in BG3. Unverified: prop spawn on these Shouts, whether Kill removes the prop after about 60 s (fallback: Script Extender Lua timer), decal mirroring, mattress notice is blank, sunglasses stall textures look like fruit, all new spell numbers/targeting, statuses `HC_ROLLERBLADE_SLALOM` etc. The co-op Version Mismatch was fixed earlier (loose HC folders removed from the game Data folder, modsettings Version64 `36028797018963969`).

## Gotchas
- Windows shell: the Bash tool mangles backslash escapes in heredoc-written Python; use `chr()` or avoid backslashes. A `cd` into a subfolder persists, use absolute paths.
- Builds are not byte-deterministic. Divine is at `tools/Packed/Tools/Divine.exe`; texconv at `work/cart/bin/texconv.exe`; Blender 5.2 for previews.
- Vanilla data copy for checking stat names: `temp_race/Public/Shared/Stats/Generated/Data/` (e.g. the slow status is `SLOW`, not `SLOWED`).
- Memory notes for this project are in `C:\Users\matth\.claude\projects\C--Users-matth-Documents-Baldurs-Gate-3-Homeless-Californian-Class\memory\` (MEMORY.md index).
