/* Legal pages: fills config links, and runs the pause-or-cancel sheet on the cancel page. */
(()=>{const C=window.ANVIL||{},$=s=>document.querySelector(s);
  if(C.supportEmail){const m=`<a href="mailto:${C.supportEmail}">${C.supportEmail}</a>`;
    document.querySelectorAll('[data-support-addr]').forEach(e=>e.innerHTML=m);
    document.querySelectorAll('[data-support-line]').forEach(e=>e.innerHTML='Help: '+m);
    document.querySelectorAll('[data-stuck]').forEach(e=>e.hidden=false)}

  /* Pressing Cancel offers a pause first. Cancelling stays one tap away, same size, same place. */
  const pz=$('#pz');if(!pz)return;
  const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const note=$('#pznote');let opener=null;
  const r=new Date();r.setMonth(r.getMonth()+1);
  $('#pzdate').textContent='on '+new Intl.DateTimeFormat('en-US',{month:'long',day:'numeric'}).format(r);
  const open=b=>{opener=b;note.textContent='';pz.classList.add('on');pz.setAttribute('aria-hidden','false');document.body.classList.add('lock');
    setTimeout(()=>$('#pzpause').focus(),RM?0:60)};
  const close=()=>{pz.classList.remove('on');pz.setAttribute('aria-hidden','true');document.body.classList.remove('lock');opener&&opener.focus()};
  document.querySelectorAll('[data-cancel]').forEach(b=>b.addEventListener('click',()=>open(b)));
  pz.querySelector('[data-pz-close]').onclick=close;
  pz.addEventListener('click',e=>{if(e.target===pz)close()});
  addEventListener('keydown',e=>{if(!pz.classList.contains('on'))return;
    if(e.key==='Escape')close();
    if(e.key==='Tab'){const f=[...pz.querySelectorAll('button')],i=f.indexOf(document.activeElement);
      if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus()}else if(!e.shiftKey&&i===f.length-1){e.preventDefault();f[0].focus()}}});
  const go=url=>{if(url){location.href=url;return}
    note.textContent='Web billing isn’t open yet. In the app: Your photo → Plan → Cancel.'};
  $('#pzpause').onclick=()=>go(C.stripePause||C.stripePortal);
  $('#pzcancel').onclick=()=>go(C.stripePortal);
  if(location.hash==='#cancel'||location.hash==='#pause'){const b=$('[data-cancel]');if(b)open(b)}
})();
