/* Texture tuner. Only runs when the URL has ?tune — visitors never see it.
   Drag the sliders, then "Copy values" and paste over the tunable block in css/texture.css. */
(()=>{if(!/[?&]tune\b/.test(location.search)&&location.hash!=='#tune')return;
const KEY='anvil-tune',root=document.documentElement;
const F=[
  ['--grain-light','Grain on light',0,1,.01,''],
  ['--grain-dark','Grain on dark',0,1,.01,''],
  ['--grain-size','Grain size',96,512,8,'px'],
  ['--vignette','Dark-edge vignette',0,1,.01,''],
  ['--glow','Glow behind phone',0,1.5,.05,''],
  ['--motion','Motion amount',0,1.5,.05,''],
  ['--rise','Reveal distance',0,40,1,'px'],
  ['--reveal-time','Reveal duration',.2,1.6,.05,'s']];
const read=k=>getComputedStyle(root).getPropertyValue(k).trim();
let saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
Object.entries(saved).forEach(([k,v])=>root.style.setProperty(k,v));

const box=document.createElement('div');
box.setAttribute('role','region');box.setAttribute('aria-label','Texture tuner');
box.style.cssText='position:fixed;right:12px;bottom:12px;z-index:9999;width:min(300px,calc(100vw - 24px));max-height:calc(100vh - 24px);overflow:auto;background:#16130F;color:#EDE6DA;border-radius:16px;padding:14px 16px;font:13px/1.4 system-ui,sans-serif;box-shadow:0 20px 50px -20px rgba(0,0,0,.7)';
box.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b style="font-size:14px">Texture & motion</b><button data-x style="all:unset;cursor:pointer;padding:2px 6px">hide</button></div>'+
  F.map(([k,l,min,max,step,u])=>{const v=parseFloat(read(k));return `<label style="display:block;margin:8px 0"><span style="display:flex;justify-content:space-between"><span>${l}</span><output data-o="${k}">${v}${u}</output></span><input type="range" data-k="${k}" data-u="${u}" min="${min}" max="${max}" step="${step}" value="${v}" style="width:100%;accent-color:#D6BE93"></label>`}).join('')+
  '<div style="display:flex;gap:8px;margin-top:10px"><button data-copy style="flex:1;height:34px;border-radius:9px;border:0;background:#D6BE93;color:#16130F;font-weight:600;cursor:pointer">Copy values</button><button data-reset style="height:34px;padding:0 12px;border-radius:9px;border:1px solid #5a5045;background:none;color:inherit;cursor:pointer">Reset</button></div><p data-msg style="margin:8px 0 0;color:#A89E8F;min-height:18px"></p>';
document.body.appendChild(box);

box.addEventListener('input',e=>{const i=e.target;if(!i.dataset.k)return;const v=i.value+i.dataset.u;root.style.setProperty(i.dataset.k,v);
  box.querySelector(`[data-o="${i.dataset.k}"]`).textContent=v;saved[i.dataset.k]=v;try{localStorage.setItem(KEY,JSON.stringify(saved))}catch(e){}
  if(i.dataset.k==='--motion'||i.dataset.k==='--rise'||i.dataset.k==='--reveal-time')replay()});
function replay(){document.querySelectorAll('[data-reveal]').forEach(el=>{const r=el.getBoundingClientRect();if(r.top<innerHeight&&r.bottom>0){el.classList.remove('in');void el.offsetWidth;requestAnimationFrame(()=>el.classList.add('in'))}})}
box.querySelector('[data-copy]').onclick=async()=>{const css=':root{\n'+F.map(([k])=>`  ${k}: ${read(k)};`).join('\n')+'\n}';
  const m=box.querySelector('[data-msg]');try{await navigator.clipboard.writeText(css);m.textContent='Copied. Paste it into css/texture.css.'}catch(e){console.log(css);m.textContent='Printed to the console; copy it from there.'}};
box.querySelector('[data-reset]').onclick=()=>{F.forEach(([k])=>root.style.removeProperty(k));saved={};try{localStorage.removeItem(KEY)}catch(e){}
  box.querySelectorAll('[data-k]').forEach(i=>{const v=parseFloat(read(i.dataset.k));i.value=v;box.querySelector(`[data-o="${i.dataset.k}"]`).textContent=v+i.dataset.u})};
box.querySelector('[data-x]').onclick=()=>box.remove();
})();
