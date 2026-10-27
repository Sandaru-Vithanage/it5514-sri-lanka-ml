"""Meaningful leakage, feature and result checks against independent recomputation."""
from pathlib import Path
import sys,json,hashlib
import numpy as np,pandas as pd,joblib
from sklearn.metrics import mean_absolute_error,root_mean_squared_error,r2_score
from prepare_data import ROOT,FEATURES
from models import gpr_predict

def main():
    quality=pd.read_csv(ROOT/'02_data/processed/daily_energy_quality.csv',parse_dates=['date']).set_index('date')
    df=pd.read_csv(ROOT/'02_data/processed/modelling_table.csv',parse_dates=['date']).set_index('date')
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append({'check':name,'passed':True})
    check('unique chronological daily modelling rows',df.index.is_unique and df.index.is_monotonic_increasing)
    # Feature reference uses calendar subtraction rather than repeating shift code.
    for date,row in df.iterrows():
        for lag in [1,2,7,14]:
            value=quality.at[date-pd.Timedelta(days=lag),'target_MWh'];assert np.isclose(row[f'lag{lag}_MWh'],value)
        past=quality.loc[date-pd.Timedelta(days=7):date-pd.Timedelta(days=1),'target_MWh']
        assert len(past)==7 and past.notna().all()
        assert np.isclose(row.rolling7_mean_MWh,past.mean()) and np.isclose(row.rolling7_std_MWh,past.std(ddof=0))
    check('every lag and rolling value uses only prior calendar days',True)
    dev=df[df.split=='development'];test=df[df.split=='test']
    check('chronological split and test held to 2025',dev.index.max()<test.index.min() and str(test.index.min().date())=='2025-01-01')
    check('targets have 96 timestamps and no explicit missing plant values',bool(quality.loc[df.index,'valid_target'].all()))
    model=joblib.load(ROOT/'05_experiments/models/GPR.joblib')
    check('scaler fitted on development features only',np.allclose(model[0].mean_,dev[FEATURES].mean().to_numpy()))
    check('GPR stores only development labels',model[-1].X_train_.shape[0]==len(dev))
    p=pd.read_csv(ROOT/'05_experiments/test_predictions.csv',parse_dates=['date']).set_index('date')
    mu,sd=gpr_predict(model,test[FEATURES]);check('saved model predictions reproduce',np.allclose(mu,p.GPR,rtol=1e-10) and np.allclose(sd,p.GPR_std_MWh,rtol=1e-10))
    check('prediction rows match test dates and targets',p.index.equals(test.index) and np.allclose(p.actual_MWh,test.target_MWh))
    table=pd.read_csv(ROOT/'05_experiments/test_metrics.csv')
    for _,r in table.iterrows():
        y=p.actual_MWh;pred=p[r.model]
        assert np.isclose(r.MAE_MWh,mean_absolute_error(y,pred))
        assert np.isclose(r.RMSE_MWh,root_mean_squared_error(y,pred))
        assert np.isclose(r.R2,r2_score(y,pred))
    check('every main metric independently recomputed from stored predictions',True)
    cv=pd.read_csv(ROOT/'05_experiments/cv_results.csv');sel=json.loads((ROOT/'05_experiments/selected_models_before_test.json').read_text())
    for name,choice in sel.items():
        scores=cv[cv.model==name].groupby('config_id').MAE_MWh.mean()
        assert int(scores.idxmin())==choice['config_id']
        assert np.isclose(scores.min(),choice['CV_MAE_MWh'])
    check('all selected configurations minimize validation MAE only',True)
    from prepare_data import write_json
    write_json(ROOT/'05_experiments/verification.json',{'checks':checks,'passed':len(checks),'status':'passed','note':'Student review, university AI-policy confirmation and Moodle upload remain human actions.'})
    print(json.dumps(checks,indent=2))
if __name__=='__main__':main()
