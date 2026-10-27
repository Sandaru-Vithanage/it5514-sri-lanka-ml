"""Obtain the public rainfall snapshot; fail closed if the rolling upstream changes."""
from pathlib import Path
import hashlib,urllib.request,json
from prepare_data import ROOT
URL='https://data.humdata.org/dataset/4302257e-5fa6-4c88-b8f7-f78730d8c48b/resource/afc6a8ca-dc55-4eb4-baf0-4afaa2c6673e/download/lka-rainfall-subnat-full.csv'
SHA='0cbede43ed79c8ac198e64592bd4a2d04da647b06853e9ca7083e3725f0716b5'
p=ROOT/'02_data/rainfall/raw/lka-rainfall-subnat-full.csv'
if p.exists():
 assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA,'Local snapshot changed; restore the pinned repository/source ZIP copy.'
 print('Pinned rainfall snapshot already present and verified.')
else:
 data=urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'IT5514 academic reproducibility'}),timeout=120).read()
 digest=hashlib.sha256(data).hexdigest()
 if digest!=SHA:raise RuntimeError('HDX is a rolling resource and its contents changed. Use the pinned snapshot in the repository/source ZIP; do not silently replace it. Received SHA-256 '+digest)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);print('Downloaded and verified',len(data),'bytes.')
