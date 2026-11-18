// node langvp.js <lang en|kz> <hash> <w> <h> <out> [scrollY|selector]
const { chromium } = require('playwright');
(async()=>{const [lang,h,w,ht,out,sc='0']=process.argv.slice(2);const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const ctx=await b.newContext({viewport:{width:+w,height:+ht},reducedMotion:'reduce'});await ctx.addInitScript(l=>{try{localStorage.setItem('hb-lang',l)}catch(e){}},lang);
const p=await ctx.newPage();await p.goto('file://'+require('path').resolve(__dirname,'../index.html')+'#'+h);await p.waitForTimeout(900);
if(isNaN(+sc)){await p.locator(sc).first().scrollIntoViewIfNeeded();await p.evaluate(()=>scrollBy(0,-90));}else await p.evaluate(y=>scrollTo(0,+y),+sc);
await p.waitForTimeout(250);await p.screenshot({path:out});await b.close();})();
