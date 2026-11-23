/* v3.5: clique no ping destaca o promotor com um cartão sobre o radar */
function radarPing(k,el){const sc=document.querySelector(".scope");if(!sc)return;const p=R().todos.find(x=>x.k===k);if(!p)return;
  document.querySelectorAll(".blip.sel").forEach(b=>b.classList.remove("sel"));
  const old=sc.querySelector(".rp-pop");if(old&&old.dataset.k===k){old.remove();return}if(old)old.remove();
  el.classList.add("sel");const px=+el.dataset.px,py=+el.dataset.py,cor={C:"var(--bad)",A:"var(--rt)",T:"var(--warn)",N:"var(--good)"}[p.cls];
  const d=document.createElement("div");d.className="rp-pop";d.dataset.k=k;d.style.setProperty("--c",cor);
  d.style.left=(px>55?px-2:px+2)+"%";d.style.top=py+"%";d.style.transform="translate("+(px>55?"-100%":"0")+",-50%)";
  const al=p.alertas.slice(0,3).map(a=>'<li>'+esc(a.tit)+'</li>').join("");
  d.innerHTML='<div class="rp-pop-h"><span class="rp-av">'+esc((p.nome.split(" ")[0]||"?")[0]+((p.nome.split(" ").filter(Boolean).pop()||"")[0]||""))+'</span><div><b>'+esc(p.nome)+'</b><small>'+esc(p.uf||"")+(p.sup?' · '+esc(p.sup):"")+'</small></div><button class="rp-pop-x" aria-label="Fechar" data-a="pingX">✕</button></div>'+
    '<div class="rp-pop-m"><span class="pill" style="background:color-mix(in srgb,'+cor+' 20%,transparent);color:'+cor+'">'+(p.niv?NIV[p.niv][0]:"Estável")+'</span><span><em>'+p.risco+'</em> risco</span><span><em>'+p.alertas.length+'</em> alertas</span></div>'+
    (al?'<ul>'+al+'</ul>':"")+'<button class="btn sm" data-a="abrir" data-v="'+esc(p.k)+'">Abrir Raio-X →</button>';
  sc.appendChild(d)}
