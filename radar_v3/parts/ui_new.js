/* ---------- Interface v3: layout original + melhorias ---------- */
const nivPill=n=>n?'<span class="pill '+NIV[n][2]+'">'+NIV[n][0]+'</span>':'<span class="pill p-good">Estável</span>';
const clsPill=p=>nivPill(p.niv)+(p.sobre?' <span class="pill p-vio">Sobrecarga</span>':"");
const periodoTxt=()=>fD(S.f.ini)+" a "+fD(S.f.fim);
const per=periodoTxt;
const SEV={3:["Alta","var(--bad)","p-bad"],2:["Média","var(--warn)","p-warn"],1:["Baixa","var(--m2)","p-m2"]};

function renderFiltros(){const r=R(),f=S.f,anos=[...new Set([f.fim.slice(0,4),...Object.keys(S.meses).map(y=>y.slice(0,4))])].sort();
  const sel=(id,lab,opts,val,all)=>'<label class="f" for="f-'+id+'"><span>'+lab+'</span><select id="f-'+id+'" data-f="'+id+'"><option value="">'+all+'</option>'+opts.map(o=>'<option'+(o===val?" selected":"")+'>'+esc(o)+'</option>').join("")+'</select></label>';
  $("filters").innerHTML=sel("uf","UF",r.ufs,f.uf,"Todas")+sel("sup","Supervisor",r.sups,f.sup,"Todos")+
    '<label class="f" for="f-ini"><span>Data início</span><input type="date" id="f-ini" data-f="ini" value="'+f.ini+'"></label><label class="f" for="f-fim"><span>Data fim</span><input type="date" id="f-fim" data-f="fim" value="'+f.fim+'"></label>'+
    '<label class="f" for="f-ano"><span>Ano</span><select id="f-ano" data-f="ano">'+anos.map(a=>'<option'+(a===f.ano?" selected":"")+'>'+a+'</option>').join("")+'</select></label>'+
    '<label class="f prom grow" for="f-q"><span>Promotor (nome ou CPF)</span><input id="f-q" data-f="q" placeholder="Digite o nome ou o CPF" value="'+esc(f.q)+'" autocomplete="off"></label>'+
    '<span class="sp"></span><button class="btn" data-a="dados">'+IC.up+'Atualizar dados</button>'}
function renderBanner(){$("banner").innerHTML=(S.demo?'<div class="banner"><b>Dados fictícios de demonstração.</b> Eles somem quando você carregar os arquivos reais em “Atualizar dados”.</div>':"")+(S.load?'<div class="banner" style="margin-top:8px">Carregando a base salva…</div>':"")+(S.msg?'<div class="banner" style="margin-top:8px">'+esc(S.msg)+' <button class="btn sec sm" data-a="fecharMsg">Fechar</button></div>':"")}
function render(){const v=S.view,r=R(),na=r.N.C+r.N.A;
  const lk=(x,i)=>'<a href="#'+x[0]+'" class="'+(v===x[0]?"active":"")+'">'+(i!=null?"":IC[x[0]])+(i!=null?'<b>'+(i+1)+'</b>':"")+esc(x[1])+(x[0]==="alertas"&&na?'<span class="n">'+na+'</span>':"")+'</a>';
  $("nav").innerHTML=VIEWS.map(x=>lk(x)).join("");$("nav2").innerHTML=lk(["config","Configurações"]);
  $("tabs").innerHTML=VIEWS.map((x,i)=>lk(x,i)).join("");$("tabs").hidden=v==="config";
  const p=pessoa();$("crumb").textContent=v==="config"?"Configurações":v==="raio-x"&&p?"Raio-X › "+p.nome:v==="dossie"&&p?"Dossiê › "+p.nome:(VIEWS.find(x=>x[0]===v)||VIEWS[0])[1];
  $("regchip").textContent=periodoTxt();
  renderBanner();renderFiltros();$("filters").hidden=v==="config";renderView()}
function renderView(){limparGraficos();const v=S.view;
  $("view").innerHTML=v==="geral"?vGeral():v==="alertas"?vAlertas():v==="raio-x"?vRaio():v==="config"?vConfig():vDossie();
  if(v==="geral")gGeral();else if(v==="raio-x")gRaio()}

/* ---------- Visão Geral ---------- */
function vGeral(){const r=R(),L=r.list,h=r.has,W=r.semanas,sum=f=>L.reduce((a,p)=>a+f(p),0),N=r.N;
  const hero='<div class="hero"><div><div class="eyebrow">Visão geral · '+periodoTxt()+(S.f.uf?" · "+S.f.uf:"")+(S.f.sup?" · "+esc(S.f.sup):"")+'</div><h2>'+plural(L.length,"promotor analisado","promotores analisados")+'</h2><p>Radar da operação com os indícios do período, calculados por regras para conferência antes de qualquer decisão.</p></div></div>';
  if(!L.length)return hero+'<div class="nobase">Nenhum promotor para este período e estes filtros.</div>';
  const prog=sum(p=>p.pes.prog),exp=sum(p=>p.pes.exp),hd=sum(p=>p.hum.dias),hn=sum(p=>p.hum.neg),ct=W.reduce((a,w)=>a+w.ct,0),rz=W.reduce((a,w)=>a+w.rz,0),c=S.cfg;
  const K=[["Aderência",h.ader&&ct?pc(rz/ct):"—",h.ader?num(rz)+" de "+num(ct)+" visitas":"base não carregada",W.map(w=>w.ct?w.rz/w.ct:null),"var(--m2)",ct&&rz/ct*100<c.m1?"t-bad":ct&&rz/ct*100<c.m2?"t-warn":""],
    ["Pesquisas expiradas",h.pesq?pc(prog?exp/prog:null):"—",h.pesq?num(exp)+" de "+num(prog)+" programadas":"base não carregada",W.map(w=>w.prog?w.exp/w.prog:null),"var(--warn)",prog&&exp/prog*100>c.t.exp[1]?"t-bad":prog&&exp/prog*100>c.t.exp[0]?"t-warn":""],
    ["Ocorrências de jornada",h.oper?num(sum(p=>p.jor.nAtr+p.jor.nSai+p.jor.nAuto)):"—",h.oper?num(sum(p=>p.jor.nAtr))+" atrasos · "+num(sum(p=>p.jor.nAuto))+" check-outs automáticos":"base não carregada",W.map(w=>w.atr+w.sai+w.auto),"var(--rt)",""],
    ["Fotos com indício",h.fotos?num(sum(p=>p.fot.length)):"—",h.fotos?"de "+num(sum(p=>p.fotN))+" fotos analisadas":"base não carregada",W.map(w=>w.fot),"var(--bad)",sum(p=>p.fot.length)?"t-bad":""],
    ["Humor negativo",h.humor?pc(hd?hn/hd:null,0):"—",h.humor?num(hn)+" de "+num(hd)+" dias com registro":"base não carregada",W.map(w=>w.hd?w.hn/w.hd:null),"var(--vio)",""],
    ["Promotores em alerta",N.C+N.A,N.C+" críticos · "+N.A+" altos · "+N.T+" em atenção",W.map(w=>w.oc),"var(--bad)",N.C?"t-bad":N.A?"t-warn":"","irAlertas"]];
  const lim=S.rkN||10,txt={C:"vários indícios graves ao mesmo tempo",A:"indícios relevantes acumulados",T:"um ponto isolado, apenas acompanhar"};
  return hero+'<div class="dash">'+radarPainel()+paramsPainel(L)+nivPainel(L)+fotosPainel(L)+'</div>'+
  '<div class="grid2"><section class="card"><div class="hd"><h2>Aderência por semana</h2><span class="legend"><span><i style="background:var(--m2)"></i>Aderência</span><span><i style="background:var(--good)"></i>Meta 93%</span></span></div>'+(h.ader?'<div class="cv"><canvas id="g-ad" role="img" aria-label="Aderência por semana"></canvas></div>':nb("ader"))+'</section>'+
  '<section class="card"><div class="hd"><h2>Pesquisas por semana</h2><span class="legend"><span><i style="background:var(--good)"></i>Respondidas</span><span><i style="background:var(--bad)"></i>Expiradas</span><span><i style="background:var(--warn)"></i>% expiradas</span></span></div>'+(h.pesq?'<div class="cv"><canvas id="g-pes" role="img" aria-label="Pesquisas por semana"></canvas></div>':nb("pesq"))+'</section></div>'+
  '<section class="card"><div class="hd"><h2>Prioridade por supervisor <small>promotores em cada nível · clique numa barra para filtrar</small></h2><span class="legend"><span><i style="background:var(--bad)"></i>Crítico</span><span><i style="background:var(--rt)"></i>Alto</span><span><i style="background:var(--warn)"></i>Atenção</span></span></div><div class="cv" style="height:'+Math.max(260,Math.min(12,new Set(L.map(p=>p.sup)).size)*34+60)+'px"><canvas id="g-sup2" role="img" aria-label="Promotores por nível em cada supervisor"></canvas></div></section>'}
function gGeral(){const r=R(),W=r.semanas,lb=W.map(semLbl),c=S.cfg,m2=css("--m2"),bad=css("--bad"),good=css("--good"),warn=css("--warn"),rt=css("--rt");nivChart();
  const v=W.map(w=>w.ct?+(w.rz/w.ct*100).toFixed(1):null);
  grafico("g-ad",{type:"bar",data:{labels:lb,datasets:[{type:"line",label:"Meta 93%",data:W.map(()=>93),borderColor:good,borderDash:[6,4],borderWidth:2,pointRadius:0,fill:false},{label:"Aderência",data:v,backgroundColor:v.map(x=>x!=null&&x<93?warn:m2),borderRadius:8,maxBarThickness:56}]},
    options:{scales:{y:{min:Math.max(0,Math.min(80,...v.filter(x=>x!=null).map(x=>Math.floor(x)-6))),max:100,ticks:{callback:x=>x+"%"}}},plugins:{tooltip:{callbacks:{label:x=>x.dataset.label+": "+String(x.raw).replace(".",",")+"%"}}}}});
  grafico("g-pes",{type:"bar",data:{labels:lb,datasets:[{type:"line",label:"% expiradas",data:W.map(w=>w.prog?+(w.exp/w.prog*100).toFixed(1):null),borderColor:warn,backgroundColor:warn,yAxisID:"y2",tension:.35,pointRadius:4,borderWidth:2.5},{label:"Respondidas",data:W.map(w=>w.resp),backgroundColor:good,stack:"s",borderRadius:6,maxBarThickness:56},{label:"Expiradas",data:W.map(w=>w.exp),backgroundColor:bad,stack:"s",borderRadius:6,maxBarThickness:56}]},
    options:{scales:{x:{stacked:true},y:{stacked:true,ticks:{callback:x=>x>=1000?(x/1000)+" mil":x}},y2:{position:"right",min:0,ticks:{callback:x=>x+"%"},grid:{display:false}}}}});
  const sp=[...group(r.list.filter(p=>p.niv),p=>p.sup||"Sem supervisor")].map(([s,ps])=>({s,C:ps.filter(p=>p.niv==="C").length,A:ps.filter(p=>p.niv==="A").length,T:ps.filter(p=>p.niv==="T").length})).sort((a,b)=>b.C-a.C||b.A-a.A||b.T-a.T).slice(0,12);
  grafico("g-sup2",{type:"bar",data:{labels:sp.map(x=>x.s.split(" ").slice(0,2).join(" ")),datasets:[["C","Crítico",bad],["A","Alto",rt],["T","Atenção",warn]].map(([k,l,cl])=>({label:l,data:sp.map(x=>x[k]),backgroundColor:cl,stack:"s",borderRadius:4,maxBarThickness:24}))},
    options:{indexAxis:"y",scales:{x:{stacked:true,ticks:{precision:0}},y:{stacked:true}},onClick:(e,el)=>{if(el.length){S.f.sup=sp[el[0].index].s;S.R=null;render()}}}})}

/* ---------- Alertas ---------- */
function vAlertas(){const r=R(),A=r.alertas,fa=S.al,h=r.has;
  const bn=A.filter(a=>!fa.niv||(fa.niv==="B"?!a.niv:a.niv===fa.niv)),vis=bn.filter(a=>!fa.tipo||a.tipo===fa.tipo);
  const dias=[];for(let d=S.f.ini;d<=S.f.fim&&dias.length<120;d=addD(d,1))dias.push(d);const pd=dias.map(d=>vis.filter(a=>a.d===d)),mx=Math.max(1,...pd.map(x=>x.length));
  const lim=S.alN||60,tipos=Object.keys(TIPOS).filter(t=>bn.some(a=>a.tipo===t)||fa.tipo===t);
  const cn=n=>A.filter(a=>(n==="B"?!a.niv:a.niv===n)&&(!fa.tipo||a.tipo===fa.tipo)).length;
  return'<div class="hero"><div><div class="eyebrow">Central de alertas</div><h2>'+plural(r.N.C+r.N.A+r.N.T,"promotor","promotores")+' com alerta</h2><p>'+plural(A.length,"ocorrência","ocorrências")+' de '+periodoTxt()+'. Os alertas são indícios calculados por regras e precisam de conferência antes de qualquer decisão.</p></div></div>'+
  '<div class="prio">'+["C","A","T"].map(n=>'<button class="pr pr-'+n+(fa.niv===n?" on":"")+'" data-a="niv" data-v="'+(fa.niv===n?"":n)+'"><span class="v">'+r.N[n]+'</span><span class="l">'+NIV[n][0]+'</span><small>promotores</small></button>').join("")+'</div>'+
  (tipos.length?'<div class="atype">'+tipos.map(t=>{const x=bn.filter(a=>a.tipo===t),n=[3,2,1].map(s=>x.filter(a=>a.sev===s).length);return'<button class="at'+(fa.tipo===t?" on":"")+'" data-a="alTipo" data-v="'+t+'"><span class="l">'+TIPOS[t]+'</span><span class="v">'+x.length+'</span><span class="bar">'+n.map((v,i)=>'<i style="width:'+(x.length?v/x.length*100:0)+'%;background:'+SEV[3-i][1]+'"></i>').join("")+'</span></button>'}).join("")+'</div>':"")+
  '<section class="card"><div class="hd"><h2>Alertas por dia</h2><small class="muted">'+periodoTxt()+'</small></div><div class="heat">'+pd.map((x,i)=>'<div title="'+fD(dias[i])+': '+x.length+' alerta(s)" style="height:'+Math.max(4,x.length/mx*100)+'%;background:'+(x.some(a=>a.sev===3)?"var(--bad)":x.length?"var(--warn)":"var(--grid)")+'"></div>').join("")+'</div></section>'+
  '<div class="row" style="justify-content:space-between"><div class="chips"><button class="chip'+(!fa.niv?" on":"")+'" data-a="niv" data-v="">Todos <b>'+A.filter(a=>!fa.tipo||a.tipo===fa.tipo).length+'</b></button>'+["C","A","T"].map(n=>'<button class="chip'+(fa.niv===n?" on":"")+'" data-a="niv" data-v="'+n+'"><span class="pill '+NIV[n][2]+'" style="padding:1px 8px">'+NIV[n][0]+'</span><b>'+cn(n)+'</b></button>').join("")+'<button class="chip'+(fa.niv==="B"?" on":"")+'" data-a="niv" data-v="B">Monitorar <b>'+cn("B")+'</b></button></div>'+(fa.tipo?'<button class="btn sec" data-a="alTipo" data-v="">Limpar tipo: '+TIPOS[fa.tipo]+'</button>':"")+'</div>'+
  (!h.rota?'<div class="small muted">Fuga de rota (posição fora da cerca de '+S.cfg.cerca+' m) aparece aqui quando a base de posição do Status Day é carregada.</div>':"")+
  (vis.length?'<div class="feed">'+vis.slice(0,lim).map(a=>'<div class="al" data-a="abrir" data-v="'+esc(a.k)+'" tabindex="0"><span class="sv" style="background:'+SEV[a.sev][1]+'"></span><span class="dt"><b>'+fDc(a.d)+'</b>'+dow(a.d)+'</span><span class="tx"><b>'+esc(a.tit)+'</b><span>'+esc(a.desc)+'</span><span class="who">'+esc(a.nome)+' · '+esc(a.sup||"sem supervisor")+' · '+esc(a.uf||"—")+' · '+TIPOS[a.tipo]+'</span></span>'+(a.tipo==="foto"?'<span class="thumb">'+(a.foto.url&&/^https?:/.test(a.foto.url)?'<a href="'+esc(a.foto.url)+'" target="_blank" rel="noopener" style="color:var(--rt)">abrir</a>':"FOTO")+'</span>':'<span class="pill '+(a.niv?NIV[a.niv][2]:"p-n")+'">'+(a.niv?NIV[a.niv][0]:"Monitorar")+'</span>')+'</div>').join("")+'</div>'+(vis.length>lim?'<button class="btn sec" data-a="alMais">Mostrar mais '+Math.min(60,vis.length-lim)+' de '+(vis.length-lim)+' restantes</button>':""):'<div class="nobase">Nenhum alerta para os filtros escolhidos.</div>')}

/* ---------- Raio-X ---------- */
function gauge(x){const a=Math.PI*(1-x/100),cx=64,cy=66,rr=54,ex=cx+rr*Math.cos(a),ey=cy-rr*Math.sin(a);
  return'<div class="gauge"><svg viewBox="0 0 128 76" aria-hidden="true"><path d="M10 66 A54 54 0 0 1 118 66" fill="none" stroke="var(--grid)" stroke-width="11" stroke-linecap="round"/>'+(x>0?'<path d="M10 66 A54 54 0 0 1 '+ex.toFixed(1)+' '+ey.toFixed(1)+'" fill="none" stroke="'+riskCor(x)+'" stroke-width="11" stroke-linecap="round"/>':"")+'<text x="64" y="62" text-anchor="middle" font-size="26" font-weight="800" fill="'+riskCor(x)+'" font-family="Inter,Arial">'+x+'</text></svg><b>Índice de risco</b></div>'}
