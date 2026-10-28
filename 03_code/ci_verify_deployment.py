"""Wait for the embedded release, then verify real HTTPS inference using only the stdlib."""
import argparse,json,math,time,urllib.request,urllib.error
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--expected',required=True);parser.add_argument('--url',default='https://lanka-dispatch-it5514-sv.azurewebsites.net');parser.add_argument('--timeout',type=int,default=600);parser.add_argument('--output',default='release_verification.json');a=parser.parse_args()
expected=json.loads(Path(a.expected).read_text());base=a.url.rstrip('/')
def request(path,payload=None):
    req=urllib.request.Request(base+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json','User-Agent':'IT5514 deployment verification'})
    try:
        with urllib.request.urlopen(req,timeout=25) as r:return r.status,json.load(r)
    except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
start=time.monotonic();attempts=0;last='Not checked'
while time.monotonic()-start<a.timeout:
    attempts+=1
    try:
        status,health=request('/api/health')
        if status==200 and health.get('commit')==expected['commit'] and health.get('model_sha256')==expected['model_sha256']:break
        last='New release not active yet'
    except (OSError,ValueError) as e:last=type(e).__name__
    time.sleep(15)
else:raise RuntimeError('Release did not become ready: '+last)
checks=['embedded source commit matches','model fingerprint matches'];tolerance=1e-6
for label,payload,key in [('historical',expected['payload'],'historical'),('edited',expected['edited_payload'],'edited')]:
    status,pred=request('/api/predict',payload);assert status==200,(label,status)
    for field in ['mean_MWh','std_MWh','lower95_MWh','upper95_MWh','actual_MWh','seasonal_naive_MWh']:assert math.isclose(pred[field],expected[key][field],rel_tol=0,abs_tol=tolerance),(label,field)
    assert pred['original_historical_inputs']==expected[key]['original_historical_inputs'];checks.append(label+' forecast and replay label match offline bundle')
status,extension=request('/api/extension');assert status==200 and extension==expected['extension'];checks.append('published experiment evidence matches')
status,repo=request('/api/deployment');assert status==200 and repo['visibility']=='Public repository' and repo['commit']==expected['commit'];checks.append('public repository and release identity match')
for value in [-1,float('nan')]:
    status,_=request('/api/predict',{**expected['payload'],'lag1_MWh':value});assert status==400;checks.append('invalid '+str(value)+' input rejected')
status,_=request('/api/predict',{'padding':'x'*13000});assert status==413;checks.append('oversize request rejected')
record={'passed':True,'url':base,'commit':expected['commit'],'model_sha256':expected['model_sha256'],'checks':checks,'readiness_attempts':attempts,'elapsed_seconds':round(time.monotonic()-start,2),'tolerance_MWh':tolerance}
Path(a.output).write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
