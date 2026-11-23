/* v3.10: aba Humor — respostas do Involves cruzadas com os outros indicadores do mesmo dia */
function humorStats(){const D=R().D||{},H=D.humor||[],neg=new Set(S.cfg.neg.map(norm)),ks=new Set(R().list.map(p=>p.k));
  const jm=new Map();R().todos.forEach(p=>p.jor.dias.forEach(x=>jm.set(p.k+"|"+x.d,x)));
  const pm=new Map();(D.pesq||[]).forEach(r=>{const k=r.k+"|"+r.d;let s=pm.get(k);if(!s)pm.set(k,s={prog:0,exp:0});s.prog++;if(r.st==="E")s.exp++});
  const O=new Map();H.filter(h=>ks.has(h.k)).forEach(h=>{let o=O.get(h.op);if(!o)O.set(h.op,o={op:h.op,neg:neg.has(norm(h.op)),dias:0,dj:0,atr:0,auto:0,prog:0,exp:0,ps:new Set()});
    o.dias++;o.ps.add(h.k);const j=jm.get(h.k+"|"+h.d);if(j){o.dj++;if(j.atraso)o.atr++;if(j.auto)o.auto++}const s=pm.get(h.k+"|"+h.d);if(s){o.prog+=s.prog;o.exp+=s.exp}});
  const L=[...O.values()].sort((a,b)=>a.neg-b.neg||b.dias-a.dias);L.forEach(o=>{o.pAtr=o.dj?o.atr/o.dj:null;o.pAuto=o.dj?o.auto/o.dj:null;o.pExp=o.prog?o.exp/o.prog:null});
  const agg=f=>{const g=L.filter(f),dj=g.reduce((a,o)=>a+o.dj,0),pr=g.reduce((a,o)=>a+o.prog,0);return{dias:g.reduce((a,o)=>a+o.dias,0),pAtr:dj?g.reduce((a,o)=>a+o.atr,0)/dj:null,pAuto:dj?g.reduce((a,o)=>a+o.auto,0)/dj:null,pExp:pr?g.reduce((a,o)=>a+o.exp,0)/pr:null}};
  return{L,pos:agg(o=>!o.neg),neg:agg(o=>o.neg)}}
function humorPainel(){const{L,pos,neg}=humorStats();if(!L.length)return'<div class="nobase">Sem respostas de humor carregadas para este período.</div>';
  const x=(a,b)=>a!=null&&b?a/b:null,fx=v=>v==null?"—":v.toFixed(1).replace(".",",")+"x",cmp=[["Atraso no check-in",neg.pAtr,pos.pAtr],["Check-out automático",neg.pAuto,pos.pAuto],["Pesquisas expiradas",neg.pExp,pos.pExp]];
  return'<section class="card hm-an"><div class="hd"><h2>Humor × desempenho no mesmo dia</h2><small class="muted">'+num(pos.dias+neg.dias)+' respostas do Involves cruzadas com jornada e pesquisas</small></div>'+
    '<div class="hm-cmp">'+cmp.map(([l,n,p])=>{const r=x(n,p);return'<div class="hm-k"><span>'+l+'</span><b class="'+(r!=null&&r>=1.2?"up":"")+'">'+fx(r)+'</b><small>dias negativos '+(n==null?"—":pc(n,0))+' · positivos '+(p==null?"—":pc(p,0))+'</small></div>'}).join("")+'</div>'+
    '<div class="hm-grid"><div class="cv" style="height:300px"><canvas id="g-hman" role="img" aria-label="Indicadores por resposta de humor"></canvas></div>'+
    '<table class="tbl hm-t"><thead><tr><th>Resposta</th><th class="num">Dias</th><th class="num">Promotores</th><th class="num">Atraso</th><th class="num">Check-out auto</th><th class="num">Pesq. expiradas</th></tr></thead><tbody>'+
    L.map(o=>'<tr><td><span class="hm-c'+(o.neg?" neg":"")+'">'+esc(o.op)+'</span></td><td class="num">'+num(o.dias)+'</td><td class="num">'+num(o.ps.size)+'</td><td class="num">'+(o.pAtr==null?"—":pc(o.pAtr,0))+'</td><td class="num">'+(o.pAuto==null?"—":pc(o.pAuto,0))+'</td><td class="num">'+(o.pExp==null?"—":pc(o.pExp,0))+'</td></tr>').join("")+'</tbody></table></div>'+
    '<small class="muted">Leitura de contexto: mostra se dias de humor negativo coincidem com mais ocorrências. Não é prova de causa nem motivo de medida; serve para cuidar da equipe.</small></section>'}
function gHumor(){const{L}=humorStats();if(!L.length)return;const v=f=>L.map(o=>f(o)==null?null:+(f(o)*100).toFixed(1));
  grafico("g-hman",{type:"bar",data:{labels:L.map(o=>o.op),datasets:[["% atraso",o=>o.pAtr,"--rt"],["% check-out auto",o=>o.pAuto,"--bad"],["% pesquisas expiradas",o=>o.pExp,"--warn"]].map(([l,f,c])=>({label:l,data:v(f),backgroundColor:css(c),borderRadius:5,maxBarThickness:26}))},
    options:{scales:{y:{beginAtZero:true,ticks:{callback:t=>t+"%"}}},plugins:{tooltip:{callbacks:{label:t=>t.dataset.label+": "+String(t.raw).replace(".",",")+"%"}}}}})}
