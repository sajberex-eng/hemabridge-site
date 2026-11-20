// node langqa.js <lang: en|kz> [shotsDir]  -> checks every page at 1440 and 390
const { chromium } = require('playwright'); const fs=require('fs');
const lang=process.argv[2]; const shots=process.argv[3];
const PAGES=['home','route','diseases','tech','clinics','doctors','physicians','partners','about','cost','faq','apply','legal','cabinet'];
(async()=>{const b=await chromium.launch({executablePath:require('./browser')});
const report=[];
for(const [w,h] of [[1440,900],[390,844]]){
  const ctx=await b.newContext({viewport:{width:w,height:h},reducedMotion:'reduce'});
  await ctx.addInitScript(l=>{try{localStorage.setItem('hb-lang',l)}catch(e){}},lang);
  const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('requestfailed',r=>errs.push('reqfail '+r.url()));
  for(const pg of PAGES){
    await p.goto((await require('./pageurl')())(pg));await p.waitForTimeout(700);
    const r=await p.evaluate((lang)=>{
      const out={cyr:[],clip:[],overflowX:document.documentElement.scrollWidth-innerWidth};
      const page=document.querySelector('[data-page]:not([hidden])');
      const scope=[document.querySelector('.site-header'),page,document.querySelector('.site-footer')];
      scope.forEach(sc=>{ if(!sc) return; const w=document.createTreeWalker(sc,NodeFilter.SHOW_TEXT);let n;
        while((n=w.nextNode())){const t=n.nodeValue.trim();if(!t||/^(RU|KZ|EN)$/.test(t))continue;const pn=n.parentNode.nodeName;if(pn==='SCRIPT'||pn==='STYLE')continue;
          if(lang==='en'&&/[А-Яа-яЁё]/.test(t)) out.cyr.push(t.slice(0,70));}
        sc.querySelectorAll('[alt],[aria-label],[title]').forEach(e=>{['alt','aria-label','title'].forEach(a=>{const v=e.getAttribute(a);if(v&&lang==='en'&&/[А-Яа-яЁё]/.test(v))out.cyr.push(a+': '+v.slice(0,60))})});
        sc.querySelectorAll('.btn,.nav a,.chip,.pending,.place,.lang button,.card h3,.rt-list button,svg text').forEach(e=>{
          const r=e.getBoundingClientRect(); if(!r.width) return;
          const cs=getComputedStyle(e);
          if(e.scrollWidth>e.clientWidth+2 && cs.overflow!=='visible' ) out.clip.push((e.textContent||'').trim().slice(0,40));
        });
      });
      // svg labels overlapping each other / leaving viewBox
      const svg=page.querySelector('svg[viewBox="0 0 1000 340"]');
      if(svg){const ts=[...svg.querySelectorAll('text.lbl,text.rt-band-label,text.rt-branch-label')].map(t=>({t:t.textContent,r:t.getBoundingClientRect()}));
        const vb=svg.getBoundingClientRect();
        ts.forEach((a,i)=>{ if(a.r.left<vb.left-1||a.r.right>vb.right+1) out.clip.push('svg-out:'+a.t);
          for(let j=i+1;j<ts.length;j++){const b2=ts[j].r; if(a.r.left<b2.right+9&&a.r.right>b2.left-9&&a.r.top<b2.bottom&&a.r.bottom>b2.top) out.clip.push('svg-overlap:'+a.t+' | '+ts[j].t);}});}
      return out;},lang);
    const bad=r.cyr.length||r.clip.length||r.overflowX>0;
    if(bad) report.push({w,pg,...r});
    if(shots && (pg==='home'||pg==='apply'||pg==='route')) await p.screenshot({path:`${shots}/${lang}-${pg}-${w}.png`,fullPage:true});
  }
  if(errs.length) report.push({w,errors:errs});
  await ctx.close();
}
console.log(JSON.stringify(report,null,1)); console.log('pages with issues:',report.length);
await b.close();})();
