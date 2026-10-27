"""Retrieve the pinned release and reconstruct local-day dispatch energy."""
from pathlib import Path
import hashlib,json,urllib.request,zipfile
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'02_data/raw'; DATA=ROOT/'02_data/processed'; EXP=ROOT/'05_experiments'
FEATURES=['lag1_MWh','lag2_MWh','lag7_MWh','lag14_MWh','rolling7_mean_MWh','rolling7_std_MWh','dow_sin','dow_cos','year_sin','year_cos','trend_days']
GROUPS={'Demand history':FEATURES[:6], 'Weekly calendar':FEATURES[6:8], 'Annual cycle / trend':FEATURES[8:]}
URL='https://zenodo.org/api/records/17175212/files/data.zip/content'
MD5='22921011c0fdabea0df5f926f3372a9e'

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,default=str,allow_nan=False))

def acquire():
    RAW.mkdir(parents=True,exist_ok=True)
    archive=RAW/'sasea_v1_data.zip'
    required=['raw_LKA_demand.csv','raw_LKA_demand.yml','daily_agg_LKA_demand.csv','daily_agg_LKA_demand.yml']
    raw_verified=all((RAW/f).exists() for f in required) and hashlib.sha256((RAW/'raw_LKA_demand.csv').read_bytes()).hexdigest()=='7dc4665e317d3fa718cea7845587cc97b7a5c13de110a5bddbd57c524f2b5a97'
    if not raw_verified and not archive.exists(): urllib.request.urlretrieve(URL,archive)
    if archive.exists():
      assert hashlib.md5(archive.read_bytes()).hexdigest()==MD5, 'Archive checksum mismatch'
    if not raw_verified:
     with zipfile.ZipFile(archive) as z:
        for member in ['data/raw/raw_LKA_demand.csv','data/raw/raw_LKA_demand.yml','data/daily_aggregates/daily_agg_LKA_demand.csv','data/daily_aggregates/daily_agg_LKA_demand.yml']:
            target=RAW/Path(member).name
            if not target.exists():target.write_bytes(z.read(member))
    write_json(RAW/'provenance.json',{'dataset_title':'SASEA Electricity Demand Data for 2013-2025','creators':['Oliver G. Coombes','Kieran Hunt','Hannah Bloomfield'],'doi':'10.5281/zenodo.17175212','version':'v1','licence':'CC-BY-4.0','url':URL,'retrieved_local_date':'2026-10-28','original_source':'PUCSL actual system dispatch API, retrieved by dataset authors; not a fresh API collection by the student','archive_md5':MD5,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest() if archive.exists() else None,'raw_lka_sha256':hashlib.sha256((RAW/'raw_LKA_demand.csv').read_bytes()).hexdigest()})

def add_calendar(df):
    df=df.copy();dt=pd.DatetimeIndex(df.index)
    df['dow_sin']=np.sin(2*np.pi*dt.day_of_week/7)
    df['dow_cos']=np.cos(2*np.pi*dt.day_of_week/7)
    # Fixed mean tropical-year denominator avoids using future learned information.
    df['year_sin']=np.sin(2*np.pi*(dt.day_of_year-1)/365.2425)
    df['year_cos']=np.cos(2*np.pi*(dt.day_of_year-1)/365.2425)
    df['trend_days']=(dt-pd.Timestamp('2023-01-01')).days
    return df

def prepare():
    DATA.mkdir(parents=True,exist_ok=True);EXP.mkdir(parents=True,exist_ok=True)
    acquire();d=pd.read_csv(RAW/'raw_LKA_demand.csv')
    d['local_time']=pd.to_datetime(d.timestamp,utc=True).dt.tz_convert('Asia/Colombo')
    keys=['local_time','powerPlantId']; dup=d.duplicated(keys)
    repeated=d[d.duplicated(keys,keep=False)]
    conflicts=int((repeated.groupby(keys).dispatchValueInMW.nunique(dropna=False)>1).sum())
    if conflicts:raise ValueError('Conflicting dispatch duplicates require manual adjudication')
    x=d.drop_duplicates(keys,keep='first').copy()
    interval=x.groupby('local_time').agg(MW=('dispatchValueInMW',lambda s:s.sum(min_count=1)), n_plants=('powerPlantId','nunique'),missing_values=('dispatchValueInMW',lambda s:s.isna().sum()),negative_clipping_MW=('dispatchValueInMW',lambda s:-s[s<0].sum()))
    interval['date']=interval.index.tz_localize(None).normalize()
    daily=interval.groupby('date').agg(n_intervals=('MW','size'),observed_MWh=('MW',lambda s:s.sum(min_count=1)*.25),missing_plant_values=('missing_values','sum'),n_plants_min=('n_plants','min'),n_plants_max=('n_plants','max'),zero_system_intervals=('MW',lambda s:int((s==0).sum())),negative_clipping_MWh=('negative_clipping_MW',lambda s:s.sum()*.25))
    calendar=pd.date_range(daily.index.min(),daily.index.max(),freq='D',name='date')
    daily=daily.reindex(calendar)
    pub=pd.read_csv(RAW/'daily_agg_LKA_demand.csv',parse_dates=['date']).set_index('date')
    daily=daily.join(pub.rename(columns={'demand_MWh':'published_daily_MWh'}))
    daily['published_ratio']=daily.published_daily_MWh/daily.observed_MWh
    daily['valid_target']=(daily.n_intervals==96)&(daily.missing_plant_values==0)
    daily['target_MWh']=daily.observed_MWh.where(daily.valid_target)
    # Do not interpolate target values, and do not shift over missing dates.
    daily.to_csv(DATA/'daily_energy_quality.csv',index_label='date')
    y=daily.target_MWh;f=pd.DataFrame(index=daily.index)
    for lag in [1,2,7,14]:f[f'lag{lag}_MWh']=y.shift(lag)
    f['rolling7_mean_MWh']=y.shift(1).rolling(7,min_periods=7).mean()
    f['rolling7_std_MWh']=y.shift(1).rolling(7,min_periods=7).std(ddof=0)
    f=add_calendar(f);f['target_MWh']=y
    f['split']=np.where(f.index<'2025-01-01','development','test')
    keep=f[FEATURES+['target_MWh']].notna().all(axis=1)
    f[keep].to_csv(DATA/'modelling_table.csv',index_label='date')
    f.assign(eligible=keep).to_csv(DATA/'feature_eligibility.csv',index_label='date')
    facts={'raw_rows':len(d),'duplicate_key_rows_removed':int(dup.sum()),'conflicting_duplicate_keys':conflicts,'raw_missing_values':int(d.dispatchValueInMW.isna().sum()),'deduplicated_missing_values':int(x.dispatchValueInMW.isna().sum()),'raw_negative_values':int((d.dispatchValueInMW<0).sum()),'deduplicated_negative_values':int((x.dispatchValueInMW<0).sum()),'plants_ever_present':int(x.powerPlantId.nunique()),'timestamps':len(interval),'calendar_days':len(daily),'raw_first_local_timestamp':str(d.local_time.min()),'raw_last_local_timestamp':str(d.local_time.max()),'partial_days':daily.index[daily.n_intervals!=96].strftime('%Y-%m-%d').tolist(),'days_with_explicit_nulls':int((daily.missing_plant_values>0).sum()),'valid_target_days':int(daily.valid_target.sum()),'eligible_rows':int(keep.sum()),'development_rows':int((keep&(f.split=='development')).sum()),'test_rows':int((keep&(f.split=='test')).sum()),'published_ratio_median':float(daily.published_ratio.median()),'published_ratio_min':float(daily.published_ratio.min()),'published_ratio_max':float(daily.published_ratio.max()),'zero_system_intervals':int(daily.zero_system_intervals.sum()),'negative_clip_max_daily_difference_MWh':float(daily.negative_clipping_MWh.max()),'negative_clip_total_difference_MWh':float(daily.negative_clipping_MWh.sum()),'reconstructed_2024_GWh':float(daily.loc['2024','observed_MWh'].sum()/1000),'daily_mean_2024_GWh':float(daily.loc['2024','observed_MWh'].mean()/1000),'unit_corroboration_2024_12_24_MWh':float(daily.loc['2024-12-24','observed_MWh']),'source_files':{'raw_sha256':hashlib.sha256((RAW/'raw_LKA_demand.csv').read_bytes()).hexdigest(),'processed_sha256':hashlib.sha256((DATA/'modelling_table.csv').read_bytes()).hexdigest()}}
    raw_daily=d.groupby(d.local_time.dt.tz_localize(None).dt.normalize()).dispatchValueInMW.sum()
    facts['published_vs_unconverted_undeduplicated_MW_sum_max_abs_difference']=float((pub.demand_MWh-raw_daily).abs().max())
    write_json(EXP/'data_audit.json',facts)
    print(json.dumps(facts,indent=2),flush=True)
    return f[keep]

if __name__=='__main__':prepare()
