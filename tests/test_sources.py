import gzip
import unittest,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from refresh import normalize,SOURCES
from source import bounds

class SourceTests(unittest.TestCase):
    def test_classifications_stay_unofficial_and_source_specific(self):
        f={'geometry':{'type':'LineString','coordinates':[[-122.6,49.1],[-122.61,49.11]]},'properties':{'OBJECTID':1,'Channel_Name':'Yorkson','Classification_Desc':"UNOFFICAL Class 'A' - Red"}}
        r=normalize(f,SOURCES[0]);self.assertTrue(r['properties']['unofficial']);self.assertIn('Class',r['properties']['classification'])
        f['properties']={'OBJECTID':1,'CLASSIFICATION':2};r=normalize(f,SOURCES[2]);self.assertEqual(r['properties']['classification'],'Class A(O)');self.assertFalse(r['properties']['unofficial'])
    def test_invalid_geography_is_rejected(self):
        with self.assertRaises(ValueError):bounds({'coordinates':[[0,0],[1,1]]})
    def test_snapshot_is_complete_with_unique_source_ids(self):
        with gzip.open(Path(__file__).resolve().parents[1]/'web/data/water.json.gz', 'rt', encoding='utf-8') as snapshot:
            d=json.load(snapshot)
        ids=[r['properties']['id'] for r in d['features']]
        self.assertGreater(len(ids),1000);self.assertEqual(len(ids),len(set(ids)));self.assertEqual(len(d['sources']),3)
