"use strict";
/* RADAR PROMOTOR v2 · TELAS: Visão Geral, Alertas, Raio-X, Configurações e carga de dados */
const VIEWS=[["geral","Visão Geral"],["alertas","Alertas"],["raio-x","Raio-X"],["dossie","Dossiê"]];
const nivPill=n=>n?'<span class="pill '+NIV[n][2]+'">'+NIV[n][0]+'</span>':'<span class="pill p-good">Sem alertas</span>';
const kpi=(l,v,s,c)=>'<div class="kpi'+(c?" k-"+c:"")+'"><div class="kpi-l">'+l+'</div><div class="kpi-v">'+v+'</div><div class="kpi-s">'+s+'</div></div>';
const nb=b=>'<div class="nobase">Base não carregada: '+BASES[b]+'. Carregue em “Atualizar dados”.</div>';
const per=()=>fD(S.f.ini)+" a "+fD(S.f.fim);
const iniciais=n=>n.split(" ").filter(x=>x.length>2).slice(0,2).map(x=>x[0]).join("").toUpperCase();
const sum=(a,f)=>a.reduce((s,x)=>s+f(x),0);
function barras(itens,sm){const mx=Math.max(1,...itens.map(i=>i.v));return'<div class="bars'+(sm?" sm":"")+'">'+itens.map(i=>'<'+(i.a?'button data-a="'+i.a+'" data-v="'+esc(i.dv||"")+'"':'div')+' class="bar"><span>'+esc(i.l)+'</span><i><b style="width:'+(i.v/mx*100).toFixed(1)+'%;'+(i.cor?'background:'+i.cor:'')+'"></b></i><span>'+(i.t!=null?i.t:i.v)+'</span></'+(i.a?'button':'div')+'>').join("")+'</div>'}

/* ---------- estrutura: menu, filtros, banner ---------- */
function render(){
  const r=R(),v=S.view,crit=r.todos.filter(p=>p.niv==="C"||p.niv==="A").length;
  $("nav").innerHTML=VIEWS.map(x=>'<a href="#'+x[0]+'" class="'+(v===x[0]?"on":"")+'">'+x[1]+(x[0]==="alertas"&&crit?'<span class="n">'+crit+'</span>':"")+'</a>').join("");
  $("nav2").innerHTML='<button data-a="dados">Atualizar dados</button><a href="#config" class="'+(v==="config"?"on":"")+'">Configurações</a>';
  const p=pessoa();$("crumb").textContent=v==="raio-x"&&p?"Raio-X › "+p.nome:v==="dossie"&&S.dos?"Dossiê › "+S.dos.nome:(VIEWS.find(x=>x[0]===v)||["","Configurações"])[1];
  renderBanner();$("filters").hidden=v==="config";if(v!=="config")renderFiltros();renderView()}
function renderBanner(){$("banner").innerHTML=(S.demo?'<div class="banner"><b>Dados fictícios de demonstração.</b> Eles somem quando você carregar os arquivos reais em “Atualizar dados”.</div>':"")+(S.load?'<div class="banner" style="margin-top:8px">Carregando a base salva…</div>':"")+(S.msg?'<div class="banner" style="margin-top:8px">'+esc(S.msg)+' <button class="btn sm sec" data-a="fecharMsg">Fechar</button></div>':"")}
function renderFiltros(){const r=R(),f=S.f,anos=[...new Set([f.fim.slice(0,4),...Object.keys(S.meses).map(y=>y.slice(0,4))])].sort();
  const sel=(id,l,ops,val,todos)=>'<label class="f" for="f-'+id+'"><span>'+l+'</span><select id="f-'+id+'" data-f="'+id+'"><option value="">'+todos+'</option>'+ops.map(o=>'<option'+(o===val?" selected":"")+'>'+esc(o)+'</option>').join("")+'</select></label>';
  $("filters").innerHTML=sel("uf","UF",r.ufs,f.uf,"Todas")+sel("sup","Supervisor",r.sups,f.sup,"Todos")+
   '<label class="f" for="f-ini"><span>Data início</span><input type="date" id="f-ini" data-f="ini" value="'+f.ini+'"></label>'+
   '<label class="f" for="f-fim"><span>Data fim</span><input type="date" id="f-fim" data-f="fim" value="'+f.fim+'"></label>'+
   '<label class="f" for="f-ano"><span>Ano</span><select id="f-ano" data-f="ano">'+anos.map(a=>'<option'+(a===f.ano?" selected":"")+'>'+a+'</option>').join("")+'</select></label>'+
   '<label class="f grow" for="f-q"><span>Promotor</span><input id="f-q" data-f="q" list="plist" placeholder="Digite o nome ou o CPF" value="'+esc(f.q)+'" autocomplete="off"></label>'+
   '<datalist id="plist">'+r.todos.map(p=>'<option value="'+esc(p.nome)+'">'+esc(p.mat||"")+'</option>').join("")+'</datalist>'+
   '<button class="btn" data-a="dados">Atualizar dados</button>'}
function renderView(){const v=S.view;$("view").innerHTML=v==="geral"?vGeral():v==="alertas"?vAlertas():v==="raio-x"?vRaio():v==="dossie"?vDossie():vConfig()}

/* ---------- 1. Visão Geral: o essencial, em uma tela ---------- */
function vGeral(){const r=R(),L=r.list,h=r.has;
  if(!L.length)return'<div class="nobase">Nenhum promotor para este período e estes filtros.</div>';
  const prog=sum(L,p=>p.pes.prog),exp=sum(L,p=>p.pes.exp),ct=sum(L,p=>p.ad.ct),rz=sum(L,p=>p.ad.rz),hd=sum(L,p=>p.hum.dias),hn=sum(L,p=>p.hum.neg);
  const nC=L.filter(p=>p.niv==="C").length,nA=L.filter(p=>p.niv==="A").length,nT=L.filter(p=>p.niv==="T").length;
  const autoP=L.filter(p=>p.jor.nAuto>=S.cfg.t.auto[0]).length,fot=sum(L,p=>p.fot.length),doente=sum(L,p=>p.hum.doente);
  const tipos=Object.keys(TIPOS).map(t=>({l:TIPOS[t],v:L.filter(p=>p.alertas.some(a=>a.tipo===t)).length,a:"tipo",dv:t})).filter(x=>x.v>0).sort((a,b)=>b.v-a.v);
  const top=L.filter(p=>p.niv).slice(0,10);
  return'<div class="hero"><div class="eyebrow">RT Intelligence</div><h2>Visão Geral</h2><p>'+per()+' · '+num(L.length)+' promotores analisados</p></div>'+
  '<div class="kpis">'+
   kpi("Promotores com alerta",num(nC+nA),nC+" críticos · "+nA+" altos",nC?"bad":nA?"warn":"good")+
   kpi("Pesquisas expiradas",h.pesq?pc(prog?exp/prog:null):"—",h.pesq?num(exp)+" de "+num(prog):"base não carregada",h.pesq&&exp/prog>.2?"warn":"")+
   kpi("Aderência",h.ader?pc(ct?rz/ct:null):"—",h.ader?num(ct-rz)+" visitas pendentes":"base não carregada",h.ader&&rz/ct*100<S.cfg.m1?"bad":"")+
   kpi("Check-out automático",h.oper?num(autoP):"—",h.oper?"promotores com "+S.cfg.t.auto[0]+"+ dias":"base não carregada")+
   kpi("Fotos com indício",h.fotos?num(fot):"—",h.fotos?"para conferir":"base não carregada")+
   kpi("Humor negativo",h.humor?pc(hd?hn/hd:null,0):"—",h.humor?num(doente)+" dias “Doente”":"base não carregada")+
  '</div>'+
  '<div class="grid2"><section class="card"><div class="hd"><h2>Prioridade dos alertas</h2><button class="link" data-a="irAlertas">Ver todos os alertas →</button></div>'+
   '<div class="niv3">'+[["C",nC],["A",nA],["T",nT]].map(x=>'<button class="nv n-'+x[0]+'" data-a="niv" data-v="'+x[0]+'"><b>'+x[1]+'</b><span>'+NIV[x[0]][0]+'</span></button>').join("")+'</div>'+
   '<div class="small muted">Crítico: vários indícios graves ao mesmo tempo. Alto: indícios relevantes. Atenção: um ponto isolado.</div></section>'+
  '<section class="card"><h2>Alertas por tipo <small>promotores</small></h2>'+(tipos.length?barras(tipos):'<div class="small muted">Nenhum alerta no período.</div>')+'</section></div>'+
  '<section class="card"><div class="hd"><h2>Maior prioridade</h2><span class="small muted">clique para abrir o Raio-X</span></div>'+
  (top.length?'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Promotor</th><th>UF</th><th>Supervisor</th><th>Nível</th><th>Principais alertas</th></tr></thead><tbody>'+
   top.map(p=>'<tr class="click" data-a="abrir" data-v="'+esc(p.k)+'" tabindex="0"><td><b>'+esc(p.nome)+'</b></td><td>'+esc(p.uf||"—")+'</td><td>'+esc(p.sup||"—")+'</td><td>'+nivPill(p.niv)+'</td><td><div class="tags">'+p.alertas.slice(0,3).map(a=>'<span class="pill p-n">'+esc(a.tit)+'</span>').join("")+(p.alertas.length>3?'<span class="pill p-n">+'+(p.alertas.length-3)+'</span>':"")+'</div></td></tr>').join("")+'</tbody></table></div>':'<div class="small muted">Nenhum promotor com alerta.</div>')+'</section>'+
  (["ader","fotos","faltas","rota"].filter(b=>!h[b]).length?'<div class="small muted">Sem dados de: '+["ader","fotos","faltas","rota"].filter(b=>!h[b]).map(b=>BASES[b].toLowerCase()).join(", ")+'. Os alertas correspondentes só aparecem quando a base é carregada.</div>':"")}

/* ---------- 2. Alertas: por prioridade, um card por promotor ---------- */
function vAlertas(){const r=R(),L=r.list.filter(p=>p.niv),f=S.al,h=r.has;
  const tc=t=>L.filter(p=>p.alertas.some(a=>a.tipo===t)).length,nv=n=>L.filter(p=>p.niv===n).length;
  const filtrados=L.filter(p=>(!f.niv||p.niv===f.niv)&&(!f.tipo||p.alertas.some(a=>a.tipo===f.tipo)));
  let o='<div class="hero"><div class="eyebrow">RT Intelligence</div><h2>Alertas</h2><p>'+per()+' · '+num(L.length)+' promotores com alerta</p></div>'+
   '<div class="chips"><button class="chip'+(!f.niv?" on":"")+'" data-a="niv" data-v="">Todos <b>'+L.length+'</b></button>'+["C","A","T"].map(n=>'<button class="chip'+(f.niv===n?" on":"")+'" data-a="niv" data-v="'+n+'">'+NIV[n][0]+' <b>'+nv(n)+'</b></button>').join("")+'</div>'+
   '<div class="chips"><button class="chip'+(!f.tipo?" on":"")+'" data-a="tipo" data-v="">Todos os tipos</button>'+Object.keys(TIPOS).filter(t=>tc(t)>0).map(t=>'<button class="chip'+(f.tipo===t?" on":"")+'" data-a="tipo" data-v="'+t+'">'+TIPOS[t]+' <b>'+tc(t)+'</b></button>').join("")+'</div>';
  if(!h.rota)o+='<div class="small muted">Fuga de rota (posição fora da cerca de '+S.cfg.cerca+' m) aparece aqui quando a base de posição do Status Day é carregada.</div>';
  for(const n of["C","A","T"]){const g=filtrados.filter(p=>p.niv===n);if(!g.length)continue;const lim=S["m"+n]||12;
    o+='<div class="grp"><h3><span class="dot" style="background:'+NIV[n][1]+'"></span>'+NIV[n][0]+' <span class="muted">'+g.length+'</span></h3>'+
     g.slice(0,lim).map(p=>'<div class="pc"><span class="sv" style="background:'+NIV[n][1]+'"></span><div class="nm"><b>'+esc(p.nome)+'</b><span>'+esc(p.uf||"—")+' · '+esc(p.sup||"sem supervisor")+'</span></div>'+
      '<ul>'+p.alertas.filter(a=>!f.tipo||a.tipo===f.tipo).map(a=>'<li><span class="dot" style="background:'+(a.sev===3?"var(--bad)":a.sev===2?"var(--warn)":"var(--m2)")+'"></span><b>'+esc(a.tit)+'</b><span>'+esc(a.det)+'</span></li>').join("")+'</ul>'+
      '<button class="btn sm sec" data-a="abrir" data-v="'+esc(p.k)+'">Raio-X</button></div>').join("")+
     (g.length>lim?'<button class="btn sec" data-a="mais" data-v="'+n+'">Ver mais '+(g.length-lim)+'</button>':"")+'</div>'}
  if(!filtrados.length)o+='<div class="nobase">Nenhum alerta para este filtro.</div>';
  return o}

/* ---------- 3. Raio-X: diagnóstico do promotor, sem juízo de medida ---------- */
function vRaio(){const r=R(),p=pessoa(),h=r.has,c=S.cfg;
  if(!p)return'<div class="nobase">Nenhum promotor para este período e estes filtros.</div>';
  S.pk=p.k;const j=p.jor,pe=p.pes;
  const dias=[];for(let d=S.f.ini;d<=S.f.fim&&dias.length<62;d=addD(d,1))dias.push(d);
  const jm=new Map(j.dias.map(x=>[x.d,x])),fm=new Map(p.fal.list.map(x=>[x.d,x]));
  const strip=dias.map(d=>{const x=jm.get(d),f=fm.get(d),n=p.hum.map.get(d);let cl="sr",tt="sem registro";
    if(f&&f.tipo==="I"){cl="fa";tt="falta injustificada"}else if(f){cl="o1";tt=f.tipo==="A"?"atestado":"falta justificada"}
    else if(x){const k=(x.atraso?1:0)+(x.saida?1:0)+(x.auto?1:0);cl=k>=2?"o2":k===1?"o1":"ok";tt=[x.atraso?"atraso "+x.atraso+" min":"",x.saida?"saída "+x.saida+" min antes":"",x.auto?"check-out automático":""].filter(Boolean).join(", ")||"sem desvios"}
    return'<div class="dy '+cl+'" title="'+fD(d)+": "+tt+(n===true?"; humor negativo":"")+'"><b>'+d.slice(8)+'</b>'+dow(d)+(n===true?"<i></i>":"")+'</div>'}).join("");
  const sem=pe.sem.map(s=>({l:"S"+s.k,v:s.exp,t:s.exp+" de "+s.prog}));
  return'<section class="card"><div class="prof"><div class="av">'+esc(iniciais(p.nome))+'</div><div><h2>'+esc(p.nome)+'</h2><div class="row" style="margin-top:4px">'+nivPill(p.niv)+'<span class="small muted">'+per()+'</span></div></div><button class="btn" data-a="dossie">Gerar dossiê</button></div>'+
   '<div class="kv"><span>CPF <b>'+esc(p.mat||"não informado")+'</b></span><span>Supervisor <b>'+esc(p.sup||"—")+'</b></span><span>UF <b>'+esc(p.uf||"—")+'</b></span><span>Jornada <b>'+esc(p.jorTxt||"não cadastrada")+'</b> · início às '+fH(p.esc.ini)+'</span><span>Dias trabalhados <b>'+j.trab+'</b></span></div>'+
   '<div class="kv"><span>Lojas atendidas ('+p.lojas.length+'): '+esc(p.lojas.join(" · ")||"—")+'</span></div></section>'+
  '<div class="kpis">'+
   kpi("Pesquisas expiradas",h.pesq&&pe.prog?pc(pe.pct):"—",h.pesq?pe.exp+" de "+pe.prog:"sem base",pe.pct*100>c.t.exp[1]?"bad":pe.pct*100>c.t.exp[0]?"warn":"")+
   kpi("Aderência",h.ader&&p.ad.pct!=null?pc(p.ad.pct):"—",h.ader?p.ad.pend+" visitas pendentes":"sem base",p.ad.pct*100<c.m1?"bad":p.ad.pct*100<c.m2?"warn":"")+
   kpi("Check-out automático",h.oper?j.nAuto:"—","de "+j.trab+" dias",lvl(j.nAuto,c.t.auto)>=2?"bad":j.nAuto?"warn":"")+
   kpi("Atrasos · Saídas",h.oper?j.nAtr+" · "+j.nSai:"—","dias no período",lvl(Math.max(j.nAtr,j.nSai),c.t.atr)>=2?"warn":"")+
   kpi("Faltas",h.faltas?p.fal.I:"—",h.faltas?p.fal.J+" justificadas · "+p.fal.A+" atestados":"sem base",p.fal.I?"bad":"")+
   kpi("Humor negativo",h.humor&&p.hum.dias?pc(p.hum.pct,0):"—",h.humor?"maior sequência: "+p.hum.seq+" dia(s)":"sem base")+
  '</div>'+
  '<section class="card"><div class="hd"><h2>Alertas do promotor <small>'+p.alertas.length+'</small></h2></div>'+
   (p.alertas.length?'<div class="grp">'+p.alertas.map(a=>'<div class="row" style="align-items:baseline"><span class="dot" style="background:'+(a.sev===3?"var(--bad)":a.sev===2?"var(--warn)":"var(--m2)")+'"></span><b>'+esc(a.tit)+'</b><span class="muted">'+esc(a.det)+'</span><span class="pill p-n">prioridade '+SEVN[a.sev]+'</span></div>').join("")+'</div>':'<div class="small muted">Nenhum alerta neste período.</div>')+'</section>'+
  '<div class="grid2"><section class="card"><h2>Pesquisas expiradas por semana</h2>'+(h.pesq&&sem.length?barras(sem,true):nb("pesq"))+
   (pe.semExec.length?'<div class="small muted">Dias sem nenhuma atividade respondida: '+pe.semExec.map(fDc).join(", ")+'</div>':"")+'</section>'+
  '<section class="card"><h2>Lojas e aderência <small>Meta 1: '+c.m1+'% · Meta 2: '+c.m2+'%</small></h2>'+(!h.ader?nb("ader"):p.ad.lojas.length?'<div class="tbl-wrap" style="max-height:260px"><table class="tbl"><thead><tr><th>Loja</th><th class="num">Contr.</th><th class="num">Real.</th><th class="num">Aderência</th></tr></thead><tbody>'+
   p.ad.lojas.map(l=>'<tr'+(l.st&&l.st!=="ok"?' class="hl"':"")+'><td>'+esc(l.loja)+'</td><td class="num">'+l.ct+'</td><td class="num">'+l.rz+'</td><td class="num">'+pc(l.pct)+'</td></tr>').join("")+'</tbody></table></div>':'<div class="small muted">Sem aderência para este promotor.</div>')+'</section></div>'+
  '<section class="card"><h2>Dia a dia</h2><div class="days">'+strip+'</div><div class="leg"><span><i style="background:var(--good-bg)"></i>sem desvios</span><span><i style="background:var(--warn)"></i>um desvio</span><span><i style="background:var(--bad)"></i>desvios ou falta</span><span><i style="background:#A78BFA"></i>humor negativo</span></div></section>'+
  '<section class="card"><h2>Humor <small>contexto de acompanhamento</small></h2>'+(!h.humor?nb("humor"):!p.hum.dias?'<div class="small muted">Sem registros de humor.</div>':
   '<div class="kv"><span>Dias com registro <b>'+p.hum.dias+'</b></span><span>Dias negativos <b>'+p.hum.neg+' ('+pc(p.hum.pct,0)+')</b></span><span>Maior sequência negativa <b>'+p.hum.seq+'</b></span><span>Dias “Doente” <b>'+p.hum.doente+'</b></span></div>'+
   (p.cruz.length?p.cruz.map(t=>'<div class="cross"><b>Leitura cruzada:</b> '+esc(t)+'.</div>').join(""):"")+'<div class="small muted">O humor é contexto para ler os outros indicadores. Não é motivo de tratativa.</div>')+'</section>'}

/* ---------- Configurações ---------- */
function vConfig(){const c=S.cfg,r=R(),n=(id,l,v)=>'<label class="f" for="c-'+id+'"><span>'+l+'</span><input class="inp" id="c-'+id+'" type="number" value="'+v+'"></label>',t=(id,l,v)=>'<label class="f" for="c-'+id+'"><span>'+l+'</span><input class="inp" id="c-'+id+'" type="time" value="'+fH(v)+'"></label>';
  return'<div class="hero"><div class="eyebrow">RT Intelligence</div><h2>Configurações</h2></div>'+
  '<section class="card"><h2>Jornada e tolerâncias</h2><div class="form">'+t("ini","Início padrão",c.esc.ini)+t("fim","Fim padrão",c.esc.fim)+n("tolAtr","Atraso (min)",c.tolAtr)+n("tolSai","Saída antecipada (min)",c.tolSai)+'</div>'+
   '<h2>Jornada por promotor <small>substitui a padrão</small></h2><div class="row"><select class="inp" id="c-pk" aria-label="Promotor">'+r.todos.slice().sort((a,b)=>a.nome.localeCompare(b.nome)).map(p=>'<option value="'+esc(p.k)+'">'+esc(p.nome)+'</option>').join("")+'</select><input class="inp" id="c-pini" type="time" value="'+fH(c.esc.ini)+'" aria-label="Início"><input class="inp" id="c-pfim" type="time" value="'+fH(c.esc.fim)+'" aria-label="Fim"><button class="btn sec" data-a="escAdd">Definir</button></div>'+
   (Object.keys(c.escP).length?'<div class="tbl-wrap"><table class="tbl"><tbody>'+Object.keys(c.escP).map(k=>'<tr><td>'+esc((r.todos.find(p=>p.k===k)||{nome:k}).nome)+'</td><td>'+fH(c.escP[k].ini)+'–'+fH(c.escP[k].fim)+'</td><td><button class="btn sm sec" data-a="escDel" data-v="'+esc(k)+'">Remover</button></td></tr>').join("")+'</tbody></table></div>':'<div class="small muted">Todos usam a jornada padrão.</div>')+'</section>'+
  '<section class="card"><h2>Metas, fotos e rota</h2><div class="form">'+n("m1","Meta 1 de aderência (%)",c.m1)+n("m2","Meta 2 de aderência (%)",c.m2)+n("distFoto","Foto fora da loja (m)",c.distFoto)+n("cerca","Cerca de rota (m)",c.cerca)+'</div></section>'+
  '<section class="card"><h2>Feriados <small>sem avaliação de atraso e saída</small></h2><label class="f" for="c-fer"><span>Uma data por linha (dd/mm/aaaa)</span><textarea class="inp" id="c-fer" rows="4">'+c.fer.map(fD).join("\n")+'</textarea></label></section>'+
  '<section class="card"><h2>Humor</h2><label class="f" for="c-neg"><span>Opções tratadas como negativas (separadas por vírgula)</span><input class="inp" id="c-neg" value="'+esc(c.neg.join(", "))+'"></label><div class="small muted">O relatório de humor também traz Luto, Incomodado, Não Valorizado e Estressado. Inclua aqui as que a área decidir.</div></section>'+
  '<section class="card"><h2>Como os alertas são classificados</h2><div class="small muted" style="display:grid;gap:4px"><span>Cada indício recebe prioridade <b>baixa</b>, <b>média</b> ou <b>alta</b> conforme a quantidade de dias ou o percentual: atrasos a partir de 4, 7 e 10 dias (em relação ao início da jornada cadastrada); check-out automático a partir de 5, 8 e 10 dias; pesquisas expiradas acima de 20%, 30% e 45% (mínimo de 20 pesquisas); dias sem atividades a partir de 2 e 4; faltas injustificadas a partir de 1 e 3; fotos com indício a partir de 1 e 3; fuga de rota a partir de 3 e 10 dias.</span><span>O nível do promotor soma as prioridades: <b>Crítico</b> com pontuação 9 ou mais, ou dois indícios de prioridade alta; <b>Alto</b> a partir de 5; <b>Atenção</b> a partir de 3. Promotores com poucos indícios de prioridade baixa não entram na lista.</span><span>A saída antecipada não é avaliada, porque o horário de término da jornada não está cadastrado. Fotos escuras ou ilegíveis ainda dependem de conferência visual.</span></div></section>'+
  '<div class="row"><button class="btn" data-a="cfgSalvar">Salvar configurações</button><button class="btn sec" data-a="cfgPadrao">Restaurar padrão</button><span class="small muted" id="c-msg"></span></div>'}
function lerConfig(){const c=S.cfg,v=id=>$("c-"+id).value,nn=(id,d)=>{const x=parseFloat(v(id));return isNaN(x)?d:x},tt=(id,d)=>{const x=tOut(v(id));return x==null?d:x};
  c.esc={ini:tt("ini",480),fim:tt("fim",1050)};c.tolAtr=nn("tolAtr",15);c.tolSai=nn("tolSai",15);c.m1=nn("m1",85);c.m2=nn("m2",93);c.distFoto=nn("distFoto",300);c.cerca=nn("cerca",200);
  c.fer=v("fer").split(/\n+/).map(pDate).filter(Boolean);c.neg=v("neg").split(",").map(s=>s.trim()).filter(Boolean)}

/* ---------- Atualizar dados ---------- */
function modalDados(log){const m=S.meses,yms=Object.keys(m).sort();
  $("modal").innerHTML='<div class="modal" data-a="fecharFora"><div class="box" role="dialog" aria-label="Atualizar dados"><div class="row" style="justify-content:space-between"><h2>Atualizar dados</h2><button class="btn sec sm" data-a="fecharModal">Fechar</button></div>'+
   '<div class="small muted">Selecione uma ou várias planilhas exportadas (.xlsx, .xls ou .csv), em qualquer ordem. O sistema identifica cada base pelo cabeçalho e guarda os dados por mês'+(db?"":" (nesta visualização a base não está disponível: os dados valem só até fechar a página)")+'.</div>'+
   '<div class="row"><input type="file" id="arq" multiple accept=".xlsx,.xls,.csv,.txt" class="inp" style="height:auto;padding:8px"><span id="arq-st" class="small muted"></span></div>'+
   (log?'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Arquivo</th><th>Base</th><th class="num">Linhas</th><th>Meses</th></tr></thead><tbody>'+log.map(l=>'<tr><td>'+esc(l.arq)+'</td><td>'+(l.base?esc(BASES[l.base]):'<span class="t-bad">não reconhecido</span><div class="muted small">'+esc(l.cab||"")+'</div>')+'</td><td class="num">'+(l.base?l.n:"")+'</td><td>'+esc(l.meses||"")+'</td></tr>').join("")+'</tbody></table></div>':"")+
   '<h2>Dados carregados'+(S.demo?' <small>(demonstração)</small>':"")+'</h2>'+(yms.length?yms.map(ym=>'<div class="base"><b>'+ym.slice(5)+'/'+ym.slice(0,4)+'</b><span class="muted">'+Object.keys(m[ym]).map(b=>BASES[b]+" ("+num(m[ym][b].n)+")").join(" · ")+'</span></div>').join(""):'<div class="small muted">Nada carregado.</div>')+
   (!S.demo&&yms.length?'<div class="row"><select class="inp" id="lm-ym" aria-label="Mês">'+yms.map(y=>'<option>'+y+'</option>').join("")+'</select><button class="btn sec sm" data-a="limparMes">Apagar este mês</button><span class="small muted" id="lm-st"></span></div>':"")+'</div></div>'}
async function importar(files){const st=$("arq-st"),log=[];st.textContent="Lendo arquivos…";
  try{const acc={};
    for(const f of files){let res;try{res=await lerArquivo(f)}catch(e){log.push({arq:f.name,base:null,cab:"não foi possível abrir o arquivo"});continue}
      for(const r of res){if(!r.base){log.push(r);continue}const g=group(r.rows,x=>x.d.slice(0,7));
        for(const[ym,rows]of g){const a=(acc[ym]=acc[ym]||{});(a[r.base]=a[r.base]||{rows:[],arq:r.arq}).rows.push(...rows)}
        log.push({arq:r.arq,base:r.base,n:r.rows.length,meses:[...g.keys()].sort().map(y=>y.slice(5)+"/"+y.slice(0,4)).join(", ")||"nenhuma linha válida"})}}
    const yms=Object.keys(acc).sort();
    if(yms.length){if(S.demo){S.demo=false;S.all={};S.meses={}}
      for(const ym of yms){await carregarMes(ym);for(const b in acc[ym]){st.textContent="Salvando "+BASES[b]+" de "+ym.slice(5)+"/"+ym.slice(0,4)+"…";await salvarBase(ym,b,acc[ym][b].rows,acc[ym][b].arq)}}
      faixaPadrao();S.f.uf="";S.f.sup="";S.f.q="";S.R=null;S.pk=null;S.dos=null;await carregarFaixa()}
  }catch(e){S.msg="Falha ao salvar os dados ("+(e.code||e.message||"erro")+"). Os dados lidos valem só nesta sessão."}
  S.R=null;render();modalDados(log)}

/* ---------- navegação e eventos ---------- */
function rota(){const h=location.hash.replace("#","");S.view=VIEWS.some(v=>v[0]===h)||h==="config"?h:"geral";$("side").classList.remove("open");render()}
function ir(v){if(location.hash==="#"+v){S.view=v;render()}else location.hash=v;window.scrollTo(0,0)}
window.addEventListener("hashchange",rota);
$("burger").addEventListener("click",()=>$("side").classList.toggle("open"));
$("scrim").addEventListener("click",()=>$("side").classList.remove("open"));
$("theme").addEventListener("click",()=>{const el=document.documentElement,cur=el.dataset.theme||(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark"),nx=cur==="dark"?"light":"dark";el.dataset.theme=nx;try{localStorage.setItem("rp-tema",nx)}catch(e){}});
try{const t=localStorage.getItem("rp-tema");if(t)document.documentElement.dataset.theme=t}catch(e){}
let tq=null;
async function refazer(){S.R=null;S.load=true;render();try{await carregarFaixa()}catch(e){}S.load=false;S.R=null;render()}
document.addEventListener("input",ev=>{const t=ev.target;
  if(t.dataset.f==="q"){S.f.q=t.value;clearTimeout(tq);tq=setTimeout(()=>{S.R=null;renderView()},200)}
  else if(t.dataset.d&&S.dos){S.dos[t.dataset.d]=t.value;if($("d-av"))$("d-av").innerHTML=avisoHtml(avisos(S.dos))}
  else if(t.dataset.b!=null&&S.dos){S.dos.blocos[+t.dataset.b].txt=t.value;if($("d-av"))$("d-av").innerHTML=avisoHtml(avisos(S.dos))}
  else if(t.id==="d-relato"&&S.dos)S.dos.relato=t.value});
document.addEventListener("change",async ev=>{const t=ev.target,f=t.dataset.f;
  if(t.id==="arq"){if(t.files.length)importar([...t.files]);return}
  if(t.dataset.conc!=null&&S.dos){S.dos.blocos[+t.dataset.conc].conc=+t.value;return}
  if(!f)return;
  if(f==="q"){const m=R().todos.find(p=>p.nome===t.value);if(m){S.pk=m.k;S.f.q="";S.dos=null;S.R=null;ir("raio-x")}return}
  if(f==="uf"||f==="sup"){S.f[f]=t.value;S.R=null;render();return}
  if(f==="ini"||f==="fim"){if(!t.value)return;S.f[f]=t.value;if(S.f.ini>S.f.fim){S.f[f==="ini"?"fim":"ini"]=t.value}S.f.ano=S.f.fim.slice(0,4);S.dos=null;await refazer();return}
  if(f==="ano"){S.f.ano=t.value;S.f.ini=t.value+"-01-01";S.f.fim=t.value+"-12-31";let mx="";for(const ym in S.meses)for(const b in S.meses[ym])if(S.meses[ym][b].dmax>mx)mx=S.meses[ym][b].dmax;if(mx&&S.f.fim>mx&&mx.slice(0,4)===t.value)S.f.fim=mx;S.dos=null;await refazer()}});
document.addEventListener("keydown",ev=>{if(ev.key==="Enter"&&ev.target.matches("tr.click"))ev.target.click();if(ev.key==="Escape")$("modal").innerHTML=""});
document.addEventListener("click",async ev=>{const b=ev.target.closest("[data-a]");if(!b)return;const a=b.dataset.a,v=b.dataset.v;
  if(a==="fecharFora"){if(ev.target===b)$("modal").innerHTML="";return}
  if(a==="abrir"){S.pk=v;S.dos=null;ir("raio-x")}
  else if(a==="irAlertas"){S.al={niv:"",tipo:""};ir("alertas")}
  else if(a==="niv"){S.al.niv=v;ir("alertas")}
  else if(a==="tipo"){S.al.tipo=v;if(S.view!=="alertas")S.al.niv="";ir("alertas")}
  else if(a==="mais"){S["m"+v]=(S["m"+v]||12)+30;renderView()}
  else if(a==="dados")modalDados();
  else if(a==="fecharModal")$("modal").innerHTML="";
  else if(a==="fecharMsg"){S.msg="";renderBanner()}
  else if(a==="limparMes"){if(b.dataset.ok!=="1"){b.dataset.ok="1";b.textContent="Confirmar: apagar";return}
    const ym=$("lm-ym").value;$("lm-st").textContent="Apagando…";try{await limparMes(ym)}catch(e){S.msg="Não foi possível apagar tudo ("+(e.code||"erro")+")."}
    if(!Object.keys(S.meses).length){S.demo=true;demo()}else faixaPadrao();S.R=null;S.pk=null;S.dos=null;$("modal").innerHTML="";await refazer()}
  else if(a==="dossie"){const p=pessoa();if(p){S.dos=montarDossie(p,"");ir("dossie")}}
  else if(a==="voltarRaio")ir("raio-x");
  else if(a==="aplicarRelato"){const num=S.dos.num;S.dos=montarDossie(pessoa(),$("d-relato").value);S.dos.num=num;renderView()}
  else if(a==="pdf"||a==="xlsx"){const st=$("d-st");b.disabled=true;st.textContent="Gerando o arquivo…";
    try{const f=a==="pdf"?await gerarPDF():await gerarExcel(),ok=await baixar(f.nome,f.data);st.textContent=ok?"Arquivo gerado: "+f.nome:"Download cancelado."}catch(e){st.textContent="Não foi possível gerar o arquivo ("+(e.message||e.code||"erro")+")."}
    b.disabled=false}
  else if(a==="cfgSalvar"){lerConfig();S.R=null;S.dos=null;await salvarCfg();render();$("c-msg").textContent="Configurações salvas"+(db?".":" (valem só nesta sessão).")}
  else if(a==="cfgPadrao"){const ep=S.cfg.escP;S.cfg=JSON.parse(JSON.stringify(CFG0));S.cfg.escP=ep;S.R=null;await salvarCfg();render();$("c-msg").textContent="Padrão restaurado."}
  else if(a==="escAdd"){const i=tOut($("c-pini").value),f=tOut($("c-pfim").value);if(i!=null&&f!=null&&f>i){const k=$("c-pk").value;lerConfig();S.cfg.escP[k]={ini:i,fim:f};S.R=null;await salvarCfg();render()}}
  else if(a==="escDel"){lerConfig();delete S.cfg.escP[v];S.R=null;await salvarCfg();render()}});

demo();rota();iniciarBase();
