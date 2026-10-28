import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {build} from 'esbuild';
const dir=path.dirname(fileURLToPath(import.meta.url));process.chdir(dir);
await mkdir('.build',{recursive:true});
execFileSync(process.execPath,['node_modules/@tailwindcss/cli/dist/index.mjs','-i','src/style.css','-o','.build/styles.css','--minify'],{stdio:'inherit'});
const script=await build({absWorkingDir:dir,entryPoints:['src/main.js'],bundle:true,minify:true,write:false,format:'iife',target:['es2022'],legalComments:'inline'});
const inter=await readFile('node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2');
const font=await readFile('node_modules/@phosphor-icons/web/src/regular/Phosphor.woff2');
const iconStyle=await readFile('node_modules/@phosphor-icons/web/src/regular/style.css','utf8');
const names=['trend-up','chart-bar','file-text','book-open','circle','info','arrow-right','line-segments'];
let icons=`@font-face{font-family:Phosphor;src:url(data:font/woff2;base64,${font.toString('base64')}) format('woff2');font-weight:normal;font-style:normal;font-display:block}.ph{font-family:Phosphor!important;font-style:normal;font-weight:normal;font-variant:normal;text-transform:none;line-height:1;letter-spacing:0;-webkit-font-smoothing:antialiased;display:inline-block}`;
for(const name of names){const escaped=name.replaceAll('-','\\-');const m=iconStyle.match(new RegExp('\\.ph-'+escaped+':before\\s*\\{[^}]*\\}'));if(!m)throw Error('Missing licensed icon: '+name);icons+=m[0];}
const fontStyle=`@font-face{font-family:Inter;font-style:normal;font-weight:100 900;font-display:swap;src:url(data:font/woff2;base64,${inter.toString('base64')}) format('woff2')}`;
const css=await readFile('.build/styles.css','utf8');let template=await readFile('src/app.template.html','utf8');
template=template.replace('{{STYLES}}',fontStyle+icons+css).replace('{{SCRIPT}}',script.outputFiles[0].text.replaceAll('</script','<\\/script'));
await writeFile('../app.html',template);
const notices=[];for(const pkg of ['tailwindcss','daisyui','echarts','motion','@phosphor-icons/web','@fontsource-variable/inter']){const meta=JSON.parse(await readFile('node_modules/'+pkg+'/package.json','utf8'));notices.push(`\n${pkg} ${meta.version} (${meta.license})\n`);for(const name of ['LICENSE','LICENSE.txt','LICENSE.md','NOTICE']){try{notices.push(await readFile('node_modules/'+pkg+'/'+name,'utf8'));}catch{}}}
await writeFile('THIRD_PARTY_NOTICES.txt',notices.join('\n'));
console.log('Built self-contained app.html:',Buffer.byteLength(template),'bytes; no runtime CDN requests.');
