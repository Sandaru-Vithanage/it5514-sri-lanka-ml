"""Historical demonstration UI backed by the frozen GPR; Azure WSGI wrapper in 10_deployment."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
from pathlib import Path
import json,math,argparse
import numpy as np,pandas as pd,joblib
from prepare_data import ROOT,FEATURES,GROUPS,add_calendar
from models import gpr_predict

EXP=ROOT/'05_experiments'
MODEL=joblib.load(EXP/'models/GPR.joblib')
TABLE=pd.read_csv(ROOT/'02_data/processed/modelling_table.csv',parse_dates=['date']).set_index('date')
DEV=TABLE[TABLE.split=='development'];TEST=TABLE[TABLE.split=='test']
REF=json.loads((EXP/'explanation_reference.json').read_text())
METRICS=pd.read_csv(EXP/'test_metrics.csv').to_dict(orient='records')
UNC=json.loads((EXP/'uncertainty.json').read_text())
IMP=pd.read_csv(EXP/'grouped_permutation_summary.csv').to_dict(orient='records')

def predict(payload):
    date=pd.Timestamp(payload['date'])
    if pd.isna(date) or date.year<2023 or date.year>2030 or date.tzinfo is not None:raise ValueError('Select an unambiguous calendar date between 2023 and 2030.')
    date=date.normalize();vals={}
    for feature in FEATURES[:6]:
        v=float(payload[feature]);limit=40000 if 'std' in feature else 80000
        if not math.isfinite(v) or not 0<=v<=limit:raise ValueError('Energy inputs must be finite and within the displayed limits.')
        vals[feature]=v
    frame=add_calendar(pd.DataFrame([vals],index=pd.DatetimeIndex([date])))[FEATURES]
    mu,std=gpr_predict(MODEL,frame);mean=float(mu[0]);sd=float(std[0]);effects=[]
    for group,cols in GROUPS.items():
        changed=frame.copy();changed.loc[:,cols]=[REF['features'][c] for c in cols]
        effects.append({'group':group,'difference_MWh':mean-float(MODEL.predict(changed)[0])})
    outside=[f for f in FEATURES[:6] if vals[f]<DEV[f].min() or vals[f]>DEV[f].max()]
    warnings=[]
    if outside:warnings.append('Some energy inputs are outside the development-data range. Treat this scenario cautiously.')
    if date>TEST.index.max() or date<DEV.index.min():warnings.append('This date is outside the evaluated historical period. No live data are connected.')
    actual=float(TABLE.loc[date,'target_MWh']) if date in TABLE.index else None
    original=bool(date in TABLE.index and np.allclose(frame[FEATURES[:6]].iloc[0],TABLE.loc[date,FEATURES[:6]].astype(float)))
    return {'mean_MWh':mean,'std_MWh':sd,'lower95_MWh':mean-1.95996398454*sd,'upper95_MWh':mean+1.95996398454*sd,'seasonal_naive_MWh':vals['lag7_MWh'],'actual_MWh':actual,'original_historical_inputs':original,'effects':effects,'warnings':warnings,'date':str(date.date())}

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,obj):
        data=json.dumps(obj,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path in ['/','/index.html']:
            body=(Path(__file__).parent/'app.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        elif parsed.path=='/api/meta':
            self.reply(200,{'dates':TEST.index.strftime('%Y-%m-%d').tolist(),'metrics':METRICS,'uncertainty':UNC,'importance':IMP,'reference_date':REF['date'],'dataset_doi':'10.5281/zenodo.17175212'})
        elif parsed.path=='/api/example':
            try:
                date=pd.Timestamp(parse_qs(parsed.query)['date'][0]);row=TABLE.loc[date]
                self.reply(200,{'date':str(date.date()),**{f:float(row[f]) for f in FEATURES[:6]}})
            except (KeyError,ValueError,TypeError):self.reply(400,{'error':'No eligible historical record for this date.'})
        elif parsed.path=='/api/health':self.reply(200,{'status':'ok','model':'Gaussian Process Regression','trained_through':'2024-12-31'})
        elif parsed.path=='/api/extension':self.reply(200,json.loads((EXP/'extension/summary.json').read_text()))
        elif parsed.path=='/api/deployment':self.reply(200,{'repository':'https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml','visibility':'Public repository','hosting':'Local development server; Azure wrapper available','commit':'local','model_sha256':'See deployment health endpoint'})
        else:self.reply(404,{'error':'Not found'})
    def do_POST(self):
        if self.path!='/api/predict':return self.reply(404,{'error':'Not found'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<=0 or n>12000:raise ValueError('Invalid request size.')
            self.reply(200,predict(json.loads(self.rfile.read(n))))
        except (ValueError,KeyError,TypeError,OverflowError) as e:self.reply(400,{'error':str(e)})

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
    print(f'Open http://127.0.0.1:{args.port} | Local historical research demo',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
