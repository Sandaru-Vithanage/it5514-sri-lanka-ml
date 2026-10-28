"""Azure-ready WSGI wrapper around the verified Python GPR inference pipeline."""
import os,sys,json,hashlib
from pathlib import Path
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from flask import Flask,request,jsonify,Response
from werkzeug.exceptions import HTTPException
ROOT=Path(__file__).resolve().parent
if not (ROOT/'03_code').exists():ROOT=ROOT.parent
sys.path.insert(0,str(ROOT/'03_code'))
import app as study
application=Flask(__name__);application.config['MAX_CONTENT_LENGTH']=12000
MODEL_HASH=hashlib.sha256((ROOT/'05_experiments/models/GPR.joblib').read_bytes()).hexdigest()
RELEASE=json.loads((ROOT/'release.json').read_text()) if (ROOT/'release.json').exists() else {}
COMMIT=RELEASE.get('commit',os.environ.get('STUDY_COMMIT','unspecified'))
if RELEASE and RELEASE.get('model_sha256')!=MODEL_HASH:raise RuntimeError('Release model fingerprint mismatch.')

@application.after_request
def headers(response):
 response.headers['X-Content-Type-Options']='nosniff';response.headers['X-Robots-Tag']='noindex, nofollow'
 response.headers['Referrer-Policy']='same-origin'
 return response

@application.get('/')
def index():
 text=(ROOT/'03_code/app.html').read_text().replace('D.V.S Sandaru Rashmika','IT5514 research project').replace('269182L','Research demo')
 return Response(text,mimetype='text/html')

@application.get('/api/health')
def health():return jsonify(status='ok',model='Gaussian Process Regression',trained_through='2024-12-31',evaluation_through='2025-04-07',model_sha256=MODEL_HASH,commit=COMMIT,historical_research_demo=True)

@application.get('/api/meta')
def meta():return jsonify(dates=study.TEST.index.strftime('%Y-%m-%d').tolist(),metrics=study.METRICS,uncertainty=study.UNC,importance=study.IMP,reference_date=study.REF['date'],dataset_doi='10.5281/zenodo.17175212')

@application.get('/api/extension')
def extension():return jsonify(json.loads((ROOT/'05_experiments/extension/summary.json').read_text()))

@application.get('/api/deployment')
def deployment():return jsonify(repository='https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml',visibility='Public repository',hosting='Azure App Service Linux · Free F1',commit=COMMIT,model_sha256=MODEL_HASH)

@application.get('/api/example')
def example():
 try:
  import pandas as pd
  date=pd.Timestamp(request.args['date']);row=study.TABLE.loc[date]
  return jsonify(date=str(date.date()),**{f:float(row[f]) for f in study.FEATURES[:6]})
 except (KeyError,ValueError,TypeError):return jsonify(error='No eligible historical record for this date.'),400

@application.post('/api/predict')
def prediction():
 try:
  payload=request.get_json()
  if not isinstance(payload,dict):raise ValueError('Expected a JSON object.')
  return jsonify(study.predict(payload))
 except (KeyError,ValueError,TypeError,OverflowError) as e:return jsonify(error=str(e)),400

@application.errorhandler(HTTPException)
def http_error(e):return jsonify(error=e.description),e.code
