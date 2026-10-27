"""Validation-only model selection followed by a frozen chronological holdout."""
import os
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[name]='1'
from pathlib import Path
import sys,json,time,platform,warnings,hashlib
import numpy as np,pandas as pd,joblib,sklearn,scipy
from sklearn.metrics import mean_absolute_error,root_mean_squared_error,r2_score
from threadpoolctl import threadpool_limits
from prepare_data import ROOT,FEATURES,GROUPS,write_json
from models import configurations,make_model,gpr_predict

EXP=ROOT/'05_experiments';OUT=EXP/'models'

def metrics(y,p):
    return {'MAE_MWh':float(mean_absolute_error(y,p)),'RMSE_MWh':float(root_mean_squared_error(y,p)),'R2':float(r2_score(y,p))}

def bootstrap_difference(a,b,block=7,seed=42,n=2000):
    delta=np.asarray(a)-np.asarray(b);rng=np.random.default_rng(seed);k=int(np.ceil(len(delta)/block));res=[]
    for _ in range(n):
        starts=rng.integers(0,len(delta),k)
        idx=np.concatenate([(s+np.arange(block))%len(delta) for s in starts])[:len(delta)]
        res.append(delta[idx].mean())
    return {'mean_difference_MWh':float(delta.mean()),'ci95_lower':float(np.quantile(res,.025)),'ci95_upper':float(np.quantile(res,.975)),'block_length':block,'replicates':n,'meaning':'GPR absolute error minus comparator absolute error; negative favours GPR'}

def main():
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    protocol_path=ROOT/'00_requirements/Experiment_Protocol.json';protocol=json.loads(protocol_path.read_text())
    write_json(EXP/'execution_start.json',{'protocol_sha256':hashlib.sha256(protocol_path.read_bytes()).hexdigest(),'python':sys.version,'platform':platform.platform(),'sklearn':sklearn.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'seed':42,'thread_limit':1,'start_utc':pd.Timestamp.now(tz='UTC').isoformat()})
    table=pd.read_csv(ROOT/'02_data/processed/modelling_table.csv',parse_dates=['date']).set_index('date')
    dev=table[table.split=='development'];test=table[table.split=='test']
    assert dev.index.max()<test.index.min()
    selected={};cv=[];foldrows=[]
    with threadpool_limits(limits=1):
        for name,configs in configurations().items():
            scores=[]
            for ci,cfg in enumerate(configs):
                foldmetrics=[]
                for fi,fold in enumerate(protocol['validation_folds'],1):
                    tr=dev.loc[:fold['train_end']];va=dev.loc[fold['validation_start']:fold['validation_end']]
                    assert tr.index.max()<va.index.min()
                    model=make_model(name,cfg);t=time.perf_counter()
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always');model.fit(tr[FEATURES],tr.target_MWh)
                    pred=model.predict(va[FEATURES]);m=metrics(va.target_MWh,pred);foldmetrics.append(m)
                    cv.append({'model':name,'config_id':ci,'config':json.dumps(cfg,sort_keys=True),'fold':fi,'n_train':len(tr),'n_validation':len(va),**m,'fit_seconds':time.perf_counter()-t,'warnings':' | '.join(str(w.message) for w in caught)})
                    foldrows.append({'model':name,'config_id':ci,'fold':fi,'train_end':str(tr.index.max().date()),'validation_start':str(va.index.min().date()),'validation_end':str(va.index.max().date()),'n_train':len(tr),'n_validation':len(va)})
                score=float(np.mean([m['MAE_MWh'] for m in foldmetrics]));scores.append(score)
                print(name,ci,cfg,'CV MAE',round(score,3),flush=True)
                pd.DataFrame(cv).to_csv(EXP/'cv_results.csv',index=False)
            best=int(np.argmin(scores));selected[name]={'config_id':best,'config':configs[best],'CV_MAE_MWh':scores[best]}
        # Baseline CV scores use exactly the same validation dates.
        for name,col in [('Persistence','lag1_MWh'),('Seasonal naive','lag7_MWh')]:
            vals=[]
            for fi,fold in enumerate(protocol['validation_folds'],1):
                va=dev.loc[fold['validation_start']:fold['validation_end']];m=metrics(va.target_MWh,va[col]);vals.append(m['MAE_MWh'])
                cv.append({'model':name,'config_id':0,'config':'{}','fold':fi,'n_train':0,'n_validation':len(va),**m,'fit_seconds':0.,'warnings':''})
            selected[name]={'config_id':0,'config':{},'CV_MAE_MWh':float(np.mean(vals))}
        pd.DataFrame(cv).to_csv(EXP/'cv_results.csv',index=False)
        pd.DataFrame(foldrows).drop_duplicates().to_csv(EXP/'cv_split_records.csv',index=False)
        # Persist choices BEFORE any heldout predictions or scores are computed.
        write_json(EXP/'selected_models_before_test.json',selected)
        predictions=pd.DataFrame({'actual_MWh':test.target_MWh},index=test.index);result=[];trained={}
        for name,details in selected.items():
            if name in ['Persistence','Seasonal naive']:
                pred=test['lag1_MWh' if name=='Persistence' else 'lag7_MWh'].to_numpy();fitsec=0.
            else:
                model=make_model(name,details['config']);t=time.perf_counter()
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always');model.fit(dev[FEATURES],dev.target_MWh)
                fitsec=time.perf_counter()-t;trained[name]=model
                details['final_fit_warnings']=[str(w.message) for w in caught]
                joblib.dump(model,OUT/(name.replace(' ','_')+'.joblib'))
                if name=='GPR':
                    pred,std=gpr_predict(model,test[FEATURES]);predictions['GPR_std_MWh']=std
                    details['fitted_kernel']=str(model[-1].kernel_)
                    details['log_marginal_likelihood']=float(model[-1].log_marginal_likelihood_value_)
                else:pred=model.predict(test[FEATURES])
            predictions[name]=pred;result.append({'model':name,**metrics(test.target_MWh,pred),'CV_MAE_MWh':details['CV_MAE_MWh'],'final_fit_seconds':fitsec})
        base_mae=next(m['MAE_MWh'] for m in result if m['model']=='Seasonal naive')
        for m in result:m['MAE_skill_vs_seasonal_naive']=1-m['MAE_MWh']/base_mae
        pd.DataFrame(result).to_csv(EXP/'test_metrics.csv',index=False)
        mu=predictions.GPR.to_numpy();sd=predictions.GPR_std_MWh.to_numpy();actual=predictions.actual_MWh.to_numpy()
        predictions['GPR_lower95_MWh']=mu-1.95996398454*sd;predictions['GPR_upper95_MWh']=mu+1.95996398454*sd
        predictions.to_csv(EXP/'test_predictions.csv',index_label='date')
        unc={'nominal_coverage':.95,'empirical_coverage':float(np.mean((actual>=predictions.GPR_lower95_MWh)&(actual<=predictions.GPR_upper95_MWh))),'mean_width_MWh':float(np.mean(2*1.95996398454*sd)),'mean_std_MWh':float(sd.mean()),'gaussian_NLPD':float(np.mean(.5*np.log(2*np.pi*sd**2)+.5*((actual-mu)/sd)**2)),'n_test':len(actual),'includes_white_kernel_observation_noise':True,'interval_recalibrated_on_test':False}
        write_json(EXP/'uncertainty.json',unc)
        # All sensitivity analyses were listed in the protocol; none reselect the model.
        diagnostics=[]
        for seed in [7,42,2026]:
            model=trained['Random forest'] if seed==42 else make_model('Random forest',selected['Random forest']['config'],seed=seed).fit(dev[FEATURES],dev.target_MWh)
            diagnostics.append({'kind':'RF_seed','setting':str(seed),**metrics(actual,model.predict(test[FEATURES]))})
        for multiplier in [.5,1.,2.]:
            model=trained['GPR'] if multiplier==1 else make_model('GPR',selected['GPR']['config'],length_multiplier=multiplier).fit(dev[FEATURES],dev.target_MWh)
            diagnostics.append({'kind':'GPR_initialization','setting':str(multiplier),**metrics(actual,model.predict(test[FEATURES])),'kernel':str(model[-1].kernel_)})
        for label,cols in [('GPR history only',FEATURES[:6]),('GPR calendar only',FEATURES[6:])]:
            model=make_model('GPR',selected['GPR']['config']).fit(dev[cols],dev.target_MWh)
            diagnostics.append({'kind':'retrained_ablation','setting':label,**metrics(actual,model.predict(test[cols])),'kernel':str(model[-1].kernel_)})
        pd.DataFrame(diagnostics).to_csv(EXP/'sensitivity_ablations.csv',index=False)
        comparators=['Seasonal naive',min(['Linear regression','Random forest','SVR'],key=lambda n:selected[n]['CV_MAE_MWh'])]
        paired=[]
        for name in comparators:
            for block in [7,14]:paired.append({'comparator':name,**bootstrap_difference(abs(actual-mu),abs(actual-predictions[name].to_numpy()),block=block)})
        write_json(EXP/'paired_block_bootstrap.json',paired)
        slices=[]
        for name,grp in [('month',predictions.index.strftime('%Y-%m')),('day_type',np.where(predictions.index.day_of_week>=5,'Weekend','Weekday'))]:
            for label in np.unique(grp):
                mask=grp==label
                for modelname in ['GPR','Seasonal naive',comparators[-1]]:
                    slices.append({'slice':name,'level':label,'model':modelname,'n':int(mask.sum()),**metrics(actual[mask],predictions.loc[mask,modelname])})
        pd.DataFrame(slices).to_csv(EXP/'error_slices.csv',index=False)
        worst=predictions.copy();worst['GPR_error_MWh']=mu-actual;worst['absolute_error_MWh']=abs(mu-actual)
        worst.sort_values('absolute_error_MWh',ascending=False).head(10).to_csv(EXP/'worst_errors.csv',index_label='date')
        residual=pd.Series(actual-mu,index=test.index)
        write_json(EXP/'residual_diagnostics.json',{'lag1_autocorrelation':float(residual.autocorr(1)),'lag7_autocorrelation':float(residual.autocorr(7)),'mean_signed_error_actual_minus_prediction_MWh':float(residual.mean())})
        write_json(EXP/'selected_models_final.json',selected)
        write_json(EXP/'execution_end.json',{'elapsed_seconds':time.perf_counter()-start,'end_utc':pd.Timestamp.now(tz='UTC').isoformat(),'n_development':len(dev),'n_test':len(test),'best_taught_comparator_by_CV':comparators[-1]})
        print(pd.DataFrame(result).to_string(index=False));print('UNCERTAINTY',unc);print('ELAPSED',time.perf_counter()-start,flush=True)

if __name__=='__main__':main()
