"""Recalculate interval evidence with scipy's independent Normal log-density."""
import json
import numpy as np,pandas as pd
from scipy.stats import norm
from prepare_data import ROOT,write_json
checks=[]
for study in ['dispatch','rainfall']:
 d=ROOT/'05_experiments/extension'/study;p=pd.read_csv(d/'test_predictions.csv')
 for row in json.loads((d/'probabilistic_metrics.json').read_text()):
  name=row['model'];mu=p[name];sd=p[name+'_std'];low=p[name+'_lower95'];high=p[name+'_upper95']
  assert np.isclose(((p.actual>=low)&(p.actual<=high)).mean(),row['coverage95']);checks.append(study+' '+name+' coverage')
  assert np.isclose((high-low).mean(),row['mean_width']) and np.isclose(-norm.logpdf(p.actual,loc=mu,scale=sd).mean(),row['gaussian_NLPD']);checks.append(study+' '+name+' width and NLPD')
  assert int((mu<0).sum())==row['negative_means'] and int((low<0).sum())==row['negative_lower95'];checks.append(study+' '+name+' support violations')
write_json(ROOT/'05_experiments/extension/probabilistic_verification.json',{'passed':True,'checks':checks,'check_count':len(checks)})
print({'passed':True,'probabilistic_checks':len(checks)})
