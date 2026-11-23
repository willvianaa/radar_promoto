"use strict";
/* =====================================================================
   RADAR PROMOTOR v2 · MOTOR: configuração, leitura dos arquivos, base de
   dados, indicadores e alertas. Tudo calculado por regras, sem IA.
   ===================================================================== */
const CFG0={saida:false,tolAtr:15,tolSai:15,distFoto:300,cerca:200,m1:85,m2:93,
  esc:{ini:480,fim:1050},escP:{},fer:["2026-09-07","2026-10-12","2026-11-02","2026-11-15","2026-11-20"],
  neg:["Cansado","Sobrecarregado","Triste","Doente"],
  t:{atr:[4,7,10],sai:[4,7,10],auto:[5,8,10],exp:[20,30,45],expMin:20,semExec:[0,2,4],falta:[0,1,3],foto:[0,1,3],pend:[0,1,10],rota:[0,3,10],humPct:40,humSeq:3}};
const BASES={oper:"Operação (check-in / check-out)",pesq:"Pesquisas",humor:"Humor",ader:"Aderência por loja",fotos:"Fotos",faltas:"Faltas e atestados",rota:"Posição (fuga de rota)"};
const FIELDS={
  oper:["k","nome","mat","sup","uf","d","pdv","cin","cout","auto","jor"],
  pesq:["k","nome","mat","sup","uf","d","loja","cli","tipo","st"],
  humor:["k","nome","mat","d","op"],
  ader:["k","nome","sup","uf","d","loja","marca","ct","rz"],
  fotos:["k","nome","mat","d","h","loja","pesq","lat","lon","llat","llon","hash","url"],
  faltas:["k","nome","mat","d","tipo","motivo"],
  rota:["k","nome","mat","d","h","loja","dist"]};
const NIV={C:["Crítico","var(--bad)","p-bad"],A:["Alto","var(--warn)","p-warn"],T:["Atenção","var(--m2)","p-m2"]};
const SEVN={3:"alta",2:"média",1:"baixa"};
const TIPOS={jor:"Check-in / Check-out",auto:"Check-out automático",pesq:"Pesquisas expiradas",exec:"Dias sem atividades",ader:"Aderência",falta:"Faltas",foto:"Fotos com indício",rota:"Fuga de rota",sobre:"Possível sobrecarga",humor:"Humor"};

/* ---------- utilitários ---------- */
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm=s=>String(s==null?"":s).normalize("NFD").replace(/[̀-ͯ]/g,"").toUpperCase().replace(/\s+/g," ").trim();
const p2=n=>(n<10?"0":"")+n;
const fD=d=>d?d.slice(8,10)+"/"+d.slice(5,7)+"/"+d.slice(0,4):"";
const fDc=d=>d?d.slice(8,10)+"/"+d.slice(5,7):"";
const fH=m=>m==null?"":p2(Math.floor(m/60))+":"+p2(Math.round(m%60));
const fDur=m=>Math.floor(m/60)+"h"+p2(Math.round(m%60));
const pc=(x,n)=>x==null||isNaN(x)?"—":(x*100).toFixed(n==null?1:n).replace(".",",")+"%";
const num=n=>n==null?"—":Number(n).toLocaleString("pt-BR");
const DOW=["dom","seg","ter","qua","qui","sex","sáb"];
const dow=d=>DOW[new Date(d+"T12:00:00").getDay()];
const addD=(d,n)=>{const t=new Date(d+"T12:00:00Z");t.setUTCDate(t.getUTCDate()+n);return t.toISOString().slice(0,10)};
const mondayOf=d=>{const t=new Date(d+"T12:00:00Z"),n=(t.getUTCDay()+6)%7;t.setUTCDate(t.getUTCDate()-n);return t.toISOString().slice(0,10)};
const fimMes=ym=>new Date(Date.UTC(+ym.slice(0,4),+ym.slice(5,7),0)).toISOString().slice(0,10);
function isoWeek(d){const t=new Date(d+"T12:00:00Z");const n=(t.getUTCDay()+6)%7;t.setUTCDate(t.getUTCDate()-n+3);const f=new Date(Date.UTC(t.getUTCFullYear(),0,4));return 1+Math.round(((t-f)/864e5-3+((f.getUTCDay()+6)%7))/7)}
function weekMonday(y,w){const j=new Date(Date.UTC(y,0,4));const n=(j.getUTCDay()+6)%7;j.setUTCDate(j.getUTCDate()-n+(w-1)*7);return j.toISOString().slice(0,10)}
function mesesEntre(a,b){const o=[];if(!a||!b)return o;let y=+a.slice(0,4),m=+a.slice(5,7);const yb=+b.slice(0,4),mb=+b.slice(5,7);while(y<yb||(y===yb&&m<=mb)){o.push(y+"-"+p2(m));if(++m>12){m=1;y++}}return o}
function pDate(v){
  if(v==null||v==="")return null;
  if(v instanceof Date)return v.getFullYear()+"-"+p2(v.getMonth()+1)+"-"+p2(v.getDate());
  if(typeof v==="number"){if(v<20000)return null;return new Date(Math.round((Math.floor(v)-25569)*864e5)).toISOString().slice(0,10)}
  const s=String(v).trim();let m=s.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})/);
  if(m){let y=+m[3];if(y<100)y+=2000;return y+"-"+p2(+m[2])+"-"+p2(+m[1])}
  m=s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);return m?m[1]+"-"+p2(+m[2])+"-"+p2(+m[3]):null}
function pTime(v){
  if(v==null||v==="")return null;
  if(v instanceof Date)return v.getHours()*60+v.getMinutes();
  if(typeof v==="number")return Math.round((v-Math.floor(v))*1440);
  const m=String(v).match(/(\d{1,2}):(\d{2})/);return m?+m[1]*60+ +m[2]:null}
function pNum(v){if(v==null||v==="")return null;if(typeof v==="number")return v;const n=parseFloat(String(v).replace(/[%\s]/g,"").replace(/\.(?=\d{3}(\D|$))/g,"").replace(",","."));return isNaN(n)?null:n}
function tOut(s){const m=String(s||"").match(/^(\d{1,2}):(\d{2})$/);return m?+m[1]*60+ +m[2]:null}
function dist(a,b,c,d){const R=6371000,r=Math.PI/180,x=(c-a)*r,y=(d-b)*r,h=Math.sin(x/2)**2+Math.cos(a*r)*Math.cos(c*r)*Math.sin(y/2)**2;return 2*R*Math.asin(Math.sqrt(h))}
function rng(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function group(rows,f){const m=new Map();for(const r of rows){const k=f(r);let a=m.get(k);if(!a)m.set(k,a=[]);a.push(r)}return m}
const plural=(n,s,p)=>n+" "+(n===1?s:p);
const avg=(a,f)=>a.length?a.reduce((s,x)=>s+f(x),0)/a.length:0;
function cpf(v){if(v==null||v==="")return"";let d=String(typeof v==="number"?Math.round(v):v).replace(/\D/g,"");if(d.length&&d.length<11&&typeof v==="number")d=d.padStart(11,"0");return d.length===11?d.slice(0,3)+"."+d.slice(3,6)+"."+d.slice(6,9)+"-"+d.slice(9):String(v).trim()}

/* ---------- leitura dos arquivos: o tipo vem do cabeçalho ---------- */
const AL={
  nome:[/^(NOME )?(DO |DA )?(COLABORADOR|PROMOTOR|FUNCIONARIO|USUARIO|RESPONSAVEL)(A)?( NOME)?$/,/^NOME$/,/COLABORADOR|PROMOTOR|RESPONSAVEL/],
  jor:[/^JORNADA/],mat:[/^CPF/,/CPF/,/^MATRICULA/],sup:[/SUPERVISOR/,/SUPERIOR/,/GESTOR|LIDER/],uf:[/^UF$/,/^ESTADO$/],
  d:[/^DATA$/,/^DATA /,/^DIA$/,/^SOLICITACAO/],pdv:[/^PDV$/,/^LOJA$/,/PONTO DE VENDA/,/^LOCAL$/,/PDV|LOJA/],
  cin:[/CHECK ?-?IN/,/^ENTRADA/,/^INICIO/],cout:[/CHECK ?-?OUT/,/^SAIDA/,/^FIM$/,/TERMINO/],
  auto:[/TIPO (DE |DO )?CHECK ?-?OUT/,/REALIZADO PEL/,/AUTOMATIC/,/OBSERVA/],
  st:[/^STATUS/,/^SITUACAO/],cli:[/^CLIENTE$/,/^MARCA$/,/CLIENTE|MARCA/],
  tipo:[/TIPO (DE |DO )?(SERVICO|PESQUISA|ATIVIDADE)/,/^PESQUISA$/,/^FORMULARIO$/,/^ATIVIDADE$/,/PESQUISA|FORMULARIO|ATIVIDADE/],
  op:[/HUMOR/,/COMO VOCE ESTA/,/SENTIMENTO/,/^RESPOSTA$/],ct:[/CONTRATAD/,/PREVIST/,/PLANEJAD/],rz:[/REALIZAD/,/EXECUTAD/],sem:[/^SEMANA/],ano:[/^ANO$/],
  h:[/^HORA/,/HORARIO/],lat:[/^LAT(ITUDE)?( DA| DO)?( FOTO| CAPTURA| COLABORADOR)?$/],lon:[/^LON(G|GITUDE)?( DA| DO)?( FOTO| CAPTURA| COLABORADOR)?$/],
  llat:[/LAT(ITUDE)? (DA |DO )?(LOJA|PDV)/],llon:[/LON(G|GITUDE)? (DA |DO )?(LOJA|PDV)/],hash:[/HASH/],url:[/URL|LINK|IMAGEM|ARQUIVO|^FOTO$/],
  dist:[/DISTANCIA/,/FORA DA CERCA/],ftipo:[/^TIPO/,/JUSTIFICAD/,/^FALTA/],motivo:[/MOTIVO/,/JUSTIFICATIVA/,/OBSERVA/]};
function mapCols(hdr){const H=hdr.map(norm),c={};for(const f in AL){for(const re of AL[f]){const i=H.findIndex(x=>x&&re.test(x));if(i>=0){c[f]=i;break}}}return c}
function tipoDe(c,hdr){const H=hdr.map(norm).join(" | ");
  if(c.ct!=null&&c.rz!=null)return"ader";
  if(c.cin!=null&&c.cout!=null)return"oper";
  if(c.dist!=null&&c.nome!=null)return"rota";
  if(c.op!=null&&c.st==null)return"humor";
  if(/FALTA|ATESTADO|AUSENCIA|JUSTIFICATIVA/.test(H)&&c.st==null)return"faltas";
  if(c.st!=null&&(c.tipo!=null||c.cli!=null))return"pesq";
  if(c.nome!=null&&(c.hash!=null||c.url!=null||(c.lat!=null&&c.lon!=null)))return"fotos";
  return null}
function linha(base,c,r,anoPad){const g=f=>c[f]==null?null:r[c[f]],s=f=>{const v=g(f);return v==null?"":String(v).trim()};
  const nome=s("nome"),k=norm(nome),o={k,nome,mat:cpf(g("mat"))};
  if(!k&&base!=="ader")return null;
  if(base==="oper"){o.d=pDate(g("d"))||pDate(g("cin"));o.cin=pTime(g("cin"));o.cout=pTime(g("cout"));if(!o.d||o.cin==null)return null;
    o.sup=s("sup");o.uf=norm(s("uf")).slice(0,2);o.pdv=s("pdv");o.auto=/SISTEMA|AUTOM/.test(norm(s("auto")))?1:0;o.jor=s("jor");return o}
  if(base==="pesq"){o.d=pDate(g("d"));if(!o.d)return null;o.sup=s("sup");o.uf=norm(s("uf")).slice(0,2);o.loja=s("pdv");o.cli=s("cli");o.tipo=s("tipo");
    const t=norm(s("st"));o.st=/EXPIR|NAO REALIZ|NAO RESPOND|PERDID|NAO EXECUT/.test(t)?"E":/RESPOND|REALIZ|CONCLU|FINALIZ|EXECUT|CRITIC/.test(t)?"R":"P";return o}
  if(base==="humor"){o.d=pDate(g("d"));o.op=s("op");return o.d&&o.op?o:null}
  if(base==="ader"){o.ct=pNum(g("ct"));o.rz=pNum(g("rz"));o.loja=s("pdv");if(!o.loja||o.ct==null)return null;o.rz=o.rz||0;
    o.d=pDate(g("d"));if(!o.d){const sv=s("sem"),m=sv.match(/(\d{4})\D+(\d{1,2})/),w=m?+m[2]:parseInt(sv,10),y=m?+m[1]:(pNum(g("ano"))||anoPad);if(w)o.d=weekMonday(y,w)}
    if(!o.d)return null;o.sup=s("sup");o.uf=norm(s("uf")).slice(0,2)||norm(o.loja).slice(0,2);o.marca=s("cli");return o}
  if(base==="fotos"){o.d=pDate(g("d"));if(!o.d)return null;o.h=pTime(g("h"));if(o.h==null)o.h=pTime(g("d"));o.loja=s("pdv");o.pesq=s("tipo");
    o.lat=pNum(g("lat"));o.lon=pNum(g("lon"));o.llat=pNum(g("llat"));o.llon=pNum(g("llon"));o.url=s("url");o.hash=s("hash")||o.url;return o}
  if(base==="faltas"){o.d=pDate(g("d"));if(!o.d)return null;const t=norm(s("ftipo")+" "+s("motivo"));o.motivo=s("motivo");
    o.tipo=/ATESTADO/.test(t)?"A":/INJUSTIF|NAO JUSTIF|SEM JUSTIF/.test(t)?"I":/JUSTIF/.test(t)||o.motivo?"J":"I";return o}
  if(base==="rota"){o.d=pDate(g("d"));if(!o.d)return null;o.h=pTime(g("h"));o.loja=s("pdv");o.dist=pNum(g("dist"));return o.dist==null?null:o}
  return null}
async function lerArquivo(file){
  const buf=await file.arrayBuffer();let wb;
  if(/\.csv$|\.txt$/i.test(file.name)){let t;try{t=new TextDecoder("utf-8",{fatal:true}).decode(buf)}catch(e){t=new TextDecoder("windows-1252").decode(buf)}wb=XLSX.read(t,{type:"string",raw:true})}
  else wb=XLSX.read(buf,{type:"array"});
  const out=[];
  for(const sn of wb.SheetNames){
    const m=XLSX.utils.sheet_to_json(wb.Sheets[sn],{header:1,defval:null,raw:true,blankrows:false});if(!m.length)continue;
    let best=null;for(let i=0;i<Math.min(15,m.length);i++){const c=mapCols(m[i]||[]),t=tipoDe(c,m[i]||[]);if(t){best={i,c,t};break}}
    if(!best){out.push({arq:file.name,aba:sn,base:null,cab:(m[0]||[]).filter(x=>x!=null).slice(0,12).join(", ")});continue}
    const ano=+(S.f.fim||"2026").slice(0,4),rows=[];for(let i=best.i+1;i<m.length;i++){const o=linha(best.t,best.c,m[i],ano);if(o)rows.push(o)}
    out.push({arq:file.name,aba:sn,base:best.t,rows,lidas:m.length-best.i-1})}
  return out}

/* ---------- estado e base de dados do artifact (por mês) ---------- */
let db=null,dl=null;
const S={view:"geral",f:{uf:"",sup:"",ini:"",fim:"",ano:"",q:""},pk:null,al:{niv:"",tipo:""},demo:true,cfg:JSON.parse(JSON.stringify(CFG0)),
  all:{},meses:{},R:null,dos:null,msg:"",load:false,contador:0};
const pack=(b,rows)=>rows.map(r=>FIELDS[b].map(f=>r[f]==null?null:r[f]));
const unpack=(b,arr)=>arr.map(a=>{const o={};FIELDS[b].forEach((f,i)=>o[f]=a[i]);return o});
function faixaDe(rows){let a="9",b="";for(const r of rows){if(r.d){if(r.d<a)a=r.d;if(r.d>b)b=r.d}}return[a,b]}
async function salvarBase(ym,base,rows,arq){
  (S.all[ym]=S.all[ym]||{})[base]=rows;const[dmin,dmax]=faixaDe(rows);
  const info={n:rows.length,arq,dmin,dmax,em:new Date().toISOString().slice(0,16).replace("T"," ")};
  const old=((S.meses[ym]||{})[base]||{}).ch||0;(S.meses[ym]=S.meses[ym]||{})[base]=info;if(!db)return;
  const arr=pack(base,rows),chunks=[];let cur=[],len=0;
  for(const a of arr){const j=JSON.stringify(a);if(len+j.length>150000&&cur.length){chunks.push(cur);cur=[];len=0}cur.push(a);len+=j.length+1}
  if(cur.length)chunks.push(cur);
  for(let i=0;i<chunks.length;i++)await db.doc("dados/"+ym+"_"+base+"_"+i).set({j:JSON.stringify(chunks[i])});
  for(let i=chunks.length;i<old;i++)await db.doc("dados/"+ym+"_"+base+"_"+i).delete();
  info.ch=chunks.length;const m={};for(const b in S.meses[ym])if(BASES[b])m[b]=S.meses[ym][b];
  await db.doc("meses/"+ym).set({bases:m})}
async function carregarMes(ym){
  if(S.all[ym]||!db||!S.meses[ym])return;S.all[ym]={};
  for(const base in S.meses[ym]){const inf=S.meses[ym][base];let rows=[];
    for(let i=0;i<(inf.ch||0);i++){const s=await db.doc("dados/"+ym+"_"+base+"_"+i).get();if(s.exists)rows=rows.concat(unpack(base,JSON.parse(s.data().j)))}
    S.all[ym][base]=rows}}
async function carregarFaixa(){for(const ym of mesesEntre(S.f.ini,S.f.fim))await carregarMes(ym)}
async function limparMes(ym){
  if(db&&S.meses[ym]){for(const base in S.meses[ym]){for(let i=0;i<(S.meses[ym][base].ch||0);i++)await db.doc("dados/"+ym+"_"+base+"_"+i).delete()}await db.doc("meses/"+ym).delete()}
  delete S.all[ym];delete S.meses[ym]}
function faixaPadrao(){let mx="",mn="9";
  for(const ym in S.meses)for(const b of["oper","pesq","humor"]){const i=S.meses[ym][b];if(i&&i.dmax){if(i.dmax>mx)mx=i.dmax;if(i.dmin<mn)mn=i.dmin}}
  if(!mx){const ms=Object.keys(S.meses).sort(),ym=ms[ms.length-1]||"2026-09";S.f.ini=ym+"-01";S.f.fim=fimMes(ym)}
  else{S.f.fim=mx;S.f.ini=mn>addD(mx,-13)?mn:addD(mx,-13)}
  S.f.ano=S.f.fim.slice(0,4)}
async function iniciarBase(){
  try{if(window.claude&&window.claude.use){db=await window.claude.use("db");dl=await window.claude.use("downloads")}}catch(e){db=null}
  if(!db)return;
  try{
    const c=await db.doc("config/geral").get();
    if(c.exists){const x=JSON.parse(c.data().j||"{}");S.cfg=Object.assign(JSON.parse(JSON.stringify(CFG0)),x);S.cfg.t=Object.assign({},CFG0.t,x.t||{})}
    const n=await db.doc("config/contador").get();if(n.exists)S.contador=n.data().n||0;
    const q=await db.collection("meses").get(),ms={};q.docs.forEach(d=>{ms[d.id]=JSON.parse(JSON.stringify(d.data().bases||{}))});
    if(Object.keys(ms).length){S.demo=false;S.all={};S.meses=ms;faixaPadrao();S.load=true;S.R=null;render();await carregarFaixa();S.load=false}
  }catch(e){S.msg="Não foi possível ler a base salva ("+(e.code||e.message||"erro")+"). Os dados de demonstração continuam na tela."}
  S.R=null;render()}
async function salvarCfg(){if(db){try{await db.doc("config/geral").set({j:JSON.stringify(S.cfg)})}catch(e){S.msg="As configurações valem nesta sessão, mas não foram salvas ("+(e.code||"erro")+")."}}}
async function baixar(nome,data){
  if(dl){try{await dl.save({filename:nome,data});return true}catch(e){if(e&&e.code==="declined")return false;S.msg="Não foi possível baixar o arquivo ("+((e&&e.code)||"erro")+").";return false}}
  const b=data instanceof Blob?data:new Blob([data]),u=URL.createObjectURL(b),a=document.createElement("a");a.href=u;a.download=nome;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);return true}

/* ---------- dados fictícios de demonstração (somem ao carregar arquivos reais) ---------- */
function demo(){
  const P=[["Joana Modelo Pereira","000.000.001-01","Carlos Exemplo Souza","BA",{atr:3,sai:3,auto:6,exp:.14,bad:3,ad:[.86,.95],fj:1,dup:1,fora:1,neg:.15}],
   ["Pedro Fictício Lima","000.000.002-02","Carlos Exemplo Souza","BA",{atr:6,sai:1,exp:.28,bad:2,ad:[.8,.88],neg:.45,run:[12,5],auto:3}],
   ["Rita Exemplo Santos","000.000.003-03","Carlos Exemplo Souza","BA",{atr:1,exp:.06,ad:[.9,.96],neg:.1}],
   ["Bruno Teste Almeida","000.000.004-04","Marta Fictícia Rocha","CE",{exp:.02,ad:[.97,1],neg:.05}],
   ["Lúcia Modelo Castro","000.000.005-05","Marta Fictícia Rocha","CE",{atr:4,exp:.22,bad:3,ad:[.84,.94],neg:.5,run:[15,4],auto:2}],
   ["Diego Exemplo Nunes","000.000.006-06","Marta Fictícia Rocha","CE",{exp:.03,ad:[.96,.98],neg:.08}],
   ["Sara Fictícia Melo","000.000.007-07","Paulo Modelo Dias","MA",{fi:2,auto:9,foraH:2,exp:.12,ad:[.88,.93],neg:.2}],
   ["Tiago Modelo Reis","000.000.008-08","Paulo Modelo Dias","MA",{atr:2,exp:.2,bad:1,ad:[.82,.9],neg:.12}],
   ["Helena Teste Barros","000.000.009-09","Paulo Modelo Dias","MA",{exp:.02,ad:[.98,.97],neg:.05}],
   ["Caio Exemplo Pinto","000.000.000-00","Marta Fictícia Rocha","CE",{sai:2,exp:.08,ad:[.93,.95],neg:.1}]];
  const W=[];for(let d=1;d<=30;d++){const s="2026-09-"+p2(d),w=new Date(s+"T12:00:00").getDay();if(w!==0&&d!==7)W.push(s)}
  const D={oper:[],pesq:[],humor:[],ader:[],fotos:[],faltas:[],rota:[]},POS=["Feliz","Motivado","Bem"],NEG=["Cansado","Sobrecarregado","Triste","Doente"],MAR=["MARCA A","MARCA B","MARCA C"];
  P.forEach((p,pi)=>{const [nome,mat,sup,uf,f]=p,k=norm(nome),r=rng(1000+pi*77),L=[uf+" / LOJA FICTICIA "+p2(pi*2+1),uf+" / LOJA FICTICIA "+p2(pi*2+2)],M=[MAR[pi%3],MAR[(pi+1)%3]];
    const ix=W.map((_,i)=>i).sort(()=>r()-.5);let c=0;const take=n=>{const a=ix.slice(c,c+(n||0));c+=n||0;return new Set(a)};
    const fal=take((f.fi||0)+(f.fj||0)),atr=take(f.atr),sai=take(f.sai),aut=take(f.auto);let fn=0;
    W.forEach((d,i)=>{const wk=isoWeek(d),base={k,nome,mat,sup,uf,d};
      if(fal.has(i)){const inj=fn<(f.fi||0);fn++;D.faltas.push({k,nome,mat,d,tipo:inj?"I":"J",motivo:inj?"":"Consulta médica"})}
      else{const c1=atr.has(i)?505+Math.floor(r()*45):472+Math.floor(r()*12);
        D.oper.push({...base,pdv:L[0],cin:c1,cout:708+Math.floor(r()*8),auto:0});
        const c2=792+Math.floor(r()*8),o2=aut.has(i)?1439:sai.has(i)?930+Math.floor(r()*55):1051+Math.floor(r()*12);
        D.oper.push({...base,pdv:L[1],cin:c2,cout:o2,auto:aut.has(i)?1:0});
        if(r()>.08){const ng=(f.run&&i>=f.run[0]&&i<f.run[0]+f.run[1])||r()<(f.neg||0);D.humor.push({k,nome,mat,d,op:(ng?NEG:POS)[Math.floor(r()*(ng?4:3))]})}}
      const wi=[36,37,38,39,40].indexOf(wk);
      for(let j=0;j<7;j++){const e=fal.has(i)||r()<(f.exp||0)*(wi===f.bad?3.2:.75);D.pesq.push({k,nome,mat,sup,uf,d,loja:L[j<4?0:1],cli:M[j<4?0:1],tipo:["Abastecimento","Ponto extra","Preço"][j%3],st:e?"E":"R"})}});
    [36,37,38,39,40].forEach(w=>{const n=W.filter(d=>isoWeek(d)===w).length;[0,1].forEach(li=>{const ct=n*(li?1:2);D.ader.push({k,nome,sup,uf,d:weekMonday(2026,w),loja:L[li],marca:M[li],ct,rz:Math.min(ct,Math.round(ct*f.ad[li]))})})});
    const lat=-12.9+pi*.3,lon=-38.5-pi*.2,vis=D.oper.filter(o=>o.k===k&&o.pdv===L[0]);
    vis.slice(0,4).forEach((v,i)=>D.fotos.push({k,nome,mat,d:v.d,h:v.cin+60+i*9,loja:L[0],pesq:"Abastecimento – "+M[0],lat,lon,llat:lat,llon:lon,hash:"H"+mat+"-"+i,url:""}));
    if(f.dup&&vis.length>8)[vis[5],vis[8]].forEach(v=>D.fotos.push({k,nome,mat,d:v.d,h:v.cin+95,loja:L[0],pesq:"Abastecimento – "+M[0],lat,lon,llat:lat,llon:lon,hash:"HDUP"+mat,url:""}));
    if(f.fora&&vis.length>10){const v=vis[10];D.fotos.push({k,nome,mat,d:v.d,h:v.cin+120,loja:L[0],pesq:"Ponto extra – "+M[1],lat:lat+.0058,lon,llat:lat,llon:lon,hash:"HF"+mat,url:""})}
    for(let i=0;i<(f.foraH||0)&&vis.length>12;i++){const v=vis[11+i];D.fotos.push({k,nome,mat,d:v.d,h:1150+i*12,loja:L[0],pesq:"Abastecimento – "+M[0],lat,lon,llat:lat,llon:lon,hash:"HH"+mat+i,url:""})}});
  const inf={};for(const b in D){if(!D[b].length)continue;const[a,z]=faixaDe(D[b]);inf[b]={n:D[b].length,arq:"dados fictícios",dmin:a,dmax:z,em:"demonstração"}}
  S.all={"2026-09":D};S.meses={"2026-09":inf};faixaPadrao()}

/* =====================================================================
   INDICADORES E ALERTAS
   ===================================================================== */
const lvl=(v,t)=>t[2]&&v>=t[2]?3:t[1]&&v>=t[1]?2:t[0]&&v>=t[0]?1:0;
function dadosDaFaixa(){
  const ini=S.f.ini,fim=S.f.fim,R={};for(const b in BASES)R[b]=[];
  for(const ym of mesesEntre(ini,fim)){const D=S.all[ym];if(!D)continue;
    for(const b in D){const a=R[b]||(R[b]=[]);for(const r of D[b]){if(b==="ader"?(r.d>=mondayOf(ini)&&r.d<=fim):(r.d>=ini&&r.d<=fim))a.push(r)}}}
  return R}
function calcular(){
  const cfg=S.cfg,T=cfg.t,R=dadosDaFaixa(),has={};for(const b in BASES)has[b]=R[b].length>0;
  /* a chave do promotor é o CPF; linhas sem CPF herdam o CPF do mesmo nome em outra base */
  const n2c=new Map();for(const b in R)for(const r of R[b])if(r.mat&&r.nome)n2c.set(norm(r.nome),r.mat);
  for(const b in R)for(const r of R[b]){const c=r.mat||n2c.get(norm(r.nome))||"";if(c){r.mat=c;r.k="C"+c}else if(r.nome)r.k=norm(r.nome)}
  const ppl=new Map();
  for(const b of["oper","pesq","ader","humor","faltas","fotos","rota"])for(const r of R[b]){if(!r.k)continue;let p=ppl.get(r.k);if(!p)ppl.set(r.k,p={k:r.k,nome:r.nome,mat:"",sup:"",uf:""});
    if(r.mat&&!p.mat)p.mat=r.mat;if(r.sup&&!p.sup)p.sup=r.sup;if(r.uf&&!p.uf)p.uf=r.uf}
  const G={};for(const b in R)G[b]=group(R[b],r=>r.k);
  const negS=new Set(cfg.neg.map(norm)),ferS=new Set(cfg.fer);
  const hc=new Map();for(const f of R.fotos){if(!f.hash)continue;let s=hc.get(f.hash);if(!s)hc.set(f.hash,s=new Set());s.add(f.k+"|"+f.d+"|"+norm(f.loja))}
  const list=[];
  for(const p of ppl.values()){
    const o=Object.assign({},p);
    const jr=(G.oper.get(p.k)||[]).find(r=>r.jor);o.jorTxt=jr?jr.jor:"";
    const mi=/INICIO (\d{1,2})H/.exec(norm(o.jorTxt));
    const e=cfg.escP[p.k]||(mi?{ini:+mi[1]*60,fim:cfg.esc.fim}:cfg.esc);o.esc=e;
    /* humor */
    const hm=new Map(),dd=[];for(const h of(G.humor.get(p.k)||[])){const n=negS.has(norm(h.op));hm.set(h.d,(hm.get(h.d)||false)||n);if(norm(h.op)==="DOENTE")dd.push(h.d)}
    const hd=[...hm.keys()].sort();let seq=0,cur=0,neg=0;for(const d of hd){if(hm.get(d)){neg++;cur++;if(cur>seq)seq=cur}else cur=0}
    o.hum={dias:hd.length,neg,pct:hd.length?neg/hd.length:null,seq,map:hm,doente:new Set(dd).size};
    /* jornada */
    const vd=group(G.oper.get(p.k)||[],r=>r.d),dias=[];
    for(const d of[...vd.keys()].sort()){const vs=vd.get(d).slice().sort((a,b)=>a.cin-b.cin),fer=ferS.has(d),last=vs[vs.length-1];
      const man=vs.filter(v=>!v.auto&&v.cout!=null),lo=man.length?Math.max(...man.map(v=>v.cout)):null,first=vs[0].cin;
      const x={d,cin:first,cout:last.auto?null:lo,auto:vs.some(v=>v.auto),atraso:0,saida:0,neg:hm.get(d)===true,lojas:new Set(vs.map(v=>v.pdv)).size};
      if(!fer&&first>e.ini+cfg.tolAtr)x.atraso=first-e.ini;
      if(cfg.saida&&!fer&&!last.auto&&lo!=null&&lo<e.fim-cfg.tolSai)x.saida=e.fim-lo;
      x.desvio=!!(x.atraso||x.saida||x.auto);dias.push(x)}
    o.jor={dias,trab:dias.length,nAtr:dias.filter(x=>x.atraso).length,nSai:dias.filter(x=>x.saida).length,nAuto:dias.filter(x=>x.auto).length,minAtr:dias.reduce((a,x)=>a+x.atraso,0),minSai:dias.reduce((a,x)=>a+x.saida,0)};
    /* pesquisas */
    const ps=G.pesq.get(p.k)||[],ag=(rows,f)=>[...group(rows,f)].map(([k,v])=>({k,prog:v.length,resp:v.filter(r=>r.st==="R").length,exp:v.filter(r=>r.st==="E").length}));
    o.pes={prog:ps.length,resp:ps.filter(r=>r.st==="R").length,exp:ps.filter(r=>r.st==="E").length,sem:ag(ps,r=>isoWeek(r.d)).sort((a,b)=>a.k-b.k),loja:ag(ps,r=>r.loja).sort((a,b)=>b.exp-a.exp),dia:ag(ps,r=>r.d).sort((a,b)=>a.k<b.k?-1:1)};
    o.pes.pct=o.pes.prog?o.pes.exp/o.pes.prog:null;
    o.pes.semExec=o.pes.dia.filter(x=>x.prog>0&&x.resp===0&&vd.has(x.k)&&!ferS.has(x.k)).map(x=>x.k);
    /* aderência */
    const al=[...group(G.ader.get(p.k)||[],r=>r.loja)].map(([loja,v])=>{const ct=v.reduce((a,r)=>a+r.ct,0),rz=v.reduce((a,r)=>a+r.rz,0),x=ct?rz/ct:null;
      return{loja,ct,rz,pend:Math.max(0,ct-rz),pct:x,st:x==null?"":x*100<cfg.m1?"abaixo da Meta 1":x*100<cfg.m2?"abaixo da Meta 2":"ok"}}).sort((a,b)=>(a.pct||0)-(b.pct||0));
    const act=al.reduce((a,l)=>a+l.ct,0);o.ad={lojas:al,ct:act,rz:al.reduce((a,l)=>a+l.rz,0),pct:act?al.reduce((a,l)=>a+l.rz,0)/act:null,baixo:al.filter(l=>l.st&&l.st!=="ok")};
    o.ad.pend=o.ad.baixo.reduce((a,l)=>a+l.pend,0);
    /* faltas */
    const fl=(G.faltas.get(p.k)||[]).slice().sort((a,b)=>a.d<b.d?-1:1);o.fal={list:fl,I:fl.filter(x=>x.tipo==="I").length,J:fl.filter(x=>x.tipo==="J").length,A:fl.filter(x=>x.tipo==="A").length};
    /* fotos */
    o.fot=[];for(const f of(G.fotos.get(p.k)||[])){const m=[];
      if(f.hash&&hc.get(f.hash).size>1)m.push("Imagem repetida em outra visita");
      if(f.lat!=null&&f.lon!=null&&f.llat!=null&&f.llon!=null){const ds=dist(f.lat,f.lon,f.llat,f.llon);if(ds>cfg.distFoto)m.push("Captura a "+Math.round(ds)+" m da loja")}
      if(has.oper&&f.h!=null){const vs=vd.get(f.d);if(vs){const nl=norm(f.loja),at=vs.filter(v=>norm(v.pdv)===nl);if(at.length&&!at.some(v=>f.h>=v.cin-5&&(v.cout==null||v.auto||f.h<=v.cout+5)))m.push("Fora do horário da visita")}}
      if(m.length)o.fot.push(Object.assign({},f,{mot:m}))}
    o.fotN=(G.fotos.get(p.k)||[]).length;
    /* fuga de rota (posição fora da cerca da loja) */
    const rt=(G.rota.get(p.k)||[]).filter(x=>x.dist>cfg.cerca);o.rota={n:rt.length,dias:new Set(rt.map(x=>x.d)).size,max:rt.length?Math.max(...rt.map(x=>x.dist)):0,list:rt};
    o.lojas=[...new Set([].concat((G.oper.get(p.k)||[]).filter(r=>!/NAO OPERACIONAL|REUNIAO/.test(norm(r.pdv))).map(r=>r.pdv),ps.map(r=>r.loja),al.map(l=>l.loja)).filter(Boolean))].sort();
    /* leitura cruzada com humor */
    const cz=[];
    if(hd.length){
      const an=dias.filter(x=>x.atraso&&x.neg).length;if(o.jor.nAtr&&an)cz.push(an+" dos "+plural(o.jor.nAtr,"atraso","atrasos")+" ocorreram em dias com humor negativo");
      const sn=dias.filter(x=>x.saida&&x.neg).length;if(sn)cz.push(sn+" das "+plural(o.jor.nSai,"saída antecipada","saídas antecipadas")+" ocorreram em dias com humor negativo");
      if(o.pes.exp>=5){const w=o.pes.sem.slice().sort((a,b)=>b.exp-a.exp)[0],nw=hd.filter(d=>isoWeek(d)===w.k&&hm.get(d)).length;
        if(nw>=2&&w.exp>=o.pes.exp*.35)cz.push("a semana "+w.k+" concentra "+w.exp+" das "+o.pes.exp+" pesquisas expiradas e teve "+nw+" dias com humor negativo")}}
    o.cruz=cz;
    o.alertas=alertasDe(o,T,cfg);
    const n3=o.alertas.filter(a=>a.sev===3).length,sc=o.alertas.reduce((a,x)=>a+x.sev,0);o.score=sc;
    o.niv=!o.alertas.length?"":(sc>=9||n3>=2)?"C":sc>=5?"A":sc>=3?"T":"";
    list.push(o)}
  const q=norm(S.f.q),qd=S.f.q.replace(/\D/g,""),ord={C:0,A:1,T:2,"":3};
  const sups=[...new Set(list.map(p=>p.sup).filter(Boolean))].sort(),ufs=[...new Set(list.map(p=>p.uf).filter(Boolean))].sort();
  const vis=list.filter(p=>(!S.f.uf||p.uf===S.f.uf)&&(!S.f.sup||p.sup===S.f.sup)&&(!q||norm(p.nome).includes(q)||(qd&&(p.mat||"").replace(/\D/g,"").includes(qd)))).sort((a,b)=>ord[a.niv]-ord[b.niv]||b.score-a.score||a.nome.localeCompare(b.nome));
  S.R={has,list:vis,todos:list,sups,ufs}}
function alertasDe(o,T,cfg){const A=[],add=(tipo,sev,tit,det)=>A.push({tipo,sev,tit,det});
  const j=o.jor,pe=o.pes;
  let s=lvl(j.nAtr,T.atr);if(s)add("jor",s,"Atrasos no check-in",plural(j.nAtr,"dia","dias")+" com check-in após a tolerância, em "+j.trab+" dias trabalhados");
  s=lvl(j.nSai,T.sai);if(s)add("jor",s,"Saídas antecipadas",plural(j.nSai,"dia","dias")+" com check-out antes do fim da jornada");
  s=lvl(j.nAuto,T.auto);if(s)add("auto",s,"Check-out automático",j.nAuto+" de "+j.trab+" dias sem check-out manual");
  if(pe.prog>=T.expMin){s=lvl((pe.pct||0)*100,T.exp);if(s)add("pesq",s,"Pesquisas expiradas",pe.exp+" de "+pe.prog+" pesquisas ("+pc(pe.pct)+")")}
  s=lvl(pe.semExec.length,T.semExec);if(s)add("exec",s,"Dias sem atividades",plural(pe.semExec.length,"dia","dias")+" com atividades programadas e nenhuma respondida");
  s=lvl(o.fal.I,T.falta);if(s)add("falta",s,"Faltas injustificadas",plural(o.fal.I,"falta","faltas")+(o.fal.A?" e "+plural(o.fal.A,"atestado","atestados"):""));
  s=lvl(o.fot.length,T.foto);if(s)add("foto",s,"Fotos com indício",plural(o.fot.length,"foto","fotos")+" de "+o.fotN+" analisadas ("+[...new Set(o.fot.flatMap(f=>f.mot.map(m=>m.replace(/\d+ m/,"X m"))))].join("; ").toLowerCase()+")");
  if(o.ad.baixo.length){s=Math.max(o.ad.baixo.some(l=>/Meta 1/.test(l.st))?2:1,lvl(o.ad.pend,T.pend));add("ader",s,"Impacto na aderência",plural(o.ad.baixo.length,"loja","lojas")+" abaixo da meta, com "+plural(o.ad.pend,"visita pendente","visitas pendentes")+" do contratado")}
  s=lvl(o.rota.dias,T.rota);if(s)add("rota",s,"Fuga de rota",o.rota.n+" posições fora da cerca de "+cfg.cerca+" m em "+plural(o.rota.dias,"dia","dias")+" (maior distância: "+Math.round(o.rota.max)+" m)");
  const h=o.hum,hNeg=h.dias>=5&&((h.pct||0)*100>=T.humPct||h.seq>=T.humSeq);
  const imp=(pe.prog>=T.expMin&&(pe.pct||0)*100>T.exp[0])||j.nAtr>=T.atr[0]||o.ad.baixo.length>0||pe.semExec.length>=2;
  if(hNeg&&imp)add("sobre",2,"Possível sobrecarga","Humor negativo em "+pc(h.pct,0)+" dos dias (maior sequência: "+plural(h.seq,"dia","dias")+"), junto com queda de desempenho e "+plural(o.lojas.length,"loja atendida","lojas atendidas"));
  else if(hNeg)add("humor",1,"Humor negativo recorrente","Humor negativo em "+pc(h.pct,0)+" dos dias com registro (maior sequência: "+plural(h.seq,"dia","dias")+")"+(h.doente?"; "+plural(h.doente,"dia","dias")+" como “Doente”":""));
  return A.sort((a,b)=>b.sev-a.sev)}
const R=()=>{if(!S.R)calcular();return S.R};
const pessoa=()=>{const r=R();return(S.pk&&r.todos.find(p=>p.k===S.pk))||r.list[0]||null};
