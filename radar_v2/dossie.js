"use strict";
/* RADAR PROMOTOR v2 · DOSSIÊ: texto formal editável, PDF e Excel em formato de relatório */
const CONC=["Confirmado pelos registros","Parcialmente confirmado","Não confirmado","Sem dados suficientes"];
const CHAVES=[["jor",/sa[ií]da|hor[áa]rio|jornada|atras|check/],["pes",/pesquisa|respond|expirad|atividade/],["ader",/ader[êe]ncia|visita|contrat/],["fal",/falt|aus[êe]n|atestado/],["fot",/foto|imagem/],["rota",/rota|fuga|cerca|fora da loja/]];
const lat1=s=>String(s==null?"":s).replace(/[“”]/g,'"').replace(/[‘’]/g,"'").replace(/[–—]/g,"-").replace(/≥/g,">=").replace(/≤/g,"<=").replace(/[^\x00-\xFF]/g,"");
const nomeTitulo=n=>n.toLowerCase().replace(/(^|\s)(\S)/g,(m,a,b)=>a+b.toUpperCase()).replace(/ (De|Da|Do|Das|Dos|E)( |$)/g,x=>x.toLowerCase());
const jornTxt=p=>p.jorTxt?(/INICIO/.test(norm(p.jorTxt))?p.jorTxt:p.jorTxt+", início considerado às "+fH(p.esc.ini)):"início considerado às "+fH(p.esc.ini);

function blocosDe(p){const c=S.cfg,h=R().has,B={},j=p.jor,pe=p.pes,ad=p.ad,cz=t=>p.cruz.length?" Como contexto, "+p.cruz.join("; ")+".":"";
  const ocorr=x=>[x.auto?"check-out automático":"",x.atraso?"atraso":"",x.saida?"saída antecipada":""].filter(Boolean).join("; ");
  if(h.oper&&(j.nAtr||j.nSai||j.nAuto)){const dv=j.dias.filter(x=>x.desvio),pt=[];
    if(j.nAtr)pt.push("check-in após o horário previsto em "+plural(j.nAtr,"dia","dias")+" (total de "+fDur(j.minAtr)+")");
    if(j.nSai)pt.push("check-out anterior ao horário previsto em "+plural(j.nSai,"dia","dias")+" (total de "+fDur(j.minSai)+")");
    if(j.nAuto)pt.push("check-out registrado automaticamente, sem encerramento manual da jornada, em "+plural(j.nAuto,"dia","dias"));
    B.jor={key:"jor",tit:"Jornada: check-in e check-out",sev:Math.max(lvl(j.nAtr,c.t.atr),lvl(j.nSai,c.t.sai),lvl(j.nAuto,c.t.auto)),
      txt:"Os registros operacionais indicam, em "+j.trab+" dias trabalhados e considerada a jornada de "+jornTxt(p)+" com tolerância de "+c.tolAtr+" minutos: "+pt.join("; ")+"."+cz(),
      tab:c.saida?{h:["Data","Check-in","Check-out","Atraso","Saída antecipada","Ocorrência"],r:dv.map(x=>[fD(x.d),fH(x.cin),x.auto?"automático":fH(x.cout),x.atraso?x.atraso+" min":"",x.saida?x.saida+" min":"",ocorr(x)])}:{h:["Data","Check-in","Check-out","Atraso","Ocorrência"],r:dv.map(x=>[fD(x.d),fH(x.cin),x.auto?"automático":fH(x.cout),x.atraso?x.atraso+" min":"",ocorr(x)])},
      bars:dv.slice(0,14).map(x=>({l:fDc(x.d),v:x.atraso+x.saida,t:(x.atraso+x.saida)+" min"})),graf:"Minutos de desvio de jornada por dia."}}
  if(h.pesq&&pe.prog&&(pe.exp||pe.semExec.length)){const w=pe.sem.slice().sort((a,b)=>b.exp-a.exp)[0];
    B.pes={key:"pes",tit:"Pesquisas expiradas e dias sem atividades",sev:Math.max(pe.prog>=c.t.expMin?lvl((pe.pct||0)*100,c.t.exp):0,lvl(pe.semExec.length,c.t.semExec)),
      txt:"No período, "+pe.prog+" pesquisas foram programadas, "+pe.resp+" foram respondidas e "+pe.exp+" expiraram ("+pc(pe.pct)+")."+(w&&w.exp?" A semana "+w.k+" concentrou "+w.exp+" das "+pe.exp+" pesquisas expiradas."+"":"")+(pe.semExec.length?" Em "+plural(pe.semExec.length,"dia","dias")+" ("+pe.semExec.map(fDc).join(", ")+") havia atividades programadas e nenhuma foi respondida.":"")+cz(),
      tab:{h:["Semana","Programadas","Respondidas","Expiradas","% expiradas"],r:pe.sem.map(s=>["S"+s.k,s.prog,s.resp,s.exp,pc(s.prog?s.exp/s.prog:0)])},
      bars:pe.sem.map(s=>({l:"S"+s.k,v:s.prog?s.exp/s.prog:0,t:pc(s.prog?s.exp/s.prog:0,0)})),graf:"Percentual de pesquisas expiradas por semana."}}
  if(h.ader&&ad.baixo.length){
    B.ader={key:"ader",tit:"Aderência das lojas atendidas",sev:Math.max(ad.baixo.some(l=>/Meta 1/.test(l.st))?2:1,lvl(ad.pend,c.t.pend)),
      txt:"As lojas atendidas somam "+ad.ct+" visitas contratadas no período, das quais "+ad.rz+" foram realizadas ("+pc(ad.pct)+"). "+plural(ad.baixo.length,"loja ficou","lojas ficaram")+" abaixo das metas de aderência (Meta 1: "+c.m1+"%; Meta 2: "+c.m2+"%), com "+plural(ad.pend,"visita pendente","visitas pendentes")+".",
      tab:{h:["Loja","Contratado","Realizado","Pendente","Aderência","Situação"],r:ad.baixo.map(l=>[l.loja,l.ct,l.rz,l.pend,pc(l.pct),l.st])},
      bars:ad.lojas.slice(0,10).map(l=>({l:l.loja.replace(/^[A-Z]{2} \/ /,"").slice(0,22),v:l.pct||0,t:pc(l.pct,0)})),graf:"Aderência por loja (realizado sobre contratado)."}}
  if(h.faltas&&p.fal.I){B.fal={key:"fal",tit:"Faltas",sev:lvl(p.fal.I,c.t.falta),txt:"Os registros indicam "+plural(p.fal.I,"falta injustificada","faltas injustificadas")+", "+plural(p.fal.J,"falta justificada","faltas justificadas")+" e "+plural(p.fal.A,"ausência","ausências")+" com atestado no período.",
      tab:{h:["Data","Dia","Tipo","Motivo"],r:p.fal.list.map(x=>[fD(x.d),dow(x.d),{I:"Injustificada",J:"Justificada",A:"Atestado"}[x.tipo],x.motivo||"-"])}}}
  if(h.fotos&&p.fot.length){B.fot={key:"fot",tit:"Fotos com indício",sev:lvl(p.fot.length,c.t.foto),txt:"Os registros indicam "+plural(p.fot.length,"foto","fotos")+" com indício de inconsistência entre as "+p.fotN+" analisadas no período. Os indícios necessitam de conferência das imagens.",
      tab:{h:["Data","Hora","Loja","Indício"],r:p.fot.map(x=>[fD(x.d),fH(x.h),x.loja,x.mot.join("; ")])}}}
  if(h.rota&&p.rota.n){B.rota={key:"rota",tit:"Fuga de rota",sev:lvl(p.rota.dias,c.t.rota),txt:"Foram registradas "+p.rota.n+" posições fora da cerca de "+c.cerca+" metros da loja, em "+plural(p.rota.dias,"dia","dias")+", com distância máxima de "+Math.round(p.rota.max)+" metros.",
      tab:{h:["Data","Hora","Loja","Distância (m)"],r:p.rota.list.slice(0,40).map(x=>[fD(x.d),fH(x.h),x.loja,Math.round(x.dist)])}}}
  return B}
function montarDossie(p,relato){const c=S.cfg,h=R().has,B=blocosDe(p),t=(relato||"").toLowerCase(),rel=t.trim()?CHAVES.filter(x=>x[1].test(t)).map(x=>x[0]):[];
  const nomeBl={jor:"Jornada: check-in e check-out",pes:"Pesquisas",ader:"Aderência das lojas atendidas",fal:"Faltas",fot:"Fotos",rota:"Fuga de rota"},bl=[];
  rel.forEach(k=>bl.push(B[k]?Object.assign({rel:true,conc:B[k].sev>=2?0:1},B[k]):{key:k,rel:true,tit:nomeBl[k],conc:3,sev:0,txt:"Não há registros carregados que permitam confrontar este ponto do relato.",tab:null}));
  Object.values(B).sort((a,b)=>b.sev-a.sev).forEach(b=>{if(!rel.includes(b.key))bl.push(b)});
  const bl5=bl.slice(0,5),ad=p.ad,pe=p.pes,hu=p.hum;
  const impacto=h.ader?"No período, as lojas atendidas somam "+num(ad.ct)+" visitas contratadas, das quais "+num(ad.rz)+" foram realizadas ("+pc(ad.pct)+"). "+(ad.baixo.length?plural(ad.baixo.length,"loja está","lojas estão")+" abaixo da Meta 1 ou da Meta 2, com "+plural(ad.pend,"visita pendente","visitas pendentes")+" do contratado. ":"Todas as lojas atendidas estão dentro das metas de aderência. ")+(h.pesq&&pe.prog?"Foram "+plural(pe.exp,"pesquisa expirada","pesquisas expiradas")+" ("+pc(pe.pct)+")"+(pe.semExec.length?" e "+plural(pe.semExec.length,"dia","dias")+" sem atividades respondidas":"")+", fatores que reduzem a execução contratada com o cliente.":""):"A base de aderência não foi carregada para este período, e por isso o impacto nas visitas contratadas não pôde ser medido.";
  const humor=h.humor&&hu.dias>=3?"Como contexto de acompanhamento, "+pc(hu.pct,0)+" dos "+hu.dias+" dias com registro de humor foram negativos, com maior sequência de "+plural(hu.seq,"dia","dias")+(hu.doente?" e "+plural(hu.doente,"dia","dias")+" registrado(s) como “Doente”":"")+"."+(p.cruz.length?" "+p.cruz.join("; ")+".":"")+" Esta informação tem finalidade de acompanhamento e não constitui fundamento de apuração.":"";
  const temas=bl5.filter(b=>b.conc==null||b.conc<2).map(b=>b.tit.toLowerCase());
  const per=fD(S.f.ini)+" a "+fD(S.f.fim);
  const fim="Sendo assim, os registros do período de "+per+" "+(temas.length?"apresentam indícios relativos a "+temas.join("; ")+", os quais necessitam ser apurados pelas áreas responsáveis, que decidirão as tratativas cabíveis.":"não apresentam indícios nos pontos analisados.")+(temas.length?" Recomenda-se o alinhamento da liderança direta com o colaborador sobre as causas dos pontos apresentados.":"");
  return{k:p.k,nome:p.nome,num:null,relato:relato||"",per,
    intro:"O presente dossiê, emitido pela RT Intelligence, reúne os registros operacionais de "+p.nome+", CPF "+(p.mat||"não informado")+", supervisionado(a) por "+(p.sup||"não informado")+", referentes ao período de "+per+". A análise considerou a jornada cadastrada ("+jornTxt(p)+"), as pesquisas programadas, a aderência das lojas atendidas e os demais registros disponíveis, todos submetidos a regras objetivas de verificação.",
    obj:"1. Apresentar os indícios identificados nos registros operacionais do período, com os números que os sustentam.\n2. Mensurar o impacto desses indícios na aderência contratada pelo cliente, isto é, nas visitas contratadas que deixaram de ser realizadas.",
    blocos:bl5,impacto,humor,fim}}
function avisos(d){const t=(d.intro+" "+d.obj+" "+d.impacto+" "+d.humor+" "+d.fim+" "+d.blocos.map(b=>b.txt).join(" ")).toLowerCase(),a=[];
  ["detrator","preguiços","irresponsáve","desonest","relapso","má-fé","má fé","mentiu","culpad"].forEach(w=>{if(t.includes(w))a.push("termo acusatório “"+w+"”")});
  ["involves","2p rt","2prt","status day"].forEach(w=>{if(t.includes(w))a.push("nome de sistema “"+w+"”")});
  ["bom dia","boa tarde","boa noite","prezad","olá"].forEach(w=>{if(t.includes(w))a.push("saudação “"+w+"”")});
  ["medida disciplinar","punição","advertência","suspensão","demissão"].forEach(w=>{if(t.includes(w))a.push("a decisão cabe às áreas responsáveis; retire “"+w+"”")});
  if(!/^sendo assim,/i.test(d.fim.trim()))a.push("as considerações finais devem começar por “Sendo assim,”");return a}
const avisoHtml=av=>av.length?'<div class="banner"><b>Revise o texto antes de baixar:</b> '+esc(av.join("; "))+'.</div>':'<div class="small muted">Texto dentro do padrão: formal, sem saudação, sem termos acusatórios e sem decisão de tratativa.</div>';
async function numero(){const d=S.dos;if(d.num)return d.num;let n=S.contador+1;
  if(db){try{const s=await db.doc("config/contador").get();n=((s.exists&&s.data().n)||0)+1;await db.doc("config/contador").set({n})}catch(e){}}
  S.contador=n;d.num="RT-"+new Date().getFullYear()+"-"+String(n).padStart(6,"0");return d.num}
const nomeArq=(d,ext)=>"Dossiê - "+d.nome+"."+ext;
async function logoData(caminho){try{const r=await fetch(caminho);if(!r.ok)return null;const b=await r.blob();const url=await new Promise(ok=>{const fr=new FileReader();fr.onload=()=>ok(fr.result);fr.readAsDataURL(b)});
  const dim=await new Promise(ok=>{const i=new Image();i.onload=()=>ok({w:i.naturalWidth,h:i.naturalHeight});i.onerror=()=>ok(null);i.src=url});return dim?{url,w:dim.w,h:dim.h}:null}catch(e){return null}}

function vDossie(){const d=S.dos,p=pessoa();
  if(!d||!p)return'<div class="hero"><div class="eyebrow">RT Intelligence</div><h2>Dossiê</h2><p>Escolha um promotor no campo “Promotor” ou abra um pelos alertas e clique em “Gerar dossiê” no Raio-X.</p></div>';
  const av=avisos(d);
  return'<div class="hero"><div class="eyebrow">RT Intelligence</div><h2>Dossiê de Análise Operacional</h2><p>'+esc(d.nome)+' · '+d.per+'</p></div>'+
  '<div class="dos"><div class="edit">'+
   '<section class="card"><label class="f" for="d-relato"><span>Relato a apurar (opcional)</span><textarea class="inp" id="d-relato" rows="2" placeholder="Ex.: a supervisão relata saídas antes do horário e pesquisas não respondidas.">'+esc(d.relato)+'</textarea></label><div class="row"><button class="btn sec sm" data-a="aplicarRelato">Refazer o texto com este relato</button><span class="small muted">Refazer o texto descarta as edições abaixo.</span></div></section>'+
   '<section class="card"><span class="lbl">Introdução</span><textarea class="inp" id="d-intro" data-d="intro" rows="5">'+esc(d.intro)+'</textarea>'+
    '<span class="lbl">Objetivos</span><textarea class="inp" id="d-obj" data-d="obj" rows="4">'+esc(d.obj)+'</textarea></section>'+
   '<section class="card"><span class="lbl">Relatos identificados <small>'+d.blocos.length+' de 5</small></span>'+(d.blocos.length?d.blocos.map((b,i)=>'<div class="edit"><b>'+(i+1)+'. '+esc(b.tit)+'</b>'+(b.rel?'<select class="inp" data-conc="'+i+'" aria-label="Conclusão" style="max-width:300px">'+CONC.map((c,x)=>'<option value="'+x+'"'+(b.conc===x?" selected":"")+'>'+c+'</option>').join("")+'</select>':"")+'<textarea class="inp" data-b="'+i+'" rows="5" aria-label="Texto do relato '+(i+1)+'">'+esc(b.txt)+'</textarea>'+(b.tab&&b.tab.r.length?'<span class="small muted">No documento: tabela com '+b.tab.r.length+' linha(s)'+(b.bars&&b.bars.length?" e gráfico":"")+'.</span>':"")+'</div>').join(""):'<div class="nobase">Nenhum indício encontrado no período. O documento sai com identificação, introdução e considerações finais.</div>')+'</section>'+
   '<section class="card"><span class="lbl">Impacto na aderência e na operação</span><textarea class="inp" data-d="impacto" rows="4">'+esc(d.impacto)+'</textarea>'+(d.humor?'<span class="lbl">Contexto de acompanhamento (humor)</span><textarea class="inp" data-d="humor" rows="3">'+esc(d.humor)+'</textarea>':"")+
    '<span class="lbl">Considerações finais</span><textarea class="inp" id="d-fim" data-d="fim" rows="4">'+esc(d.fim)+'</textarea></section></div>'+
  '<div class="aside"><section class="card"><h2>Emitir</h2><button class="btn" data-a="pdf">Baixar PDF</button><button class="btn sec" data-a="xlsx">Baixar Excel</button><button class="btn sec sm" data-a="voltarRaio">← Voltar ao Raio-X</button><div id="d-st" class="small muted"></div></section>'+
   '<section class="card"><h2>Revisão</h2><div id="d-av" class="chk">'+avisoHtml(av)+'</div></section></div></div>'}

/* ---------- PDF ---------- */
async function gerarPDF(){const p=pessoa(),d=S.dos,num=await numero(),{jsPDF}=window.jspdf,doc=new jsPDF({unit:"mm",format:"a4"}),W=210,M=18,TW=W-2*M;let y=M;
  const hoje=new Date(),emis=p2(hoje.getDate())+"/"+p2(hoje.getMonth()+1)+"/"+hoje.getFullYear();
  const need=h=>{if(y+h>297-22){doc.addPage();y=M}};
  const par=(t,o)=>{o=o||{};doc.setFont("helvetica",o.b?"bold":"normal");doc.setFontSize(o.s||10);doc.setTextColor(20);const ls=doc.splitTextToSize(lat1(t),TW-(o.in||0)),lh=(o.s||10)*.45;for(const l of ls){need(lh);doc.text(l,M+(o.in||0),y);y+=lh}y+=o.gap==null?2.5:o.gap};
  const tit=t=>{need(14);y+=2;par(t,{b:true,s:11,gap:1.5});doc.setDrawColor(200);doc.setLineWidth(.2);doc.line(M,y-1.2,W-M,y-1.2);y+=1.5};
  const tab=(hd,rows,o)=>{doc.autoTable(Object.assign({startY:y,head:[hd.map(lat1)],body:rows.map(x=>x.map(lat1)),margin:{left:M,right:M,bottom:22},styles:{font:"helvetica",fontSize:8,cellPadding:1.4,textColor:20,lineColor:190,lineWidth:.1},headStyles:{fillColor:[16,38,59],textColor:255,fontStyle:"bold"},alternateRowStyles:{fillColor:[245,247,250]},theme:"grid",rowPageBreak:"avoid"},o||{}));y=doc.lastAutoTable.finalY+5};
  const graf=(it,leg)=>{if(!it||!it.length)return;const bh=5.2,lw=26,mx=Math.max(...it.map(i=>i.v),0.0001);need(it.length*bh+10);doc.setFontSize(8);
    it.forEach(b=>{doc.setTextColor(20);doc.text(lat1(b.l),M,y+3.6);doc.setFillColor(228,232,238);doc.rect(M+lw,y,TW-lw-22,3.8,"F");doc.setFillColor(244,86,42);doc.rect(M+lw,y,(TW-lw-22)*Math.min(1,b.v/mx),3.8,"F");doc.text(lat1(String(b.t)),W-M,y+3.6,{align:"right"});y+=bh});
    doc.setTextColor(90);doc.setFontSize(8);doc.text(lat1(leg||""),M,y+2.5);y+=11};
  /* cabeçalho */
  const lg=await logoData("assets/rt-intelligence.png");
  if(lg)doc.addImage(lg.url,"PNG",M,y,56,56*lg.h/lg.w);else{doc.setFillColor(244,86,42);doc.roundedRect(M,y,14,14,2.5,2.5,"F");doc.setTextColor(255);doc.setFont("helvetica","bold");doc.setFontSize(15);doc.text("rt",M+7,y+9.4,{align:"center"})}
  doc.setTextColor(20);doc.setFont("helvetica","normal");doc.setFontSize(9);doc.text(lat1("Documento nº "+num),W-M,y+3,{align:"right"});doc.text(lat1("Emissão: "+emis),W-M,y+7.5,{align:"right"});doc.setFont("helvetica","bold");doc.text("CONFIDENCIAL",W-M,y+12,{align:"right"});
  y+=17;doc.setDrawColor(16,38,59);doc.setLineWidth(.5);doc.line(M,y,W-M,y);y+=9;
  doc.setFont("helvetica","bold");doc.setFontSize(15);doc.setTextColor(16,38,59);doc.text(lat1("DOSSIÊ DE ANÁLISE OPERACIONAL"),M,y);y+=6;
  doc.setFont("helvetica","normal");doc.setFontSize(10);doc.setTextColor(86,105,126);doc.text(lat1(p.nome+" · "+d.per),M,y);doc.setTextColor(20);y+=7;
  tit("1. Identificação");
  tab(["Campo","Informação"],[["Nome",p.nome],["CPF",p.mat||"não informado"],["Supervisor",p.sup||"-"],["UF",p.uf||"-"],["Jornada",jornTxt(p)],["Lojas atendidas",p.lojas.join("; ")||"-"],["Período analisado",d.per]],{columnStyles:{0:{cellWidth:38,fontStyle:"bold"}},showHead:false});
  tit("2. Introdução e objetivos");par(d.intro);par("Objetivos",{b:true,gap:1});d.obj.split("\n").filter(x=>x.trim()).forEach(l=>par(l,{in:2,gap:1}));y+=1.5;
  let n=3;
  if(d.relato&&d.relato.trim()){tit(n+". Relato a apurar");par("“"+d.relato.trim()+"”");n++}
  if(d.blocos.length){tit(n+". Relatos identificados");d.blocos.forEach((b,i)=>{need(20);par((n)+"."+(i+1)+" "+b.tit+(b.rel?" - "+CONC[b.conc]:""),{b:true,gap:1});par(b.txt);if(b.tab&&b.tab.r.length)tab(b.tab.h,b.tab.r.slice(0,40));graf(b.bars,b.graf)});n++}
  tit(n+". Impacto na aderência e na operação");par(d.impacto);n++;
  if(d.humor){tit(n+". Contexto de acompanhamento");par(d.humor);n++}
  tit(n+". Considerações finais");par(d.fim.replace(/\s*\n+\s*/g," "));
  /* anexos */
  const aj=p.jor.dias,al=p.ad.lojas;
  if(aj.length||al.length||p.fot.length){doc.addPage();y=M;
    if(aj.length){tit("Anexo A - Jornada dia a dia");tab(["Data","Dia","Check-in","Check-out","Atraso","Ocorrência"],aj.map(x=>[fD(x.d),dow(x.d),fH(x.cin),x.auto?"automático":fH(x.cout),x.atraso?x.atraso+" min":"",[x.auto?"check-out automático":"",x.atraso?"atraso":""].filter(Boolean).join("; ")||"sem desvios"]))}
    if(al.length){tit("Anexo B - Aderência por loja");tab(["Loja","Contratado","Realizado","Pendente","Aderência"],al.map(l=>[l.loja,l.ct,l.rz,l.pend,pc(l.pct)]))}
    if(p.pes.loja.length){tit("Anexo C - Pesquisas por loja");tab(["Loja","Programadas","Respondidas","Expiradas","% expiradas"],p.pes.loja.map(s=>[s.k,s.prog,s.resp,s.exp,pc(s.prog?s.exp/s.prog:0)]))}
    if(p.fot.length){tit("Anexo D - Fotos com indício");tab(["Data","Hora","Loja","Pesquisa","Indício"],p.fot.map(f=>[fD(f.d),fH(f.h),f.loja,f.pesq,f.mot.join("; ")]))}}
  const tp=doc.getNumberOfPages();for(let i=1;i<=tp;i++){doc.setPage(i);doc.setDrawColor(150);doc.setLineWidth(.2);doc.line(M,297-17,W-M,297-17);doc.setFont("helvetica","normal");doc.setFontSize(8);doc.setTextColor(80);
    doc.text(lat1("RT Intelligence · "+num),M,297-12.5);doc.text(lat1("Página "+i+" de "+tp),W-M,297-12.5,{align:"right"});doc.text(lat1("Este relatório apresenta indícios baseados em registros operacionais."),W/2,297-8.5,{align:"center"})}
  return{nome:nomeArq(d,"pdf"),data:doc.output("blob")}}

/* ---------- Excel em formato de relatório ---------- */
async function gerarExcel(){const p=pessoa(),d=S.dos,num=await numero(),c=S.cfg,wb=new ExcelJS.Workbook(),dt=s=>s?new Date(Date.UTC(+s.slice(0,4),+s.slice(5,7)-1,+s.slice(8,10))):null;
  const DF="dd/mm/yyyy",PF="0.0%",LAR={fgColor:{argb:"FFF4562A"}},AZ={fgColor:{argb:"FF10263B"}};
  const folha=(nome,titulo,cols,rows,sub)=>{const ws=wb.addWorksheet(nome,{views:[{state:"frozen",ySplit:4}]});
    ws.getCell("A1").value="RT Intelligence · "+titulo;ws.getCell("A1").font={bold:true,size:14,color:{argb:"FF10263B"}};
    ws.getCell("A2").value=(sub||p.nome+" · "+d.per)+" · Documento nº "+num;ws.getCell("A2").font={size:10,color:{argb:"FF56697E"}};
    const hr=ws.getRow(4);cols.forEach((c0,i)=>{const ce=hr.getCell(i+1);ce.value=c0[0];ce.font={bold:true,color:{argb:"FFFFFFFF"}};ce.fill=Object.assign({type:"pattern",pattern:"solid"},AZ);ce.alignment={vertical:"middle",wrapText:true};ws.getColumn(i+1).width=c0[1]||16;if(c0[2])ws.getColumn(i+1).numFmt=c0[2]});
    rows.forEach((r,ri)=>{const row=ws.addRow(r);row.eachCell(ce=>{ce.border={bottom:{style:"thin",color:{argb:"FFD5DEE8"}}};ce.alignment={vertical:"top",wrapText:true}});if(ri%2)row.eachCell(ce=>{ce.fill={type:"pattern",pattern:"solid",fgColor:{argb:"FFF5F7FA"}}})});
    ws.autoFilter={from:{row:4,column:1},to:{row:4,column:cols.length}};return ws};
  /* capa e resumo */
  const cp=wb.addWorksheet("Dossiê");cp.getColumn(1).width=30;cp.getColumn(2).width=110;
  const lgx=await logoData("assets/rt-intelligence.png");
  if(lgx){const idl=wb.addImage({base64:lgx.url,extension:"png"});cp.getRow(1).height=26;cp.getRow(2).height=26;cp.addImage(idl,{tl:{col:0,row:0},ext:{width:220,height:Math.round(220*lgx.h/lgx.w)}})}
  else{cp.getCell("A1").value="RT Intelligence";cp.getCell("A1").font={bold:true,size:18,color:{argb:"FFF4562A"}}}
  cp.getCell("A3").value="Dossiê de Análise Operacional";cp.getCell("A3").font={bold:true,size:14,color:{argb:"FF10263B"}};
  cp.getCell("A4").value="Documento nº "+num+" · Emissão "+new Date().toLocaleDateString("pt-BR")+" · CONFIDENCIAL";cp.getCell("A4").font={size:10,color:{argb:"FF56697E"}};
  let rw=6;const lin=(a,b,neg)=>{const r=cp.getRow(rw++);r.getCell(1).value=a;r.getCell(1).font={bold:true,color:{argb:"FF10263B"}};r.getCell(2).value=b;r.getCell(2).alignment={wrapText:true,vertical:"top"};r.getCell(1).alignment={vertical:"top"};if(neg)r.getCell(1).fill=Object.assign({type:"pattern",pattern:"solid"},{fgColor:{argb:"FFE6EBF1"}})};
  const sec=t=>{const r=cp.getRow(rw++);r.getCell(1).value=t;r.getCell(1).font={bold:true,color:{argb:"FFFFFFFF"}};r.getCell(1).fill=Object.assign({type:"pattern",pattern:"solid"},LAR);r.getCell(2).fill=Object.assign({type:"pattern",pattern:"solid"},LAR)};
  sec("1. Identificação");lin("Nome",p.nome);lin("CPF",p.mat||"não informado");lin("Supervisor",p.sup||"-");lin("UF",p.uf||"-");lin("Jornada",jornTxt(p));lin("Lojas atendidas",p.lojas.join("; ")||"-");lin("Período analisado",d.per);rw++;
  sec("2. Introdução e objetivos");lin("Introdução",d.intro);lin("Objetivos",d.obj);rw++;
  let n=3;if(d.relato&&d.relato.trim()){sec(n+". Relato a apurar");lin("Relato",d.relato.trim());rw++;n++}
  if(d.blocos.length){sec(n+". Relatos identificados");d.blocos.forEach((b,i)=>lin((i+1)+". "+b.tit+(b.rel?" ("+CONC[b.conc]+")":""),b.txt));rw++;n++}
  sec(n+". Impacto na aderência e na operação");lin("Impacto",d.impacto);n++;if(d.humor)lin("Contexto (humor)",d.humor);rw++;
  sec(n+". Considerações finais");lin("Considerações",d.fim);rw++;
  const ob=cp.getRow(rw);ob.getCell(1).value="Este relatório apresenta indícios baseados em registros operacionais.";ob.getCell(1).font={italic:true,size:9,color:{argb:"FF56697E"}};
  folha("Pesquisas","Pesquisas",[["Semana",10],["Programadas",14],["Respondidas",14],["Expiradas",12],["% expiradas",13,PF]],p.pes.sem.map(s=>["S"+s.k,s.prog,s.resp,s.exp,s.prog?s.exp/s.prog:0]).concat([["Total",p.pes.prog,p.pes.resp,p.pes.exp,p.pes.pct||0]]));
  folha("Aderência","Aderência por loja",[["Loja",40],["Contratado",13],["Realizado",13],["Pendente",12],["Aderência",12,PF],["Situação",20]],p.ad.lojas.map(l=>[l.loja,l.ct,l.rz,l.pend,l.pct||0,l.st==="ok"?"meta atingida":l.st]),p.nome+" · Meta 1: "+c.m1+"% · Meta 2: "+c.m2+"%");
  folha("Jornada","Jornada dia a dia",[["Data",12,DF],["Dia",8],["Check-in",10],["Check-out",12],["Atraso (min)",12],["Check-out automático",14],["Humor",14]],p.jor.dias.map(x=>[dt(x.d),dow(x.d),fH(x.cin),x.auto?"automático":fH(x.cout),x.atraso||0,x.auto?"Sim":"Não",p.hum.map.has(x.d)?(x.neg?"negativo":"ok"):"sem registro"]),p.nome+" · jornada "+jornTxt(p)+" · tolerância "+c.tolAtr+" min");
  folha("Faltas","Faltas e atestados",[["Data",12,DF],["Dia",8],["Tipo",16],["Motivo",50]],p.fal.list.map(x=>[dt(x.d),dow(x.d),{I:"Injustificada",J:"Justificada",A:"Atestado"}[x.tipo],x.motivo||""]));
  folha("Fotos","Fotos com indício",[["Data",12,DF],["Hora",8],["Loja",36],["Pesquisa",30],["Indício",50]],p.fot.map(f=>[dt(f.d),fH(f.h),f.loja,f.pesq,f.mot.join("; ")]));
  folha("Humor","Humor (contexto)",[["Data",12,DF],["Dia",8],["Registro",14]],[...p.hum.map.keys()].sort().map(x=>[dt(x),dow(x),p.hum.map.get(x)?"negativo":"ok"]),p.nome+" · informação de acompanhamento");
  folha("Parâmetros","Parâmetros usados",[["Parâmetro",46],["Valor",30]],[["Jornada aplicada",jornTxt(p)],["Tolerância de atraso (min)",c.tolAtr],["Tolerância de saída antecipada (min)",c.tolSai],["Meta 1 de aderência (%)",c.m1],["Meta 2 de aderência (%)",c.m2],["Cerca de rota (m)",c.cerca],["Foto fora da loja (m)",c.distFoto],["Humor negativo",c.neg.join(", ")],["Feriados",c.fer.map(fD).join(", ")],["Período",d.per]]);
  const buf=await wb.xlsx.writeBuffer();return{nome:nomeArq(d,"xlsx"),data:new Blob([buf])}}
