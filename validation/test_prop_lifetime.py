"""Evidence and shared-status integration checks for temporary prop spawns."""
from pathlib import Path
import tempfile
import unittest
import hc_prop_lifetime as lifetime
import hc_dumpster, hc_lawnchair, hc_curbpile, hc_trashbags
from validation.test_dumpster import generator, stat_fields

ROOT = Path(__file__).resolve().parents[1]


class PropLifetimeTests(unittest.TestCase):
    def test_recipe_tokens_have_vanilla_precedent(self):
        public = ROOT / 'temp_race/Public'
        def read(layer, file):
            return (public / layer / 'Stats/Generated/Data' / file).read_text(encoding='utf-8')
        self.assertIn('GROUND:Spawn(c18cc156-f016-4505-9eb7-e09d29183f3b, ,END_NAUTILOID_POD_MIND_FLAYER)', read('GustavDev','Spell_ProjectileStrike.txt'))
        self.assertIn('SetStatusDuration(MAG_GISH_ARCANE_ACUITY,3,ForceSet)', read('SharedDev','Status_BOOST.txt'))
        self.assertIn('SetStatusDuration(MAG_ATTACK_DEBUFF, 10, ForceSet)', read('Gustav','Status_BOOST.txt'))
        fields=stat_fields(read('GustavDev','Status_BOOST.txt'),'SHA_SHADOWQUAKE_COSMETIC')
        self.assertEqual(fields['OnRemoveFunctors'],'Kill()')
        self.assertEqual(fields['RemoveEvents'],'OnRemove')
        for layer in ('Shared','SharedDev','Gustav','GustavDev','Honour'):
            for path in (public/layer/'Stats/Generated/Data').glob('*.txt'):
                self.assertNotIn(f'new entry "{lifetime.STATUS}"',path.read_text(encoding='utf-8'))

    def test_all_four_modules_share_one_status_and_distinct_spawn_roots(self):
        modules=(hc_dumpster,hc_lawnchair,hc_curbpile,hc_trashbags)
        with tempfile.TemporaryDirectory() as tmp:
            public=Path(tmp)/'Public/HomelessCalifornian';stats=public/'Stats/Generated/Data';stats.mkdir(parents=True)
            for module in modules:
                (stats/(module.SPELL+'.txt')).write_text(f'new entry "{module.SPELL}"\ntype "SpellData"\ndata "SpellProperties" "Keep()"\n')
            roots=[]
            for module in modules:
                function=getattr(module,'generate_'+module.__name__[3:])
                function(public,generator.add_loca,generator.get_guid)
                roots.append(generator.get_guid(module.TEMPLATE_KEY))
                before=(stats/(module.SPELL+'.txt')).read_bytes()
                function(public,generator.add_loca,generator.get_guid)
                self.assertEqual(before,(stats/(module.SPELL+'.txt')).read_bytes())
            status_text='\n'.join(p.read_text() for p in stats.glob('*.txt'))
            self.assertEqual(status_text.count('new entry "'+lifetime.STATUS+'"'),1)
            self.assertEqual(len(set(roots)),4)

    def test_missing_properties_and_duplicate_spell_are_clear_errors(self):
        for module in (hc_dumpster,hc_lawnchair,hc_curbpile,hc_trashbags):
            patch=getattr(module,'patch_'+module.__name__[3:]+'_spell')
            guid=generator.get_guid(module.TEMPLATE_KEY)
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'a.txt';path.write_text(f'new entry "{module.SPELL}"\ntype "SpellData"\n')
                with self.assertRaisesRegex(ValueError,'no SpellProperties'):patch(tmp,guid)
                (Path(tmp)/'b.txt').write_bytes(path.read_bytes())
                with self.assertRaisesRegex(ValueError,'found 2'):patch(tmp,guid)


if __name__=='__main__':unittest.main()
