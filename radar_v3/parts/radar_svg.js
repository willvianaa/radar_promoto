/* Radar da operação v3.4: pings com nome ao passar o mouse, UFs destacadas, sem colunas de nomes */
function radarNomes(){return""}
function radarSvg(L,cor){const CX=300,CY=300,R0=245,W=600,H=600,uf=!!(S.f.uf||S.f.sup);
  const gs=uf?[["",L]]:[...group(L,p=>p.uf||"—")].sort((a,b)=>b[1].length-a[1].length),n=gs.length;
  const rad=x=>22+(100-Math.max(0,Math.min(100,x)))/100*(R0-30);
  const nm=s=>{const w=s.split(" ").filter(Boolean);return w.length>1?w[0]+" "+w[w.length-1]:w[0]||""};
  let g='<defs><radialGradient id="rg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="var(--bad)" stop-opacity=".34"/><stop offset=".45" stop-color="var(--warn)" stop-opacity=".14"/><stop offset="1" stop-color="var(--good)" stop-opacity=".05"/></radialGradient></defs>';
  g+='<circle cx="'+CX+'" cy="'+CY+'" r="'+(R0+10)+'" fill="none" stroke="var(--rt)" stroke-opacity=".18" stroke-width="6" class="halo"/>';
  g+='<circle cx="'+CX+'" cy="'+CY+'" r="'+R0+'" fill="url(#rg)" stroke="var(--rt)" stroke-opacity=".55" stroke-width="1.4"/>';
  for(let d=0;d<360;d+=5){const a=d*Math.PI/180,l=d%30?4:9,r1=R0+2,r2=R0+2+l;g+='<line x1="'+(CX+r1*Math.cos(a)).toFixed(1)+'" y1="'+(CY+r1*Math.sin(a)).toFixed(1)+'" x2="'+(CX+r2*Math.cos(a)).toFixed(1)+'" y2="'+(CY+r2*Math.sin(a)).toFixed(1)+'" stroke="var(--rt)" stroke-opacity="'+(d%30?.35:.8)+'" stroke-width="'+(d%30?1:1.6)+'"/>'}
  [[rad(30),"ATENÇÃO"],[rad(55),"ALTO"],[rad(80),"CRÍTICO"]].forEach(([r,t])=>g+='<circle cx="'+CX+'" cy="'+CY+'" r="'+r.toFixed(1)+'" fill="none" stroke="var(--rt-line)" stroke-opacity=".5" stroke-dasharray="2 5"/><text x="'+(CX+5)+'" y="'+(CY-r+11).toFixed(1)+'" class="rl">'+t+'</text>');
  g+='<circle cx="'+CX+'" cy="'+CY+'" r="30" fill="none" stroke="var(--bad)" stroke-width="1.5" class="pulse"/><circle cx="'+CX+'" cy="'+CY+'" r="30" fill="none" stroke="var(--bad)" stroke-width="1.5" class="pulse p2"/>';
  const pts=[],ufl=[];
  gs.forEach(([s,ps],gi)=>{const a0=-Math.PI/2+gi/n*2*Math.PI,a1=a0+2*Math.PI/n,am=(a0+a1)/2;
    if(n>1){g+='<line x1="'+CX+'" y1="'+CY+'" x2="'+(CX+R0*Math.cos(a0)).toFixed(1)+'" y2="'+(CY+R0*Math.sin(a0)).toFixed(1)+'" stroke="var(--border-2)" stroke-opacity=".6"/>';
      const ux=CX+(R0-22)*Math.cos(am),uy=CY+(R0-22)*Math.sin(am),crit=ps.filter(p=>p.cls==="C").length;
      ufl.push('<g class="ufb'+(crit?" uc":"")+'"><rect x="'+(ux-17).toFixed(1)+'" y="'+(uy-10).toFixed(1)+'" width="34" height="20" rx="10"/><text x="'+ux.toFixed(1)+'" y="'+(uy+4).toFixed(1)+'" text-anchor="middle">'+esc(s)+'</text></g>')}
    ps.slice().sort((a,b)=>a.k<b.k?-1:1).forEach((p,i)=>{const t=(i+.5)/ps.length,a=a0+(a1-a0)*(.12+.76*t),d=rad(p.risco),x=CX+d*Math.cos(a),y=CY+d*Math.sin(a),sz=p.niv?5+Math.min(4,p.score/3):2.6,hot=p.cls==="C"||p.sobre;
      const right=x<CX+150,tx=right?x+sz+6:x-sz-6,lb=nm(p.nome)+" · "+(p.niv?NIV[p.niv][0]:"Estável")+" · "+p.risco,tw=lb.length*6.3+14;
      pts.push([p.niv?1:0,'<g class="blip'+(hot?" hot":"")+'" data-a="ping" data-px="'+(x/W*100).toFixed(2)+'" data-py="'+(y/H*100).toFixed(2)+'" data-v="'+esc(p.k)+'" tabindex="0" role="button" aria-label="'+esc(p.nome)+', risco '+p.risco+'">'+(hot?'<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+sz+'" fill="none" stroke="'+cor[p.cls]+'" class="ping"/>':"")+'<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+(sz+6)+'" fill="transparent"/><circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="'+sz+'" fill="'+cor[p.cls]+'" stroke="var(--card)" stroke-width="1.5" class="dot"/>'+
        '<g class="hl"><rect x="'+(right?tx-4:tx-tw+4).toFixed(1)+'" y="'+(y-11).toFixed(1)+'" width="'+tw.toFixed(1)+'" height="22" rx="11" stroke="'+cor[p.cls]+'"/><text x="'+(right?tx+3:tx-3).toFixed(1)+'" y="'+(y+4).toFixed(1)+'" text-anchor="'+(right?"start":"end")+'">'+esc(lb)+'</text></g></g>'])})});
  pts.sort((a,b)=>a[0]-b[0]);g+=pts.map(x=>x[1]).join("")+ufl.join("");
  const crit=L.filter(p=>p.cls==="C").length;
  g+='<circle cx="'+CX+'" cy="'+CY+'" r="20" fill="var(--card)" stroke="var(--bad)" stroke-width="2"/><text x="'+CX+'" y="'+(CY+5)+'" text-anchor="middle" font-size="15" font-weight="800" fill="var(--bad)" font-family="Inter,Arial">'+crit+'</text>';
  return'<svg viewBox="0 0 '+W+' '+H+'" class="scope-svg" role="img" aria-label="Radar dos promotores: quanto mais perto do centro, maior o risco">'+g+'</svg>'}
