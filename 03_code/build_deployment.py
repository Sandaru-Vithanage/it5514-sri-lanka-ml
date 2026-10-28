"""Build the explicit inference bundle; CI embeds its immutable source commit."""
from pathlib import Path
import argparse,hashlib,json,os,re,zipfile
from prepare_data import ROOT,write_json

MAPPING={f'10_deployment/{n}':n for n in ['wsgi.py','startup.sh','requirements.txt']}
for n in ['app.py','app.html','models.py','prepare_data.py']:MAPPING['03_code/'+n]='03_code/'+n
for n in ['models/GPR.joblib','explanation_reference.json','test_metrics.csv','uncertainty.json','grouped_permutation_summary.csv','extension/summary.json']:MAPPING['05_experiments/'+n]='05_experiments/'+n
MAPPING['02_data/processed/modelling_table.csv']='02_data/processed/modelling_table.csv'

def build(commit):
    if commit!='local-working-tree' and not re.fullmatch(r'[0-9a-f]{40}',commit):
        raise ValueError('Release commit must be a full Git SHA or local-working-tree.')
    model_hash=hashlib.sha256((ROOT/'05_experiments/models/GPR.joblib').read_bytes()).hexdigest()
    release={'commit':commit,'model_sha256':model_hash,'repository':'https://github.com/Sandaru-Vithanage/it5514-sri-lanka-ml','deployment':'GitHub Actions; frozen model, no automatic retraining'}
    contents={dest:(ROOT/src).read_bytes() for src,dest in MAPPING.items()}
    contents['release.json']=(json.dumps(release,indent=2)+'\n').encode()
    target=ROOT/'10_deployment/deployment.zip';entries=[]
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for dest,data in sorted(contents.items()):
            info=zipfile.ZipInfo(dest,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data)
            entries.append({'source':next((src for src,dst in MAPPING.items() if dst==dest),'generated release metadata'),'deployed_path':dest,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    manifest={'release_commit':commit,'files':entries,'zip_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'zip_bytes':target.stat().st_size,'excluded':['raw datasets','lecture materials','account state','credentials','notebooks','authoring packages','unrelated models']}
    write_json(ROOT/'10_deployment/bundle_manifest.json',manifest)
    print(json.dumps({'files':len(entries),'bytes':target.stat().st_size,'commit':commit},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--commit',default=os.environ.get('GITHUB_SHA','local-working-tree'))
    build(parser.parse_args().commit)
