// node vp.js <page id> <w> <h> <out> [scheme] [scrollY]
const { chromium } = require('playwright');
(async()=>{const [h,w,ht,out,scheme='light',y='0']=process.argv.slice(2);const b=await chromium.launch({executablePath:require('./browser')});
const p=await b.newPage({viewport:{width:+w,height:+ht},colorScheme:scheme,reducedMotion:'reduce'});
await p.goto((await require('./pageurl')())(h));await p.waitForTimeout(600);await p.evaluate(y=>scrollTo(0,+y),y);await p.waitForTimeout(200);
await p.screenshot({path:out});await b.close();})();
