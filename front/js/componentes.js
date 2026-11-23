/* Peças visuais reutilizáveis. Todas devolvem HTML já escapado. */
import { esc, css } from "./util.js";

export const NIV = {
  C: ["Crítico", "var(--bad)", "p-bad"], A: ["Alto", "var(--rt)", "p-rt"],
  T: ["Atenção", "var(--warn)", "p-warn"], N: ["Estável", "var(--good)", "p-good"],
};
export const SEV = { 3: ["Alta", "var(--bad)", "p-bad"], 2: ["Média", "var(--warn)", "p-warn"], 1: ["Baixa", "var(--m2)", "p-m2"] };
export const TIPOS = {
  jor: "Atrasos e saídas", auto: "Check-out automático", pesq: "Pesquisas expiradas", exec: "Dias sem atividades",
  ader: "Impacto na aderência", falta: "Faltas", foto: "Fotos com indício", rota: "Fuga de rota", sobre: "Sobrecarga", humor: "Humor (contexto)",
};
const ic = (d) => '<svg viewBox="0 0 24 24" aria-hidden="true">' + d + "</svg>";
export const IC = {
  geral: ic('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12l6-4"/>'),
  alertas: ic('<path d="M6 9a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6z"/><path d="M10 19a2 2 0 0 0 4 0"/>'),
  "raio-x": ic('<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>'),
  dossie: ic('<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>'),
  doc: ic('<path d="M12 4v11m0 0l-4-4m4 4l4-4M5 20h14"/>'),
  sair: ic('<path d="M9 4H5v16h4M15 8l4 4-4 4M19 12H9"/>'),
};

export const nivPill = (n) => { const x = NIV[n || "N"] || NIV.N; return `<span class="pill ${x[2]}">${x[0]}</span>`; };
export const clsPill = (p) => nivPill(p.nivel) + (p.sobrecarga ? ' <span class="pill p-vio">Sobrecarga</span>' : "");
export const riscoCor = (r) => (r >= 55 ? "var(--bad)" : r >= 30 ? "var(--warn)" : "var(--good)");
export const riskBar = (r) => `<div class="risk"><i><b style="width:${r}%;background:${riscoCor(r)}"></b></i><span>${r}</span></div>`;
export const nb = (txt = "Sem dados para este recorte.") => `<div class="nobase">${esc(txt)}</div>`;

/** Mini-gráfico de linha em SVG para os KPIs (sem Chart.js, leve em 375 px). */
export function spark(serie, cor) {
  const v = serie.filter((x) => x != null);
  if (v.length < 2) return "";
  const mn = Math.min(...v), mx = Math.max(...v), w = 100, h = 30;
  const pts = serie.map((x, i) => (x == null ? null : [(i / (serie.length - 1)) * w, h - 3 - ((x - mn) / (mx - mn || 1)) * (h - 8)])).filter(Boolean);
  const d = pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" aria-hidden="true"><path d="${d} L${w} ${h} L0 ${h}Z" fill="${cor}" opacity=".12"/><path d="${d}" fill="none" stroke="${cor}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>`;
}

export function kpi({ rotulo, valor, sub, serie, cor = "var(--m2)", tom = "", acao }) {
  const tag = acao ? "button" : "div";
  return `<${tag} class="kpi${acao ? " click" : ""}"${acao ? ` data-acao="${acao}"` : ""} style="--acc:${cor}"><span class="kpi-l">${esc(rotulo)}</span><span class="kpi-v ${tom}">${valor}</span><span class="kpi-s">${esc(sub || "")}</span>${serie ? spark(serie, cor) : ""}</${tag}>`;
}

export function hero(eyebrow, titulo, texto, acoes = "") {
  return `<div class="hero"><div><div class="eyebrow">${esc(eyebrow)}</div><h2>${titulo}</h2>${texto ? `<p>${texto}</p>` : ""}</div>${acoes ? `<div class="row">${acoes}</div>` : ""}</div>`;
}
export { css };
