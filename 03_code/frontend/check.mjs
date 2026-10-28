import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {forecastPoints} from './src/chart-data.js';
// A unit-conversion or point-order mistake would misrepresent the uncertainty plot.
const example={mean_MWh:42325.97557366114,lower95_MWh:37430,upper95_MWh:47230,actual_MWh:42070,seasonal_naive_MWh:43910};
const p=forecastPoints(example);assert(Math.abs(p.mean-42.32597557366114)<1e-10);assert(p.low<p.actual&&p.actual<p.mean&&p.mean<p.naive&&p.naive<p.high);assert(p.min<=p.low&&p.max>=p.high);
const outside=forecastPoints({...example,actual_MWh:12000});assert(outside.min<12&&outside.max>=p.high);
assert.equal(forecastPoints({...example,actual_MWh:null}).actual,null);
const html=await readFile(new URL('../app.html',import.meta.url),'utf8');assert(html.includes('data-theme="ocean"'));assert(!html.includes('{{STYLES}}'));assert(!html.includes('{{SCRIPT}}'));assert(!/<script[^>]*src=/.test(html));assert(!/<link[^>]*stylesheet/.test(html));
console.log('Frontend checks passed: GWh conversion, true marker order, outlying actual, missing actual, bundled browser assets.');
