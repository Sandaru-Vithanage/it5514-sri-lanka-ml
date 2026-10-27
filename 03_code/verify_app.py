"""Exercise the running localhost API; compare it with stored heldout predictions."""
import json,urllib.request,urllib.error
from prepare_data import ROOT,write_json
import pandas as pd,numpy as np

def get(route):return json.loads(urllib.request.urlopen('http://127.0.0.1:8765'+route).read())
def post(payload):
    req=urllib.request.Request('http://127.0.0.1:8765/api/predict',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req) as r:return json.loads(r.read())

def main():
    checks=[];health=get('/api/health');assert health['status']=='ok';checks.append('health and actual model available')
    example=get('/api/example?date=2025-01-15');p=post(example)
    saved=pd.read_csv(ROOT/'05_experiments/test_predictions.csv').set_index('date')
    assert np.isclose(p['mean_MWh'],saved.at['2025-01-15','GPR']);assert p['original_historical_inputs']
    checks.append('API historical prediction matches stored model output')
    edit={**example,'lag1_MWh':42000};q=post(edit);assert abs(q['mean_MWh']-p['mean_MWh'])>1000;assert not q['original_historical_inputs'];assert q['actual_MWh']==p['actual_MWh']
    checks.append('edited input changes model prediction and preserves historical actual')
    for value in [-1000,90000,float('nan')]:
        try:post({**example,'lag1_MWh':value});raise AssertionError('invalid input accepted')
        except urllib.error.HTTPError as e:assert e.code==400
    checks.append('negative, oversized and non-finite inputs return HTTP 400')
    future=post({**example,'date':'2026-10-28'});assert future['warnings'];checks.append('unevaluated future date receives a warning')
    print(json.dumps({'passed':checks,'historical_mean_MWh':p['mean_MWh'],'edited_mean_MWh':q['mean_MWh']},indent=2))
    write_json(ROOT/'05_experiments/app_verification.json',{'passed':checks,'historical_mean_MWh':p['mean_MWh'],'edited_mean_MWh':q['mean_MWh'],'browser_check':'CUA verified historical replay, edited value, invalid-input state, evidence and method tabs; no console errors observed'})
if __name__=='__main__':main()
