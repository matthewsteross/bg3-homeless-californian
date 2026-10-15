# Ten minutes of rubbish decisions

Playtest the Homeless Californian class for Baldur's Gate 3 on PC.

[Download the current release (October 15, v0.3.0)](https://github.com/matthewsteross/bg3-homeless-californian/releases/tag/playtest-2026-10-15)
(the older [October 12 ZIP](https://github.com/matthewsteross/bg3-homeless-californian/releases/tag/playtest-2026-10-12)
is still available) and import HomelessCalifornian.pak using your usual BG3 mod manager. Enable it
and export your load order where your manager requires it. Do not install a
second copy. Use a separate test save, and create a new character or respec.
The public package is intentionally overpowered. Windows installation has
been checked; other platforms and compatibility combinations need reports.

## Pick one route

| Route | Try | What to report |
|---|---|---|
| Any class level 1 | Brick, Bags, Lawn Chair | Correct Junk spending? Hit/save/effect matches tooltip? |
| Class level 2 | Spend Junk, leave combat, Dumpster Dive, short rest | Dive restores 2 up to capacity; rest refills supply? |
| Venice level 3 | Hit with Heirloom Furniture, then Chair-Leg Shiv | Follow-up appears on hit and is consumed on hit or miss? |
| Tenderloin level 3 | Pigeon Witness Protection | Raven familiar appears, spends Junk, replaces old familiar? |
| BART level 6 | Wrong Platform against an enemy | Failed Wisdom save swaps positions? Any invalid locations? |
| Class level 7 | Fent Lean, then Moving Day | Lean ends and movement improves for one turn? |

Available spells differ by class level and subclass. Do not expect every row
on the same character. Junk capacity should be 3 at class level 1, 5 at 5 and
7 at 9. Take a short rest after level-up to check refill behavior.

Save and reload once. Note missing icons, lost grants, or changed resource
behavior. Actual effects are not comprehensively gameplay-tested yet.
The familiar uses a raven model; furniture and clothes use existing visuals.
There is no custom chair model, gun or voice pack; the only custom mesh is the Abandoned Cart. The level-12 Squatter's Rights capstone is in the October 13 build.
A fourth subclass (Overpass Riverbed Dweller) and a few new choices exist in the source only; their test routes are at the bottom of this page.

## Tell us what happened

[File a bug report](https://github.com/matthewsteross/bg3-homeless-californian/issues/new/choose)
with game patch/platform, class/subclass and multiclass levels, other mods,
steps, expected/actual behavior, and whether a reload reproduces it.

A successful test is useful too: [leave a playtest result](https://github.com/matthewsteross/bg3-homeless-californian/issues/1).
Screenshots and short clips are welcome, but optional. Please label which build
you used. Source/package checks do not prove gameplay or save compatibility.

## Share it

Share the release link with players who enjoy absurd custom classes. One clear
example of what happened in-game is more useful than repeated promotional posts.
The design is directed by Matthew; Claude, Gemini and Codex assist with code,
and Gemini generated custom icon art, and the shopping cart model is AI-generated too. Follow each community's posting rules.


## October 13 build (v0.2.0) - new abilities to try (all untested in game)

Pick one or two; ten minutes is plenty. New grants need a new character or a respec. Reach the listed class level
(a fast way: level up in a test save).

| Class level | Try | What to report |
|---|---|---|
| 5 | **Guilt Trip** on any enemy, then again after Aggressive Panhandling (class 2) | Castable on an un-shamed enemy? Extra damage and Socially Shamed removed when shamed? (The v0.2.0 download may show Invalid Target; fixed in v0.3.0.) |
| 6 | **Public Scene** on an enemy, shamed and un-shamed | Frightened on a failed save? Longer if shamed? (Same Invalid Target caveat on v0.2.0.) |
| 8 | **Trapped in the Invisible Box** | Enemy cannot move for a turn? Short rest resets it? |
| 9 | **Bucket Drum Solo** into a group | Damage, push, Homeless Fatigue icon, advantage against fatigued targets? |
| 10 | **Compassion Burnout** on a normal and on a fatigued target | Castable on both? Extra damage and fatigue removed when fatigued? (Same caveat on v0.2.0.) |
| 11 | **Punctured Lithium Cell** | Both damage types, fire on the ground, friendly-fire indoors? |
| Venice 6 | **Sublet** on an ally | Ally gets +2 AC / STR-save advantage / Prone immunity, you do not? |
| Tenderloin 10 | **Everybody Knows This Guy** | Breadcrumbed status, advantage against, disadvantage on its attacks? |
| 5 | **Beg** on a friendly NPC (trader, townsperson) | Did gold arrive in YOUR inventory? Did the NPC turn hostile or cause a crime? Did Homeless Fatigue stay on them? |
| 12 | Subclass **Squatter's Rights** capstone | Does it activate, grant its effects, and expire as described? |

Please say which build you used (the Nexus file is now version 0.3.0, the 2026-10-15 build).

## Newest additions in v0.3.0 (untested in game)

These are new in v0.3.0 (not in the older v0.2.0 download). If you are testing a local build from the repository, a new character or respec
is needed for race and class grants.

| Level / source | Try | What to report |
|---|---|---|
| Californian race | **Runyon Canyon Glutes** (passive), **Emotional Support Hydroflask** | Longer jumps and more carry weight? Hydroflask heals, cures Poisoned, once per short rest? |
| Beachborn 1 / 3 / 5 | **Hang Ten**, **Rip Current**, **Golden Hour** | Hang Ten speed and Prone immunity? Rip Current pulls the target and can knock Prone? Golden Hour blinds nearby enemies and gives you the glow? |
| Siliconite 1 / 3 / 5 | **Vibe Check** + Siliconite Synergy, **Disruptive Pivot**, **Non-Disclosure Agreement** | Extra 1d4 Psychic on weapon hits? Pivot teleports and gives advantage on the next attack? NDA silences on a failed save? |
| Inland Emperor 1 / 3 / 5 | **Dust Devil**, **Overpass Exhaust**, **Heatstroke** (plus Smog Lungs, Heat Index Mastery) | Dust Devil blinds and gives Blur? Exhaust cone hits as a cone for Poison and Fire? Heatstroke applies and slows? |
| Class 2 | **Dumpster Dive**, then check inventory | 2 Junk restored plus cheese and an apple in the inventory? |
| Class 2 (Street Trade) | Pick **Busker** or **Can Collector** | Option listed? Advantage on the named skill checks? |
| Class 4 (Junk Doctrine) | Pick **Twitchy** | Initiative +3? |
| Class 7 | **I Was Here First**, and **Moving Day** out of Fent Lean | Buffs for 2 turns and a rubbish ring appears? Does the ring slow enemies without trapping you? |
| Tenderloin 3 | **Pigeon Witness Protection**, then **Pigeon Lunch Rush** from the raven | Does the raven get the ability? Enemies in 4 m get disadvantage on a failed Dexterity save? |
| BART 6 | **Fare Evasion Audit** | Fined status, slower movement, no reactions on a failed Wisdom save? |
| Venice 3 | **Abandoned Cart** | Exactly one cart appears? Faces sensibly, blocks movement, Junk spent on a real character, looks good in daylight? (Partly verified live 2026-10-14: cart spawns, is visible, one per cast.) |
| Class 4 | **Coat-Hanger Slim Jim** on a locked door or chest | Unlocks within 1.5 m, spends 1 Junk? |
| Tenderloin 6 | **Curbside Needle Exchange** on an adjacent ally | Cures Poisoned/Disease/Blinded/Paralysed, heals 2d6+CON, once per short rest? |
| Venice 10 | **Chair Check** | Weapon damage plus 2d8; Prone only on a failed Strength save? Junk spent? |

## Source-only additions after v0.3.0 (NOT in the public download, NOT verified in game)

The public v0.3.0 download does **not** contain anything below. These routes only apply if you build the mod yourself from the
repository source (a new character or respec is needed for the grants). Nothing here has been played in game; only file-level
checks have passed.

| Level / source | Try | What to report |
|---|---|---|
| Overpass Riverbed Dweller 3 | Pick the subclass; check **Concrete Bank Traction** | Subclass listed with its name and icon? Mud, webs and other difficult terrain do not slow you? |
| Overpass 3 | **Storm Drain Flash Flood** into a group | 9 m line shape sensible? Strength save for `2d8 + CON` Bludgeoning, Prone only on a failed save, half on a success? Standing water left for 2 turns? Junk spent, once per short rest? |
| Overpass 3 | **Blue Tarp Lean-To** with allies nearby, ideally with fire on the ground | You and allies within 3 m get +1 AC and Dexterity-save advantage for 2 turns? Fire on the ground doused? |
| Overpass 6 | **Culvert Siphon** on an ally and on yourself, ideally while Burning | Castable at 9 m (not touch range)? Heals `2d6 + CON`, ends Burning, douses the ground, spends 1 Junk? |
| Overpass 6 / 10 | **Underpass Climate Control**, **Rebar Anchor** | Lightning and Cold resistance shown? +1 AC and Strength-save advantage shown? |
| Overpass 10 | **Drainage Ditch Dig-In** on an enemy group | 3 m Mud for 3 turns? Enemies slowed in it, you not slowed? |
| Overpass 12 | **Squatter's Rights: Spillway Sovereignty** | Restores all Junk, +2 AC and +3 m movement for 3 turns? Mud around you within 4 m: does it slow enemies without trapping you? |
| Class 2 (Street Trade) | Pick **Squeegee Technician**, or **Notary** on another character | Both listed (7 options in total)? Squeegee: advantage on Intimidation and Insight. Notary: advantage on Investigation and Persuasion? |
| Class 4 (Junk Doctrine) | Pick **Cardboard Insulator**, or **Tinfoil Deflector** on another character | Both listed (6 options in total)? Cardboard Insulator: Cold damage resisted. Tinfoil Deflector: Psychic damage resisted (try One-Star Citation or Vicious Mockery from an enemy)? |
| Californian race 1 | **NIMBY Zoning Defense** (passive) | Listed on the character sheet? Advantage on saves against Charmed (try a charm spell from an enemy)? |
| Class 2 | **Sprinkler Violation** at a group, ideally near fire or a lightning source | Castable at 9 m for a bonus action and 1 Junk, once per short rest? 2 m water puddle for 2 turns; creatures inside become Wet for 3 turns? Does anything just outside the puddle get Wet? |
| Class 4 | **Catalytic Converter Sawzall** on an adjacent enemy | Melee spell attack within 1.5 m for `3d8` Slashing; a hit leaves Decatted Exhaust for 2 turns (-2 AC, no reactions)? Junk spent, once per short rest? Which cast and hit effects play (it borrows Inflict Wounds)? |
| Class 8 | **One-Star Citation** on enemies that pass and fail the Wisdom save | `2d8` Psychic damage at 9 m? Bane for 2 turns only on a failed save? Does damage land on a successful save too? Junk spent, no cooldown? |
| Class 11 | **HOV Lane** to a spot you can see, then to a spot you cannot | Teleport up to 12 m for a bonus action and 1 Junk, once per short rest? Invalid or blocked locations refused? (It leaves no mud behind: that part was left out.) |
| Californian Inland Emperor 3 | **Bakersfield Tule Fog** (new character or respec) | Appears beside Overpass Exhaust? One action, no Junk, once per short rest? 4 m fog cloud at 9 m for 2 turns? Does casting it break an existing concentration spell (it should not)? |
