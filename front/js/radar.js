/* Radar da operação: fatias por UF (ou por supervisor quando há filtro), um ponto por colaborador,
   top 24 em risco com nome em duas colunas fora do círculo, linha-guia e nota de risco.
   Os dados vêm de /painel/radar; aqui só se desenha. */
import { esc } from "./util.js";
import { NIV } from "./componentes.js";

const COR = { C: "var(--bad)", A: "var(--rt)", T: "var(--warn)", N: "var(--good)" };
const nomeCurto = (s) => { const w = s.split(" ").filter(Boolean); return w.length > 1 ? w[0] + " " + w[w.length - 1] : w[0] || ""; };
const agrupa = (l, f) => { const m = new Map(); l.forEach((x) => { const k = f(x); (m.get(k) || m.set(k, []).get(k)).push(x); }); return m; };
export const topRisco = (L, n = 24) => L.filter((p) => p.nivel === "C" || p.nivel === "A").sort((a, b) => b.risco - a.risco).slice(0, n);

export function radarSvg(L) {
  const CX = 410, CY = 270, R0 = 235, W = 820, H = 540;
  const gs = [...agrupa(L, (p) => p.fatia || "—")].sort((a, b) => b[1].length - a[1].length), n = gs.length;
  const rad = (x) => 20 + (100 - Math.max(0, Math.min(100, x))) / 100 * (R0 - 26);
  const top = new Set(topRisco(L).map((p) => p.id));
  let g = '<defs><radialGradient id="rg" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="var(--bad)" stop-opacity=".32"/><stop offset=".45" stop-color="var(--warn)" stop-opacity=".14"/><stop offset="1" stop-color="var(--good)" stop-opacity=".06"/></radialGradient></defs>';
  g += `<circle cx="${CX}" cy="${CY}" r="${R0 + 10}" fill="none" stroke="var(--rt)" stroke-opacity=".18" stroke-width="6" class="halo"/>`;
  g += `<circle cx="${CX}" cy="${CY}" r="${R0}" fill="url(#rg)" stroke="var(--rt)" stroke-opacity=".55" stroke-width="1.4"/>`;
  for (let d = 0; d < 360; d += 5) {
    const a = d * Math.PI / 180, l = d % 30 ? 4 : 9, r1 = R0 + 2, r2 = R0 + 2 + l;
    g += `<line x1="${(CX + r1 * Math.cos(a)).toFixed(1)}" y1="${(CY + r1 * Math.sin(a)).toFixed(1)}" x2="${(CX + r2 * Math.cos(a)).toFixed(1)}" y2="${(CY + r2 * Math.sin(a)).toFixed(1)}" stroke="var(--rt)" stroke-opacity="${d % 30 ? .35 : .8}" stroke-width="${d % 30 ? 1 : 1.6}"/>`;
  }
  g += `<circle cx="${CX}" cy="${CY}" r="30" fill="none" stroke="var(--bad)" stroke-width="1.5" class="pulse"/><circle cx="${CX}" cy="${CY}" r="30" fill="none" stroke="var(--bad)" stroke-width="1.5" class="pulse p2"/>`;
  [[rad(30), "ATENÇÃO"], [rad(55), "ALTO"], [rad(80), "CRÍTICO"]].forEach(([r, t]) => {
    g += `<circle cx="${CX}" cy="${CY}" r="${r.toFixed(1)}" fill="none" stroke="var(--rt-line)" stroke-opacity=".5" stroke-dasharray="2 5"/><text x="${CX + 5}" y="${(CY - r + 11).toFixed(1)}" class="rl">${t}</text>`;
  });
  const lab = [], pts = [];
  gs.forEach(([s, ps], gi) => {
    const a0 = -Math.PI / 2 + gi / n * 2 * Math.PI, a1 = a0 + 2 * Math.PI / n, am = (a0 + a1) / 2;
    if (n > 1) {
      g += `<line x1="${CX}" y1="${CY}" x2="${(CX + R0 * Math.cos(a0)).toFixed(1)}" y2="${(CY + R0 * Math.sin(a0)).toFixed(1)}" stroke="var(--border-2)" stroke-opacity=".6"/>`;
      g += `<text x="${(CX + (R0 + 15) * Math.cos(am)).toFixed(1)}" y="${(CY + (R0 + 15) * Math.sin(am) + 4).toFixed(1)}" text-anchor="middle" class="ru">${esc(nomeCurto(s))}</text>`;
    }
    ps.slice().sort((a, b) => (a.id < b.id ? -1 : 1)).forEach((p, i) => {
      const t = (i + .5) / ps.length, a = a0 + (a1 - a0) * (.1 + .8 * t), d = rad(p.risco), x = CX + d * Math.cos(a), y = CY + d * Math.sin(a);
      const emNivel = p.nivel !== "N", sz = emNivel ? 5 + Math.min(4, p.score / 3) : 2.6, hot = p.nivel === "C" || p.sobrecarga, c = COR[p.nivel] || COR.N;
      pts.push([emNivel ? 1 : 0, `<g class="blip${hot ? " hot" : ""}" data-acao="abrir" data-v="${esc(p.id)}" tabindex="0" role="button" aria-label="${esc(p.nome)}, risco ${p.risco}"><title>${esc(p.nome)} · ${esc(p.uf)} · risco ${p.risco} · ${(NIV[p.nivel] || NIV.N)[0]}</title>${hot ? `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${sz}" fill="none" stroke="${c}" class="ping"/>` : ""}<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${sz}" fill="${c}" stroke="var(--card)" stroke-width="1.5"/></g>`]);
      if (top.has(p.id)) lab.push({ x, y, t: nomeCurto(p.nome), c, id: p.id, r: p.risco });
    });
  });
  pts.sort((a, b) => a[0] - b[0]); g += pts.map((x) => x[1]).join("");
  const col = (side, arr) => {
    arr.sort((a, b) => a.y - b.y);
    const gap = Math.min(17, (H - 30) / Math.max(1, arr.length)); const y0 = Math.max(18, CY - gap * (arr.length - 1) / 2);
    const lx = side > 0 ? CX + R0 + 42 : CX - R0 - 42;
    arr.forEach((l, i) => {
      const ly = y0 + i * gap;
      g += `<path d="M${l.x.toFixed(1)} ${l.y.toFixed(1)} L${side > 0 ? lx - 14 : lx + 14} ${ly.toFixed(1)} L${side > 0 ? lx - 4 : lx + 4} ${ly.toFixed(1)}" class="rgd" stroke="${l.c}"/>`;
      g += `<text x="${lx}" y="${(ly + 4).toFixed(1)}" text-anchor="${side > 0 ? "start" : "end"}" class="rn" data-acao="abrir" data-v="${esc(l.id)}" tabindex="0" role="button">${esc(l.t)} <tspan class="rr" fill="${l.c}">${l.r}</tspan></text>`;
    });
  };
  const half = Math.ceil(lab.length / 2), R = lab.filter((l) => l.x >= CX).sort((a, b) => a.x - b.x), Lf = lab.filter((l) => l.x < CX).sort((a, b) => b.x - a.x);
  while (R.length > half) Lf.push(R.shift());
  while (Lf.length > half) R.push(Lf.shift());
  col(1, R); col(-1, Lf);
  const crit = L.filter((p) => p.nivel === "C").length;
  g += `<circle cx="${CX}" cy="${CY}" r="18" fill="var(--card)" stroke="var(--bad)" stroke-width="2"/><text x="${CX}" y="${CY + 5}" text-anchor="middle" font-size="15" font-weight="800" fill="var(--bad)" font-family="Inter,Arial">${crit}</text>`;
  return `<svg viewBox="0 0 ${W} ${H}" class="scope-svg" role="img" aria-label="Radar dos promotores: quanto mais perto do centro, maior o risco; ao lado, os nomes com maior risco">${g}</svg>`;
}

/** No celular os nomes saem do SVG e viram chips tocáveis abaixo do radar. */
export function radarChips(L) {
  const t = topRisco(L);
  if (!t.length) return "";
  return `<div class="rp-chips" aria-label="Promotores com maior risco">${t.map((p) => `<button class="rpn" data-acao="abrir" data-v="${esc(p.id)}"><i style="background:${COR[p.nivel]}"></i>${esc(nomeCurto(p.nome))}<b>${p.risco}</b></button>`).join("")}</div>`;
}

export function radarPainel(L, ctx) {
  const crit = L.filter((p) => p.nivel === "C").length;
  const fatias = ctx.S.f.uf || ctx.S.f.supervisor ? "as equipes de cada supervisor" : "os estados";
  return `<section class="radarp"><div class="rp-head"><div><div class="eyebrow">Radar da operação</div>
    <h2>${crit ? `${crit} ${crit === 1 ? "promotor em nível crítico" : "promotores em nível crítico"}` : "Nenhum promotor em nível crítico"}</h2>
    <p>Cada ponto é um promotor; quanto mais perto do centro, maior o risco. As fatias são ${fatias}. Pontos pequenos são promotores estáveis. Toque num ponto ou nome para abrir o Raio-X. Os níveis indicam prioridade de conferência, não conclusão.</p></div>
    <div class="legend"><span><i style="background:var(--bad)"></i>Crítico</span><span><i style="background:var(--rt)"></i>Alto</span><span><i style="background:var(--warn)"></i>Atenção</span><span><i style="background:var(--good)"></i>Estável</span></div></div>
    <div class="scope"><div class="sweep" aria-hidden="true"></div>${L.length ? radarSvg(L) : '<div class="nobase">Nenhum promotor para este recorte.</div>'}</div>${radarChips(L)}</section>`;
}
