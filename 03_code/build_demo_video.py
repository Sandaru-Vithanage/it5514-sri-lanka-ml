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
SCENES=[
 {'title':'A Sri Lankan forecasting study','tag':'01 / SOURCE & TASK','shot':'05_data_method.png','start_y':250,'end_y':1050,'points':['PUCSL dispatch records','Pinned public release','One local day ahead'], 'text':'This walkthrough presents Lanka Dispatch, the Applied Machine Learning prototype prepared for Sandaru Rashmika, index number two six nine one eight two L. It forecasts the next local day of recorded electricity dispatch energy in Sri Lanka. The source is the Sri Lankan raw subset of a versioned public dataset compiled from PUCSL records. The daily target was rebuilt from raw readings after detecting duplicate plant and timestamp records and a missing interval conversion in the published daily file. This is a historical research tool, with no connection to live grid operations.'},
 {'title':'Replay a recorded case','tag':'02 / REAL MODEL PREDICTION','shot':'01_historical_replay.png','start_y':310,'end_y':900,'points':['15 January 2025','Only earlier demand inputs','42.33 GWh estimate'], 'text':'In the Forecast Lab, select the day to predict and load its recorded inputs. The six editable values describe earlier demand: one, two, seven and fourteen day lags, and the previous week\'s mean and variability. Calendar coordinates come from the selected date. For fifteen January twenty twenty five, the trained Gaussian process predicts about forty two point three three gigawatt hours. Its nominal ninety five percent observation interval runs from thirty seven point four three to forty seven point two three. The historical observed outcome is displayed separately. The interface calls the saved Python model, rather than a mock formula.'},
 {'title':'Edit an input and inspect the effect','tag':'03 / INTERACTIVE SCENARIO','shot':'02_edited_input.png','start_y':500,'end_y':1020,'points':['Previous day → 42 GWh','New estimate: 44.22 GWh','Actual outcome stays fixed'], 'text':'Next, change only the previous day\'s energy to forty two gigawatt hours and generate another forecast. The estimate rises to about forty four point two two gigawatt hours. The badge identifies hypothetical inputs, while the recorded outcome stays unchanged. Below the estimate, three bars show separate group replacement sensitivities against a representative training day. They describe changes in this fitted model\'s output. They do not add up to the prediction and they do not prove causal effects. Internally consistent historical inputs remain preferable to arbitrary scenarios.'},
 {'title':'Reject invalid input','tag':'04 / INPUT VALIDATION','shot':'03_invalid_input.png','start_y':510,'end_y':650,'points':['Negative values rejected','No new prediction accepted','Last valid result labelled'], 'text':'The interface also checks input validity. Entering a negative energy value produces an error instead of accepting a new prediction. The prediction panel is explicitly labelled as the last valid estimate. The backend independently rejects negative, oversized and non finite values. Dates outside the evaluated historical period receive a warning because no live data feed is available.'},
 {'title':'Read the comparative evidence','tag':'05 / EVALUATION & XAI','shot':'04_evaluation.png','start_y':300,'end_y':1120,'points':['GPR MAE: 1.599 GWh','29.7% vs weekly naïve','92.8% interval coverage'], 'text':'The evaluation tab reports the same saved experimental results as the report. Three chronological validation windows selected hyperparameters before the ninety seven day test. Gaussian process regression achieves a mean absolute error of one point five nine nine gigawatt hours, improving the weekly naive baseline by twenty nine point seven percent. It does not win every comparison: support vector regression has the lowest test mean absolute error, and random forest has the lowest root mean squared error. The global explanation shows greatest reliance on demand history and weekly calendar. Nominal ninety five percent intervals cover ninety two point eight percent of test outcomes.'},
 {'title':'Inspect a failure and its limits','tag':'06 / CRITICAL INTERPRETATION','shot':'06_exceptional_day.png','start_y':900,'end_y':1030,'points':['4 February: large miss','Holiday signal omitted','Fresh holdout for revisions'], 'text':'Finally, replay four February twenty twenty five, Independence Day. The model forecasts about forty four point three seven gigawatt hours, while recorded dispatch is only thirty three point seven four. Several large errors coincide with verified Sri Lankan holidays omitted from the frozen predictors. That association suggests a future improvement, but adding holiday features now would require a fresh holdout. Recorded dispatch is also a coverage limited proxy for demand. The source package includes data provenance, code, executed notebook, model artefacts, explanations and independent checks. This video uses genuine interface captures with panning and synthesized narration. Student review and an accurate assistance disclosure remain part of submission.'}
]

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
        image=Image.open(D/scene['shot']).convert('RGB');scale=1.12;image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
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
            region=image.crop((0,offset,min(view_width,image.width),offset+view_height));x=505+(view_width-region.width)//2;frame.paste(region,(x,125));draw.rounded_rectangle((500,120,1574,881),radius=9,outline='#cadbdc',width=2)
            now=timing['start_seconds']+j/fps;cap=next((c['text'] for c in captions if c['start']<=now<c['end']),None)
            draw.rectangle((0,900,W,H),fill='#112f3a')
            if cap:
                ls=lines(cap,F(23),1490)
                for k,line in enumerate(ls[:2]):draw.text((48,915+k*32),line,font=F(23),fill='white')
            draw.rectangle((0,995,int(W*now/cursor),999),fill='#5ab9aa');writer.append_data(np.asarray(frame))
    writer.close();output=D/'269182L_IT5514_Demo.mp4'
    subprocess.run([ff,'-y','-i',str(silent),'-i',str(soundtrack),'-c:v','copy','-c:a','aac','-b:a','128k','-movflags','+faststart','-shortest',str(output)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    (D/'269182L_IT5514_Demo.srt').write_text('\n\n'.join(f"{c['id']}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for c in captions)+'\n')
    (D/'Demo_Transcript.md').write_text('# Front-end demo transcript\n\nNarrated captured-interface walkthrough, using actual states of the working local app. Visual panning is an edit, not continuous screen recording. Narration is the macOS Samantha system voice.\n\n'+'\n\n'.join('## '+str(i+1)+'. '+s['title']+'\n\n'+s['text'] for i,s in enumerate(SCENES)))
    metadata={'duration_seconds':cursor,'frames_per_second':fps,'width':W,'height':H,'narration':'macOS Samantha system voice, 162 words/minute','format':'captured-interface narrated walkthrough with panning; not continuous live recording','scenes':timings,'bytes':output.stat().st_size}
    assert 180<=cursor<=300,'Video outside required 3-5 minute range'
    (D/'demo_metadata.json').write_text(json.dumps(metadata,indent=2));print(json.dumps({k:v for k,v in metadata.items() if k!='scenes'},indent=2))
if __name__=='__main__':main()
