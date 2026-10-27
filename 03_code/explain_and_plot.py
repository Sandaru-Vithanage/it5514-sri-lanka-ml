"""Heldout model inspection and figures; no model selection occurs here."""
import os
os.environ['MPLCONFIGDIR']=str(__import__('pathlib').Path(__file__).resolve().parents[1]/'work/matplotlib')
from pathlib import Path
import json
import numpy as np,pandas as pd,joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.metrics import mean_absolute_error
from threadpoolctl import threadpool_limits
from prepare_data import ROOT,FEATURES,GROUPS,write_json
from models import gpr_predict

EXP=ROOT/'05_experiments';FIG=ROOT/'06_figures'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':190,'axes.titleweight':'bold','axes.labelcolor':'#26394b','text.color':'#203345','axes.prop_cycle':matplotlib.cycler(color=['#007f84','#e6a343','#597796','#b75b50','#9375a0'])})

def save(name):
    for axis in plt.gcf().axes:
        if isinstance(axis.xaxis.get_major_locator(), mdates.AutoDateLocator):
            locator=mdates.AutoDateLocator(minticks=3,maxticks=5)
            axis.xaxis.set_major_locator(locator);axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    plt.savefig(FIG/(name+'.png'),bbox_inches='tight',facecolor='white');plt.close()

def representative_row(dev,model):
    z=model[0].transform(dev[FEATURES]);mid=np.median(z,axis=0)
    return dev.iloc[int(np.argmin(np.sum((z-mid)**2,axis=1)))][FEATURES]

def local_replacements(model,row,reference):
    frame=pd.DataFrame([row],columns=FEATURES);base=float(model.predict(frame)[0]);values=[]
    for group,cols in GROUPS.items():
        changed=frame.copy();changed.loc[:,cols]=reference[cols].to_numpy()
        replacement=float(model.predict(changed)[0]);values.append({'group':group,'prediction_MWh':base,'replacement_prediction_MWh':replacement,'difference_MWh':base-replacement})
    return values

def main():
    FIG.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(ROOT/'02_data/processed/modelling_table.csv',parse_dates=['date']).set_index('date');dev=df[df.split=='development'];test=df[df.split=='test']
    p=pd.read_csv(EXP/'test_predictions.csv',parse_dates=['date']).set_index('date');model=joblib.load(EXP/'models/GPR.joblib')
    metrics=pd.read_csv(EXP/'test_metrics.csv');unc=json.loads((EXP/'uncertainty.json').read_text())
    rng=np.random.default_rng(42);X=test[FEATURES];y=test.target_MWh;base=mean_absolute_error(y,model.predict(X));rows=[]
    with threadpool_limits(limits=1):
        for group,cols in GROUPS.items():
            for r in range(20):
                blocks=[np.arange(s,min(s+7,len(X))) for s in range(0,len(X),7)]
                order=rng.permutation(len(blocks));idx=np.concatenate([blocks[i] for i in order]);idx=np.roll(idx,int(rng.integers(0,7)))
                changed=X.copy();changed.loc[:,cols]=X.iloc[idx][cols].to_numpy()
                rows.append({'group':group,'repeat':r,'MAE_increase_MWh':float(mean_absolute_error(y,model.predict(changed))-base)})
        imp=pd.DataFrame(rows);imp.to_csv(EXP/'grouped_permutation_repeats.csv',index=False)
        summary=imp.groupby('group').MAE_increase_MWh.agg(['mean','std','min','max']).sort_values('mean',ascending=False)
        summary.to_csv(EXP/'grouped_permutation_summary.csv')
        ref=representative_row(dev,model);write_json(EXP/'explanation_reference.json',{'date':str(ref.name.date()),'features':ref.to_dict(),'method':'Actual development row nearest to standardized coordinate-wise median; one shared reference for demo and local sensitivity plots'})
        local=[]
        # Fixed demonstration date and largest-error case; no changes to the model.
        cases=[pd.Timestamp('2025-01-15'),(p.actual_MWh-p.GPR).abs().idxmax()]
        for date in cases:
            for item in local_replacements(model,test.loc[date,FEATURES],ref):local.append({'date':str(date.date()),**item})
        pd.DataFrame(local).to_csv(EXP/'local_group_replacements.csv',index=False)
        pdp=[]
        refsample=dev[FEATURES].iloc[::5].copy()
        for feature in ['lag1_MWh','lag7_MWh']:
            for value in np.linspace(dev[feature].quantile(.05),dev[feature].quantile(.95),25):
                z=refsample.copy();z[feature]=value
                pdp.append({'feature':feature,'grid_MWh':float(value),'mean_prediction_MWh':float(model.predict(z).mean()),'n_reference':len(z)})
        pd.DataFrame(pdp).to_csv(EXP/'partial_dependence_data.csv',index=False)
    # EDA and quality: preserve raw and audit values, label every unit explicitly.
    quality=pd.read_csv(ROOT/'02_data/processed/daily_energy_quality.csv',parse_dates=['date']).set_index('date')
    fig,ax=plt.subplots(2,1,figsize=(10,6),layout='constrained')
    ax[0].plot(quality.index,quality.observed_MWh/1000,lw=.8,label='Reconstructed dispatch');ax[0].axvspan(pd.Timestamp('2025-01-01'),pd.Timestamp('2025-04-07'),alpha=.1,color='#e6a343',label='Heldout test');ax[0].set(ylabel='Recorded energy (GWh/day)',title='Sri Lankan recorded dispatch: local calendar days');ax[0].legend(loc='lower left',ncol=2,fontsize=8)
    ax[1].plot(quality.index,quality.published_ratio,lw=.8,color='#b75b50');ax[1].axhline(4,color='#33485a',ls='--',lw=.8);ax[1].set(ylabel='Published / reconstructed',title='Published daily CSV is inconsistent with the raw MW integration');save('01_data_audit')
    fig,ax=plt.subplots(figsize=(9,3.5),layout='constrained')
    vals=[dev.loc[dev.index.day_of_week==i,'target_MWh']/1000 for i in range(7)]
    ax.boxplot(vals,tick_labels=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],patch_artist=True,boxprops={'facecolor':'#cbe6e4'},medianprops={'color':'#007f84'});ax.set(ylabel='Recorded energy (GWh/day)',title='Development data: weekly structure');save('02_weekly_structure')
    fig,ax=plt.subplots(figsize=(9,3.6),layout='constrained')
    m=metrics.sort_values('MAE_MWh');ax.barh(m.model,m.MAE_MWh/1000,color=['#007f84' if n=='GPR' else '#a9bdc7' for n in m.model]);ax.invert_yaxis();ax.set(xlabel='Heldout mean absolute error (GWh)',title='Frozen model comparison, 97 test days');save('03_model_comparison')
    fig,ax=plt.subplots(figsize=(10,4),layout='constrained')
    ax.fill_between(p.index,p.GPR_lower95_MWh/1000,p.GPR_upper95_MWh/1000,alpha=.2,color='#007f84',label='Nominal 95% observation interval');ax.plot(p.index,p.actual_MWh/1000,color='#243c50',lw=1.4,label='Observed');ax.plot(p.index,p.GPR/1000,color='#007f84',lw=1.1,label='GPR');ax.set(ylabel='Recorded energy (GWh/day)',title='One-day-ahead historical replay; parameters frozen at 31 December 2024');ax.legend(ncol=3,loc='lower left',fontsize=8);save('04_test_forecast')
    fig,ax=plt.subplots(1,2,figsize=(9,3.8),layout='constrained')
    ax[0].scatter(p.actual_MWh/1000,p.GPR/1000,s=18,alpha=.75);limits=[min(p.actual_MWh.min(),p.GPR.min())/1000-1,max(p.actual_MWh.max(),p.GPR.max())/1000+1];ax[0].plot(limits,limits,'--',color='#a3b1bb');ax[0].set(xlabel='Observed (GWh)',ylabel='Predicted (GWh)',title='Agreement and extreme misses')
    residual=(p.actual_MWh-p.GPR)/1000;ax[1].plot(p.index,residual,marker='.',ms=3,lw=.6);ax[1].axhline(0,color='#a3b1bb');ax[1].set(ylabel='Observed - predicted (GWh)',title='Errors remain on unusual days');save('05_error_analysis')
    fig,ax=plt.subplots(figsize=(9,3.2),layout='constrained');s=summary.sort_values('mean');ax.barh(s.index,s['mean']/1000,xerr=s['std']/1000,color='#007f84',capsize=4);ax.set(xlabel='Increase in test MAE after grouped shuffle (GWh)',title='Grouped permutation importance (mean +/- SD; 20 block shuffles)');save('06_grouped_importance')
    fig,ax=plt.subplots(1,2,figsize=(9,3.6),layout='constrained');pddata=pd.DataFrame(pdp)
    for a,feature in zip(ax,['lag1_MWh','lag7_MWh']):
        s=pddata[pddata.feature==feature];a.plot(s.grid_MWh/1000,s.mean_prediction_MWh/1000);a.set(xlabel=feature.replace('_MWh','')+' (GWh)',ylabel='Average model output (GWh)',title='PDP: '+feature.replace('_MWh',''));a.plot(dev[feature].iloc[::10]/1000,np.repeat(s.mean_prediction_MWh.min()/1000-.3,len(dev.iloc[::10])),'|',alpha=.25,color='#647d8c')
    save('07_partial_dependence')
    fig,ax=plt.subplots(1,2,figsize=(9,3.3),layout='constrained')
    for a,date in zip(ax,cases):
        ss=pd.DataFrame(local);ss=ss[ss.date==str(date.date())];a.barh(ss.group,ss.difference_MWh/1000,color=['#007f84' if v>=0 else '#b75b50' for v in ss.difference_MWh]);a.axvline(0,color='#8095a0');a.set(xlabel='Original - group-replaced output (GWh)',title=str(date.date()))
    save('08_local_sensitivity')
    ab=pd.read_csv(EXP/'sensitivity_ablations.csv');a=ab[ab.kind=='retrained_ablation'];labels=['GPR full']+a.setting.tolist();maes=[float(metrics[metrics.model=='GPR'].MAE_MWh.iloc[0])]+a.MAE_MWh.tolist()
    fig,ax=plt.subplots(figsize=(8,3),layout='constrained');ax.barh(labels,np.array(maes)/1000,color=['#007f84','#a9bdc7','#e6a343']);ax.invert_yaxis();ax.set(xlabel='Test MAE (GWh)',title='Retrained ablations with the selected kernel family; no retuning');save('09_ablations')
    print(summary.to_string());print('FIGURES',len(list(FIG.glob('*.png'))),flush=True)

if __name__=='__main__':main()
