"""Render editable report_content.json to a PDF and Markdown reading copy."""
from pathlib import Path
import json,re,html,sys
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,Preformatted,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
from PIL import Image as PILImage
from prepare_data import ROOT

FONT=Path(matplotlib.get_data_path())/'fonts/ttf'
for name,file in [('Body','DejaVuSans.ttf'),('BodyBold','DejaVuSans-Bold.ttf'),('BodyItalic','DejaVuSans-Oblique.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='BodyItalic',boldItalic='BodyBold')
W,H=595.2756,841.8898; M=46; CW=W-2*M
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9.5,leading=13.7,spaceAfter=8,textColor=colors.HexColor('#253a48'),splitLongWords=True),
 'title':ParagraphStyle('title',fontName='BodyBold',fontSize=22,leading=27,spaceAfter=15,textColor=colors.HexColor('#153746')),
 'cover':ParagraphStyle('cover',fontName='BodyBold',fontSize=29,leading=35,spaceAfter=22,textColor=colors.HexColor('#153746')),
 'kicker':ParagraphStyle('kicker',fontName='BodyBold',fontSize=8,leading=12,spaceAfter=10,textColor=colors.HexColor('#087d79')),
 'sub':ParagraphStyle('sub',fontName='BodyBold',fontSize=11.2,leading=16,spaceBefore=5,spaceAfter=6,textColor=colors.HexColor('#126c70')),
 'caption':ParagraphStyle('caption',fontName='Body',fontSize=7.8,leading=10.9,spaceBefore=5,spaceAfter=10,textColor=colors.HexColor('#5d6f78')),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=8.2,leading=11.5,textColor=colors.HexColor('#253a48')),
 'header':ParagraphStyle('header',fontName='BodyBold',fontSize=8.1,leading=11,textColor=colors.white),
 'ref':ParagraphStyle('ref',fontName='Body',fontSize=8.25,leading=12,spaceAfter=10,textColor=colors.HexColor('#253a48'),splitLongWords=True)
}

def page_decor(c,doc):
    c.saveState();c.setStrokeColor(colors.HexColor('#d7e5e5'));c.setLineWidth(.6);c.line(M,38,W-M,38)
    c.setFont('Body',7);c.setFillColor(colors.HexColor('#60747c'));c.drawString(M,25,'IT5514  |  269182L  |  AI-assisted research draft');c.drawRightString(W-M,25,str(doc.page));c.restoreState()

def plain(s):return re.sub('<[^>]+>','',html.unescape(s)).replace('\n',' ')

def main():
    data=json.loads((ROOT/'07_report/report_content.json').read_text());story=[];md=['# '+data['title'],''];words=[]
    for pi,page in enumerate(data['pages']):
        story.extend([Paragraph(page['kicker'],styles['kicker']),Paragraph(page['title'].replace('\n','<br/>'),styles['cover'] if pi==0 else styles['title'])]);md+=['## '+page['title'].replace('\n',' '),''];words.append(page['title'])
        for block in page['blocks']:
            t=block['type']
            if t=='paragraph':
                st=styles['ref'] if page['title'].startswith('References') else styles['body'];story.append(Paragraph(block['text'],st));md+=[plain(block['text'].replace('<br/>','\n')),''];words.append(plain(block['text']))
            elif t=='subheading':story.append(Paragraph(block['text'],styles['sub']));md+=['### '+block['text'],''];words.append(block['text'])
            elif t=='equation':
                for line in block['text'].split('\n'):story.append(Paragraph(html.escape(line),ParagraphStyle('eq',parent=styles['body'],fontName='Body',fontSize=9.2,leading=14,backColor=colors.HexColor('#edf6f4'),borderPadding=7,spaceBefore=3,spaceAfter=7)))
                md+=['```text',block['text'],'```','']
            elif t=='table':
                rows=[[Paragraph(str(c),styles['header']) for c in block['headers']]]+[[Paragraph(str(c),styles['cell']) for c in row] for row in block['rows']]
                widths=block.get('widths');widths=[v*CW for v in widths] if widths else None
                tab=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
                tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1b4c58')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f6f5'),colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#1b4c58')),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#d9e5e4'))]));story.extend([tab,Spacer(1,10)])
                md+=['| '+' | '.join(block['headers'])+' |','| '+' | '.join(['---']*len(block['headers']))+' |']+['| '+' | '.join(str(x) for x in row)+' |' for row in block['rows']]+['']
                words.extend(' '.join(str(x) for x in row) for row in block['rows'])
            elif t=='figure':
                p=ROOT/block['file'];im=PILImage.open(p);iw,ih=im.size;scale=min(CW/iw,block['max_height']/ih);story.extend([Image(str(p),width=iw*scale,height=ih*scale),Paragraph(block['caption'],styles['caption'])]);md+=['!['+block['caption']+'](../'+block['file']+')',''];words.append(block['caption'])
        if pi<len(data['pages'])-1:story.append(PageBreak())
    out=ROOT/'07_report/269182L_IT5514_Report.pdf'
    doc=SimpleDocTemplate(str(out),pagesize=(W,H),rightMargin=M,leftMargin=M,topMargin=39,bottomMargin=52,title=data['title'],author=data['author'],subject='IT5514 Applied Machine Learning assignment; AI-assisted draft',pageCompression=1)
    doc.build(story,onFirstPage=page_decor,onLaterPages=page_decor)
    (ROOT/'07_report/269182L_IT5514_Report.md').write_text('\n'.join(md))
    from pypdf import PdfReader
    info={'pdf_pages':len(PdfReader(out).pages),'authored_sections':len(data['pages']),'approximate_words_including_tables_references_captions':len(' '.join(words).split()),'format':'A4; 9.5-point body; 13.7-point leading; numbered references; no supplied length/font requirement'}
    (ROOT/'07_report/report_build_info.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
if __name__=='__main__':main()
