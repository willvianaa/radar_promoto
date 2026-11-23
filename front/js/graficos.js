/* Chart.js (vendor/, versão fixa + SRI). Cores sempre lidas dos tokens do tema atual. */
import { css } from "./util.js";

let vivos = [];
export function limparGraficos() { vivos.forEach((c) => c.destroy()); vivos = []; }

export function cores() {
  return { rt: css("--rt"), m2: css("--m2"), bad: css("--bad"), good: css("--good"), warn: css("--warn"), vio: css("--vio"),
    ink2: css("--ink-2"), ink3: css("--ink-3"), grid: css("--grid"), card: css("--card") };
}

/** Cria o gráfico em #id aplicando o visual padrão; se não houver Chart.js, deixa o texto alternativo. */
export function grafico(id, cfg) {
  const el = document.getElementById(id);
  if (!el || !window.Chart) return null;
  const c = cores();
  Chart.defaults.font.family = css("--font");
  Chart.defaults.color = c.ink2;
  Chart.defaults.borderColor = c.grid;
  const base = {
    responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
    interaction: { mode: "index", intersect: false },
    plugins: { legend: { display: false }, tooltip: { padding: 10, cornerRadius: 8, boxPadding: 4 } },
    scales: {},
  };
  const mescla = (a, b) => { for (const k in b) { a[k] = b[k] && typeof b[k] === "object" && !Array.isArray(b[k]) ? mescla(a[k] || {}, b[k]) : b[k]; } return a; };
  cfg.options = mescla(base, cfg.options || {});
  if (cfg.type !== "radar" && cfg.type !== "doughnut") {
    for (const eixo of ["x", "y"]) {
      cfg.options.scales[eixo] = mescla({ grid: { color: eixo === "y" ? c.grid : "transparent" }, ticks: { color: c.ink2 } }, cfg.options.scales[eixo] || {});
    }
  }
  const g = new Chart(el, cfg);
  vivos.push(g);
  return g;
}
