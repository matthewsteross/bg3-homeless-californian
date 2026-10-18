"""Offline tests for meshy_client.py: key handling, request bodies and the dry-run spend guard. No network calls."""
from pathlib import Path
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import meshy_client as mc


class MeshyClientTests(unittest.TestCase):
    def test_key_from_environment_wins(self):
        self.assertEqual(mc.load_key({"MESHY_API_KEY": " abc "}, env_file=ROOT / "no-such-file"), "abc")

    def test_key_from_env_file_and_quotes_stripped(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / ".env"
            f.write_text('OTHER=1\nMESHY_API_KEY="k-123"\n', encoding="utf-8")
            self.assertEqual(mc.load_key({}, env_file=f), "k-123")

    def test_missing_key_is_empty_and_call_refuses(self):
        self.assertEqual(mc.load_key({}, env_file=ROOT / "no-such-file"), "")
        with self.assertRaises(mc.MeshyError):
            mc.call("GET", "/openapi/v1/balance", key="")

    def test_env_file_is_git_ignored(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".env", [x.strip() for x in ignore])

    def test_text_bodies_follow_the_documented_fields(self):
        b = mc.text_preview_body("a cart", 8000)
        self.assertEqual((b["mode"], b["topology"], b["target_polycount"], b["pose_mode"]), ("preview", "triangle", 8000, "a-pose"))
        self.assertEqual(b["ai_model"], "latest")
        with self.assertRaises(mc.MeshyError):
            mc.text_preview_body("x" * 801)
        r = mc.text_refine_body("tid", True, "worn teal paint")
        self.assertEqual((r["mode"], r["preview_task_id"], r["enable_pbr"]), ("refine", "tid", True))
        self.assertNotIn("pose_mode", mc.text_preview_body("x", a_pose=False))

    def test_remesh_and_rig_bodies_validate_ranges(self):
        self.assertEqual(mc.remesh_body("t", 15000, ["glb", "fbx"])["target_formats"], ["glb", "fbx"])
        with self.assertRaises(mc.MeshyError):
            mc.remesh_body("t", 50)
        with self.assertRaises(mc.MeshyError):
            mc.remesh_body("t", 400000)
        self.assertEqual(mc.rig_body("t", 1.8)["height_meters"], 1.8)
        with self.assertRaises(mc.MeshyError):
            mc.rig_body("t", 0)

    def test_image_body_turns_a_local_file_into_a_data_uri(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "a.png"
            p.write_bytes(b"\x89PNG\r\n")
            self.assertTrue(mc.image_body(str(p))["image_url"].startswith("data:image/png;base64,"))
        self.assertEqual(mc.image_body("https://x.test/a.png")["image_url"], "https://x.test/a.png")

    def test_creating_without_yes_is_a_dry_run_and_never_calls_the_api(self):
        buf = io.StringIO()
        with mock.patch.object(mc, "call") as fake, redirect_stdout(buf):
            code = mc.main(["text3d", "a surfboard", "--name", "t"])
        self.assertEqual(code, 0)
        fake.assert_not_called()
        self.assertIn("DRY RUN", buf.getvalue())

    def test_collect_urls_names_models_and_textures(self):
        urls = mc.collect_urls({"model_urls": {"glb": "https://a/b.glb"},
                                "texture_urls": [{"base_color": "https://a/c.png"}],
                                "result": {"rigged_character_glb_url": "https://a/r.glb",
                                           "basic_animations": {"walking_glb_url": "https://a/w.glb"}}})
        self.assertIn("model.glb", urls)
        self.assertIn("texture0_base_color.png", urls)
        self.assertIn("rigged_character_glb_url", urls)
        self.assertIn("walking_glb_url", urls)


if __name__ == "__main__":
    unittest.main()
