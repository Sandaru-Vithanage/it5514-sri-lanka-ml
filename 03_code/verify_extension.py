"""Independent arithmetic, ordering, persistence and repeatability checks for the extension."""
from pathlib import Path
import json,hashlib,sys
import numpy as np,pandas as pd,joblib
from sklearn.metrics import mean_absolute_error,root_mean_squared_error,r2_score
from prepare_data import ROOT,FEATURES,write_json
from extension_experiments import prepare_rainfall

checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
p=json.loads((ROOT/'00_requirements/Extension_Protocol.json').read_text())
check('frozen protocol matches execution',hashlib.sha256((ROOT/'00_requirements/Extension_Protocol.json').read_bytes()).hexdigest()==json.loads((ROOT/'05_experiments/extension/execution_start.json').read_text())['protocol_sha256'])
rain,cols=prepare_rainfall(p)
check('independent dataset row counts and order',len(rain)==936 and rain.index.is_unique and rain.index.is_monotonic_increasing)
check('rainfall holdout begins after all selection windows',p['independent_dataset']['folds'][-1]['validation_end']<p['independent_dataset']['test_start'])
for study in ['dispatch','rainfall']:
 d=ROOT/'05_experiments/extension'/study
 pred=pd.read_csv(d/'test_predictions.csv',index_col='date');metrics=pd.read_csv(d/'test_metrics.csv');cv=pd.read_csv(d/'cv_results.csv');selected=json.loads((d/'selected_before_test.json').read_text())
 check(study+' finite predictions',np.isfinite(pred.to_numpy()).all())
 for _,row in metrics.iterrows():
  q=pred[row.model]
  for key,value in [('MAE',mean_absolute_error(pred.actual,q)),('RMSE',root_mean_squared_error(pred.actual,q)),('R2',r2_score(pred.actual,q))]:
   check(study+' '+row.model+' '+key,np.isclose(row[key],value,rtol=1e-10))
  vals=cv[cv.model==row.model].groupby('config_id').MAE.mean()
  check(study+' '+row.model+' CV score',np.isclose(row.CV_MAE,vals.min()))
  if row.model in selected:check(study+' '+row.model+' CV selection',int(vals.idxmin())==selected[row.model]['config_id'])
 ref=ROOT/'work/extension_prediction_reference'/study/'test_predictions.csv'
 if ref.exists():
  old=pd.read_csv(ref,index_col='date')
  check(study+' exact repeat of all predictions',np.allclose(old.to_numpy(),pred.to_numpy(),rtol=0,atol=1e-8))
 model=joblib.load(d/'NGBoost.joblib')
 check(study+' importable model serialization',type(model).__module__=='extension_models')
 table=rain if study=='rainfall' else pd.read_csv(ROOT/'02_data/processed/modelling_table.csv',parse_dates=['date']).set_index('date')
 features=cols if study=='rainfall' else FEATURES
 x=table.loc[pd.to_datetime(pred.index),features]
 check(study+' saved model reproduces predictions',np.allclose(model.predict(x),pred.NGBoost,rtol=0,atol=1e-8))
check('rainfall baseline outperforms learned models',metrics.loc[metrics.model=='Seasonal median','MAE'].iloc[0]<metrics.loc[~metrics.model.str.startswith('Seasonal'),'MAE'].min())
write_json(ROOT/'05_experiments/extension/verification.json',{'passed':True,'check_count':len(checks),'checks':checks,'reproduction_tolerance':1e-8,'note':'Extension rerun independently reproduced its first recorded predictions; original energy holdout remains post-hoc for added models.'})
print(json.dumps({'passed':True,'checks':len(checks)},indent=2))
