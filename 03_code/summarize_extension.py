"""Create tables and figures directly from recorded original and extension experiments."""
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from prepare_data import ROOT,write_json
D=ROOT/'05_experiments/extension'
a=pd.read_csv(ROOT/'05_experiments/test_metrics.csv').rename(columns={'MAE_MWh':'MAE','RMSE_MWh':'RMSE'})
b=pd.read_csv(D/'dispatch/test_metrics.csv');a=pd.concat([a,b[b.model!='Seasonal naive']],ignore_index=True)
r=pd.read_csv(D/'rainfall/test_metrics.csv')
records=lambda frame:json.loads(frame[['model','MAE','RMSE','R2']].to_json(orient='records',double_precision=12))
summary={'protocol':'Extension_Protocol.json','dispatch':{'unit':'MWh','n_test':97,'status':'Original six-model study preserved; NGBoost, KNN and gradient boosting are supplementary post-hoc comparisons.','metrics':records(a)},'rainfall':{'unit':'mm','n_test':72,'status':'Separate Colombo CHIRPS-v2 rainfall task; refitted models, six-dekad input delay and training embargo. Corrected retrospective 2024–2025 audit; holdout previously inspected during timing review.','metrics':records(r)},'findings':['GPR remains the main new algorithm; NGBoost is an additional probabilistic method absent from the supplied notes.','SVR has the lowest dispatch test MAE; random forest the lowest RMSE.','Rainfall seasonal median beats all learned models; do not select a deployment model by these already inspected test outcomes.']}
write_json(D/'summary.json',summary)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,2,figsize=(11.5,5.2),layout='constrained')
for ax,frame,scale,title,label in [(axs[0],a,1000,'Recorded electricity dispatch','Test MAE (GWh)'),(axs[1],r,1,'Colombo dekadal rainfall','Test MAE (mm)')]:
 frame=frame.sort_values('MAE',ascending=False)
 colors=['#087d79' if x=='GPR' else '#d39551' if x.startswith('Seasonal') or x=='Persistence' else '#9eb4bf' for x in frame.model]
 ax.barh(frame.model,frame.MAE/scale,color=colors,height=.65);ax.set_title(title,fontweight='bold',loc='left',pad=14);ax.set_xlabel(label);ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True);ax.set_xlim(0,(frame.MAE/scale).max()*1.22)
 for i,v in enumerate(frame.MAE/scale):ax.text(v+.015*(frame.MAE/scale).max(),i,f'{v:.3f}' if scale==1000 else f'{v:.2f}',va='center',fontsize=9)
fig.savefig(ROOT/'06_figures/10_extended_model_comparison.png',dpi=180,facecolor='white');plt.close(fig)
pred=pd.read_csv(D/'rainfall/test_predictions.csv',parse_dates=['date']).set_index('date')
fig,ax=plt.subplots(figsize=(10.8,3.8),layout='constrained');ax.plot(pred.index,pred.actual,label='Recorded final rainfall',color='#153746',lw=1.5);ax.plot(pred.index,pred.GPR,label='GPR',color='#087d79',lw=1.2);ax.plot(pred.index,pred['Seasonal median'],label='Training-only seasonal median',color='#d39551',lw=1.2);ax.set_ylabel('Dekadal rainfall (mm)');ax.legend(ncol=3,frameon=False,loc='upper left',fontsize=9);ax.set_title('Independent rainfall holdout: seasonal structure beats novelty',loc='left',fontweight='bold');ax.grid(alpha=.15);fig.savefig(ROOT/'06_figures/11_rainfall_holdout.png',dpi=180,facecolor='white');plt.close(fig)
# Paired circular moving-block sensitivity; fixed predictions, no refitting or selection.
rng=np.random.default_rng(269182);rows=[]
for name in ['GPR','NGBoost','SVR']:
 delta=np.abs(pred[name]-pred.actual)-np.abs(pred['Seasonal median']-pred.actual)
 for block in [3,6]:
  means=[]
  for _ in range(2000):
   starts=rng.integers(0,len(delta),size=int(np.ceil(len(delta)/block)));ix=((starts[:,None]+np.arange(block))%len(delta)).ravel()[:len(delta)];means.append(float(delta.iloc[ix].mean()))
  low,high=np.quantile(means,[.025,.975]);rows.append({'model_minus':'Seasonal median','model':name,'block_dekads':block,'difference_MAE_mm':float(delta.mean()),'CI_lower':float(low),'CI_upper':float(high),'bootstrap_replicates':2000})
pd.DataFrame(rows).to_csv(D/'rainfall/paired_bootstrap.csv',index=False)
print(json.dumps({'dispatch_models':len(a),'rainfall_models':len(r),'figures':2,'bootstrap':rows},indent=2))
