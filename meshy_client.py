"""Small Meshy API client for the Homeless Californian mod (standard library only).

Docs used: https://docs.meshy.ai/en/api/ (text-to-3d v2, remesh v1, rigging v1, image-to-3d v1).
Auth: `Authorization: Bearer <key>`. The key comes from the MESHY_API_KEY environment variable or, if that is unset,
from a line `MESHY_API_KEY=...` in the git-ignored `.env` file next to this script. The key is NEVER printed, logged
or written anywhere by this script.

Every command that creates a task SPENDS CREDITS, so without `--yes` it only prints the request it would send
(dry run). Results are downloaded to assets/meshy/<name>/ and every task is appended to work/meshy/tasks.jsonl.

Examples (run from the project folder):
  python meshy_client.py check
  python meshy_client.py text3d "sun-faded surfboard leaning on a cart" --name surfboard --polycount 8000 --yes
  python meshy_client.py remesh <task_id> --name surfboard --polycount 15000 --formats glb fbx --yes
  python meshy_client.py rig <task_id> --name adventurer --height 1.75 --yes
  python meshy_client.py status text-to-3d <task_id>

UNVERIFIED: image3d has not been run against the live API; credit prices are on Meshy's Pricing page, not here.
"""
import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://api.meshy.ai"
OUT_DIR = ROOT / "assets" / "meshy"
LOG_FILE = ROOT / "work" / "meshy" / "tasks.jsonl"
ENV_FILE = ROOT / ".env"
DONE = {"SUCCEEDED"}
FAILED = {"FAILED", "CANCELED"}

PATHS = {
    "text-to-3d": "/openapi/v2/text-to-3d",
    "image-to-3d": "/openapi/v1/image-to-3d",
    "remesh": "/openapi/v1/remesh",
    "rigging": "/openapi/v1/rigging",
}


class MeshyError(RuntimeError):
    pass


def load_key(env=None, env_file=ENV_FILE):
    """Return the API key from the environment or the .env file ('' if none). Never prints it."""
    env = os.environ if env is None else env
    key = (env.get("MESHY_API_KEY") or "").strip()
    if not key and Path(env_file).is_file():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("MESHY_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    return key


def call(method, path, body=None, key="", timeout=60):
    if not key:
        raise MeshyError("No API key found. Put MESHY_API_KEY=... in the .env file (see MESHY.md).")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:400].replace(key, "***")
        hint = " (402 = out of credits)" if e.code == 402 else " (401 = bad or missing key)" if e.code == 401 else ""
        raise MeshyError(f"HTTP {e.code} on {method} {path}{hint}: {detail}") from None


# ---- request bodies (pure functions, unit tested) -------------------------------------------------------------

def text_preview_body(prompt, polycount=15000, model_type="standard", a_pose=True):
    if len(prompt) > 800:
        raise MeshyError("Prompt is longer than Meshy's 800 character limit.")
    body = {"mode": "preview", "prompt": prompt, "model_type": model_type, "topology": "triangle",
            "target_polycount": int(polycount), "target_formats": ["glb"]}
    if model_type == "standard":
        body["ai_model"] = "latest"
        body["should_remesh"] = True
    if a_pose:
        body["pose_mode"] = "a-pose"
    return body


def text_refine_body(preview_id, pbr=True, texture_prompt=None):
    body = {"mode": "refine", "preview_task_id": preview_id, "enable_pbr": bool(pbr), "target_formats": ["glb"]}
    if texture_prompt:
        body["texture_prompt"] = texture_prompt[:800]
    return body


def remesh_body(task_id, polycount=15000, formats=("glb",), topology="triangle"):
    if not 100 <= int(polycount) <= 300000:
        raise MeshyError("Remesh target polycount must be 100 to 300000.")
    return {"input_task_id": task_id, "target_formats": list(formats), "topology": topology,
            "target_polycount": int(polycount)}


def rig_body(task_id, height=1.75):
    if height <= 0:
        raise MeshyError("Height must be positive.")
    return {"input_task_id": task_id, "height_meters": float(height)}


def image_body(image, smart_topology=False):
    if image.startswith(("http://", "https://", "data:")):
        url = image
    else:
        p = Path(image)
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        url = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")
    body = {"image_url": url}
    if smart_topology:
        body["model_type"] = "smart-topology"
    return body


# ---- task handling ---------------------------------------------------------------------------------------------

def log_task(kind, task_id, name, extra=None):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    row = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "id": task_id, "name": name}
    row.update(extra or {})
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def wait_for(kind, task_id, key, every=10, limit=1800):
    start = time.time()
    while True:
        task = call("GET", f"{PATHS[kind]}/{task_id}", key=key)
        status = task.get("status")
        print(f"  {kind} {task_id[:8]}: {status} {task.get('progress', 0)}%", flush=True)
        if status in DONE:
            return task
        if status in FAILED:
            raise MeshyError(f"{kind} task {status}: {task.get('task_error')}")
        if time.time() - start > limit:
            raise MeshyError(f"Timed out after {limit}s; check later with: status {kind} {task_id}")
        time.sleep(every)


def collect_urls(task):
    """All downloadable result URLs in a finished task, as {filename: url}."""
    urls = {}
    for fmt, url in (task.get("model_urls") or {}).items():
        urls[f"model.{fmt}"] = url
    result = task.get("result") or {}
    for field, url in result.items():
        if field == "basic_animations":
            for k, v in (url or {}).items():
                urls[k] = v
        elif isinstance(url, str) and url.startswith("http"):
            urls[field] = url
    for i, tex in enumerate(task.get("texture_urls") or []):
        for k, v in tex.items():
            urls[f"texture{i}_{k}.png"] = v
    if task.get("thumbnail_url"):
        urls["thumbnail.png"] = task["thumbnail_url"]
    return urls


def download_all(task, name):
    folder = OUT_DIR / name
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    for fname, url in collect_urls(task).items():
        ext = Path(url.split("?")[0]).suffix or ""
        dest = folder / (fname if Path(fname).suffix else fname + ext)
        urllib.request.urlretrieve(url, dest)
        saved.append(dest.name)
    (folder / f"task-{task.get('id', 'unknown')[:8]}.json").write_text(
        json.dumps({k: v for k, v in task.items() if "url" not in k}, indent=1), encoding="utf-8")
    print(f"  saved to {folder}: {', '.join(saved)}")
    return folder


def run_create(kind, body, name, args, key):
    if not args.yes:
        print(f"DRY RUN (no credits spent). Would POST {PATHS[kind]}:")
        print(json.dumps({k: (v[:60] + "...") if isinstance(v, str) and len(v) > 80 else v for k, v in body.items()}, indent=1))
        print("Re-run with --yes to spend credits.")
        return None
    resp = call("POST", PATHS[kind], body, key=key)
    task_id = resp.get("result")
    log_task(kind, task_id, name)
    print(f"created {kind} task {task_id}")
    task = wait_for(kind, task_id, key)
    print(f"  consumed credits: {task.get('consumed_credits', '?')}")
    download_all(task, name)
    return task


def main(argv=None):
    ap = argparse.ArgumentParser(description="Meshy API helper (dry-run unless --yes).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="verify a key is configured and ask Meshy for the credit balance")
    t = sub.add_parser("text3d"); t.add_argument("prompt"); t.add_argument("--name", required=True)
    t.add_argument("--polycount", type=int, default=15000); t.add_argument("--smart", action="store_true")
    t.add_argument("--refine", action="store_true", help="also texture it (second paid step)")
    t.add_argument("--texture-prompt"); t.add_argument("--no-pose", action="store_true"); t.add_argument("--yes", action="store_true")
    i = sub.add_parser("image3d"); i.add_argument("image"); i.add_argument("--name", required=True)
    i.add_argument("--smart", action="store_true"); i.add_argument("--yes", action="store_true")
    r = sub.add_parser("remesh"); r.add_argument("task_id"); r.add_argument("--name", required=True)
    r.add_argument("--polycount", type=int, default=15000); r.add_argument("--formats", nargs="+", default=["glb"])
    r.add_argument("--yes", action="store_true")
    g = sub.add_parser("rig"); g.add_argument("task_id"); g.add_argument("--name", required=True)
    g.add_argument("--height", type=float, default=1.75); g.add_argument("--yes", action="store_true")
    s = sub.add_parser("status"); s.add_argument("kind", choices=sorted(PATHS)); s.add_argument("task_id")
    a = ap.parse_args(argv)
    key = load_key()
    try:
        if a.cmd == "check":
            print(f"API key found ({len(key)} characters)." if key else "No API key configured (see MESHY.md).")
            if key:
                try:
                    print("balance:", json.dumps(call("GET", "/openapi/v1/balance", key=key)))
                except MeshyError as e:
                    print("key present, balance call failed:", e)
        elif a.cmd == "text3d":
            mt = "smart-topology" if a.smart else "standard"
            prev = run_create("text-to-3d", text_preview_body(a.prompt, a.polycount, mt, not a.no_pose), a.name + "_preview", a, key)
            if prev and a.refine:
                run_create("text-to-3d", text_refine_body(prev["id"], True, a.texture_prompt), a.name, a, key)
        elif a.cmd == "image3d":
            run_create("image-to-3d", image_body(a.image, a.smart), a.name, a, key)
        elif a.cmd == "remesh":
            run_create("remesh", remesh_body(a.task_id, a.polycount, a.formats), a.name, a, key)
        elif a.cmd == "rig":
            run_create("rigging", rig_body(a.task_id, a.height), a.name, a, key)
        elif a.cmd == "status":
            task = call("GET", f"{PATHS[a.kind]}/{a.task_id}", key=key)
            print(json.dumps({k: v for k, v in task.items() if "url" not in k and k != "result"}, indent=1))
    except MeshyError as e:
        print("ERROR:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
