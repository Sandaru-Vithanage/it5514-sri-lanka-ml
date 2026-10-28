"""Validate a built inference bundle offline before granting the deployment job an Azure token."""
import argparse,hashlib,json,math,sys,tempfile,unittest,zipfile
from pathlib import Path
SOURCE=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--bundle',default='10_deployment/deployment.zip');parser.add_argument('--expected',default='10_deployment/smoke_expected.json');args=parser.parse_args()
manifest=json.loads((SOURCE/'10_deployment/bundle_manifest.json').read_text())
archive=SOURCE/args.bundle
assert hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['zip_sha256']
workspace=tempfile.TemporaryDirectory();ROOT=Path(workspace.name).resolve()
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))==15
    for n in z.namelist():
        assert (ROOT/n).resolve().is_relative_to(ROOT),n
        assert not any(p in Path(n).parts for p in ['work','.git','.venv','01_source_materials']),n
    for e in manifest['files']:assert hashlib.sha256(z.read(e['deployed_path'])).hexdigest()==e['sha256']
    z.extractall(ROOT)
sys.path.insert(0,str(ROOT))
from wsgi import application,study,MODEL_HASH,COMMIT
import numpy as np,pandas as pd

class InferenceBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.client=application.test_client()
    def example(self):return self.client.get('/api/example?date=2025-01-15').json
    def test_recorded_holdout_predictions(self):
        reference=pd.read_csv(SOURCE/'05_experiments/test_predictions.csv',parse_dates=['date']).set_index('date')
        mu,sd=study.gpr_predict(study.MODEL,study.TABLE.loc[reference.index,study.FEATURES])
        np.testing.assert_allclose(mu,reference.GPR,rtol=0,atol=1e-6)
        np.testing.assert_allclose(sd,reference.GPR_std_MWh,rtol=0,atol=1e-6)
    def test_release_identity(self):
        h=self.client.get('/api/health');self.assertEqual(h.status_code,200)
        self.assertEqual(h.json['commit'],manifest['release_commit']);self.assertEqual(h.json['model_sha256'],MODEL_HASH)
        self.assertEqual(COMMIT,json.loads((ROOT/'release.json').read_text())['commit'])
    def test_historical_case(self):
        r=self.client.post('/api/predict',json=self.example());self.assertEqual(r.status_code,200)
        self.assertTrue(r.json['original_historical_inputs']);self.assertAlmostEqual(r.json['mean_MWh'],42325.97557366114,delta=1e-6)
        self.assertLess(r.json['lower95_MWh'],r.json['mean_MWh']);self.assertGreater(r.json['upper95_MWh'],r.json['mean_MWh'])
    def test_changed_input_and_fixed_actual(self):
        p=self.example();first=self.client.post('/api/predict',json=p).json;p['lag1_MWh']=42000;r=self.client.post('/api/predict',json=p).json
        self.assertFalse(r['original_historical_inputs']);self.assertEqual(r['actual_MWh'],first['actual_MWh']);self.assertAlmostEqual(r['mean_MWh'],44217.78536168519,delta=1e-6)
    def test_invalid_values(self):
        for value in [-1,80001,float('nan'),float('inf')]:
            with self.subTest(value=value):
                p=self.example();p['lag1_MWh']=value;self.assertEqual(self.client.post('/api/predict',json=p).status_code,400)
    def test_invalid_request_shape_and_size(self):
        self.assertEqual(self.client.post('/api/predict',json=[]).status_code,400)
        self.assertEqual(self.client.post('/api/predict',json={'padding':'x'*13000}).status_code,413)
    def test_historical_lookup(self):
        self.assertEqual(self.client.get('/api/example?date=2030-01-01').status_code,400)
    def test_published_evidence(self):
        x=self.client.get('/api/extension').json;expected=json.loads((SOURCE/'05_experiments/extension/summary.json').read_text())
        self.assertEqual(x,expected);self.assertEqual(len(x['dispatch']['metrics']),9);self.assertEqual(len(x['rainfall']['metrics']),9)
    def test_public_repository_and_headers(self):
        r=self.client.get('/api/deployment');self.assertEqual(r.json['visibility'],'Public repository');self.assertEqual(r.json['commit'],COMMIT)
        self.assertEqual(r.headers['X-Content-Type-Options'],'nosniff')
        html=self.client.get('/').data.decode();self.assertNotIn('D.V.S Sandaru Rashmika',html);self.assertIn('GitHub Actions',html)

result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InferenceBundleTests))
if not result.wasSuccessful():sys.exit(1)
payload=application.test_client().get('/api/example?date=2025-01-15').json
client=application.test_client();historical=client.post('/api/predict',json=payload).json;edited_payload={**payload,'lag1_MWh':42000}
expected={'commit':COMMIT,'model_sha256':MODEL_HASH,'payload':payload,'historical':historical,'edited_payload':edited_payload,'edited':client.post('/api/predict',json=edited_payload).json,'extension':client.get('/api/extension').json,'tests_passed':result.testsRun,'holdout_predictions_checked':97}
path=SOURCE/args.expected;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(expected,indent=2,allow_nan=False))
print(json.dumps({'tests_passed':result.testsRun,'recorded_predictions_checked':97,'bundle_files':15,'release_commit':COMMIT},indent=2))
workspace.cleanup()
