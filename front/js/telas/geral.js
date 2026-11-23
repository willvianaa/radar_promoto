/* Visão Geral: hero, Radar da operação, prioridade, KPIs, gráficos e ranking. Tudo vem de /painel, /painel/radar e /painel/ranking. */
import { $, esc, num, pc, dec, plural, semLbl, soma } from "../util.js";
import { kpi, hero, clsPill, riskBar, nb, NIV } from "../componentes.js";
import { grafico, cores } from "../graficos.js";
import { radarPainel } from "../radar.js";

const TXT = { C: "vários indícios graves ao mesmo tempo", A: "indícios relevantes acumulados", T: "um ponto isolado, apenas acompanhar" };
const META1 = 85, META2 = 93;   // CLAUDE.md §4.3

export async function mostrar(ctx, _id, vivo) {
  const f = ctx.filtrosApi();
  const [p, radar, rk] = await Promise.all([ctx.api.painel({ ...f }), ctx.api.radar(f), ctx.api.ranking({ ...f, limite: 15 })]);
  if (!vivo()) return {};
  const N = p.contagem, K = p.kpis, W = p.semanas || [], total = N.C + N.A + N.T + N.N;
  const temHumor = K.humor_negativo_pct != null;
  const serie = (fn) => W.map(fn);
  const tomAder = K.aderencia < META1 ? "t-bad" : K.aderencia < META2 ? "t-warn" : "t-good";
  const kpis = [
    kpi({ rotulo: "Aderência", valor: pc(K.aderencia), sub: `Meta 1 ${META1}% · Meta 2 ${META2}%`, serie: serie((w) => (w.contratadas ? w.realizadas / w.contratadas * 100 : null)), cor: "var(--m2)", tom: tomAder }),
    kpi({ rotulo: "Pesquisas expiradas", valor: pc(K.pesquisas_expiradas_pct), sub: `${num(soma(W, (w) => w.expiradas))} de ${num(soma(W, (w) => w.programadas))} programadas`, serie: serie((w) => (w.programadas ? w.expiradas / w.programadas * 100 : null)), cor: "var(--warn)", tom: K.pesquisas_expiradas_pct > 12 ? "t-bad" : "" }),
    kpi({ rotulo: "Ocorrências de jornada", valor: num(K.atrasos + K.checkout_auto), sub: `${num(K.atrasos)} atrasos · ${num(K.checkout_auto)} check-outs automáticos`, serie: serie((w) => w.ocorrencias_jornada), cor: "var(--rt)" }),
    ...(temHumor ? [kpi({ rotulo: "Humor negativo", valor: pc(K.humor_negativo_pct, 0), sub: "agregado · contexto de acompanhamento", serie: serie((w) => w.humor_negativo_pct ?? null), cor: "var(--vio)" })] : []),
    kpi({ rotulo: "Promotores em alerta", valor: num(N.C + N.A), sub: `${N.C} críticos · ${N.A} altos · ${N.T} em atenção`, cor: "var(--bad)", tom: N.C ? "t-bad" : N.A ? "t-warn" : "", acao: "alertas" }),
  ];
  const cv = (id, tit, leg, alt, vazio) => `<section class="card"><div class="hd"><h2>${tit}</h2>${leg ? `<span class="legend">${leg}</span>` : ""}</div>${vazio ? nb(vazio) : `<div class="cv"><canvas id="${id}" role="img" aria-label="${alt}"></canvas></div>`}</section>`;
  const dot = (c, t) => `<span><i style="background:var(--${c})"></i>${t}</span>`;
  const leitura = (p.leitura_automatica || []).map((t) => `<div class="in"><span class="dot"></span><span>${esc(t)}</span></div>`).join("");

  $("view").innerHTML =
    hero("RT Intelligence" + (f.uf ? " · " + f.uf : "") + (f.supervisor ? " · " + f.supervisor : ""), ctx.periodoTxt(),
      `${plural(total, "promotor analisado", "promotores analisados")} no escopo do seu perfil. Os alertas são indícios calculados por regras e pedem conferência.`,
      `<button class="btn sec" data-acao="alertas">Ver alertas</button>`) +
    radarPainel(radar, ctx) +
    `<section class="prio">${["C", "A", "T"].map((n) => `<button class="pr pr-${n}" data-acao="nivel" data-v="${n}"><span class="v">${N[n]}</span><span class="l">${NIV[n][0]}</span><small>${TXT[n]}</small></button>`).join("")}</section>` +
    `<section class="kpis">${kpis.join("")}</section>` +
    (leitura ? `<section class="card"><div class="hd"><h2>Leitura automática <small>gerada a partir dos dados do filtro</small></h2></div><div class="ins">${leitura}</div></section>` : "") +
    `<div class="grid2">${cv("g-ad", "Aderência por semana", dot("m2", "Aderência") + dot("warn", "Meta 1") + dot("good", "Meta 2"), "Aderência por semana", W.length ? "" : "Sem semanas fechadas no período.")}` +
    `${cv("g-pes", "Pesquisas por semana", dot("good", "Respondidas") + dot("bad", "Expiradas") + dot("warn", "% expiradas"), "Pesquisas por semana", W.length ? "" : "Sem pesquisas no período.")}</div>` +
    `<div class="grid2">${temHumor && W.some((w) => w.humor_negativo_pct != null)
      ? cv("g-hum", 'Humor × ocorrências <small>contexto de carga de trabalho</small>', dot("vio", "% dias com humor negativo") + dot("rt", "Ocorrências de jornada"), "Humor agregado e ocorrências por semana")
      : cv("g-oc", "Ocorrências por semana", dot("rt", "Ocorrências de jornada"), "Ocorrências de jornada por semana", W.length ? "" : "Sem ocorrências.")}` +
    `${cv("g-dow", "Ocorrências por dia da semana", "", "Ocorrências por dia da semana", (p.dia_semana || []).some(Boolean) ? "" : "Sem ocorrências no período.")}</div>` +
    `<section class="card"><div class="hd"><h2>Risco por supervisor <small>promotores por nível de prioridade</small></h2><span class="legend">${dot("bad", "Crítico") + dot("rt", "Alto") + dot("warn", "Atenção")}</span></div>${(p.risco_por_supervisor || []).length ? `<div class="cv" style="height:${Math.max(160, p.risco_por_supervisor.length * 44 + 50)}px"><canvas id="g-sup" role="img" aria-label="Promotores por nível e supervisor"></canvas></div>` : nb()}</section>` +
    `<section class="card"><div class="hd"><h2>Maior prioridade <small>toque para abrir o Raio-X</small></h2><small class="muted">${num(rk.total)} promotores</small></div>
      <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Promotor</th><th>Supervisor</th><th>UF</th><th>Prioridade</th><th>Risco</th></tr></thead><tbody id="rk-corpo">${linhasRanking(rk.itens)}</tbody></table></div>
      <div id="rk-mais">${rk.proximo_cursor ? '<button class="btn sec" data-acao="maisRk">Mostrar mais</button>' : ""}</div></section>`;

  /* ---- gráficos ---- */
  const c = cores(), lb = W.map((w) => semLbl(w.semana_ini));
  const meta = (v, cor, rot) => ({ type: "line", label: rot, data: W.map(() => v), borderColor: cor, borderDash: [5, 4], borderWidth: 1.5, pointRadius: 0, fill: false });
  const ader = W.map((w) => (w.contratadas ? +(w.realizadas / w.contratadas * 100).toFixed(1) : null));
  grafico("g-ad", { type: "bar", data: { labels: lb, datasets: [meta(META1, c.warn, "Meta 1"), meta(META2, c.good, "Meta 2"), { label: "Aderência", data: ader, backgroundColor: ader.map((v) => (v != null && v < META1 ? c.bad : c.m2)), borderRadius: 6, maxBarThickness: 46 }] },
    options: { scales: { y: { min: Math.max(0, Math.min(70, ...ader.filter((v) => v != null).map((v) => Math.floor(v) - 5))), max: 100, ticks: { callback: (v) => v + "%" } } }, plugins: { tooltip: { callbacks: { label: (x) => x.dataset.label + ": " + dec(x.raw) + "%" } } } } });
  grafico("g-pes", { type: "bar", data: { labels: lb, datasets: [{ type: "line", label: "% expiradas", data: W.map((w) => (w.programadas ? +(w.expiradas / w.programadas * 100).toFixed(1) : null)), borderColor: c.warn, backgroundColor: c.warn, yAxisID: "y2", tension: .35, pointRadius: 3 }, { label: "Respondidas", data: W.map((w) => w.respondidas), backgroundColor: c.good, stack: "s", borderRadius: 4, maxBarThickness: 46 }, { label: "Expiradas", data: W.map((w) => w.expiradas), backgroundColor: c.bad, stack: "s", borderRadius: 4, maxBarThickness: 46 }] },
    options: { scales: { x: { stacked: true }, y: { stacked: true }, y2: { position: "right", min: 0, ticks: { callback: (v) => v + "%" }, grid: { display: false } } } } });
  grafico("g-hum", { type: "bar", data: { labels: lb, datasets: [{ type: "line", label: "% humor negativo", data: W.map((w) => w.humor_negativo_pct ?? null), borderColor: c.vio, backgroundColor: c.vio + "33", fill: true, yAxisID: "y2", tension: .35, pointRadius: 3 }, { label: "Ocorrências de jornada", data: W.map((w) => w.ocorrencias_jornada), backgroundColor: c.rt, borderRadius: 5, maxBarThickness: 40 }] },
    options: { scales: { y: { beginAtZero: true }, y2: { position: "right", min: 0, max: 100, ticks: { callback: (v) => v + "%" }, grid: { display: false } } } } });
  grafico("g-oc", { type: "bar", data: { labels: lb, datasets: [{ label: "Ocorrências", data: W.map((w) => w.ocorrencias_jornada), backgroundColor: c.rt, borderRadius: 6, maxBarThickness: 40 }] }, options: { scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } });
  const ord = [1, 2, 3, 4, 5, 6, 0], dw = p.dia_semana || [0, 0, 0, 0, 0, 0, 0], mx = Math.max(...dw);
  grafico("g-dow", { type: "bar", data: { labels: ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"], datasets: [{ label: "Ocorrências", data: ord.map((i) => dw[i]), backgroundColor: ord.map((i) => (dw[i] === mx && mx ? c.rt : c.m2)), borderRadius: 6, maxBarThickness: 44 }] }, options: { scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } });
  const rs = p.risco_por_supervisor || [];
  grafico("g-sup", { type: "bar", data: { labels: rs.map((s) => s.supervisor.replace("Supervisor ", "")), datasets: [["C", "Crítico", c.bad], ["A", "Alto", c.rt], ["T", "Atenção", c.warn]].map(([k, l, cor]) => ({ label: l, data: rs.map((s) => s[k]), backgroundColor: cor, stack: "s", borderRadius: 3, maxBarThickness: 26 })) },
    options: { indexAxis: "y", scales: { x: { stacked: true, ticks: { precision: 0 } }, y: { stacked: true } }, plugins: { legend: { display: false } } } });

  let cursor = rk.proximo_cursor;
  return {
    acoes: {
      abrir: (el) => ctx.ir("raio-x", el.dataset.v),
      alertas: () => ctx.ir("alertas"),
      nivel: (el) => { ctx.S.alt.nivel = el.dataset.v; ctx.ir("alertas"); },
      maisRk: async (el) => {
        el.disabled = true;
        const r = await ctx.api.ranking({ ...f, limite: 30, cursor });
        $("rk-corpo").insertAdjacentHTML("beforeend", linhasRanking(r.itens));
        cursor = r.proximo_cursor; if (!cursor) $("rk-mais").innerHTML = ""; else el.disabled = false;
      },
    },
  };
}

function linhasRanking(itens) {
  return itens.map((c) => `<tr class="click" data-acao="abrir" data-v="${esc(c.id)}" tabindex="0"><td><b>${esc(c.nome)}</b><div class="muted small">CPF ${esc(c.cpf_mascarado)}</div></td><td>${esc(c.supervisor)}</td><td>${esc(c.uf)}</td><td>${clsPill(c)}</td><td>${riskBar(c.risco)}</td></tr>`).join("");
}
