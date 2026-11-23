/* ---------- extras v3: eventos (feed de alertas), filtros leves, leitura automática ---------- */
const cpfM=c=>/^\d{3}\.\d{3}\.\d{3}-\d{2}$/.test(c||"")?"***."+c.slice(4,11)+"-**":(c||"");
const ymAtual=()=>{const ms=mesesEntre(S.f.ini,S.f.fim).filter(y=>S.meses[y]);return ms[ms.length-1]||Object.keys(S.meses).sort().pop()||"2026-09"};
function eventosDe(o,cfg,T){const E=[],ts=new Set(o.alertas.map(a=>a.tipo)),sv=t=>Math.max(0,...o.alertas.filter(a=>a.tipo===t).map(a=>a.sev)),e=o.esc,fim=S.f.fim;
  const ad=(tipo,sev,d,tit,desc,ex)=>E.push(Object.assign({k:o.k,nome:o.nome,sup:o.sup,uf:o.uf,niv:o.niv,tipo,sev,d,tit,desc},ex||{}));
  if(ts.has("jor"))o.jor.dias.forEach(x=>{
    if(x.atraso)ad("jor",sv("jor"),x.d,"Atraso de "+x.atraso+" min","Primeiro check-in às "+fH(x.cin)+" · jornada iniciada às "+fH(e.ini));
    if(x.saida)ad("jor",sv("jor"),x.d,"Saída antecipada de "+fDur(x.saida),"Check-out às "+fH(x.cout)+" · jornada até "+fH(e.fim))});
  if(ts.has("auto"))o.jor.dias.filter(x=>x.auto).forEach(x=>ad("auto",sv("auto"),x.d,"Check-out automático","Último check-in às "+fH(x.vs[x.vs.length-1].cin)+" · sem encerramento manual da jornada"));
  if(ts.has("pesq"))o.pes.sem.forEach(s=>{const r=s.prog?s.exp/s.prog:0;if(s.prog>=5&&r*100>T.exp[0]){const d=o.pes.dia.filter(x=>isoWeek(x.k)===s.k).map(x=>x.k).sort().pop()||fim;
    ad("pesq",sv("pesq"),d,"Semana "+s.k+": "+pc(r)+" de pesquisas expiradas",s.exp+" de "+s.prog+" programadas não foram respondidas")}});
  if(ts.has("exec"))o.pes.semExec.forEach(d=>ad("exec",sv("exec"),d,"Dia sem atividades","Havia atividades programadas e nenhuma foi respondida"));
  if(ts.has("falta"))o.fal.list.filter(x=>x.tipo==="I").forEach(x=>ad("falta",sv("falta"),x.d,"Falta injustificada",x.motivo||"Sem motivo registrado"));
  if(ts.has("foto"))o.fot.forEach(f=>ad("foto",sv("foto"),f.d,f.mot[0],(f.loja||"loja não informada")+" · "+(f.pesq||"pesquisa")+(f.h!=null?" · "+fH(f.h):""),{foto:f}));
  if(ts.has("ader")&&o.ad.baixo.length){const b=o.ad.baixo,w=b[0],nl=b.length;
    ad("ader",sv("ader"),fim,nl>1?"Aderência abaixo da meta em "+nl+" lojas":"Aderência de "+pc(w.pct)+" em "+w.loja.replace(/^[A-Z]{2} \/ /,""),(nl>1?"Pior: "+w.loja.replace(/^[A-Z]{2} \/ /,"")+" com "+pc(w.pct)+" · ":"")+plural(o.ad.pend,"visita pendente","visitas pendentes")+" no total")}
  if(ts.has("rota"))[...group(o.rota.list,x=>x.d)].forEach(([d,v])=>ad("rota",sv("rota"),d,"Fuga de rota",v.length+" posições fora da cerca de "+cfg.cerca+" m · maior distância "+Math.round(Math.max(...v.map(x=>x.dist)))+" m"));
  ["sobre","humor"].forEach(t=>{if(ts.has(t)){const a=o.alertas.find(x=>x.tipo===t);ad(t,a.sev,o.hum.seqFim||fim,a.tit,a.det)}});
  return E}
function filtrar(){const P=S.PL,list=P.list,R=P.R,ini=S.f.ini,fim=S.f.fim,ord={C:0,A:1,T:2,"":3};
  const q=norm(S.f.q),qd=S.f.q.replace(/\D/g,"");
  const base=list.filter(p=>(!S.f.uf||p.uf===S.f.uf)&&(!S.f.sup||p.sup===S.f.sup));
  const vis=base.filter(p=>!q||norm(p.nome).includes(q)||(qd.length>2&&(p.mat||"").replace(/\D/g,"").includes(qd))).sort((a,b)=>ord[a.niv]-ord[b.niv]||b.score-a.score||b.risco-a.risco||a.nome.localeCompare(b.nome));
  const ks=new Set(vis.map(p=>p.k)),Wm=new Map(),wk=d=>{const m=mondayOf(d);let w=Wm.get(m);if(!w)Wm.set(m,w={m,ct:0,rz:0,prog:0,resp:0,exp:0,hd:0,hn:0,oc:0,atr:0,sai:0,auto:0,fot:0});return w};
  R.ader.filter(r=>ks.has(r.k)).forEach(r=>{const w=wk(r.d);w.ct+=r.ct;w.rz+=r.rz});
  R.pesq.filter(r=>ks.has(r.k)).forEach(r=>{const w=wk(r.d);w.prog++;if(r.st==="R")w.resp++;if(r.st==="E")w.exp++});
  vis.forEach(p=>{p.hum.map.forEach((n,d)=>{const w=wk(d);w.hd++;if(n)w.hn++});p.jor.dias.forEach(x=>{if(x.atraso||x.saida||x.auto)wk(x.d).oc++;if(x.atraso)wk(x.d).atr++;if(x.saida)wk(x.d).sai++;if(x.auto)wk(x.d).auto++});p.fot.forEach(f=>wk(f.d).fot++)});
  const semanas=[...Wm.values()].filter(w=>w.m>=addD(ini,-6)&&w.m<=fim).sort((a,b)=>a.m<b.m?-1:1);
  const dowC=[0,0,0,0,0,0,0];vis.forEach(p=>p.jor.dias.forEach(x=>{if(x.atraso||x.saida||x.auto)dowC[new Date(x.d+"T12:00:00").getDay()]++}));
  let nN=0,oN=0,nP=0,oP=0;vis.forEach(p=>p.jor.dias.forEach(x=>{if(!p.hum.map.has(x.d))return;const o=!!(x.atraso||x.saida||x.auto);if(x.neg){nN++;if(o)oN++}else{nP++;if(o)oP++}}));
  const alertas=[].concat(...vis.map(p=>p.ev)).sort((a,b)=>b.sev-a.sev||ord[a.niv]-ord[b.niv]||(a.d<b.d?1:-1));
  S.R={has:P.has,D:R,list:vis,base,todos:list,semanas,dowC,alertas,hx:{nN,oN,nP,oP},N:{C:vis.filter(p=>p.niv==="C").length,A:vis.filter(p=>p.niv==="A").length,T:vis.filter(p=>p.niv==="T").length},
    ufs:[...new Set(list.map(p=>p.uf).filter(Boolean))].sort(),sups:[...new Set(list.filter(p=>!S.f.uf||p.uf===S.f.uf).map(p=>p.sup).filter(Boolean))].sort()}}
const R=()=>{if(!S.R){if(!S.PL)calcular();filtrar()}return S.R};
const pessoa=()=>{const r=R();return(S.pk&&r.todos.find(p=>p.k===S.pk))||r.list[0]||null};

/* Leitura automática: frases calculadas a partir dos dados do filtro */
function insights(){const r=R(),L=r.list,c=S.cfg,out=[],add=(cor,txt)=>out.push([cor,txt]);if(!L.length)return out;
  const oc=L.map(p=>[p,p.jor.nAtr+p.jor.nSai+p.jor.nAuto]).sort((a,b)=>b[1]-a[1]),tot=oc.reduce((a,x)=>a+x[1],0);
  if(tot>=10&&L.length>3&&oc.slice(0,3).reduce((a,x)=>a+x[1],0)/tot>=.3){const t3=oc.slice(0,3),s3=t3.reduce((a,x)=>a+x[1],0);add("var(--bad)","<b>"+pc(s3/tot,0)+"</b> das ocorrências de jornada (atrasos e check-out automático) estão concentradas em 3 promotores: "+t3.map(x=>esc(x[0].nome.split(" ")[0])).join(", ")+".")}
  const sw=r.semanas.filter(w=>w.prog>=50);if(sw.length>1){const pior=sw.slice().sort((a,b)=>b.exp/b.prog-a.exp/a.prog)[0],med=sw.reduce((a,w)=>a+w.exp,0)/sw.reduce((a,w)=>a+w.prog,0);
    if(pior.exp/pior.prog>med*1.3)add("var(--warn)","A semana <b>S"+isoWeek(pior.m)+"</b> teve <b>"+pc(pior.exp/pior.prog)+"</b> de pesquisas expiradas, contra média de "+pc(med)+" no período.")}
  const h=r.hx;if(h.nN>=20&&h.nP>=20){const tn=h.oN/h.nN,tp=h.oP/h.nP;if(tp>0&&tn/tp>=1.3)add("var(--vio)","Em dias com humor negativo, a chance de atraso ou check-out automático é <b>"+(tn/tp).toFixed(1).replace(".",",")+"x maior</b> ("+pc(tn,0)+" contra "+pc(tp,0)+"). Contexto para entender a carga de trabalho, não motivo de tratativa.");
    else if(tn>0)add("var(--vio)","Ocorrências de jornada em dias com humor negativo: <b>"+pc(tn,0)+"</b>; em dias positivos: "+pc(tp,0)+".")}
  const au=L.reduce((a,p)=>a+p.jor.nAuto,0),pa=L.filter(p=>p.jor.nAuto>=c.t.auto[0]).length;if(au)add("var(--bad)","<b>"+num(au)+"</b> dias com check-out automático no período; <b>"+plural(pa,"promotor","promotores")+"</b> com "+c.t.auto[0]+" ou mais.");
  const dw=r.dowC,mx=Math.max(...dw);if(mx>=10){const i=dw.indexOf(mx),t=dw.reduce((a,b)=>a+b,0);add("var(--warn)","<b>"+["Domingo","Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado"][i]+"</b> concentra "+pc(mx/t,0)+" das ocorrências de jornada.")}
  const lj=[].concat(...L.map(p=>p.ad.lojas.map(l=>Object.assign({p},l)))).filter(l=>l.pct!=null&&l.pct*100<c.m1).sort((a,b)=>a.pct-b.pct);if(lj.length)add("var(--bad)","<b>"+plural(lj.length,"loja","lojas")+"</b> abaixo da Meta 1 ("+c.m1+"%). Pior resultado: "+esc(lj[0].loja)+" com <b>"+pc(lj[0].pct)+"</b>.");
  const fd=L.reduce((a,p)=>a+p.fot.filter(f=>f.mot.some(m=>/repetida/.test(m))).length,0),ff=L.reduce((a,p)=>a+p.fot.filter(f=>f.mot.some(m=>/m da loja/.test(m))).length,0);if(fd||ff)add("var(--bad)","Fotos com indício: <b>"+fd+"</b> repetidas e <b>"+ff+"</b> tiradas fora do raio de "+c.distFoto+" m da loja.");
  const rt=L.reduce((a,p)=>a+p.rota.dias,0);if(rt)add("var(--bad)","<b>"+plural(rt,"dia","dias")+"</b> com fuga de rota (posição a mais de "+c.cerca+" m da loja).");
  const sb=L.filter(p=>p.sobre);if(sb.length)add("var(--vio)","<b>"+plural(sb.length,"promotor","promotores")+"</b> com indício de sobrecarga (carga de visitas com queda de aderência e/ou humor negativo recorrente). Verificar a carga de trabalho antes de qualquer conclusão.");
  return out.slice(0,8)}
