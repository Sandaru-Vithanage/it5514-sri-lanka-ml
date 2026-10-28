"""Narrated walkthrough using genuine interface captures; not a live recording."""
from pathlib import Path
import json,subprocess,wave,math,textwrap
import numpy as np
import imageio.v2 as imageio
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from prepare_data import ROOT
import matplotlib

D=ROOT/'08_demo';WORK=ROOT/'work/video';WORK.mkdir(parents=True,exist_ok=True)
FONT=Path(matplotlib.get_data_path())/'fonts/ttf'
F=lambda size,bold=False:ImageFont.truetype(str(FONT/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
ff=imageio_ffmpeg.get_ffmpeg_exe();W,H=1600,1000;fps=8
SCENES=[{'title': 'A Sri Lankan forecasting study', 'tag': '01 / SOURCE & TASK', 'shot': '11_hosted_method.png', 'start_y': 0, 'end_y': 500, 'points': ['Public PUCSL dispatch records', 'Raw-data quality audit', 'One local day ahead'], 'text': 'This is the Applied Machine Learning study prepared for Sandaru Rashmika, index number two six nine one eight two L. Lanka Dispatch forecasts next day recorded electricity dispatch energy in Sri Lanka. The source is a versioned public compilation of PUCSL records. We rebuilt daily energy after finding duplicate plant timestamps and a missing quarter hour conversion in the published daily file. The main unfamiliar algorithm is Gaussian Process Regression. This is historical research, with no live grid connection.'}, {'title': 'Replay a case on Azure', 'tag': '02 / HOSTED MODEL INFERENCE', 'shot': '07_hosted_replay.png', 'start_y': 0, 'end_y': 170, 'points': ['15 January 2025', 'Estimate: 42.33 GWh', 'Real saved Python model'], 'text': 'The working interface is deployed to Azure. Select fifteen January twenty twenty five and load recorded inputs. Six history values describe demand lags, the previous week mean, and variability. The date supplies calendar features. The original trained Gaussian process predicts forty two point three three gigawatt hours, with a nominal ninety five percent observation interval from thirty seven point four three to forty seven point two three. The historical actual is displayed separately. The browser calls real Python inference from the saved model.', 'crop_x': 224}, {'title': 'Change history and inspect sensitivity', 'tag': '03 / INTERACTIVE SCENARIO', 'shot': '08_hosted_edited.png', 'start_y': 0, 'end_y': 170, 'points': ['Previous day → 42 GWh', 'Estimate → 44.22 GWh', 'Actual outcome unchanged'], 'text': 'Change only previous day energy to forty two gigawatt hours and generate another forecast. The estimate becomes forty four point two two. Hypothetical inputs are clearly labelled and the historical actual stays fixed. Group replacement bars show separate changes against a representative training day. They are reference dependent sensitivity checks, not additive contributions or causal explanations. The wider study also includes grouped block permutation, partial dependence and retrained feature ablations.', 'crop_x': 224}, {'title': 'Reject invalid values', 'tag': '04 / INPUT VALIDATION', 'shot': '09_hosted_invalid.png', 'start_y': 0, 'end_y': 170, 'points': ['Negative input rejected', 'Last valid estimate labelled', 'Backend also validates'], 'text': 'A negative input produces an error, and the panel is labelled last valid estimate. Backend checks independently reject negative, non finite and oversized requests. Scenarios outside the evaluated date range receive warnings. These checks also passed against the actual hosted HTTPS service.', 'crop_x': 224}, {'title': 'Interpret the original comparison', 'tag': '05 / EVALUATION & XAI', 'shot': '10_hosted_evaluation.png', 'start_y': 0, 'end_y': 170, 'points': ['GPR MAE: 1.599 GWh', '29.7% vs weekly naïve', '92.8% interval coverage'], 'text': 'Three chronological validation windows selected settings before the original ninety seven day test. GPR has mean absolute error one point five nine nine gigawatt hours, twenty nine point seven percent below weekly naive. It does not dominate: SVR has the lowest test mean absolute error and random forest the lowest root mean squared error. Grouped importance indicates strongest reliance on demand history and weekly calendar. Nominal ninety five percent intervals cover ninety two point eight percent, so uncertainty estimates still need critical interpretation.', 'crop_x': 224}, {'title': 'Test broader algorithms and data', 'tag': '06 / EXTENDED EVIDENCE', 'shot': '13_hosted_extension.png', 'start_y': 0, 'end_y': 550, 'points': ['Seven learned algorithms', 'Two Sri Lankan tasks', 'Seasonal rainfall baseline wins'], 'text': 'The extension adds NGBoost, K nearest neighbours and gradient boosting, giving seven learned algorithms on two Sri Lankan tasks. Added electricity comparisons are explicitly post hoc because the original test was already seen. The separate Colombo rainfall audit uses CHIRPS records, delayed inputs and a training embargo for publication timing. Review corrected a preliminary timing issue; that history is preserved. The seasonal median wins with mean absolute error forty one point three nine millimetres, ahead of SVR and GPR. Novelty does not guarantee better accuracy.', 'crop_x': 224}, {'title': 'Inspect deployment and source', 'tag': '07 / AZURE & PUBLIC REPOSITORY', 'shot': '13_hosted_extension.png', 'start_y': 0, 'end_y': 0, 'points': ['Azure Linux · Free F1', 'Public GitHub source', 'Matching model fingerprint'], 'text': 'The deployment panel shows the actual Azure address, public GitHub repository, source commit and model fingerprint. Anyone can inspect the code. Azure App Service uses Python three point thirteen and the free F one plan. Predictions match local inference within one millionth of a megawatt hour. The approved ten dollar credit cap is a maximum. Free tier quotas and cold starts limit availability.', 'crop_x': 224, 'crop_y': 1100}, {'title': 'Deploy automatically after validation', 'tag': '08 / GITHUB ACTIONS', 'shot': '14_actions_success.png', 'start_y': 160, 'end_y': 350, 'points': ['Push app/model changes to main', 'Validate → deploy → verify', 'Frozen model is not retrained'], 'text': 'This successful GitHub Actions run rebuilds the interface and validates the saved model before deployment. App or model changes pushed to main rebuild the explicit bundle, check all ninety seven saved predictions, deploy to Azure, and verify nine HTTPS checks. Pull requests validate only. Short lived federated credentials access this app. Deployment does not retrain the model.'}, {'title': 'Keep failure and limitations visible', 'tag': '09 / CRITICAL REVIEW', 'shot': '12_hosted_exceptional_day.png', 'start_y': 0, 'end_y': 170, 'points': ['Independence Day: large miss', 'Holiday signal omitted', 'Fresh evaluation for redesign'], 'text': 'Four February, Independence Day, is a large failure: the model forecasts about forty four point three seven gigawatt hours against recorded energy thirty three point seven three. Holiday indicators were omitted from the frozen predictors; future redesign needs fresh evaluation. Dispatch coverage and publication timing also constrain interpretation. The package includes reproducible code, pinned data, both notebooks, experiments, report and deployment evidence. This walkthrough uses genuine hosted interface captures, edited panning and synthesized narration. Student review and accurate assistance disclosure remain essential.', 'crop_x': 224}]

def lines(text,font,width):
    words=text.split();out=[];line=''
    for word in words:
        trial=(line+' '+word).strip()
        if font.getlength(trial)>width and line:out.append(line);line=word
        else:line=trial
    if line:out.append(line)
    return out

def stamp(t):
    n=int(round(t*1000));hh,n=divmod(n,3600000);mm,n=divmod(n,60000);ss,ms=divmod(n,1000);return f'{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}'

def main():
    audio=[];timings=[];captions=[];cursor=0.;caption_id=1
    for i,scene in enumerate(SCENES,1):
        txt=WORK/f'scene_{i}.txt';txt.write_text(scene['text'])
        aiff=WORK/f'scene_{i}.aiff';wav=WORK/f'scene_{i}.wav'
        subprocess.run(['/usr/bin/say','-v','Samantha','-r','162','-f',str(txt),'-o',str(aiff)],check=True)
        subprocess.run([ff,'-y','-i',str(aiff),'-ar','22050','-ac','1','-c:a','pcm_s16le',str(wav)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        with wave.open(str(wav),'rb') as r:data=r.readframes(r.getnframes());seconds=r.getnframes()/r.getframerate()
        duration=math.ceil((seconds+1.5)*fps)/fps;pad=int(round(duration*22050))-len(data)//2
        audio.append(data+b'\0\0'*pad);timings.append({'scene':i,'start_seconds':cursor,'duration_seconds':duration,'audio_seconds':seconds,'capture':scene['shot'],'narration':scene['text']})
        chunks=textwrap.wrap(scene['text'],width=105);chunkdur=seconds/len(chunks)
        for j,chunk in enumerate(chunks):captions.append({'id':caption_id,'start':cursor+j*chunkdur,'end':cursor+(j+1)*chunkdur,'text':chunk});caption_id+=1
        cursor+=duration
    soundtrack=WORK/'narration.wav'
    with wave.open(str(soundtrack),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(b''.join(audio))
    silent=WORK/'silent.mp4';writer=imageio.get_writer(str(silent),fps=fps,codec='libx264',quality=7,macro_block_size=8,ffmpeg_log_level='error')
    for scene,timing in zip(SCENES,timings):
        image=Image.open(D/scene['shot']).convert('RGB');image=image.crop((scene.get('crop_x',0),scene.get('crop_y',0),image.width,image.height));scale=1060/image.width;image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
        view_width=1060;view_height=750;N=int(round(timing['duration_seconds']*fps))
        start=min(scene['start_y']*scale,max(0,image.height-view_height));end=min(scene['end_y']*scale,max(0,image.height-view_height))
        print('Render scene',timing['scene'],'duration',timing['duration_seconds'],flush=True)
        for j in range(N):
            q=j/max(1,N-1);ease=q*q*(3-2*q);offset=int(start+(end-start)*ease)
            frame=Image.new('RGB',(W,H),'#edf3f4');draw=ImageDraw.Draw(frame)
            draw.rectangle((0,0,W,102),fill='#112f3a');draw.text((42,24),'LANKA DISPATCH / FORECAST LAB',font=F(25,True),fill='#f1f9f8');draw.text((1040,31),'IT5514  •  269182L',font=F(20),fill='#a8cfcb')
            draw.text((42,143),scene['tag'],font=F(17,True),fill='#087d79')
            y=190
            for line in lines(scene['title'],F(36,True),400):draw.text((42,y),line,font=F(36,True),fill='#17313b');y+=48
            y+=30
            for text in scene['points']:
                draw.ellipse((43,y+9,50,y+16),fill='#087d79')
                for line in lines(text,F(23),335):draw.text((66,y),line,font=F(23),fill='#3e5e68');y+=35
                y+=15
            draw.text((42,775),'Actual interface capture',font=F(17,True),fill='#53747c');draw.text((42,807),'Panning + synthesized narration',font=F(16),fill='#6b838a')
            region=image.crop((0,offset,min(view_width,image.width),min(image.height,offset+view_height)));x=505+(view_width-region.width)//2;draw.rectangle((505,125,1565,875),fill='#0a1e30');frame.paste(region,(x,125+(view_height-region.height)//2));draw.rounded_rectangle((500,120,1574,881),radius=9,outline='#cadbdc',width=2)
            now=timing['start_seconds']+j/fps;cap=next((c['text'] for c in captions if c['start']<=now<c['end']),None)
            draw.rectangle((0,900,W,H),fill='#112f3a')
            if cap:
                ls=lines(cap,F(23),1490)
                for k,line in enumerate(ls[:2]):draw.text((48,915+k*32),line,font=F(23),fill='white')
            draw.rectangle((0,995,int(W*now/cursor),999),fill='#5ab9aa');writer.append_data(np.asarray(frame))
    writer.close();output=D/'269182L_IT5514_Demo.mp4'
    subprocess.run([ff,'-y','-i',str(silent),'-i',str(soundtrack),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart','-shortest',str(output)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    (D/'269182L_IT5514_Demo.srt').write_text('\n\n'.join(f"{c['id']}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for c in captions)+'\n')
    (D/'Demo_Transcript.md').write_text('# Front-end demo transcript\n\nNarrated captured-interface walkthrough, using actual states of the working hosted Azure application. Visual panning is an edit, not continuous screen recording. Narration is the macOS Samantha system voice.\n\n'+'\n\n'.join('## '+str(i+1)+'. '+s['title']+'\n\n'+s['text'] for i,s in enumerate(SCENES)))
    metadata={'duration_seconds':cursor,'frames_per_second':fps,'width':W,'height':H,'narration':'macOS Samantha system voice, 162 words/minute','format':'captured-interface narrated walkthrough with panning; not continuous live recording','scenes':timings,'bytes':output.stat().st_size}
    assert 180<=cursor<=300,'Video outside required 3-5 minute range'
    (D/'demo_metadata.json').write_text(json.dumps(metadata,indent=2));print(json.dumps({k:v for k,v in metadata.items() if k!='scenes'},indent=2))
if __name__=='__main__':main()
