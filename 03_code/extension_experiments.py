"""Predeclared supplementary algorithms and an independent Sri Lankan rainfall task."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,time,hashlib,warnings
import numpy as np,pandas as pd,joblib
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from ngboost import NGBRegressor
from ngboost.distns import Normal
from ngboost.scores import LogScore
from sklearn.base import BaseEstimator,RegressorMixin
from sklearn.metrics import mean_absolute_error,root_mean_squared_error,r2_score
from threadpoolctl import threadpool_limits
from prepare_data import ROOT,FEATURES,write_json
from models import configurations,make_model,gpr_predict

OUT=ROOT/'05_experiments/extension'
EXTRA={
 'NGBoost':[{'max_depth':d,'n_estimators':n} for d in [2,3] for n in [200,400,600]],
 'KNN':[{'n_neighbors':n,'weights':w} for n in [5,15,31] for w in ['uniform','distance']],
 'Gradient boosting':[{'max_depth':d,'n_estimators':n} for d in [1,2] for n in [100,300,600]]
}

from extension_models import ScaledNGBoost

def extra_model(name,cfg):
 if name=='NGBoost':return ScaledNGBoost(**cfg)
 if name=='KNN':return make_pipeline(StandardScaler(),KNeighborsRegressor(**cfg))
 if name=='Gradient boosting':return GradientBoostingRegressor(learning_rate=.03,min_samples_leaf=10,random_state=42,**cfg)
 return make_model(name,cfg)

def metric(y,p):return {'MAE':float(mean_absolute_error(y,p)),'RMSE':float(root_mean_squared_error(y,p)),'R2':float(r2_score(y,p))}

def prepare_rainfall(protocol):
 path=ROOT/'02_data/rainfall/raw/lka-rainfall-subnat-full.csv'
 assert hashlib.sha256(path.read_bytes()).hexdigest()==protocol['independent_dataset']['sha256']
 raw=pd.read_csv(path,parse_dates=['date']);c=raw[(raw.adm_level==2)&(raw.PCODE=='LK11')&(raw.version=='final')].copy()
 assert not c.date.duplicated().any()
 c=c.set_index('date').sort_index();calendar=pd.DatetimeIndex([pd.Timestamp(year=y,month=m,day=d) for y in range(1981,2027) for m in range(1,13) for d in [1,11,21]],name='date')
 y=c.rfh.reindex(calendar);y=y.where(np.isfinite(y)&(y>=0));f=pd.DataFrame(index=calendar)
 for lag in [6,7,9,36]:f[f'lag{lag}_mm']=y.shift(lag)
 f['rolling3_mean_at_lag6_mm']=y.shift(6).rolling(3,min_periods=3).mean();f['rolling3_std_at_lag6_mm']=y.shift(6).rolling(3,min_periods=3).std(ddof=0)
 f['period']=(calendar.month-1)*3+np.where(calendar.day==1,0,np.where(calendar.day==11,1,2))
 f['annual_sin']=np.sin(2*np.pi*f.period/36);f['annual_cos']=np.cos(2*np.pi*f.period/36);f['trend_dekads']=(calendar.year-2000)*36+f.period
 f['target']=y;cols=protocol['independent_dataset']['features'];f=f.loc['2000':'2025'];f=f.dropna(subset=cols+['target'])
 dst=ROOT/'02_data/rainfall/processed';dst.mkdir(parents=True,exist_ok=True);f.to_csv(dst/'colombo_modelling.csv',index_label='date')
 # Independent calendar lookup verifies each supplied lag rather than just reusing shift().
 lookup={d:i for i,d in enumerate(calendar)}
 for date,row in f.iterrows():
  for lag in [6,7,9,36]:assert np.isclose(row[f'lag{lag}_mm'],y.loc[calendar[lookup[date]-lag]])
 facts={'raw_rows':len(raw),'all_admin_units':int(raw.PCODE.nunique()),'districts':int(raw[raw.adm_level==2].PCODE.nunique()),'provinces':int(raw[raw.adm_level==1].PCODE.nunique()),'colombo_final_rows':len(c),'model_rows':len(f),'development_rows':int((f.index<'2024-01-01').sum()),'test_rows':int((f.index>='2024-01-01').sum()),'lag_lookup_checks_passed':True,'forecast_type':'retrospective next-dekad, conservative six-dekad observation lag','final_vintage_revision_limit':True}
 write_json(OUT/'rainfall_data_audit.json',facts);return f,cols

def evaluate(study,table,cols,folds,cutoff,models,unit,baseline_specs):
 folder=OUT/study;folder.mkdir(parents=True,exist_ok=True);dev=table.loc[:cutoff];test=table[table.index>pd.Timestamp(cutoff)];cv=[];selected={};start=time.perf_counter()
 for name,configs in models.items():
  scores=[]
  for ci,cfg in enumerate(configs):
   values=[]
   for fi,fold in enumerate(folds,1):
    tr=dev.loc[:fold['train_end']];va=dev.loc[fold['validation_start']:fold['validation_end']];model=extra_model(name,cfg)
    with warnings.catch_warnings(record=True) as caught:
     warnings.simplefilter('always');model.fit(tr[cols],tr.target)
    p=model.predict(va[cols]);m=metric(va.target,p);values.append(m['MAE'])
    cv.append({'model':name,'config_id':ci,'config':json.dumps(cfg,sort_keys=True),'fold':fi,'n_train':len(tr),'n_validation':len(va),**m,'warnings':' | '.join(str(w.message) for w in caught)})
   scores.append(float(np.mean(values)));pd.DataFrame(cv).to_csv(folder/'cv_results.csv',index=False)
   print(study,name,ci,'CV MAE',round(scores[-1],4),flush=True)
  best=int(np.argmin(scores));selected[name]={'config_id':best,'config':configs[best],'CV_MAE':scores[best]}
 baseline_cv={}
 for name,spec in baseline_specs.items():
  vals=[]
  for fi,fold in enumerate(folds,1):
   tr=dev.loc[:fold['train_end']];va=dev.loc[fold['validation_start']:fold['validation_end']]
   bp=va.period.map(tr.groupby('period').target.median()).to_numpy() if spec=='seasonal_median' else va[spec].to_numpy()
   bm=metric(va.target,bp);vals.append(bm['MAE']);cv.append({'model':name,'config_id':0,'config':'{}','fold':fi,'n_train':len(tr),'n_validation':len(va),**bm,'warnings':''})
  baseline_cv[name]=float(np.mean(vals))
 pd.DataFrame(cv).to_csv(folder/'cv_results.csv',index=False)
 # These choices are persisted before accessing the study's heldout outcomes for scoring.
 write_json(folder/'selected_before_test.json',selected)
 pred=pd.DataFrame({'actual':test.target},index=test.index);metrics=[];prob=[]
 for name,choice in selected.items():
  t=time.perf_counter();model=extra_model(name,choice['config']).fit(dev[cols],dev.target);fit=time.perf_counter()-t
  if name=='GPR':mu,sd=gpr_predict(model,test[cols])
  elif name=='NGBoost':mu,sd=model.distribution(test[cols])
  else:mu=model.predict(test[cols]);sd=None
  pred[name]=mu;metrics.append({'study':study,'model':name,'unit':unit,'n_train':len(dev),'n_test':len(test),'CV_MAE':choice['CV_MAE'],**metric(test.target,mu),'fit_seconds':fit})
  if sd is not None:
   lower=mu-1.95996398454*sd;upper=mu+1.95996398454*sd;pred[name+'_std']=sd;pred[name+'_lower95']=lower;pred[name+'_upper95']=upper
   prob.append({'model':name,'coverage95':float(np.mean((test.target>=lower)&(test.target<=upper))),'mean_width':float(np.mean(upper-lower)),'gaussian_NLPD':float(np.mean(.5*np.log(2*np.pi*sd**2)+.5*((test.target-mu)/sd)**2)),'negative_means':int((mu<0).sum()),'negative_lower95':int((lower<0).sum())})
  joblib.dump(model,folder/(name.replace(' ','_')+'.joblib'))
 for name,spec in baseline_specs.items():
  if spec=='seasonal_median':mu=test.period.map(dev.groupby('period').target.median()).to_numpy()
  else:mu=test[spec].to_numpy()
  pred[name]=mu;metrics.append({'study':study,'model':name,'unit':unit,'n_train':len(dev),'n_test':len(test),'CV_MAE':baseline_cv[name],**metric(test.target,mu),'fit_seconds':0.})
 seasonal=next((m['MAE'] for m in metrics if m['model']=='Seasonal naive'),None)
 if seasonal is not None:
  for m in metrics:m['MAE_skill_vs_seasonal']=1-m['MAE']/seasonal
 pred.to_csv(folder/'test_predictions.csv',index_label='date');pd.DataFrame(metrics).to_csv(folder/'test_metrics.csv',index=False);write_json(folder/'probabilistic_metrics.json',prob)
 write_json(folder/'execution.json',{'elapsed_seconds':time.perf_counter()-start,'n_candidates':sum(len(v) for v in models.values()),'cv_fit_count':3*sum(len(v) for v in models.values()),'test_policy':'supplementary post-hoc comparison on already examined dispatch holdout' if study=='dispatch' else 'independent rainfall-task holdout; not a transferred electricity model'})
 print(pd.DataFrame(metrics).to_string(index=False),flush=True)

def main():
 OUT.mkdir(parents=True,exist_ok=True);pp=ROOT/'00_requirements/Extension_Protocol.json';p=json.loads(pp.read_text())
 write_json(OUT/'execution_start.json',{'protocol_sha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'UTC':pd.Timestamp.now(tz='UTC').isoformat(),'seed':42,'NGBoost':'0.5.11','original_test_already_examined':True})
 with threadpool_limits(limits=1):
  original=json.loads((ROOT/'00_requirements/Experiment_Protocol.json').read_text());dispatch=pd.read_csv(ROOT/'02_data/processed/modelling_table.csv',parse_dates=['date']).set_index('date').rename(columns={'target_MWh':'target'})
  evaluate('dispatch',dispatch,FEATURES,original['validation_folds'],'2024-12-31',EXTRA,'MWh',{'Seasonal naive':'lag7_MWh'})
  rain,cols=prepare_rainfall(p);search={**configurations(),**EXTRA}
  evaluate('rainfall',rain,cols,p['independent_dataset']['folds'],'2023-12-31',search,'mm',{'Seasonal naive':'lag36_mm','Seasonal median':'seasonal_median'})
if __name__=='__main__':main()
