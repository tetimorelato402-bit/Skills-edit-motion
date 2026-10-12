/* Fills config-driven links on the legal pages. Missing values leave a clear "coming soon" instead of a dead link. */
(()=>{const C=window.ANVIL||{};
  document.querySelectorAll('[data-portal]').forEach(a=>{if(C.stripePortal)a.href=C.stripePortal;else{a.setAttribute('aria-disabled','true');a.title='Online billing opens soon. Use the app for now.'}});
  if(C.supportEmail){const m=`<a href="mailto:${C.supportEmail}">${C.supportEmail}</a>`;
    document.querySelectorAll('[data-support-addr]').forEach(e=>e.innerHTML=m);
    document.querySelectorAll('[data-support-line]').forEach(e=>e.innerHTML='Help: '+m)}})();
