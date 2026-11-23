/* Alertas: prioridade, cards por tipo, alertas por dia e feed com filtros. Dados de /alertas. */
import { $, esc, num, plural, fD, fDc, dow } from "../util.js";
import { hero, nivPill, NIV, SEV, TIPOS, nb } from "../componentes.js";

export async function mostrar(ctx, _id, vivo) {
  const S = ctx.S, f = ctx.filtrosApi();
  const [todos, ver] = await Promise.all([ctx.api.alertas({ ...f, limite: 1 }), ctx.api.alertas({ ...f, nivel: S.alt.nivel, tipo: S.alt.tipo, limite: 60 })]);
  if (!vivo()) return {};
  const C = todos.contagem, tipos = Object.entries(todos.por_tipo).sort((a, b) => b[1] - a[1]);
  const totalEv = tipos.reduce((s, x) => s + x[1], 0), mx = Math.max(1, ...todos.por_dia.map((d) => d.n));
  const feed = (itens) => itens.map((a) => `<div class="al" data-acao="abrir" data-v="${esc(a.colaborador.id)}" tabindex="0" role="button">
      <span class="sv" style="background:${SEV[a.severidade][1]}"></span>
      <span class="dt"><b>${fDc(a.data)}</b>${dow(a.data)}</span>
      <span class="tx"><b>${esc(a.titulo)}</b><span>${esc(a.descricao)}</span><span class="who">${esc(a.colaborador.nome)} · ${esc(a.colaborador.supervisor)} · ${esc(a.colaborador.uf)} · ${esc(TIPOS[a.tipo] || a.tipo)}</span></span>
      <span class="pill ${SEV[a.severidade][2]}">${SEV[a.severidade][0]}</span></div>`).join("");

  $("view").innerHTML =
    hero("Central de alertas", `${plural(C.C + C.A + C.T, "promotor", "promotores")} com alerta`,
      `${plural(totalEv, "ocorrência", "ocorrências")} de ${ctx.periodoTxt()}. Os alertas são indícios calculados por regras e precisam de conferência antes de qualquer decisão.`) +
    `<div class="prio">${["C", "A", "T"].map((n) => `<button class="pr pr-${n}${S.alt.nivel === n ? " on" : ""}" data-acao="nivel" data-v="${S.alt.nivel === n ? "" : n}" aria-pressed="${S.alt.nivel === n}"><span class="v">${C[n]}</span><span class="l">${NIV[n][0]}</span><small>promotores</small></button>`).join("")}</div>` +
    (tipos.length ? `<div class="atype">${tipos.map(([t, n]) => `<button class="at${S.alt.tipo === t ? " on" : ""}" data-acao="tipo" data-v="${t}" aria-pressed="${S.alt.tipo === t}"><span class="l">${esc(TIPOS[t] || t)}</span><span class="v">${num(n)}</span><span class="bar"><i style="width:${n / totalEv * 100}%"></i></span></button>`).join("")}</div>` : "") +
    `<section class="card"><div class="hd"><h2>Alertas por dia</h2><small class="muted">${ctx.periodoTxt()}</small></div>${todos.por_dia.length ? `<div class="heat" role="img" aria-label="Alertas por dia">${todos.por_dia.map((d) => `<div title="${fD(d.data)}: ${d.n} alerta(s)" style="height:${Math.max(6, d.n / mx * 100)}%;background:${d.n / mx > .66 ? "var(--bad)" : d.n / mx > .33 ? "var(--rt)" : "var(--warn)"}"></div>`).join("")}</div>` : nb("Nenhum alerta no período.")}</section>` +
    `<div class="row" style="justify-content:space-between"><div class="chips"><button class="chip${!S.alt.nivel ? " on" : ""}" data-acao="nivel" data-v="">Todos</button>${["C", "A", "T"].map((n) => `<button class="chip${S.alt.nivel === n ? " on" : ""}" data-acao="nivel" data-v="${n}">${nivPill(n)}<b>${C[n]}</b></button>`).join("")}</div>${S.alt.tipo ? `<button class="btn sec sm" data-acao="tipo" data-v="">Limpar tipo: ${esc(TIPOS[S.alt.tipo] || S.alt.tipo)}</button>` : ""}</div>` +
    (ver.itens.length ? `<div class="feed" id="feed">${feed(ver.itens)}</div><div id="al-mais">${ver.proximo_cursor ? '<button class="btn sec" data-acao="mais">Mostrar mais</button>' : ""}</div>` : '<div class="nobase">Nenhum alerta para os filtros escolhidos.</div>');

  let cursor = ver.proximo_cursor;
  return {
    acoes: {
      abrir: (el) => ctx.ir("raio-x", el.dataset.v),
      nivel: (el) => { S.alt.nivel = el.dataset.v; ctx.renderizar(); },
      tipo: (el) => { S.alt.tipo = S.alt.tipo === el.dataset.v ? "" : el.dataset.v; ctx.renderizar(); },
      mais: async (el) => {
        el.disabled = true;
        const r = await ctx.api.alertas({ ...f, nivel: S.alt.nivel, tipo: S.alt.tipo, limite: 60, cursor });
        $("feed").insertAdjacentHTML("beforeend", feed(r.itens));
        cursor = r.proximo_cursor; if (!cursor) $("al-mais").innerHTML = ""; else el.disabled = false;
      },
    },
  };
}
