"""Build a minimal Linux deployment from explicit, credential-free input files."""
from pathlib import Path
import zipfile,hashlib,json
from prepare_data import ROOT,write_json
mapping={f'10_deployment/{name}':name for name in ['wsgi.py','startup.sh','requirements.txt']}
for name in ['app.py','app.html','models.py','prepare_data.py']:mapping['03_code/'+name]='03_code/'+name
for name in ['models/GPR.joblib','explanation_reference.json','test_metrics.csv','uncertainty.json','grouped_permutation_summary.csv','extension/summary.json']:mapping['05_experiments/'+name]='05_experiments/'+name
mapping['02_data/processed/modelling_table.csv']='02_data/processed/modelling_table.csv'
entries=[];target=ROOT/'10_deployment/deployment.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for src,dest in mapping.items():
  p=ROOT/src;data=p.read_bytes();z.writestr(dest,data);entries.append({'source':src,'deployed_path':dest,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
with zipfile.ZipFile(target) as z:assert z.testzip() is None
write_json(ROOT/'10_deployment/bundle_manifest.json',{'files':entries,'zip_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'zip_bytes':target.stat().st_size,'excluded':['raw datasets','lecture materials','account state','credentials','notebooks','authoring packages','unrelated models']})
print(json.dumps({'files':len(entries),'bytes':target.stat().st_size},indent=2))
