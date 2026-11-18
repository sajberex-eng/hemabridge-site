// node vp.js <hash> <w> <h> <out> [scheme] [scrollY]
const { chromium } = require('playwright');
(async()=>{const [h,w,ht,out,scheme='light',y='0']=process.argv.slice(2);const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p=await b.newPage({viewport:{width:+w,height:+ht},colorScheme:scheme,reducedMotion:'reduce'});
await p.goto('file://'+require('path').resolve(__dirname,'../index.html')+'#'+h);await p.waitForTimeout(600);await p.evaluate(y=>scrollTo(0,+y),y);await p.waitForTimeout(200);
await p.screenshot({path:out});await b.close();})();
