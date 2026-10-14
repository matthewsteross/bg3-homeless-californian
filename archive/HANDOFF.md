> **SUPERSEDED 2026-10-13: read `HANDOFF-2026-10-13.md` first.** The repo is now public and the mod is on Nexus; the "all pushed, installed, clean" status below is out of date.

# HANDOFF for a fresh Claude instance (written 2026-10-12 by Sonnet 5.5 for Matt)

## Goal now
Only work on **HomelessCalifornian** (Matt's mod). **Do NOT change PatriotClass** (Ducq's mod); Ducq decides what to do with the findings in `Information for Ducq.md` (already pushed to the shared repo). Keep Opus usage minimal; delegate to Gemini (Antigravity CLI), Codex, Grok. Matt is near his weekly Claude limit, so keep your own steps few and cheap.

## Where things stand (all pushed, installed, clean)
- Project (generator + src + dist): `C:\Users\matth\Documents\Baldurs Gate 3 Homeless Californian Class` (git, master, remote origin = private repo matthewsteross/bg3-homeless-californian). Source of truth is `generate_mod.py`; `src/` is generated; `dist/HomelessCalifornian.pak` is the build.
- Shared repo with Ducq: `C:\Users\matth\Documents\bg3-meme-mods` (github.com/ZellisE82/bg3-meme-mods, branch main). HC lives in `mods/HomelessCalifornian/` (pak + `source/` + README). Last HC commit there: 1d9abff. Rules are in its CLAUDE.md: `py -3 tools/verify.py HomelessCalifornian` must PASS before commit; commit pak + source together; end commits with `Co-Authored-By: Claude <noreply@anthropic.com>`; no Actions; one pull/one push.
- Both mods are installed in Matt's BG3 Mods folder and match the repos; ImprovedUI is enabled. Matt confirmed in-game: Californian spells work, class + Self-Made Man icons show, new Patriot loads.
- Build/install: `python build.py --install` (close BG3 first; check `tasklist | grep -i bg3`). Then copy `src/HomelessCalifornian/.` to `mods/HomelessCalifornian/source/` and `dist/HomelessCalifornian.pak` to `mods/HomelessCalifornian/HomelessCalifornian.pak` in the shared repo, run verify, commit, push both repos. Never install if verify fails.

## What's left (the open list)
1. **Two-mod compatibility check never completed** (HC + PatriotClass loaded together: duplicate UUIDs / stat names / loca handles / shadowed file paths, in either load order).
2. **Two Antigravity suggestions never verified** against vanilla: (a) `generate_cc_presets_lsx()` emits a "Base" race preset with all-zero SubRaceUUID; (b) the level-1 race progression uses `SelectPassives(..., CaliforniaIdentity)` with no `DefaultValues/Passives.lsx`. Answer each with vanilla evidence (vanilla data is extracted at `...\Homeless Californian Class\temp_race\Public\Shared` and `\SharedDev`; gitignored). Earlier, other Antigravity claims (missing `SelectorId`, 3 default skills) turned out NOT to match vanilla, so verify before changing anything.
3. A second mechanics audit of HC (Codex) and a light creative/naming pass (Grok) were about to run.
4. Matt will play-test HC harder later; in-game confirmation so far is only the spells working and icons showing.

## The review briefs are already written
`handoff-prompts\hc_common.txt` (shared context + rules), `hc_agy.txt` (compat + character creation), `hc_codex.txt` (mechanics audit), `hc_grok.txt` (names/flavour). Each AI job = common + its own file. All are READ-ONLY.
Run them headless in the background (no babysitting), one per Bash call with `run_in_background: true`, NO inner `&` (a backgrounded subshell gets killed when its parent exits), output to a file:
- Gemini 3.1 Pro: `cd <HC project> && timeout 1200 agy -p "$(cat common; cat hc_agy.txt)" --model gemini-3.1-pro-high --mode plan --print-timeout 1100s --add-dir C:\Users\matth\Documents\bg3-meme-mods > out.txt 2>&1`
- Codex: `codex exec --sandbox read-only --skip-git-repo-check - < combined_prompt.txt > out.txt` (its shell helper was flaky earlier: "setup refresh had errors"; if it fails, tell it to use non-shell file tools, or skip it and give the mechanics audit to Gemini Pro)
- Grok: `grok --cwd <HC project> --max-turns 8 -p "$(cat common; cat hc_grok.txt)"` (free tier; light jobs only)
Then verify each reported finding with a quick grep/vanilla lookup (a Sonnet/Flash agent can do that) before trusting it, and summarize for Matt. Do not change files until Matt approves the list, unless a fix is trivial and clearly correct.

## Gotchas learned today
- Headless `agy -p` may finish its work but never exit; check output/process (`tasklist | grep -i agy`) and kill it (TaskStop or taskkill). Interactive Antigravity asks permission for every script; approve only after reading the script (`grep` it for writes/deletes).
- Solo (free tier): max 3 running agents; `solo-cli.exe processes output <id>` reads an agent's terminal cheaply. The `mcp__solo` tools are allowed in Matt's settings; spawning an agent with `--dangerously-skip-permissions` is blocked by the safety classifier.
- Codex headless/sandbox shell can fail to start; Gemini Flash (`gemini-3.8-flash-high`) is good for README/art; image generation = Antigravity's generate_image (hits 429 quota sometimes).
- Pak repack without Ducq's lstool: stage source, `Divine.exe -g bg3 -a convert-resource` each `*.lsf.lsx` -> `.lsf`, `-a create-package`. Divine is at `...\Homeless Californian Class\tools\Packed\Tools\Divine.exe` (HC only needs `python build.py`).
- Don't pass `Existential Dread` anywhere: the Vibe Check debuff is "Vibe Checked" (fixed); Touch Grass applies "Existential Daze".
- Style: Matt likes a casual tone, short answers, plain-language instructions (he's not a coder), and honesty about what's verified vs tested in-game.

## Memory/notes
`NOTES-2026-10-12.md` (full day log) and the project memory files `solo-agent-team`, `delegate-to-smaller-models`, `handoff-2026-10-12` have more detail.
