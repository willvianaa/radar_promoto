import re, base64, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
B = r"C:\Users\RT-151\Desktop\radar_promotor"
rd = lambda p: open(p, encoding="utf-8").read()
v1 = rd(B + r"\radar_v3\v1_original.html").split("\n")
L = lambda a, b: "\n".join(v1[a-1:b])
e2 = rd(B + r"\radar_v2\engine.js").split("\n")
u2 = rd(B + r"\radar_v2\ui.js").split("\n")
d2 = rd(B + r"\radar_v2\dossie.js").split("\n")
E = lambda a, b: "\n".join(e2[a-1:b])
U = lambda a, b: "\n".join(u2[a-1:b])
D = lambda a, b: "\n".join(d2[a-1:b])
P = lambda n: rd(B + r"\radar_v3\parts\\" + n)

def sub(txt, old, new, count=1):
    assert txt.count(old) >= 1, "nao achou: " + old[:70]
    if count == 1:
        assert txt.count(old) == 1, "ambiguo (%d): %s" % (txt.count(old), old[:70])
    return txt.replace(old, new)

# ---------------- motor (v2) + ajustes ----------------
eng = E(6, 291)
eng = sub(eng, 'A:["Alto","var(--warn)","p-warn"],T:["Atenção","var(--m2)","p-m2"]', 'A:["Alto","var(--rt)","p-rt"],T:["Atenção","var(--warn)","p-warn"]')
eng = re.sub(r'const TIPOS=\{.*?\};', 'const TIPOS={jor:"Jornada: início tardio e saída",auto:"Jornada: check-out automático",pesq:"Pesquisas expiradas",exec:"Dias sem atividades",ader:"Impacto na aderência",falta:"Ausências: falta não justificada",foto:"Fotos com indício",rota:"Fuga de rota",sobre:"Sobrecarga",humor:"Humor"};', eng, count=1, flags=re.S)
eng = sub(eng, 'al:{niv:"",tipo:""},demo:true', 'al:{niv:"",tipo:""},alN:60,rkN:15,PL:null,demo:true')
eng = sub(eng, 'const x={d,cin:first,', 'const x={d,vs,cin:first,')
eng = sub(eng, 'let seq=0,cur=0,neg=0;for(const d of hd){if(hm.get(d)){neg++;cur++;if(cur>seq)seq=cur}else cur=0}', 'let seq=0,cur=0,neg=0,seqFim=null;for(const d of hd){if(hm.get(d)){neg++;cur++;if(cur>seq){seq=cur;seqFim=d}}else cur=0}')
eng = sub(eng, 'seq,map:hm,doente:new Set(dd).size}', 'seq,seqFim,map:hm,doente:new Set(dd).size}')
eng = sub(eng, '(mi?{ini:+mi[1]*60,fim:cfg.esc.fim}:cfg.esc)', '(mi?{ini:+mi[1]*60,fim:+mi[1]*60+(cfg.esc.fim-cfg.esc.ini)}:cfg.esc)')
a = eng.index("    o.alertas=alertasDe(o,T,cfg);")
b = eng.index("function alertasDe(")
novo = '''    o.alertas=alertasDe(o,T,cfg);
    const n3=o.alertas.filter(a=>a.sev===3).length,sc=o.alertas.reduce((a,x)=>a+x.sev,0);o.score=sc;
    o.niv=!o.alertas.length?"":(sc>=9||n3>=2)?"C":sc>=5?"A":sc>=3?"T":"";
    o.cls=o.niv||"N";o.sobre=o.alertas.some(a=>a.tipo==="sobre");
    const cl=x=>Math.max(0,Math.min(100,Math.round(x))),j=o.jor;
    o.dim={"Aderência":o.ad.pct==null?null:cl(o.ad.pct*100),"Pesquisas":o.pes.pct==null?null:cl(100-o.pes.pct*400),"Pontualidade":j.trab?cl(100-(j.nAtr+j.nSai)/j.trab*200):null,"Registro de jornada":j.trab?cl(100-j.nAuto/j.trab*200):null,"Fotos":o.fotN?cl(100-o.fot.length/o.fotN*500):null,"Presença":has.faltas?cl(100-o.fal.I*25-o.fal.J*6):null,"Humor":o.hum.dias?cl(100-o.hum.pct*100):null};
    const dv=Object.entries(o.dim).filter(x=>x[0]!=="Humor"&&x[1]!=null).map(x=>x[1]);
    o.risco=cl(sc*10);
    o.ev=eventosDe(o,cfg,T);
    list.push(o)}
  S.PL={has,R,list}}
'''
eng = eng[:a] + novo + eng[b:]
eng = eng.replace("S.R=null", "S.PL=S.R=null")
# armazenamento novo (o antigo tem outro formato de campos)
eng = eng.replace('"dados/"+ym', '"dados3/"+ym').replace('doc("meses/"', 'doc("meses3/"').replace('collection("meses")', 'collection("meses3")')
eng = sub(eng, 'len+j.length>150000', 'len+j.length>(Z?700000:150000)')
eng = sub(eng, '.set({j:JSON.stringify(chunks[i])})', '.set({j:Z?"z:"+await gz(JSON.stringify(chunks[i])):JSON.stringify(chunks[i])})')
eng = sub(eng, 'rows=rows.concat(unpack(base,JSON.parse(s.data().j)))', 'rows=rows.concat(unpack(base,JSON.parse(await lerJ(s.data().j))))')
eng = sub(eng, 'async function salvarBase(', '''const Z=typeof CompressionStream!=="undefined";
async function gz(s){const cs=new CompressionStream("gzip"),w=cs.writable.getWriter();w.write(new TextEncoder().encode(s));w.close();const u=new Uint8Array(await new Response(cs.readable).arrayBuffer());let b="";for(let i=0;i<u.length;i+=8192)b+=String.fromCharCode.apply(null,u.subarray(i,i+8192));return btoa(b)}
async function lerJ(t){if(t.slice(0,2)!=="z:")return t;const bin=atob(t.slice(2)),u=new Uint8Array(bin.length);for(let i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);const ds=new DecompressionStream("gzip"),w=ds.writable.getWriter();w.write(u);w.close();return await new Response(ds.readable).text()}
async function salvarBase(''')
eng = sub(eng, 'FIELDS[b].map(f=>r[f]==null?null:r[f])', 'FIELDS[b].map(f=>f==="k"||r[f]==null?null:r[f])')
assert 'dados/' not in eng and '"meses/' not in eng
tail = P("engine_tail.js")

# ---------------- v3.1: aderência 2PRT, PDOH e carga de trabalho ----------------
eng = sub(eng, 'for(const b of["oper","pesq","humor"]){const i=S.meses[ym][b]', 'for(const b of["oper","pesq","humor","ader"]){const i=S.meses[ym][b]')
eng = sub(eng, 'rota:"Posição (fuga de rota)"};', 'rota:"Posição (fuga de rota)",pdoh:"PDOH (horas por colaborador)"};')
eng = sub(eng, 'rota:["k","nome","mat","d","h","loja","dist"]};', 'rota:["k","nome","mat","d","h","loja","dist"],\n  pdoh:["k","nome","sup","uf","d","dias","prod","desl","ocio","hnr"]};')
eng = sub(eng, '    o.ad.pend=o.ad.baixo.reduce((a,l)=>a+l.pend,0);', """    o.ad.pend=o.ad.baixo.reduce((a,l)=>a+l.pend,0);
    const aw=[...group(G.ader.get(p.k)||[],r=>r.d)].map(([d,v])=>{const ct=v.reduce((a,r)=>a+r.ct,0),rz=v.reduce((a,r)=>a+r.rz,0);return{d,ct,rz,lojas:new Set(v.filter(r=>r.ct>0).map(r=>r.loja)).size,pct:ct?rz/ct:null}}).sort((a,b)=>a.d<b.d?-1:1);
    o.ad.sem=aw;o.carga={media:aw.length?aw.reduce((a,w)=>a+w.ct,0)/aw.length:0,lojas:aw.length?Math.max(...aw.map(w=>w.lojas)):0,queda:aw.length>=2&&aw[0].pct!=null&&aw[aw.length-1].pct!=null?aw[0].pct-aw[aw.length-1].pct:0};
    const pdr=G.pdoh.get(p.k)||[];o.pd=null;if(pdr.length){const sm=f=>pdr.reduce((a,r)=>a+(r[f]||0),0),pd={dias:Math.max(...pdr.map(r=>r.dias||0)),prod:sm("prod"),desl:sm("desl"),ocio:sm("ocio"),hnr:sm("hnr")};pd.tot=pd.prod+pd.desl+pd.ocio+pd.hnr;if(pd.tot>0)o.pd=pd}""")
eng = sub(eng, '''  if(hNeg&&imp)add("sobre",2,"Possível sobrecarga","Humor negativo em "+pc(h.pct,0)+" dos dias (maior sequência: "+plural(h.seq,"dia","dias")+"), junto com queda de desempenho e "+plural(o.lojas.length,"loja atendida","lojas atendidas"));''', """  const cg=o.carga,cgAlta=!!cg&&o.ad.sem.length>=2&&cg.media>=(T.carga||44)&&cg.queda*100>=(T.quedaPp||5);
  const pdT=o.pd?"PDOH: "+pc(o.pd.prod/o.pd.tot,0)+" produtivo, "+pc(o.pd.ocio/o.pd.tot,0)+" ócio e "+pc(o.pd.hnr/o.pd.tot,0)+" sem registro.":"";
  const cgT=cgAlta?"Média de "+Math.round(cg.media)+" visitas contratadas por semana (até "+plural(cg.lojas,"loja","lojas")+") e aderência de "+pc(o.ad.sem[0].pct,0)+" para "+pc(o.ad.sem[o.ad.sem.length-1].pct,0)+" nas semanas fechadas.":"";
  const hT=hNeg?"Humor negativo em "+pc(h.pct,0)+" dos dias (maior sequência: "+plural(h.seq,"dia","dias")+")"+(imp&&!cgAlta?", junto com queda de desempenho e "+plural(o.lojas.length,"loja atendida","lojas atendidas"):"")+".":"";
  if((hNeg&&imp)||cgAlta)add("sobre",hNeg&&cgAlta?3:2,"Possível sobrecarga",[cgT,hT,pdT].filter(Boolean).join(" "));""")

# ---------------- v4.0: jornada unificada + ausências (afastamentos) ----------------
eng = sub(eng, 'if(/FALTA|ATESTADO|AUSENCIA|JUSTIFICATIVA/.test(H)', 'if(/FALTA|ATESTADO|AUSENCIA|AFASTAMENT|JUSTIFICATIVA/.test(H)')
eng = sub(eng, 'ftipo:[/^TIPO/,/JUSTIFICAD/,/^FALTA/]', 'ftipo:[/^TIPO/,/JUSTIFICAD/,/^FALTA/,/AFASTAMENT/]')
eng = sub(eng, 'o.motivo=s("motivo");', 'o.motivo=s("motivo")||s("ftipo");')
eng = sub(eng, 'motivo:inj?"":"Consulta médica"', 'motivo:inj?"":["Atestado médico","Oportunidade no aparelho","Consulta médica","Curso da empresa"][fn%4]')

# ---------------- UI ----------------
radar = L(736, 765)
radar = sub(radar, 'cor={D:"var(--bad)",S:"var(--vio)",M:"var(--warn)",N:"var(--good)"}', 'cor={C:"var(--bad)",A:"var(--rt)",T:"var(--warn)",N:"var(--good)"}')
radar = sub(radar, 'hot=p.cls==="D"||p.cls==="S"', 'hot=p.cls==="C"||p.sobre')
radar = sub(radar, 'CLS[p.cls][0].toLowerCase()', '(p.niv?NIV[p.niv][0]:"Estável").toLowerCase()')
radar = sub(radar, 'const crit=L.filter(p=>p.risco>=55).length;', 'const crit=L.filter(p=>p.cls==="C").length;')
radar = sub(radar, '100-(c.c.jor||90)', '10')
radar = sub(radar, 'c.c.exp', 'c.t.exp[0]')
radar = sub(radar, 'c.c.humPct', 'c.t.humPct')
radar = sub(radar, 'p.jor.dias.filter(x=>x.n).length', 'p.jor.dias.filter(x=>x.desvio).length')
radar = sub(radar, 'Possível medida</span>', 'Crítico</span>')
radar = sub(radar, '<i style="background:var(--vio)"></i>Sobrecarga</span>', '<i style="background:var(--rt)"></i>Alto</span>')
radar = sub(radar, 'Melhoria</span>', 'Atenção</span>')
radar = sub(radar, 'Sem pontos</span>', 'Estável</span>')
radar = sub(radar, 'Clique num ponto para abrir o Raio-X.', 'Pontos que pulsam indicam nível crítico ou possível sobrecarga. Clique num ponto para abrir o Raio-X.')
radar = radar.replace('Nenhum promotor na zona crítica', 'Nenhum promotor em nível crítico').replace('na zona crítica', 'em nível crítico')

radar = sub(radar, 'gs=[...group(L,p=>p.sup||"Sem supervisor")]', 'gs=[...group(L,p=>S.f.uf||S.f.sup?(p.sup||"Sem supervisor"):(p.uf||"—"))]')
radar = sub(radar, 'sz=4+Math.min(5,p.alertas.length/5)', 'sz=p.niv?4+Math.min(4,p.score/3):2.4')
radar = sub(radar, "(p.risco>=45?'<text", "(p.cls===\"C\"?'<text")
radar = sub(radar, "gs.forEach(([s,ps],gi)=>{", "const bl0=[],bl1=[];gs.forEach(([s,ps],gi)=>{")
radar = sub(radar, "svg+='<g class=\"blip'", "(p.niv?bl1:bl0).push('<g class=\"blip'")
radar = sub(radar, "+'</g>'})});", "+'</g>')})});svg+=bl0.join(\"\")+bl1.join(\"\");")
radar = sub(radar, 'As fatias são as equipes de cada supervisor.', 'As fatias são os estados (com a UF filtrada, as equipes de cada supervisor). Pontos pequenos são promotores estáveis.')

# v3.2: radar novo (nomes dos promotores, fatias por UF)
i0 = radar.index("  const rad=x=>"); i1 = radar.index("  /* parâmetros */")
radar = radar[:i0] + '  const crit=L.filter(p=>p.cls==="C").length,svg=radarSvg(L,cor);\n' + radar[i1:]
radar = sub(radar, "'+svg+'</div>'", "'+svg+'</div>'+radarNomes(L,cor)")
radar = sub(radar, '<div class="rp-grid"><div class="scope">', '<div class="rp-grid"><div class="rp-card"><div class="scope">')
radar = sub(radar, "'+svg+'</div>'+radarNomes(L,cor)", "'+svg+'</div></div>'+radarNomes(L,cor)")
radar, nins = re.subn(r"'<div class=\"rp-ins\">.*?</div>'\)\+'</div>", "'", radar, count=1, flags=re.S)
assert nins == 1, "leitura automatica nao removida"
radar = radar.replace("ins=insights(),", "")
radar, np_ = re.subn(r"<p>Cada ponto é um promotor\..*?</p>", "", radar, count=1, flags=re.S)
assert np_ == 1, "texto do radar nao removido"

radar = sub(radar, "return'<div class=\"prm\">", "return'<div class=\"prm prm-click\" data-a=\"setor\" data-v=\"'+({\"Aderência\":\"ader\",\"Pesquisas expiradas\":\"pesq\",\"Dias com ocorrência de jornada\":\"jor\",\"Check-out automático\":\"auto\",\"Humor negativo\":\"humor\",\"Fotos com indício\":\"foto\"}[l]||\"\")+'\">")
handlers = U(143, 190)
handlers = handlers.replace("S.R=null", "S.PL=S.R=null")
handlers = sub(handlers, 'tq=setTimeout(()=>{S.PL=S.R=null;renderView()},200)', 'tq=setTimeout(()=>{S.R=null;renderView()},200)')
handlers = sub(handlers, 'S.dos=null;S.PL=S.R=null;ir("raio-x")}return}', 'S.dos=null;S.R=null;ir("raio-x")}return}')
handlers = sub(handlers, 'S.f[f]=t.value;S.PL=S.R=null;render();return', 'S.f[f]=t.value;S.R=null;S.dos=null;render();return')
handlers = sub(handlers, '  if(!f)return;', '  if(t.id==="rx-p"){S.pk=t.value;S.dos=null;renderView();return}\n  if(!f)return;')
handlers = sub(handlers, '  else if(a==="dados")modalDados();', '  else if(a==="alTipo"){S.al.tipo=S.al.tipo===v?"":v;S.alN=60;renderView()}\n  else if(a==="fotoZoom"){fotoZoom(+v)}\n  else if(a==="ping"){radarPing(v,b)}\n  else if(a==="pingX"){document.querySelectorAll(".rp-pop").forEach(x=>x.remove());document.querySelectorAll(".blip.sel").forEach(x=>x.classList.remove("sel"))}\n  else if(a==="alLimpar"){S.al.niv="";S.al.tipo="";S.alN=24;renderView()}\n  else if(a==="fotoRx"){fotoRx(+v)}\n  else if(a==="kpiM"){kpiModal(v)}\n  else if(a==="nivM"){nivModal(v)}\n  else if(a==="fgPause"){const fv=document.querySelector(".fg-view");if(fv)fv.classList.toggle("paused")}\n  else if(a==="setor"){if(v==="geral"){window.scrollTo({top:0,behavior:"smooth"})}else{S.al.tipo=v;S.al.niv="";S.alN=60;ir("alertas")}}\n  else if(a==="alMais"){S.alN=(S.alN||60)+60;renderView()}\n  else if(a==="maisRk"){S.rkN=(S.rkN||15)+30;renderView()}\n  else if(a==="dados")modalDados();')
handlers = sub(handlers, 'try{localStorage.setItem("rp-tema",nx)}catch(e){}});', 'try{localStorage.setItem("rp-tema",nx)}catch(e){}renderView()});\nmatchMedia("(prefers-color-scheme: light)").addEventListener("change",()=>renderView());')
handlers = sub(handlers, '  else if(a==="niv"){S.al.niv=v;ir("alertas")}', '  else if(a==="niv"){S.al.niv=v;S.alN=60;ir("alertas")}')

# ---------------- dossiê (v2) ----------------
logo = base64.b64encode(open(B + r"\radar_v2\assets\rt-intelligence.png", "rb").read()).decode()
dos_a = D(3, 60)
dos_a = sub(dos_a, '  return B}\nfunction montarDossie', """  const cg=p.carga;if(cg&&p.ad.sem&&p.ad.sem.length&&(cg.media>=44||(p.pd&&cg.queda*100>=5))){const sm=p.ad.sem,pd=p.pd,alta=cg.media>=44&&cg.queda*100>=5&&sm.length>=2;
    B.carga={key:"carga",tit:"Carga de trabalho: visitas contratadas e horas (PDOH)",sev:alta?2:1,
      txt:"Em "+plural(sm.length,"semana fechada","semanas fechadas")+", o colaborador teve em média "+num(Math.round(cg.media))+" visitas contratadas por semana, em até "+plural(cg.lojas,"loja","lojas")+". A aderência foi de "+pc(sm[0].pct)+" na primeira semana e de "+pc(sm[sm.length-1].pct)+" na última."+(pd?" No PDOH ("+pd.dias+" dias), "+pc(pd.prod/pd.tot)+" do tempo foi produtivo, "+pc(pd.desl/pd.tot)+" de deslocamento, "+pc(pd.ocio/pd.tot)+" de ócio e "+pc(pd.hnr/pd.tot)+" de horas não registradas.":"")+" O conjunto indica carga elevada de trabalho e deve ser avaliado pela supervisão, não constituindo, por si só, falha do colaborador.",
      tab:{h:["Semana","Lojas","Contratadas","Realizadas","Aderência"],r:sm.map(w=>["S"+isoWeek(w.d),w.lojas,w.ct,w.rz,pc(w.pct)])},
      bars:sm.map(w=>({l:"S"+isoWeek(w.d),v:w.pct||0,t:pc(w.pct,0)})),graf:"Aderência por semana (realizado sobre contratado)."}}
  return B}
function montarDossie""")
dos_a = sub(dos_a, 'rota:"Fuga de rota"},bl=[]', 'rota:"Fuga de rota",carga:"Carga de trabalho"},bl=[]')
dos_b = 'const LOGO={url:"data:image/png;base64,' + logo + '",w:760,h:182};\nasync function logoData(){return LOGO}\n'
dos_c = D(78, 147)
# v3.11: PDF com fotos com indício e barras alinhadas
dos_c = sub(dos_c, """  const graf=(it,leg)=>{if(!it||!it.length)return;const bh=5.2,lw=26,mx=Math.max(...it.map(i=>i.v),0.0001);need(it.length*bh+10);doc.setFontSize(8);
    it.forEach(b=>{doc.setTextColor(20);doc.text(lat1(b.l),M,y+3.6);doc.setFillColor(228,232,238);doc.rect(M+lw,y,TW-lw-22,3.8,"F");doc.setFillColor(244,86,42);doc.rect(M+lw,y,(TW-lw-22)*Math.min(1,b.v/mx),3.8,"F");doc.text(lat1(String(b.t)),W-M,y+3.6,{align:"right"});y+=bh});
    doc.setTextColor(90);doc.setFontSize(8);doc.text(lat1(leg||""),M,y+2.5);y+=11};""", """  const graf=(it,leg)=>{if(!it||!it.length)return;const bh=6.4,lw=58,vw=16,bw=TW-lw-vw-4,mx=Math.max(...it.map(i=>i.v),0.0001);need(it.length*bh+14);
    doc.setFont("helvetica","bold");doc.setFontSize(8.5);doc.setTextColor(16,38,59);doc.text(lat1(leg||""),M,y+3);y+=6;doc.setDrawColor(210);doc.setLineWidth(.15);
    it.forEach((b,i)=>{if(i%2===0){doc.setFillColor(247,248,250);doc.rect(M,y-1.1,TW,bh,"F")}doc.setFont("helvetica","normal");doc.setFontSize(8);doc.setTextColor(40);
      const lb=doc.splitTextToSize(lat1(String(b.l)),lw-3)[0];doc.text(lb,M+1.5,y+3.1);doc.setFillColor(226,230,236);doc.roundedRect(M+lw,y+.6,bw,3.2,1.2,1.2,"F");
      const w=Math.max(.8,bw*Math.min(1,b.v/mx));doc.setFillColor(244,86,42);doc.roundedRect(M+lw,y+.6,w,3.2,1.2,1.2,"F");doc.setFont("helvetica","bold");doc.setTextColor(16,38,59);doc.text(lat1(String(b.t)),W-M-1.5,y+3.1,{align:"right"});y+=bh});
    doc.line(M,y,W-M,y);y+=7};
  const imgData=u=>fetch(u).then(r=>r.ok?r.blob():null).then(b=>b?new Promise(ok=>{const fr=new FileReader();fr.onload=()=>ok(fr.result);fr.readAsDataURL(b)}):null).catch(()=>null);
  const fotosPDF=async(fs,tt)=>{if(!fs.length)return;tit(tt);const cols=4,gap=4,cw=(TW-gap*(cols-1))/cols,ch=cw*4/3;
    for(let i=0;i<fs.length;i++){const f=fs[i],c=i%cols;if(c===0)need(ch+14);const x=M+c*(cw+gap),u=/^https?:/.test(f.url||"")?f.url:"fotos/"+String(f.url||"").split("/").pop(),im=await imgData(u);
      if(im){doc.addImage(im,"JPEG",x,y,cw,ch);doc.setDrawColor(200);doc.setLineWidth(.2);doc.rect(x,y,cw,ch)}else{doc.setFillColor(236,239,243);doc.rect(x,y,cw,ch,"F")}
      doc.setFont("helvetica","bold");doc.setFontSize(7);doc.setTextColor(16,38,59);doc.text(lat1(fD(f.d)+(f.h!=null?" "+fH(f.h):"")),x,y+ch+3.2);
      doc.setFont("helvetica","normal");doc.setTextColor(80);doc.text(doc.splitTextToSize(lat1(String(f.loja||"").replace(/^[A-Z]{2} \\/ /,"")+" - "+f.mot.join("; ")),cw).slice(0,2),x,y+ch+6.4);
      if(c===cols-1||i===fs.length-1)y+=ch+13}};""")
dos_c = sub(dos_c, """  tit(n+". Impacto na aderência e na operação");par(d.impacto);n++;""", """  if(p.fot.length){await fotosPDF(p.fot.slice(0,12),n+". Fotos com indício");n++}
  tit(n+". Impacto na aderência e na operação");par(d.impacto);n++;""")
dos = dos_a + "\n" + dos_b + "\n" + dos_c

script = "\n".join([
    '(function(){\n"use strict";',
    eng, tail,
    L(305, 314),
    L(658, 675),
    P("ui_new.js"),
    P("radar_svg.js"),
    P("radar_ping.js"),
    P("alertas_v2.js"),
    P("extras_v37.js"),
    P("v39.js"),
    P("indicadores_v40.js"),
    P("humor_analise.js"),
    P("setores.js"),
    radar,
    P("ui_raio.js"),
    L(781, 798),
    L(815, 820),
    U(107, 120),
    U(122, 141).replace("S.R=null", "S.PL=S.R=null"),
    dos,
    "",
])
# handlers contem rota()/ir() (linhas 144-145 dentro de 143-190); evita duplicar
script += "\n" + handlers + "\n\ndemo();rota();iniciarBase();\nwindow.addEventListener(\"load\",()=>{if(window.Chart)renderView()});\n})();"

script = sub(script, 'else if(v==="raio-x")gRaio()}', 'else if(v==="raio-x")gRaio();else if(v==="alertas")gAlertas()}')
# decisão do dono (23/11): Luto, Incomodado, Estressado e Não Valorizado contam como humor negativo
script = sub(script, 'neg:["Cansado","Sobrecarregado","Triste","Doente"]', 'neg:["Cansado","Sobrecarregado","Triste","Doente","Luto","Incomodado","Estressado","Não Valorizado"]')
script = sub(script, 'S.cfg=Object.assign(JSON.parse(JSON.stringify(CFG0)),x);', 'S.cfg=Object.assign(JSON.parse(JSON.stringify(CFG0)),x);S.cfg.neg=[...new Set([...(S.cfg.neg||[]),...CFG0.neg])];')
# v3.9: só a meta de aderência de 93% (sem Meta 1 / Meta 2)
for a, b in [
    ('st:x==null?"":x*100<cfg.m1?"abaixo da Meta 1":x*100<cfg.m2?"abaixo da Meta 2":"ok"', 'st:x==null?"":x*100<cfg.m2?"abaixo da meta de "+cfg.m2+"%":"ok"'),
    ('" abaixo das metas de aderência (Meta 1: "+c.m1+"%; Meta 2: "+c.m2+"%), com "', '" abaixo da meta de aderência de "+c.m2+"%, com "'),
    ('" abaixo da Meta 1 ou da Meta 2, com "', '" abaixo da meta de aderência de "+c.m2+"%, com "'),
    ('["Meta 1 de aderência (%)",c.m1],["Meta 2 de aderência (%)",c.m2],', '["Meta de aderência (%)",c.m2],'),
    ('"</b> abaixo da Meta 1 ("+c.m1+"%). Pior resultado: "', '"</b> abaixo da meta de "+c.m2+"%. Pior resultado: "'),
]:
    if a in script:
        script = script.replace(a, b)
script = script.replace('.baixo.some(l=>/Meta 1/.test(l.st))?2:1', '.baixo.some(l=>l.pct!=null&&l.pct*100<85)?2:1')
script = script.replace('n("m1","Meta 1 de aderência (%)",c.m1)+n("m2","Meta 2 de aderência (%)",c.m2)', 'n("m2","Meta de aderência (%)",c.m2)')
script = script.replace('p.nome+" · Meta 1: "+c.m1+"% · Meta 2: "+c.m2+"%"', 'p.nome+" · Meta de aderência: "+c.m2+"%"')
# calendário: x.n não existe mais; conta as ocorrências do dia
_oc = "((x.atraso?1:0)+(x.saida?1:0)+(x.auto?1:0))"
script = sub(script, "n=(x?x.n:0)+nf", "n=(x?" + _oc + ":0)+nf")
script = sub(script, "plural(x.n,\"ocorrência\"", "plural(" + _oc + ",\"ocorrência\"")

# ---------------- HTML ----------------
css = L(8, 250) + "\n" + P("extra.css") + "\n</style>"
body = L(252, 278)
body = sub(body, 'Radar <b>Promotor</b></div><div class="brand-sub">2PRT · Análise de promotor</div>', 'Radar <b>Promotor</b></div><div class="brand-sub">RT Intelligence · P&amp;P</div>')
body = sub(body, 'Uso interno · escritório<br>Feito por: Willams Viana', 'RT Intelligence<br>Planejamento e Produtividade')
head = L(1, 6) + '\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">'
cdn = L(280, 284)
html = head + "\n<style>\n" + css + "\n" + body + "\n\n" + cdn + "\n<script>\n" + script + "\n</script>\n\n</body></html>"
out = B + r"\radar_v3\index.html"
open(out, "w", encoding="utf-8", newline="\n").write(html)
open(B + r"\radar_v3\app.js", "w", encoding="utf-8", newline="\n").write(script)
print("ok", len(html))


