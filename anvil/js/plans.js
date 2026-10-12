/* Plans page: billing toggle, trial disclosure, checkout sheet. Needs site.js loaded first. */
/* ---- pricing ---- */
let bill='m';
const P={m:{cp:'$6.99',cu:'a month',cpp:'Charged monthly after your 7 free days',trial:7,tb:'First 7 days free',act:'Then $6.99 a month until you cancel.',amt:'$6.99',per:'a month',every:'every month',link:()=>CFG.stripeMonthly},
         y:{cp:'$69.99',cu:'a year',cpp:'Works out to $5.83 a month, charged yearly after 3 free weeks',trial:21,tb:'First 21 days free',act:'Then $69.99 a year until you cancel.',amt:'$69.99',per:'a year',every:'every year',link:()=>CFG.stripeYearly}};
function setBill(b){bill=b;[['#bm','m'],['#by','y']].forEach(([s,k])=>{$(s).classList.toggle('on',b===k);$(s).setAttribute('aria-pressed',String(b===k))});const p=P[b];
  $('#cp').textContent=p.cp;$('#cu').textContent=p.cu;$('#cpp').textContent=p.cpp;$('#trialb').textContent=p.tb;$('#actnote').textContent=p.act;$('#trialdays').textContent=p.trial+' days';
  $('#tdisc').innerHTML=`<b>How the trial works:</b> it’s free for ${p.trial} days. If you don’t cancel before it ends, you’ll be charged ${p.amt} ${p.per} until you cancel. We’ll remind you 3 days before the trial ends`+(b==='y'?', and again 15 to 45 days before each yearly renewal.':'.');
  ['#cp','#cpp'].forEach(s=>{const e=$(s);e.classList.remove('flip');void e.offsetWidth;e.classList.add('flip')});setTrialBtn()}
$('#bm').onclick=()=>setBill('m');$('#by').onclick=()=>setBill('y');

/* Trial button: web checkout if a Stripe link is set, otherwise the App Store, otherwise "coming soon". */
const trialBtn=$('[data-plan]');
function setTrialBtn(){const has=!!(P[bill].link()||CFG.appStore);trialBtn.disabled=!has;trialBtn.textContent=has?'Start free trial':'Coming soon'}
setTrialBtn();

const co=$('#co');let lastFocus;
const fmtD=d=>d.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
trialBtn.onclick=()=>{const p=P[bill];if(!p.link()){if(CFG.appStore)location.href=CFG.appStore;return}
  lastFocus=trialBtn;const end=new Date();end.setDate(end.getDate()+p.trial);
  $('#coh').textContent='Anvil, '+(bill==='y'?'yearly':'monthly');$('#cot').textContent=fmtD(end);$('#cod').textContent=p.amt+' on '+fmtD(end);$('#cor').textContent=p.amt+' '+p.every+' until you cancel';
  $('#coagreet').textContent=`I agree that Anvil will charge me ${p.amt} ${p.per}, starting ${fmtD(end)} when my free trial ends, and ${p.every} after that until I cancel. I can cancel anytime: in the app (my photo → Plan → Cancel) or on the Cancel page.`;
  $('#coagree').checked=false;$('#copay').disabled=true;
  co.classList.add('on');co.setAttribute('aria-hidden','false');setTimeout(()=>$('#cox').focus(),50)};
$('#coagree').addEventListener('change',e=>{$('#copay').disabled=!e.target.checked});
const coClose=()=>{co.classList.remove('on');co.setAttribute('aria-hidden','true');lastFocus&&lastFocus.focus()};
$('#cox').onclick=coClose;co.addEventListener('click',e=>{if(e.target===co)coClose()});
co.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const f=$$('#co button:not(:disabled),#co input,#co a');const i=f.indexOf(document.activeElement);
  if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus()}else if(!e.shiftKey&&i===f.length-1){e.preventDefault();f[0].focus()}});
addEventListener('keydown',e=>{if(e.key==='Escape'&&co.classList.contains('on'))coClose()});
$('#copay').onclick=()=>{const l=P[bill].link();if(l&&$('#coagree').checked)location.href=l};

