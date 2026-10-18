"""Rejected-model checks: broken podium must never reach generated content."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import hc_podium


class PodiumRejectionTests(unittest.TestCase):
    def test_rejected_before_any_output_or_callbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            public=Path(tmp)/'Public/HC'
            def unexpected(*args):
                self.fail('Rejected model invoked a generation callback')
            with self.assertRaisesRegex(ValueError,'HC_CouncilPodium withheld.*floating detached'):
                hc_podium.generate_podium(public,unexpected,unexpected)
            self.assertFalse(public.exists())

    def test_no_delivery_binaries_and_diagnostic_previews_exist(self):
        asset=ROOT/'assets/models/HC_CouncilPodium'
        self.assertEqual(list(asset.glob('*.GR2')),[])
        self.assertEqual(list(asset.glob('*.DDS')),[])
        for angle in ('front','bg3','threeq_rear'):
            self.assertTrue((ROOT/f'work/podium/out/preview_{angle}_v1.png').is_file())


if __name__=='__main__':
    unittest.main()
