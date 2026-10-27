"""Compare production HTTP inference with the trusted local saved-model computation."""
import sys,json,urllib.request,urllib.error,hashlib
from prepare_data import ROOT,write_json
import app
base=sys.argv[1].rstrip('/') if len(sys.argv)>1 else 'http://127.0.0.1:8766'
checks=[]
def request(path,data=None):
 req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=120) as r:return r.status,json.loads(r.read())
 except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
def check(name,ok):
 assert ok,name
 checks.append(name)
status,h=request('/api/health');check('healthy endpoint',status==200 and h['status']=='ok')
check('identical model bytes',h['model_sha256']==hashlib.sha256((ROOT/'05_experiments/models/GPR.joblib').read_bytes()).hexdigest())
_,p=request('/api/example?date=2025-01-15');status,out=request('/api/predict',p);expected=app.predict(p)
check('historical forecast matches local inference',status==200 and abs(out['mean_MWh']-expected['mean_MWh'])<1e-6)
p['lag1_MWh']=42000;status,edited=request('/api/predict',p)
check('edited forecast matches local inference',status==200 and abs(edited['mean_MWh']-app.predict(p)['mean_MWh'])<1e-6)
check('edited inputs are labelled and actual stays fixed',not edited['original_historical_inputs'] and edited['actual_MWh']==out['actual_MWh'])
p['lag1_MWh']=-1;status,_=request('/api/predict',p);check('negative input rejected',status==400)
p['lag1_MWh']=float('nan');status,_=request('/api/predict',p);check('nonfinite input rejected',status==400)
status,_=request('/api/predict',{'oversize':'x'*13000});check('oversize request rejected',status==413)
status,x=request('/api/extension');check('both task comparisons exposed',status==200 and len(x['dispatch']['metrics'])==9 and len(x['rainfall']['metrics'])==9)
status,d=request('/api/deployment');check('review repository linked',status==200 and d['repository']=='https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml')
result={'passed':True,'base_url':base,'UTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'checks':checks,'model_sha256':h['model_sha256'],'application_commit':h['commit'],'historical_mean_MWh':out['mean_MWh'],'edited_mean_MWh':edited['mean_MWh'],'tolerance_MWh':1e-6}
write_json(ROOT/('10_deployment/remote_verification.json' if base.startswith('https:') else '05_experiments/production_local_verification.json'),result)
print(json.dumps(result,indent=2))
