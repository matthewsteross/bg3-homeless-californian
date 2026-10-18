"""Rejected H geometry must never enter generated content."""
from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import hc_dumbbells


class DumbbellRejectionTests(unittest.TestCase):
    def test_rejects_without_writes_or_callbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            public=Path(tmp)/'Public/HC'
            def unexpected(*args):
                self.fail('Rejected source invoked a callback')
            with self.assertRaisesRegex(ValueError,'HC_DumbbellRack withheld.*floating unsupported'):
                hc_dumbbells.generate_dumbbells(public,unexpected,unexpected)
            self.assertFalse(public.exists())

    def test_no_delivery_binaries_and_previews_retained(self):
        asset=ROOT/'assets/models/HC_DumbbellRack'
        self.assertEqual(list(asset.glob('*.GR2')),[])
        self.assertEqual(list(asset.glob('*.DDS')),[])
        for angle in ('front','side','bg3'):
            self.assertTrue((ROOT/f'work/dumbbells/out/preview_{angle}_v1.png').is_file())


if __name__=='__main__':
    unittest.main()
