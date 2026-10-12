const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const CFG=window.ANVIL||{};
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---- nav: hairline once scrolled, highlight the section you're in ---- */
(()=>{const nav=$('#nav'),links=$$('.nav .r a.t').filter(l=>l.getAttribute('href').startsWith('#')),cre=$('#creators')||{hidden:true};
  const upd=()=>{nav.classList.toggle('sc',scrollY>8);if(!cre.hidden)return;const y=innerHeight*.35;let on=null;
    links.forEach(l=>{const e=$(l.getAttribute('href'));if(!e)return;const r=e.getBoundingClientRect();if(r.top<=y&&r.bottom>y)on=l});
    links.forEach(l=>l.classList.toggle('on',l===on))};
  addEventListener('scroll',upd,{passive:true});upd();})();

/* ---- reveal on scroll, once ---- */
(()=>{const els=$$('[data-reveal]');if(RM||!('IntersectionObserver' in window)){els.forEach(e=>e.classList.add('in'));return}
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -8% 0px',threshold:.12});
  els.forEach(e=>io.observe(e));})();

/* ---- film: scale to the phone, chapters, play only when visible ---- */
(()=>{const scr=$('#fscreen'),film=$('#film'),v=$('#fv');if(!film||!v)return;const T=12.9;
  const fit=()=>{film.style.transform=`scale(${scr.clientWidth/393})`};fit();new ResizeObserver(fit).observe(scr);
  const play=()=>{const p=v.play();if(p)p.catch(()=>{})};
  const CH=[[0,'Say it.','Pick what you’ll do and how many times a week.'],[2.5,'Get there.','The camera stays locked until you’re there.'],
    [5.1,'Your circle sees.','Every check-in fills a slice of the ring.'],[7.7,'Keep the week.','Everyone’s week, at a glance.'],[10.3,'Bring them.','Invite the people who’d notice.']];
  const bars=$('#cbars');CH.forEach((c,i)=>{const b=document.createElement('button');b.type='button';b.setAttribute('aria-label',`Chapter ${i+1}: ${c[1]}`);b.innerHTML='<i><b></b></i>';
    b.onclick=()=>{try{v.currentTime=c[0]+.05}catch(e){}if(RM)v.pause();tick(true)};bars.appendChild(b)});
  let cur=-1,vis=false;
  function tick(force){const t=v.currentTime||0;let k=CH.length-1;for(let i=0;i<CH.length;i++){if(t<(CH[i+1]?CH[i+1][0]:T)){k=i;break}}
    [...bars.children].forEach((b,i)=>{b.classList.toggle('done',i<k);const fb=b.querySelector('b');if(i===k){const s=CH[i][0],e=CH[i+1]?CH[i+1][0]:T;fb.style.transform=`scaleX(${Math.min(1,(t-s)/(e-s)).toFixed(3)})`}else fb.style.transform=''});
    if(k!==cur||force){cur=k;$('#cn').textContent=String(k+1).padStart(2,'0');$('#ct').textContent=CH[k][1];$('#cd').textContent=CH[k][2]}}
  (function loop(){if(vis||cur<0)tick();requestAnimationFrame(loop)})();
  const sb=$('#snd');sb.onclick=()=>{v.muted=!v.muted;sb.setAttribute('aria-pressed',String(!v.muted));sb.setAttribute('aria-label',v.muted?'Turn sound on':'Turn sound off');if(!v.muted)play()};
  if(RM){v.addEventListener('loadedmetadata',()=>{v.currentTime=5.9},{once:true});v.pause()}
  else new IntersectionObserver(es=>{vis=es[0].isIntersecting;vis?play():v.pause()},{threshold:.15}).observe(scr);
})();

/* ---- links that depend on config ---- */
(()=>{if(CFG.appStore){$$('[data-app]').forEach(a=>{a.href=CFG.appStore;a.rel='noopener'})}
  if(CFG.supportEmail){const m='mailto:'+CFG.supportEmail;$$('[data-support]').forEach(p=>{p.innerHTML=`Email <a class="ink" href="${m}">${CFG.supportEmail}</a> and a person will write back.`});
    $$('[data-support-link]').forEach(a=>{a.href=m;a.hidden=false})}
  else $$('[data-support]').forEach(p=>{const q=p.closest('.qa');if(q)q.hidden=true});})();

/* ---- creators ---- */
(()=>{const cre=$('#creators');if(!cre)return;let back=0;
  const openC=()=>{back=scrollY;cre.hidden=false;document.body.classList.add('lock');cre.scrollTop=0;setTimeout(()=>$('#creclose').focus(),50)};
  const closeC=()=>{cre.hidden=true;document.body.classList.remove('lock');if(location.hash==='#creators')history.replaceState(null,'',location.pathname+location.search);scrollTo(0,back)};
  $$('a[href="#creators"]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();openC()}));
  $('#creclose').onclick=closeC;addEventListener('keydown',e=>{if(e.key==='Escape'&&!cre.hidden)closeC()});
  if(location.hash==='#creators')openC();

  const f=$('#cf'),note=$('#cnote'),done=$('#cdone');
  const err=t=>{note.textContent=t;note.classList.add('err')};
  f.addEventListener('submit',async e=>{e.preventDefault();note.classList.remove('err');note.textContent='';
    const d={platform:(f.querySelector('input[name=plat]:checked')||{}).value||'',username:$('#cu1').value.trim().slice(0,60),email:$('#ce1').value.trim().slice(0,120),link:$('#cl1').value.trim().slice(0,400),message:$('#cm1').value.trim().slice(0,800)};
    if(!d.username){err('Add your username.');$('#cu1').focus();return}
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)){err('Add an email we can reach you at.');$('#ce1').focus();return}
    if(!/^https?:\/\/\S+\.\S+/.test(d.link)){err('Paste the full link to your video, starting with https://');$('#cl1').focus();return}
    if(!$('#cok').checked){err('Tick the box to confirm the video is yours and public.');return}
    if(!CFG.formEndpoint){
      if(!CFG.supportEmail){err('Submissions open soon. Check back in a few days.');return}
      const body=`Platform: ${d.platform}\nUsername: ${d.username}\nEmail: ${d.email}\nVideo: ${d.link}\n\n${d.message}`;
      location.href=`mailto:${CFG.supportEmail}?subject=${encodeURIComponent('Creator video: '+d.username)}&body=${encodeURIComponent(body)}`;return}
    const b=$('#csend');b.disabled=true;b.textContent='Sending…';
    try{const r=await fetch(CFG.formEndpoint,{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify(d)});if(!r.ok)throw 0;
      f.style.display='none';done.classList.add('on');f.reset()}
    catch(e2){err('That didn’t go through. Please try again in a minute.')}
    b.disabled=false;b.textContent='Send it'});
  $('#cagain').onclick=()=>{done.classList.remove('on');f.style.display='';note.textContent=''};
})();
