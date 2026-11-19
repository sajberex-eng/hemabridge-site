const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:require('./browser')});
const p=await b.newPage({viewport:{width:1280,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(require('url').pathToFileURL(require('path').resolve(__dirname,'../index.html')).href+'#home');await p.waitForTimeout(600);
const keys=await p.evaluate(()=>window.__i18nKeys());
fs.writeFileSync(require('path').resolve(__dirname,'../src/keys.json'),JSON.stringify(keys,null,1));
const kinds={};keys.forEach(k=>kinds[k.ctx.kind]=(kinds[k.ctx.kind]||0)+1);
console.log(keys.length,JSON.stringify(kinds),'chars',keys.reduce((a,k)=>a+k.key.length,0),'errs',errs);await b.close();})();
