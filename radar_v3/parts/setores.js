/* v3.3: um sistema, vários setores + galeria de fotos com indício */
if(window.Chart){Chart.defaults.font.family="'Plus Jakarta Sans',Inter,Arial,sans-serif";Chart.defaults.font.size=12}
function setoresPainel(L,h){const sum=f=>L.reduce((a,p)=>a+f(p),0),ct=sum(p=>p.ad.ct||0),rz=sum(p=>p.ad.rz||0),N=R().N;
  const S5=[
    ["Diretoria","M3 3v18h18M7 15l4-4 3 3 5-6","Visão consolidada da operação",[[num(L.length),"promotores"],[ct?pc(rz/ct):"—","aderência"],[N.C,"críticos"]],"geral","#7c8cff"],
    ["DP","M12 7v5l3 2M12 3a9 9 0 1 0 0 18a9 9 0 0 0 0-18","Jornada, atrasos e check-out automático",[[num(sum(p=>p.jor.nAtr)),"atrasos"],[num(sum(p=>p.jor.nAuto)),"check-outs auto"],h.faltas?[num(sum(p=>p.fal.I||0)),"faltas"]:[num(sum(p=>p.pes.semExec.length)),"dias sem atividade"]],"jor","var(--warn)"],
    ["Compliance","M12 3l8 3v6c0 5-3.5 8-8 9c-4.5-1-8-4-8-9V6z","Indícios, fotos e dossiê formal",[[num(sum(p=>p.fot.length)),"fotos com indício"],[num(N.C+N.A),"em apuração"],["RP","dossiê numerado"]],"foto","var(--bad)"],
    ["Merchandising","M4 7h16l-1.5 10h-13zM8 7V5h8v2","Aderência das lojas e pesquisas",[[num(sum(p=>p.ad.baixo.length)),"lojas abaixo da meta"],[pc(sum(p=>p.pes.exp)/Math.max(1,sum(p=>p.pes.prog))),"pesquisas expiradas"]],"ader","var(--m2)"],
    ["RH e P&P","M12 21s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 11c0 5.5-7 10-7 10z","Cuidado: sobrecarga e humor",[[num(L.filter(p=>p.sobre).length),"possível sobrecarga"],[pc(sum(p=>p.hum.neg)/Math.max(1,sum(p=>p.hum.dias)),0),"humor negativo"]],"sobre","var(--vio)"]];
  return'<section class="setores"><div class="st-grid">'+
    S5.map(([n,ic,d,ms,t,c])=>'<button class="st" style="--c:'+c+'" data-a="setor" data-v="'+t+'"><span class="st-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="'+ic+'"/></svg></span><b>'+n+'</b><small>'+d+'</small><span class="st-ms">'+ms.map(m=>'<span><em>'+m[0]+'</em>'+m[1]+'</span>').join("")+'</span></button>').join("")+'</div></section>'}
function fotoZoom(i){const g=(window.__FG||[])[i];if(!g)return;const fv=document.querySelector(".fg-view");if(fv)fv.classList.add("paused");
  const p=g.a.p,el=document.createElement("div");el.className="modal lb";
  const fig=(f,src)=>'<figure><img src="'+esc(src)+'" alt="Foto da visita"><figcaption><b>'+fDc(f.d)+(f.h!=null?" · "+fH(f.h):"")+'</b><span>'+esc(f.loja||"")+'</span><span>'+esc(f.pesq||"")+'</span></figcaption></figure>';
  el.innerHTML='<div class="box lb-box" role="dialog" aria-label="Fotos com indício"><div class="lb-hd"><div><div class="eyebrow">Fotos com indício · imagem repetida em visitas diferentes</div><h2>'+esc(p.nome)+'</h2><small class="muted">'+esc(p.sup||"")+' · '+esc(p.uf||"")+'</small></div><button class="btn sec sm lb-x" aria-label="Fechar">✕</button></div><div class="lb-pair">'+fig(g.a,g.ia)+fig(g.b,g.ib)+'</div><div class="lb-ft"><span class="muted small">Indício para conferência. Não constitui conclusão.</span><button class="btn" data-a="abrir" data-v="'+esc(p.k)+'">Abrir Raio-X do promotor →</button></div></div>';
  const fechar=()=>{el.remove();document.removeEventListener("keydown",esc_)},esc_=e=>{if(e.key==="Escape")fechar()};
  el.addEventListener("click",e=>{if(e.target===el||e.target.closest(".lb-x"))fechar();else if(e.target.closest('[data-a="abrir"]'))setTimeout(fechar,0)});
  document.addEventListener("keydown",esc_);document.body.appendChild(el)}
function fotosPainel(L){const G=new Map();L.forEach(p=>p.fot.forEach(f=>{if(!f.url||!f.mot.some(m=>/repetida/.test(m)))return;const k=f.hash||f.url;let g=G.get(k);if(!g)G.set(k,g=[]);g.push(Object.assign({p},f))}));
  const gs=[...G.values()].filter(g=>g.length>1).sort((a,b)=>b[0].p.risco-a[0].p.risco).slice(0,24);if(!gs.length)return"";
  const im=f=>/^https?:/.test(f.url)?f.url:"fotos/"+f.url.split("/").pop();
  window.__FG=gs.map(g=>({a:g[0],b:g[1],ia:im(g[0]),ib:im(g[1])}));
  const card=(g,i)=>{const a=g[0],b=g[1];return'<div class="fg"><span class="fg-pair" data-a="fotoZoom" data-v="'+i+'" title="Ampliar"><img loading="lazy" src="'+esc(im(a))+'" alt="Foto de '+esc(fDc(a.d))+'"><img loading="lazy" src="'+esc(im(b))+'" alt="Foto de '+esc(fDc(b.d))+'"><i class="fg-tag">Repetida</i></span><span class="fg-cap"><b>'+esc(a.p.nome.split(" ")[0]+" "+a.p.nome.split(" ").filter(Boolean).pop())+'</b><small>'+esc((a.loja||"").replace(/^[A-Z]{2} \/ /,""))+' · '+fDc(a.d)+' e '+fDc(b.d)+'</small><button class="btn sec sm" data-a="abrir" data-v="'+esc(a.p.k)+'">Abrir Raio-X</button></span></div>'};
  const h=gs.map((g,i)=>card(g,i)).join("");
  return'<section class="card fotos-g"><div class="hd"><h2>Fotos com indício</h2><button class="btn sec sm" data-a="setor" data-v="foto">Ver todas</button></div><div class="fg-view" data-a="fgPause" title="Clique para pausar ou continuar"><div class="fg-track" style="--n:'+gs.length+'">'+h+h+'</div><span class="fg-st">❚❚ pausado</span></div></section>'}
