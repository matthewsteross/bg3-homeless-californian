"""Isolated cooler-fire tests; never invokes a shared generator or build."""
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import unittest
import uuid
import xml.etree.ElementTree as ET
import hc_coolerfire as m

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work/coolerfire'

class CoolerFireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (WORK/'tmp').mkdir(parents=True,exist_ok=True)
        cls.tmp=tempfile.TemporaryDirectory(dir=WORK/'tmp')
        cls.public=Path(cls.tmp.name)/'Public/HomelessCalifornian'
        cls.loca={}
        def loca(key,value):
            cls.loca[key]=value
            return 'h'+uuid.uuid5(uuid.NAMESPACE_URL,key).hex
        cls.guid=staticmethod(lambda key:str(uuid.uuid5(uuid.NAMESPACE_URL,key)))
        cls.grants=m.generate_coolerfire(cls.public,loca,cls.guid)
        cls.stats=cls.public/'Stats/Generated/Data'
        cls.spell=(cls.stats/'HC_Spells_CoolerFire.txt').read_text()
        cls.status=(cls.stats/'HC_Status_CoolerFire.txt').read_text()
        cls.obj=(cls.stats/'HC_Object_CoolerFire.txt').read_text()
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_grant(self):
        self.assertEqual(self.grants,{'base':{4:[m.SPELL]},'subclasses':{},'existing_list_spells':{}})
    def test_spell_contract(self):
        for text in ['using "Projectile_GEB_Perform_TossCoin"','"TargetRadius" "9"','"UseCosts" "ActionPoint:1;HC_Junk:1"','"Cooldown" "OncePerShortRest"']:
            self.assertIn(text,self.spell)
        self.assertIn(f'GROUND:Spawn({self.guid(m.TEMPLATE_KEY)});ApplyStatus(SELF,{m.STATUS},100,3)',self.spell)
    def test_unique_status(self):
        for text in [f'"StackId" "{m.STATUS}"','"StackType" "Overwrite"','"TickType" "EndTurn"','Resistance(Cold,Resistant);CharacterWeaponDamage(1d4,Fire)']:
            self.assertIn(text,self.status)
        for path in ROOT.glob('hc_*.py'):
            if 'patriot' in str(path).lower() or path.name=='hc_coolerfire.py':continue
            source=path.read_text(encoding='utf-8-sig')
            for name in [m.SPELL,m.STATUS,m.OBJECT_STAT]:self.assertNotIn('"'+name+'"',source,str(path))
    def test_description(self):
        self.assertEqual(self.loca[m.SPELL+'_Name'],'Illegal Sidewalk Cookout')
        desc=self.loca[m.SPELL+'_Description']
        self.assertTrue(3<=len(re.findall(r'[.!?](?:\s|$)',desc))<=5)
        for term in ['9 m','1 Junk','short rest','3 turns','Cold','1d4 Fire']:self.assertIn(term,desc)
    def test_vanilla_precedent(self):
        data=ROOT/'temp_race/Public'
        projectile=(data/'Shared/Stats/Generated/Data/Spell_Projectile.txt').read_text(encoding='utf-8-sig')
        self.assertIn('new entry "'+m.DONOR+'"',projectile)
        self.assertIn('ApplyStatus(SELF,',projectile)
        armor=(data/'Shared/Stats/Generated/Data/Armor.txt').read_text(encoding='utf-8-sig').replace(' ','')
        boost=(data/'SharedDev/Stats/Generated/Data/Status_BOOST.txt').read_text(encoding='utf-8-sig').replace(' ','')
        self.assertIn('Resistance(Cold,Resistant)',armor)
        self.assertIn('CharacterWeaponDamage(1d4,Fire)',boost)
        for path in (data/'Honour/Stats/Generated/Data').glob('*.txt'):
            if 'patriot' not in str(path).lower():
                self.assertNotIn('new entry "'+m.DONOR+'"',path.read_text(encoding='utf-8-sig'))
    def test_icons_exist(self):
        data=ROOT/'temp_race/Public/Shared/Stats/Generated/Data'
        self.assertIn('"'+m.SPELL_ICON_FALLBACK+'"',(data/'Spell_Projectile.txt').read_text())
        self.assertIn('"'+m.STATUS_ICON_FALLBACK+'"',(data/'Spell_Target.txt').read_text())
    def test_root_links_bounds(self):
        root=ET.parse(self.public/'RootTemplates/HC_CoolerFire.lsf.lsx')
        attrs={a.get('id'):a.get('value') for a in root.findall('.//node[@id="GameObjects"]/attribute')}
        self.assertEqual(attrs['MapKey'],self.guid(m.TEMPLATE_KEY))
        self.assertEqual(attrs['Stats'],m.OBJECT_STAT)
        self.assertEqual(attrs['VisualTemplate'],self.guid('HC_CoolerFire_visual'))
        self.assertEqual(attrs['CanBePickedUp'],'False')
        self.assertIn('"RootTemplate" "'+attrs['MapKey']+'"',self.obj)
        bounds=root.findall('.//node[@id="Bound"]')
        self.assertEqual(len(bounds),3)
        for bound in bounds:
            a={v.get('id'):v.get('value') for v in bound.findall('attribute')}
            self.assertEqual(float(a['Height']),float(a['Max'].split()[1]))
    def test_visual_resource(self):
        path=self.public/'Content/Assets/Props/[PAK]_HC_CoolerFire/_merged.lsf.lsx'
        root=ET.parse(path)
        objects=root.findall('.//node[@id="Objects"]')
        self.assertEqual(len(objects),3)
        for obj in objects:
            attrs={v.get('id'):v.get('value') for v in obj.findall('attribute')}
            self.assertEqual(attrs['MaterialID'],self.guid('HC_CoolerFire_mat'))
        self.assertEqual(len(root.findall('.//node[@id="Texture2DParameters"]')),3)
    def test_copied_assets(self):
        dest=Path(self.tmp.name)/'Generated/Public/HomelessCalifornian/Assets/Props/HC_CoolerFire/Resources'
        for name in m.ASSET_FILES:self.assertEqual((dest/name).read_bytes(),(m.ASSET_SRC/name).read_bytes())
    def test_dds(self):
        for kind,size in [('BM',1024),('NM',256),('PM',256)]:
            data=(m.ASSET_SRC/f'HC_CoolerFire_{kind}.DDS').read_bytes()
            self.assertEqual(data[:4],b'DDS ')
            self.assertEqual(struct.unpack_from('<II',data,12),(size,size))
            self.assertIn(data[84:88],(b'DXT1',b'DXT5'))
            self.assertGreater(struct.unpack_from('<I',data,28)[0],1)
    def test_mesh_bounds(self):
        data=json.loads((WORK/'out/coolerfire_preview.json').read_text())
        self.assertEqual(len(data['tri']),m.TRIANGLES)
        self.assertLess(m.TRIANGLES,3500)
        for p in data['pos']:
            for axis in range(3):self.assertTrue(m.BMIN[axis]-1e-6<=p[axis]<=m.BMAX[axis]+1e-6)
        self.assertAlmostEqual(min(p[1] for p in data['pos']),0)
    def test_gr2_roundtrip(self):
        target=Path(self.tmp.name)/'roundtrip.dae'
        result=subprocess.run([str(ROOT/'tools/Packed/Tools/Divine.exe'),'-g','bg3','-a','convert-model','-s',str(m.ASSET_SRC/'HC_CoolerFire.GR2'),'-d',str(target),'-i','gr2','-o','dae','-l','warn'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        root=ET.parse(target)
        ns={'c':'http://www.collada.org/2005/11/COLLADASchema'}
        geometry=root.findall('.//c:geometry',ns)
        self.assertEqual(len(geometry),3)
        for geo in geometry:self.assertEqual(sum(int(t.get('count')) for t in geo.findall('.//c:triangles',ns)),m.TRIANGLES)
    def test_generated_xml_compiles(self):
        for path in self.public.rglob('*.lsx'):
            result=subprocess.run([str(ROOT/'tools/Packed/Tools/Divine.exe'),'-g','bg3','-a','convert-resource','-s',str(path),'-d',str(Path(self.tmp.name)/(path.parent.name+'.lsf')),'-i','lsx','-o','lsf','-l','warn'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
