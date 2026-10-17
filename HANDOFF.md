# HANDOFF (current)

Read this first. Updated 2026-10-17 by Gemini Argon (lead). Older handoffs are in `archive/` (`HANDOFF-2026-10-13.md`, `HANDOFF-2026-10-14.md`, `HANDOFF.md` from 2026-10-12) and are history only.

## State in one paragraph

Homeless Californian (HC) v0.4.0 is still the public playtest download on Nexus (mod 25761) and GitHub (`playtest-2026-10-15-v0.4.0`). Locally, `master` includes **Round 4** (`hc_round4.py`: Freeway Directions, Weather Complaint, Permit Pending), **Round 5** (`hc_round5.py`: 10 stereotype/street comedy spells + 7 statuses), **Round 6** (`hc_round6.py` + `hc_choices.py` + `hc_doctrines.py`: Oakland Flea Market contraband table with 4 equippable/consumable items, 3 subrace stereotype spells, 3 street-tactics spells, 2 new Street Trades, and 2 new Junk Doctrines), and **Round 7** (`hc_round7.py`: 11 spells + 8 statuses rounding out subclass L3/L10, subrace L1/L5, and base class L1/L2/L7/L12), compiled into `dist/HomelessCalifornian.pak` and installed to the local BG3 `Mods` folder. All **149 validation unit tests** and `validation/validate.py --pak dist/HomelessCalifornian.pak` pass (240 own stats, 84 icons, 505 localization handles). Read the "Verified" and "Not verified" lists before saying anything is working.

## Verified vs not verified

Keep these separate every time you report.

**Verified in game (Matthew watched or the Script Extender harness checked it):**
- All 66 spells, 38 statuses and 41 passives load with names and text.
- Effect fields of 96 of 97 spell entries parse (Storm Drain Flash Flood's SpellProperties is empty on purpose).
- Shopping Cart prop and Abandoned Cart spell spawn one cart.
- Curb Alert creates the four junk items in the caster's inventory.
- Blue Tarp Lean-To spawns one tarp at the caster's feet and applies Blue Tarp Cover.
- Storm Drain Flash Flood leaves Water along the line; Drainage Ditch Dig-In leaves Mud; Sprinkler Violation leaves Water.
- Bakersfield Tule Fog: fixed in `0efac8b` to copy vanilla Fog Cloud; Matthew confirmed the fog appears.
- `UnlockSpell` on a summoned raven (Pigeon Lunch Rush); Hydroflask heals and leaves Water.

**Not verified in game:**
- Damage and save outcomes for all new spells.
- Junk costs and level-up grants on a real HC character.
- Race and subrace progression on a real character.
- Overpass Exhaust `not Ally()` against the caster.
- Enemy-only area shouts with no enemy in range.
- Cart and tarp facing, collision and look; kombucha heal override; item equip and visuals.
- Balance and whether anything is fun. Only Matthew can judge this by playing.

## Rules

- Matthew is not a coder and wants short, plain answers. Claude leads and does the work; don't ask for permission on routine steps.
- Do not touch `PatriotClass` (Ducq's).
- Credit only Matthew and AI tools. Always disclose AI use. No Reddit posts. No adult or Quality of Life tags on Nexus.
- Shared repo `ZellisE82/bg3-meme-mods` belongs to Ducq (Zach). Its rules apply: no GitHub Actions, no polling, `verify.py` must PASS, pak and source committed together, one pull and one push. It has not been checked in this handoff.
- This project's repo is `matthewsteross/bg3-homeless-californian`.

## Release gate

- Matthew's standing rule: nothing new goes to Nexus or a GitHub release until he has verified it in game.
- Exception used for v0.4.0: he explicitly asked for the push ("push this to Nexus and github"). Don't read that as a standing exception.
- Source-only content (anything newer than the release) must be marked as not in the public download in the docs.

## How to test live

- Recipe and checklist: `work/cart/RUN_INGAME_CHECK.md`; harness scripts `t_all.lua` and `t_parse.lua`.
- Launch that worked on 2026-10-15: start `bg3_dx11.exe --skip-launcher -continueGame` with `SteamAppId=1086940` set, with Steam running. The game may stop at "Press any key" and need one physical key press.
- Back up saves first. Restore the clean `dist` pak after a test. Take real screenshots; don't poll blind.
- A probe that returns the same result for the vanilla control is blind. Ask Matthew to look.

## Open items

1. Full cast and damage tests of the Californian content (Solo todo #22 is only partly done).
2. Playtester engagement: check Nexus Bugs/Posts and GitHub issues, then triage (Solo #13).
3. Cart and tarp follow-ups: facing, collision, texture in light, Junk cost, AI credit note (Solo #23).
4. Larian forum intro once the account is approved (Solo #14); mod.io ticket 17041 (thumbnail).
5. Unknown credit "Shimon Schwartz (@shimonenator)": not found in either repo; ask Matthew for a link (Solo #24).
6. Custom recorded audio and voice lines pipeline (Solo #6) and combat audio barks (Solo #5) are still open.

## Where things live

- Solo project 2, scratchpad #28 ("CLAUDE LEAD"): progress log. Its "Next actions" section is out of date; this file is the current list.
- `validation/README.md`: what the validator checks and what it doesn't.
- `README.md` and `TESTING.md`: public-facing; keep them in step with the release.
