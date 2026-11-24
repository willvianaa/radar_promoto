/* v4.0: 6 indicadores da operação (jornada unificada + ausências) e detalhe ao clicar com abas por categoria */
const KPI={
  ader:{l:"Aderência",ic:"M3 12l5 5L21 6",c:"#3B82F6",meta:93,up:true,t:"meta",al:"ader"},
  pesq:{l:"Pesquisas expiradas",ic:"M9 11l3 3 8-8M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11",c:"#F59E0B",meta:20,t:"limite",al:"pesq"},
  jor:{l:"Ocorrências de jornada",ic:"M12 7v5l3 2M12 3a9 9 0 1 0 0 18a9 9 0 0 0 0-18",c:"#F4562A",meta:10,t:"limite",al:"jor"},
  humor:{l:"Humor",ic:"M12 21a9 9 0 1 0 0-18a9 9 0 0 0 0 18zM8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01",c:"#8B5CF6",meta:40,t:"limite",al:"humor"},
  foto:{l:"Fotos com indício",ic:"M4 7h3l2-3h6l2 3h3v12H4zM12 17a4 4 0 1 0 0-8a4 4 0 0 0 0 8",c:"#14B8A6",meta:2,t:"limite",al:"foto"},
  aus:{l:"Ausências",ic:"M8 3v3M16 3v3M4 8h16M5 5h14v15H5zM9.5 13.5l5 5M14.5 13.5l-5 5",c:"#EC4899",meta:3,t:"limite",al:"falta"}};
/* categorias de ausência a partir do tipo e do motivo registrados */
const AUS=[["nj","Falta não justificada","#E11D48"],["at","Atestado médico","#EC4899"],["ap","Problema no aparelho","#F59E0B"],["ou","Outras justificativas","#64748B"]];
function ausCat(x){const t=norm((x.motivo||"")+" "+(x.tpTxt||""));if(x.tipo==="I")return"nj";if(x.tipo==="A"||/ATESTAD|MEDIC|SAUDE|DOENC|CONSULTA|\bCID\b|HOSPITAL|EXAME/.test(t))return"at";
  if(/APARELHO|CELULAR|SMARTPHONE|BATERIA|SINAL|APLICATIVO|\bAPP\b|SISTEMA|TELEFONE/.test(t))return"ap";return"ou"}
/* EXEMPLO FICTÍCIO: aparece só sem a base de ausências; nunca se mistura com promotores reais nem entra em alertas, nível ou risco */
const AUS_EX=(()=>{const N=[["Ana Exemplo Prado","BA","Supervisor Fictício 1"],["Bruno Fictício Reis","PE","Supervisor Fictício 2"],["Carla Modelo Dias","CE","Supervisor Fictício 3"],["Diego Teste Lima","MA","Supervisor Fictício 1"],["Elisa Exemplo Rocha","BA","Supervisor Fictício 2"],["Fábio Modelo Nunes","PE","Supervisor Fictício 3"],["Gisele Teste Alves","CE","Supervisor Fictício 1"],["Hugo Fictício Melo","MA","Supervisor Fictício 2"]];
  const C=[["nj",[0,0,3,5]],["at",[1,4,4,6,7]],["ap",[2,2,5,7]],["ou",[3,6]]],o=[];C.forEach(([c,ix],ci)=>ix.forEach((i,j)=>o.push({c,i,d:"2026-09-"+String(3+ci*5+j*2).padStart(2,"0")})));
  return N.map((n,i)=>{const p={k:"ex"+i,nome:n[0],uf:n[1],sup:n[2],niv:""},a={nj:[],at:[],ap:[],ou:[]};o.filter(x=>x.i===i).forEach(x=>a[x.c].push({d:x.d}));return[p,a]}).filter(y=>AUS.some(x=>y[1][x[0]].length))})();
const EXP='<span class="pill p-warn ex-pill">exemplo · dados fictícios</span>';
function ausDe(p){const o={nj:[],at:[],ap:[],ou:[]};((p.fal&&p.fal.list)||[]).forEach(x=>o[ausCat(x)].push(x));return o}
/* fuga de rota: posições fora da cerca, por dia, com a ocorrência de jornada do mesmo dia */
function rotaDet(p){const D=new Map(p.jor.dias.map(x=>[x.d,x]));return[...group(p.rota.list,x=>x.d)].sort((a,b)=>a[0]<b[0]?-1:1).slice(0,4).map(([d,v])=>{const j=D.get(d),oc=j?[j.atraso?"início tardio":"",j.saida?"saída antecipada":"",j.auto?"check-out automático":""].filter(Boolean):[],
  hs=v.map(x=>x.h).filter(x=>x!=null).sort((a,b)=>a-b);return fDc(d)+": "+v.length+(v.length>1?" posições":" posição")+" fora (até "+Math.round(Math.max(...v.map(x=>x.dist)))+" m"+(hs.length?", "+fH(hs[0])+(hs.length>1?"–"+fH(hs[hs.length-1]):""):"")+")"+(oc.length?" · no mesmo dia: "+oc.join(", "):"")}).join(" | ")+(new Set(p.rota.list.map(x=>x.d)).size>4?" | …":"")}
/* dossiê: texto factual para "foto da foto" (decisão do dono 24/11: rótulo da tela mantido; documento sem "falsa") */
function motDoc(m){return(m||[]).map(t=>/foto da foto/i.test(t)?"Imagem de outra tela"+(/hor[áa]rio/i.test(t)?" (captura fora do horário da visita)":""):t).join("; ")}
/* categorias de foto e de jornada */
const FOTC=[["rep","Imagem repetida",/repetida/i,"#E11D48"],["dist","Fora do raio da loja",/m da loja|raio|dist/i,"#F59E0B"],["falsa","Foto da foto (possível foto falsa)",/foto da foto|falsa|hor[áa]rio/i,"#8B5CF6"],["preta","Foto preta",/preta|escura/i,"#94A3B8"]];
const fotCat=f=>{const m=(f.mot||[]).join(" ");const c=["preta","falsa","rep","dist"].map(k=>FOTC.find(x=>x[0]===k)).find(x=>x[2].test(m));return c?c[0]:"out"};
const JORC=[["atr","Início tardio","#F4562A"],["sai","Saída antecipada","#F59E0B"],["auto","Check-out automático","#E11D48"]];
const jorN=(p,k)=>k==="atr"?p.jor.nAtr:k==="sai"?p.jor.nSai:p.jor.nAuto;
function humRows(){const r=R(),ks=new Set(r.list.map(p=>p.k));return((r.D||{}).humor||[]).filter(x=>ks.has(x.k)&&x.d>=S.f.ini&&x.d<=S.f.fim)}
const fmtP=v=>v==null?"—":String(Math.round(v*10)/10).replace(".",",")+"%";
function kpiVals(L){const s=f=>L.reduce((a,p)=>a+(f(p)||0),0),h=R().has,ct=s(p=>p.ad.ct),rz=s(p=>p.ad.rz),pg=s(p=>p.pes.prog),ex=s(p=>p.pes.exp),tr=s(p=>p.jor.trab),
    dc=s(p=>p.jor.dias.filter(x=>x.atraso||x.saida||x.auto).length),hd=s(p=>p.hum.dias),hn=s(p=>p.hum.neg),fn=s(p=>p.fotN),fs=s(p=>p.fot.length);
  const J={atr:s(p=>p.jor.nAtr),sai:s(p=>p.jor.nSai),auto:s(p=>p.jor.nAuto)},A={nj:0,at:0,ap:0,ou:0};L.forEach(p=>{const a=ausDe(p);for(const k in A)A[k]+=a[k].length});
  const na=A.nj+A.at+A.ap+A.ou,F={rep:0,dist:0,falsa:0,preta:0};L.forEach(p=>p.fot.forEach(f=>{const c=fotCat(f);if(c in F)F[c]++}));
  const op=[...group(humRows(),x=>x.op)].map(([o,v])=>[o,v.length]).sort((a,b)=>b[1]-a[1]),neg=new Set(S.cfg.neg.map(norm));
  const pa=L.filter(p=>p.ad.pct!=null),pe=L.filter(p=>p.pes.prog>=20);
  return{
    ader:{v:ct?rz/ct*100:null,big:num(rz)+" / "+num(ct),d:"visitas realizadas sobre contratadas",mix:[["Abaixo de 85%",pa.filter(p=>p.ad.pct*100<85).length,"#E11D48"],["85% a 93%",pa.filter(p=>p.ad.pct*100>=85&&p.ad.pct*100<93).length,"#F59E0B"],["Na meta",pa.filter(p=>p.ad.pct*100>=93).length,"#10B981"]],u:"promotores"},
    pesq:{v:pg?ex/pg*100:null,big:num(ex),d:"de "+num(pg)+" pesquisas expiraram",mix:[["Acima de 30%",pe.filter(p=>p.pes.pct*100>30).length,"#E11D48"],["20% a 30%",pe.filter(p=>p.pes.pct*100>20&&p.pes.pct*100<=30).length,"#F59E0B"],["Dias sem atividade",s(p=>p.pes.semExec.length),"#64748B"]],u:""},
    jor:{v:tr?dc/tr*100:null,big:num(J.atr+J.sai+J.auto),d:"ocorrências em "+num(tr)+" dias trabalhados",mix:JORC.filter(x=>x[0]!=="sai"||J.sai).map(x=>[x[1],J[x[0]],x[2]]),u:""},
    humor:{v:hd?hn/hd*100:null,big:num(hn),d:"respostas negativas de "+num(hd),mix:op.slice(0,4).map(([o,n])=>[o,n,neg.has(norm(o))?"#8B5CF6":"#10B981"]),u:""},
    foto:{v:fn?fs/fn*100:null,big:num(fs),d:"fotos com indício de "+num(fn)+" analisadas",mix:FOTC.filter(x=>F[x[0]]).map(x=>[x[1],F[x[0]],x[3]]).concat(h.rota&&s(p=>p.rota.dias)?[["Fuga de rota (cerca 200 m)",s(p=>p.rota.dias),"#F97316"]]:[]),u:""},
    aus:h.faltas?{v:(tr+na)?na/(tr+na)*100:null,big:num(na),d:"dias de ausência no período",mix:AUS.map(x=>[x[1],A[x[0]],x[2]]),u:""}:(()=>{const T={};AUS.forEach(x=>T[x[0]]=AUS_EX.reduce((a,y)=>a+y[1][x[0]].length,0));const n=Object.values(T).reduce((a,b)=>a+b,0);return{v:n/(AUS_EX.length*20+n)*100,ex:true,big:num(n),d:"exemplo com dados fictícios: carregue o export de afastamentos",mix:AUS.map(x=>[x[1],T[x[0]],x[2]]),u:""}})()}}
function paramsPainel(L){const V=kpiVals(L);
  return'<section class="card pp-side"><div class="hd"><h2>Parâmetros da operação</h2><small class="muted">clique num card para ver quem está em cada situação</small></div><div class="pp-grid">'+Object.entries(KPI).map(([k,d])=>{const x=V[k],v=x.v,ok=v==null?null:d.up?v>=d.meta:v<=d.meta,w=v==null?0:Math.min(100,d.up?v:v/Math.max(d.meta*2.2,v)*100),mk=d.up?d.meta:d.meta/Math.max(d.meta*2.2,v||0)*100;
    return'<button class="pp" style="--k:'+d.c+'" data-a="kpiM" data-v="'+k+'"><span class="pp-h"><span class="pp-ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="'+d.ic+'"/></svg></span><span class="pp-l">'+d.l+'</span><span class="pp-st '+(x.ex?"ex":ok==null?"":ok?"ok":"no")+'">'+(x.ex?"exemplo":ok==null?"sem dados":ok?"dentro":"fora")+'</span></span>'+
      '<span class="pp-vv"><span class="pp-v">'+fmtP(v)+'</span><span class="pp-n"><b>'+x.big+'</b>'+x.d+'</span></span>'+
      '<span class="pp-b"><i style="width:'+w+'%"></i><em style="left:'+mk+'%"></em></span>'+
      (x.mix.length?'<span class="pp-mix">'+x.mix.map(m=>'<span style="--m:'+m[2]+'"><i></i>'+esc(m[0])+' <b>'+num(m[1])+'</b></span>').join("")+'</span>':"")+
      '<small>'+d.t+' '+d.meta+'% · ver detalhes →</small></button>'}).join("")+'</div></section>'}
/* modal de indicador: números no topo, abas por categoria e a lista de promotores de cada aba */
function modalKpi(k,tiles,tabs,nota){const d=KPI[k],V=kpiVals(R().list)[k],el=document.createElement("div");el.className="modal lb";
  const tb=tabs.filter(t=>t.rows.length||t.fixa);
  el.innerHTML='<div class="box km kx" style="--k:'+d.c+'"><div class="lb-hd"><div><div class="eyebrow">Parâmetro da operação · '+d.t+' '+d.meta+'%</div><h2>'+d.l+' <span class="kx-v">'+fmtP(V.v)+'</span>'+(V.ex?EXP:"")+'</h2></div><button class="btn sec sm lb-x" aria-label="Fechar">✕</button></div>'+
    '<div class="kx-tiles">'+tiles.map(t=>'<div class="kx-t" style="--m:'+(t[2]||d.c)+'"><b>'+t[0]+'</b><span>'+t[1]+'</span></div>').join("")+'</div>'+
    (tb.length?'<div class="kx-tabs" role="tablist">'+tb.map((t,i)=>'<button class="kx-tab'+(i?"":" on")+'" role="tab" data-tab="'+i+'" style="--m:'+t.c+'"><i></i>'+esc(t.l)+' <b>'+num(t.n!=null?t.n:t.rows.length)+'</b></button>').join("")+'</div>'+
      tb.map((t,i)=>'<div class="km-l kx-p" data-p="'+i+'"'+(i?" hidden":"")+'>'+(t.rows.join("")||'<div class="nobase">Ninguém nesta situação.</div>')+'</div>').join(""):'<div class="nobase">'+(k==="aus"?"Sem base de ausências carregada. Use “Atualizar dados” com o export de afastamentos.":"Sem dados para os filtros escolhidos.")+'</div>')+
    '<div class="lb-ft"><span class="muted small">'+nota+'</span><button class="btn" data-a="setor" data-v="'+d.al+'">Ver alertas deste tipo →</button></div></div>';
  const fechar=()=>{el.remove();document.removeEventListener("keydown",ek)},ek=e=>{if(e.key==="Escape")fechar()};
  el.addEventListener("click",e=>{const t=e.target.closest(".kx-tab");if(t){el.querySelectorAll(".kx-tab").forEach(b=>b.classList.toggle("on",b===t));el.querySelectorAll(".kx-p").forEach(p=>p.hidden=p.dataset.p!==t.dataset.tab);return}
    if(e.target===el||e.target.closest(".lb-x"))fechar();else if(e.target.closest("[data-a]"))setTimeout(fechar,0)});
  document.addEventListener("keydown",ek);document.body.appendChild(el)}
function exRow(p,val,det,cor){return'<div class="kr ex-row"><span class="kr-av" style="background:var(--m2)">'+esc(p.nome[0]+p.nome.split(" ").pop()[0])+'</span><span class="kr-n"><b>'+esc(p.nome)+'</b><small>'+esc(p.uf)+' · '+esc(p.sup)+'</small><small class="kr-d">'+esc(det)+'</small></span><span class="kr-v" style="color:'+cor+'">'+val+'</span></div>'}
function kpiModal(k){const d=KPI[k];if(!d)return;const L=R().list,V=kpiVals(L)[k],neg=new Set(S.cfg.neg.map(norm)),dts=a=>a.slice(0,6).map(x=>fDc(x.d||x)).join(", ")+(a.length>6?" e mais "+(a.length-6):"");
  const tab=(l,c,ps,row,n)=>({l,c,rows:ps.map(row),n});let tiles=[],tabs=[],nota="Indícios para conferência antes de qualquer decisão.";
  if(k==="ader"){const pa=L.filter(p=>p.ad.pct!=null).sort((a,b)=>a.ad.pct-b.ad.pct),r=p=>kmRow(p,pc(p.ad.pct),num(p.ad.rz)+" de "+num(p.ad.ct)+" visitas · "+plural(p.ad.baixo.length,"loja","lojas")+" abaixo da meta · "+plural(p.ad.pend,"visita pendente","visitas pendentes"),p.ad.pct*100<85?"var(--bad)":p.ad.pct*100<93?"var(--warn)":"var(--good)");
    tiles=[[V.big,"visitas realizadas / contratadas"],[num(L.reduce((a,p)=>a+p.ad.baixo.length,0)),"lojas abaixo da meta","#E11D48"],[num(L.reduce((a,p)=>a+p.ad.pend,0)),"visitas pendentes","#F59E0B"]];
    tabs=[tab("Abaixo de 85%","#E11D48",pa.filter(p=>p.ad.pct*100<85),r),tab("85% a 93%","#F59E0B",pa.filter(p=>p.ad.pct*100>=85&&p.ad.pct*100<93),r),tab("Na meta (93% ou mais)","#10B981",pa.filter(p=>p.ad.pct*100>=93).reverse(),r)]}
  if(k==="pesq"){const pe=L.filter(p=>p.pes.prog>=20).sort((a,b)=>b.pes.pct-a.pes.pct),r=p=>kmRow(p,pc(p.pes.pct),num(p.pes.exp)+" de "+num(p.pes.prog)+" pesquisas expiradas",p.pes.pct*100>30?"var(--bad)":p.pes.pct*100>20?"var(--warn)":"var(--good)"),se=L.filter(p=>p.pes.semExec.length).sort((a,b)=>b.pes.semExec.length-a.pes.semExec.length);
    tiles=[[V.big,"pesquisas expiradas","#F59E0B"],[num(L.reduce((a,p)=>a+p.pes.prog,0)),"pesquisas programadas"],[num(L.reduce((a,p)=>a+p.pes.semExec.length,0)),"dias sem atividade","#64748B"]];
    tabs=[tab("Acima de 30%","#E11D48",pe.filter(p=>p.pes.pct*100>30),r),tab("20% a 30%","#F59E0B",pe.filter(p=>p.pes.pct*100>20&&p.pes.pct*100<=30),r),tab("Dias sem atividade","#64748B",se,p=>kmRow(p,p.pes.semExec.length,"Programadas e nenhuma respondida: "+dts(p.pes.semExec),"var(--ink)"))];
    nota="Considera só promotores com 20 ou mais pesquisas programadas no período."}
  if(k==="jor"){tiles=JORC.filter(x=>x[0]!=="sai"||L.some(p=>p.jor.nSai)).map(x=>[num(L.reduce((a,p)=>a+jorN(p,x[0]),0)),x[1].toLowerCase()+" · "+plural(L.filter(p=>jorN(p,x[0])).length,"promotor","promotores"),x[2]]);
    const det={atr:p=>plural(p.jor.nAtr,"início tardio","inícios tardios")+" · "+fDur(p.jor.minAtr)+" no total · "+dts(p.jor.dias.filter(x=>x.atraso)),sai:p=>plural(p.jor.nSai,"saída antecipada","saídas antecipadas")+" · "+dts(p.jor.dias.filter(x=>x.saida)),auto:p=>p.jor.nAuto+" de "+p.jor.trab+" dias sem check-out manual · "+dts(p.jor.dias.filter(x=>x.auto))};
    tabs=JORC.map(x=>tab(x[1],x[2],L.filter(p=>jorN(p,x[0])).sort((a,b)=>jorN(b,x[0])-jorN(a,x[0])),p=>kmRow(p,jorN(p,x[0]),det[x[0]](p),x[2])));
    nota="Início tardio: primeiro check-in depois da tolerância de "+S.cfg.tolAtr+" min. Check-out automático: jornada encerrada pelo sistema."}
  if(k==="humor"){const H=humRows(),byK=group(H,x=>x.k),P=new Map(L.map(p=>[p.k,p]));
    const ops=[...group(H,x=>x.op)].sort((a,b)=>(neg.has(norm(b[0]))-neg.has(norm(a[0])))||b[1].length-a[1].length);
    tiles=[[V.big,"respostas negativas","#8B5CF6"],[num(H.length),"respostas registradas"],[num(L.filter(p=>p.hum.neg).length),"promotores com humor negativo","#8B5CF6"],[num(L.filter(p=>p.hum.seq>=S.cfg.t.humSeq).length),"com "+S.cfg.t.humSeq+"+ dias negativos seguidos","#E11D48"]];
    tabs=ops.map(([o,v])=>{const ng=neg.has(norm(o)),pk=[...group(v,x=>x.k)].map(([kk,vv])=>[P.get(kk),vv]).filter(x=>x[0]).sort((a,b)=>b[1].length-a[1].length);
      return{l:o,c:ng?"#8B5CF6":"#10B981",n:pk.length,rows:pk.map(([p,vv])=>kmRow(p,vv.length+(vv.length>1?" dias":" dia"),dts(vv.slice().sort((a,b)=>a.d<b.d?-1:1))+" · "+plural((byK.get(p.k)||[]).length,"resposta","respostas")+" no período",ng?"var(--vio)":"var(--good)"))}});
    nota="Humor é contexto de acompanhamento e cuidado, nunca motivo de medida."}
  if(k==="foto"){tiles=[[V.big,"fotos com indício","#14B8A6"],...FOTC.map(x=>[num(L.reduce((a,p)=>a+p.fot.filter(f=>fotCat(f)===x[0]).length,0)),x[1].toLowerCase(),x[3]])].concat(R().has.rota?[[num(L.reduce((a,p)=>a+p.rota.dias,0)),"dias com fuga de rota (cerca "+S.cfg.cerca+" m)","#F97316"]]:[]);
    tabs=FOTC.map(x=>{const ps=L.map(p=>[p,p.fot.filter(f=>fotCat(f)===x[0])]).filter(y=>y[1].length).sort((a,b)=>b[1].length-a[1].length);return{l:x[1],c:x[3],n:ps.length,rows:ps.map(([p,fs])=>kmRow(p,fs.length,fs.length+" de "+p.fotN+" fotos · "+dts(fs)+" · "+[...new Set(fs.map(f=>(f.loja||"").replace(/^[A-Z]{2} \/ /,"")))].slice(0,2).join(", "),x[3]))}});
    if(R().has.rota){const ps=L.filter(p=>p.rota.dias).sort((a,b)=>b.rota.dias-a.rota.dias);
      tabs.push({l:"Fuga de rota (cerca "+S.cfg.cerca+" m)",c:"#F97316",n:ps.length,rows:ps.map(p=>kmRow(p,p.rota.dias+(p.rota.dias>1?" dias":" dia"),rotaDet(p),"#F97316"))})}
    nota="Fuga de rota: posição fora da cerca de "+S.cfg.cerca+" m da loja durante a jornada, cruzada com a ocorrência de jornada do mesmo dia."}
  if(k==="aus"){const ex=!R().has.faltas,AP=ex?AUS_EX:L.map(p=>[p,ausDe(p)]);
    tiles=[[V.big,"dias de ausência","#EC4899"],...AUS.map(x=>[num(AP.reduce((a,y)=>a+y[1][x[0]].length,0)),x[1].toLowerCase()+" · "+plural(AP.filter(y=>y[1][x[0]].length).length,"promotor","promotores"),x[2]])];
    tabs=AUS.map(x=>{const ps=AP.filter(y=>y[1][x[0]].length).sort((a,b)=>b[1][x[0]].length-a[1][x[0]].length);return{l:x[1],c:x[2],n:ps.length,rows:ps.map(([p,a])=>{const v=a[x[0]];return ex?exRow(p,v.length+(v.length>1?" dias":" dia"),dts(v),x[2]):kmRow(p,v.length+(v.length>1?" dias":" dia"),dts(v),x[2])})}});
    nota=ex?"EXEMPLO com nomes e números fictícios, só para mostrar como o detalhe vai funcionar. Some quando o export de afastamentos for carregado.":"Só falta não justificada gera alerta. Atestados e justificativas aparecem para acompanhamento."}
  modalKpi(k,tiles,tabs,nota)}
