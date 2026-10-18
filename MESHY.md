# Meshy API setup (for Matthew and the Solo agents)

`meshy_client.py` lets any agent in this project make 3D assets with Meshy. It uses only Python's standard library.

## One-time setup (Matthew does this part; it needs his Meshy login and card)
1. Meshy's API needs a **paid plan**. Free accounts only get a playground key. Check meshy.ai/pricing to confirm what
   API calls cost and whether API credits are separate from the website credits (not verified here).
2. Make a key at https://www.meshy.ai/developers/keys. **It is shown only once**, so copy it right away.
3. Open the `.env` file in the project folder (`notepad .env`) and put the key after the equals sign:
   `MESHY_API_KEY=msy_xxxxxxxx`
   Save and close. `.env` is git-ignored, so it is never pushed. Do not paste the key into chat or into any other file.
4. Test it: `python meshy_client.py check` (it prints whether a key was found and the credit balance; never the key).

## Rules for the agents (Claude, Codex, Gemini, Grok, local models)
- Run commands from the project folder. The client finds the key by itself.
- **Never open, print or copy `.env`** and never put the key in a prompt, log, commit or file.
- Every create command is a **dry run** unless it has `--yes`. Dry run shows the request and spends nothing.
  Only add `--yes` when Matthew has asked for that asset. Keep `--polycount` modest (BG3 props: 3,000 to 15,000).
- Each task is logged to `work/meshy/tasks.jsonl`; downloads land in `assets/meshy/<name>/`
  (Meshy only keeps result files for 3 days, so the client downloads them straight away).
- Meshy output is a plain GLB, not a BG3 asset. It still has to go through our conversion pipeline
  (Blender cleanup, texture re-paint to BG3's three DDS maps, Divine to GR2, root template and stat entries) and be
  tested in game. Say so in the Nexus AI disclosure when a Meshy model ships.

## Commands
| Goal | Command |
|---|---|
| Check key and balance | `python meshy_client.py check` |
| Text to 3D (untextured preview) | `python meshy_client.py text3d "prompt" --name thing --polycount 8000 --yes` |
| Add textures (second paid step) | add `--refine` (and optionally `--texture-prompt "..."`) |
| Image to 3D | `python meshy_client.py image3d path-or-url.png --name thing --yes` |
| Reduce polygons | `python meshy_client.py remesh TASK_ID --name thing --polycount 15000 --formats glb fbx --yes` |
| Rig a humanoid | `python meshy_client.py rig TASK_ID --name guy --height 1.75 --yes` |
| Look up a task | `python meshy_client.py status text-to-3d TASK_ID` |

Rigging only works on textured humanoids, faces +Z, and under 300,000 faces (remesh first). Tests:
`python -m unittest validation.test_meshy_client` (offline, no key needed).
