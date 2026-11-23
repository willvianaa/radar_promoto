/* Raio-X individual. Mostra só o que a API devolve para o perfil: sem `humor`, a seção some; CPF como veio (mascarado ou completo). */
import { $, esc, num, pc, dec, plural, fD, fDc, dow, addD, isoWeek, semLbl } from "../util.js";
import { hero, clsPill, riskBar, riscoCor, nb, SEV, TIPOS } from "../componentes.js";
import { grafico, cores } from "../graficos.js";
import { podeGerarDossie, cpfCompleto } from "../perfis.js";

const gauge = (x) => {
  const a = Math.PI * (1 - x / 100), ex = 64 + 54 * Math.cos(a), ey = 66 - 54 * Math.sin(a), c = riscoCor(x);
  return `<div class="gauge"><svg viewBox="0 0 128 76" role="img" aria-label="Índice de risco ${x}"><path d="M10 66 A54 54 0 0 1 118 66" fill="none" stroke="var(--grid)" stroke-width="11" stroke-linecap="round"/>${x > 0 ? `<path d="M10 66 A54 54 0 0 1 ${ex.toFixed(1)} ${ey.toFixed(1)}" fill="none" stroke="${c}" stroke-width="11" stroke-linecap="round"/>` : ""}<text x="64" y="62" text-anchor="middle" font-size="26" font-weight="800" fill="${c}" font-family="Inter,Arial">${x}</text></svg><b>Índice de risco</b></div>`;
};

function calendario(dias, ini, fim) {
  const mapa = new Map(dias.map((d) => [d.data, d]));
  const dd = []; for (let d = ini; d <= fim && dd.length < 70; d = addD(d, 1)) dd.push(d);
  if (!dd.length) return nb();
  const pad = (new Date(dd[0] + "T12:00:00").getDay() + 6) % 7;
  const cel = dd.map((d) => {
    const x = mapa.get(d), at = x && x.atraso_min > 0, au = x && x.checkout_auto;
    const cl = !x ? "" : at && au ? "o2" : at || au ? "o1" : "ok";
    const t = x ? `${fD(d)}: ${at ? "atraso de " + x.atraso_min + " min" : "sem atraso"}${au ? ", check-out automático" : ""}` : `${fD(d)}: sem registro`;
    return `<div class="d ${cl}" title="${esc(t)}" aria-label="${esc(t)}">${d.slice(8)}${au ? "<i></i>" : ""}</div>`;
  }).join("");
  return `<div class="cal">${["S", "T", "Q", "Q", "S", "S", "D"].map((h) => `<div class="h">${h}</div>`).join("")}${'<div class="d x"></div>'.repeat(pad)}${cel}</div>
    <div class="legend"><span><i style="background:var(--good)"></i>Sem ocorrência</span><span><i style="background:var(--warn)"></i>Uma ocorrência</span><span><i style="background:var(--bad)"></i>Atraso e check-out automático</span></div>`;
}

const hm = (s) => { const [h, m] = s.split(":").map(Number); return h * 60 + m; };
function linhaTempo(dias, jornada) {
  const d30 = dias.slice(-30); if (!d30.length) return nb("Sem jornada registrada no período.");
  const X0 = 6 * 60, X1 = 20 * 60, W = 900, L = 56, RH = 17, H = d30.length * RH + 30;
  const x = (m) => L + (Math.max(X0, Math.min(X1, m)) - X0) / (X1 - X0) * (W - L - 8);
  const [js, je] = jornada ? jornada.split("–").map(hm) : [480, 1050];
  let g = "";
  for (let h = 6; h <= 20; h += 2) g += `<line x1="${x(h * 60)}" x2="${x(h * 60)}" y1="14" y2="${H - 14}" stroke="var(--grid)"/><text x="${x(h * 60)}" y="${H - 2}" text-anchor="middle" font-size="10" fill="var(--ink-3)">${String(h).padStart(2, "0")}h</text>`;
  d30.forEach((d, i) => {
    const y = 18 + i * RH;
    g += `<text x="${L - 6}" y="${y + 9}" text-anchor="end" font-size="10" fill="var(--ink-2)">${fDc(d.data)}</text><rect x="${x(js)}" y="${y}" width="${x(je) - x(js)}" height="12" rx="3" fill="var(--grid)"/>`;
    d.visitas.forEach((v) => { if (v.fim) g += `<rect x="${x(hm(v.ini))}" y="${y + 2}" width="${Math.max(2, x(hm(v.fim)) - x(hm(v.ini)))}" height="8" rx="2" fill="${v.tipo_pdv === "NÃO OPERACIONAL" ? "var(--ink-3)" : "var(--m2)"}"><title>${esc(v.pdv)} ${v.ini}–${v.fim}</title></rect>`; });
    if (d.atraso_min > 0) g += `<rect x="${x(js)}" y="${y - 1}" width="${Math.max(3, x(hm(d.checkin)) - x(js))}" height="14" rx="2" fill="var(--warn)" opacity=".8"><title>Atraso de ${d.atraso_min} min</title></rect>`;
    if (d.checkout) g += `<circle cx="${x(hm(d.checkout))}" cy="${y + 6}" r="4.5" fill="${d.checkout_auto ? "var(--bad)" : "var(--good)"}"><title>${d.checkout_auto ? "Check-out automático" : "Check-out"} ${d.checkout}</title></circle>`;
  });
  return `<div class="tline"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Assinatura de jornada: check-in, visitas e check-out dos últimos dias">${g}</svg></div>`;
}

export async function mostrar(ctx, id, vivo) {
  if (!id) {
    const rk = await ctx.api.ranking({ ...ctx.filtrosApi(), limite: 30 });
    if (!vivo()) return {};
    $("view").innerHTML = hero("Raio-X do promotor", "Escolha um promotor", "Busque pelo nome ou CPF no filtro acima, ou abra um dos promotores de maior prioridade.") +
      `<section class="card"><div class="tbl-wrap"><table class="tbl"><thead><tr><th>Promotor</th><th>UF</th><th>Prioridade</th><th>Risco</th></tr></thead><tbody>${rk.itens.map((c) => `<tr class="click" data-acao="abrir" data-v="${esc(c.id)}" tabindex="0"><td><b>${esc(c.nome)}</b><div class="muted small">CPF ${esc(c.cpf_mascarado)}</div></td><td>${esc(c.uf)}</td><td>${clsPill(c)}</td><td>${riskBar(c.risco)}</td></tr>`).join("")}</tbody></table></div></section>`;
    return { acoes: { abrir: (el) => ctx.ir("raio-x", el.dataset.v) } };
  }
  const f = ctx.filtrosApi();
  const r = await ctx.api.raioX(id, f);
  if (!vivo()) return {};
  const c = r.colaborador, ini = c.nome.split(" ").filter(Boolean), av = ((ini[0] || "?")[0] + ((ini[ini.length - 1] || "")[0] || "")).toUpperCase();
  const dim = r.dimensoes, tem = (k) => dim[k] != null;
  const carga = r.carga || {}, pd = carga.pdoh, sem = carga.semanas || [];
  const alta = (carga.media_contratadas || 0) >= 44 && sem.length >= 2 && sem[0].aderencia - sem[sem.length - 1].aderencia >= 5;
  const fa = r.faltas, hu = r.humor;

  const secHumor = hu ? `<section class="card"><div class="hd"><h2>Contexto de acompanhamento</h2><span class="pill p-vio">Só para perfis autorizados</span></div>
      <div class="cross">${hu.alerta_cuidado ? "Há sinal de cuidado no acompanhamento do período. " : "Sem sinal de cuidado no período. "}${hu.negativos_pct != null ? `Registros negativos em ${pc(hu.negativos_pct, 0)} dos ${num(hu.dias_registrados)} dias com resposta.` : ""}</div>
      ${hu.opcoes ? `<div class="kv">${Object.entries(hu.opcoes).filter(([, v]) => v > 0).map(([k, v]) => `<span>${esc(k)} <b>${v}</b></span>`).join("")}</div>` : ""}
      <small class="muted">O humor é contexto de acompanhamento para ler os demais indicadores. Não é motivo de medida e não fundamenta conclusão do dossiê.</small></section>` : "";

  $("view").innerHTML =
    `<section class="card prof-card"><div class="prof"><div class="av">${esc(av)}</div><div><div class="eyebrow">Raio-X do promotor</div><h2>${esc(c.nome)}</h2>
      <div class="row" style="margin-top:6px">${clsPill(c)}<span class="small muted">${ctx.periodoTxt()}</span></div>
      <div class="kv" style="margin-top:8px"><span>CPF <b>${esc(c.cpf)}</b>${cpfCompleto(c.cpf) ? "" : ' <small class="muted">(mascarado para o seu perfil)</small>'}</span><span>Supervisor <b>${esc(c.supervisor)}</b></span><span>UF <b>${esc(c.uf)}</b></span><span>Jornada <b>${esc(c.jornada || "não cadastrada")}</b></span></div>
      <div class="kv" style="margin-top:4px"><span>Lojas atendidas <b>${(c.lojas || []).length}</b></span><span>Dias com jornada <b>${r.jornada_dias.length}</b></span>${fa ? `<span>Faltas injustificadas <b>${fa.injustificadas}</b></span><span>Justificadas <b>${fa.justificadas}</b></span><span>Atestados <b>${fa.atestados}</b></span>` : ""}</div></div>${gauge(c.risco)}</div>
      <div class="row"><button class="btn sec" data-acao="voltar">← Lista</button><span style="flex:1"></span>${podeGerarDossie(ctx.S.usuario) ? '<button class="btn big" data-acao="dossie">Gerar dossiê</button>' : ""}</div></section>` +
    `<div class="g-rx"><section class="card"><div class="hd"><h2>Perfil em ${Object.keys(dim).length} dimensões</h2><span class="legend"><span><i style="background:var(--rt)"></i>Promotor</span><span><i style="background:var(--m2)"></i>Média do filtro</span></span></div><div class="cv" style="height:310px"><canvas id="g-radar" role="img" aria-label="Perfil do promotor em dimensões de 0 a 100"></canvas></div><small class="muted">Cada dimensão vai de 0 (crítico) a 100 (ideal).</small></section>
    <section class="card"><div class="hd"><h2>Alertas do promotor</h2><small class="muted">${plural(r.alertas.length, "alerta", "alertas")}</small></div>${r.alertas.length ? `<div class="pts">${r.alertas.map((a) => `<div class="pt"><span class="pill ${SEV[a.severidade][2]}">${SEV[a.severidade][0]}</span><span><b>${esc(a.titulo)}</b><br><span class="muted">${esc(a.detalhe)}</span></span></div>`).join("")}</div><small class="muted">Indícios calculados por regras; exigem conferência.</small>` : nb("Nenhum alerta neste período.")}</section></div>` +
    secHumor +
    `<div class="g-rx"><section class="card"><div class="hd"><h2>Calendário de ocorrências</h2><small class="muted">${ctx.periodoTxt()}</small></div>${calendario(r.jornada_dias, f.ini, f.fim)}</section>
    <section class="card"><div class="hd"><h2>Pesquisas por semana</h2></div>${r.pesquisas_semana.length ? '<div class="cv sm"><canvas id="g-rpes" role="img" aria-label="Pesquisas por semana"></canvas></div>' : nb()}<h2>Aderência por loja</h2>${r.aderencia_lojas.length ? `<div class="cv sm" style="height:${Math.max(120, r.aderencia_lojas.length * 44 + 30)}px"><canvas id="g-rad" role="img" aria-label="Aderência por loja"></canvas></div>` : nb()}</section></div>` +
    `<section class="card"><div class="hd"><h2>Carga de trabalho <small>visitas contratadas, aderência e horas</small></h2>${alta ? '<span class="pill p-rt">Indício de sobrecarga</span>' : ""}</div>
      <div class="g-rx"><div>${sem.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Semana</th><th class="num">Lojas</th><th class="num">Contratadas</th><th class="num">Realizadas</th><th class="num">Aderência</th></tr></thead><tbody>${sem.map((w) => `<tr><td>${semLbl(w.semana_ini)}</td><td class="num">${w.lojas}</td><td class="num">${w.contratadas}</td><td class="num">${w.realizadas}</td><td class="num"><b>${pc(w.aderencia)}</b></td></tr>`).join("")}</tbody></table></div><small class="muted">Média de ${Math.round(carga.media_contratadas)} visitas contratadas por semana.</small>` : nb("Sem aderência 2PRT para este colaborador.")}</div>
      <div>${pd ? `<div class="pdoh">${[["prod", "Produtivo", pd.produtivo_pct, "var(--good)"], ["desl", "Deslocamento", pd.deslocamento_pct, "var(--m2)"], ["ocio", "Ócio", pd.ocio_pct, "var(--ink-3)"], ["hnr", "Não registrado", pd.nao_registrado_pct, "var(--warn)"]].map((x) => `<i title="${x[1]} ${pc(x[2])}" style="width:${x[2]}%;background:${x[3]}"></i>`).join("")}</div><div class="legend">${[["Produtivo", pd.produtivo_pct, "good"], ["Deslocamento", pd.deslocamento_pct, "m2"], ["Ócio", pd.ocio_pct, "ink-3"], ["Não registrado", pd.nao_registrado_pct, "warn"]].map((x) => `<span><i style="background:var(--${x[2]})"></i>${x[0]} <b>${pc(x[1])}</b></span>`).join("")}</div><small class="muted">PDOH de ${fD(pd.periodo.ini)} a ${fD(pd.periodo.fim)} (${pd.dias} dias). Contexto de carga, não conclusão.</small>` : nb("Sem PDOH para este colaborador.")}</div></div></section>` +
    `<section class="card"><div class="hd"><h2>Assinatura de jornada <small>check-in e check-out de cada dia contra a jornada cadastrada</small></h2><span class="legend"><span><i style="background:var(--grid)"></i>Jornada</span><span><i style="background:var(--m2)"></i>Visita</span><span><i style="background:var(--ink-3)"></i>PDV não operacional</span><span><i style="background:var(--bad)"></i>Check-out automático</span><span><i style="background:var(--warn)"></i>Atraso</span></span></div>${linhaTempo(r.jornada_dias, c.jornada)}</section>` +
    (r.fotos_indicio.length ? `<section class="card"><div class="hd"><h2>Fotos com indício</h2><small class="muted">${plural(r.fotos_indicio.length, "foto", "fotos")} · link temporário</small></div><div class="fotos">${r.fotos_indicio.map((x) => `<figure class="foto"><img src="${esc(x.url_assinada)}" alt="Foto com indício de ${esc(x.loja)} em ${fD(x.data)}" loading="lazy" referrerpolicy="no-referrer"><figcaption><b>${fD(x.data)}</b> · ${esc(x.loja)}<br><span class="muted">${esc(x.motivos.join(" · "))}</span></figcaption></figure>`).join("")}</div></section>` : "");

  /* ---- gráficos ---- */
  const k = cores(), nomes = Object.keys(dim);
  grafico("g-radar", { type: "radar", data: { labels: nomes, datasets: [{ label: "Média do filtro", data: nomes.map((n) => r.media_filtro[n] ?? 0), borderColor: k.m2, backgroundColor: k.m2 + "22", pointRadius: 2 }, { label: "Promotor", data: nomes.map((n) => dim[n] ?? 0), borderColor: k.rt, backgroundColor: k.rt + "40", pointBackgroundColor: k.rt, pointRadius: 3 }] },
    options: { scales: { r: { min: 0, max: 100, ticks: { display: false, stepSize: 25 }, grid: { color: k.grid }, angleLines: { color: k.grid }, pointLabels: { color: k.ink2, font: { size: 11 } } } } } });
  grafico("g-rpes", { type: "bar", data: { labels: r.pesquisas_semana.map((w) => "S" + w.semana), datasets: [{ label: "Respondidas", data: r.pesquisas_semana.map((w) => w.respondidas), backgroundColor: k.good, stack: "s", borderRadius: 4 }, { label: "Expiradas", data: r.pesquisas_semana.map((w) => w.expiradas), backgroundColor: k.bad, stack: "s", borderRadius: 4 }] }, options: { scales: { x: { stacked: true }, y: { stacked: true } } } });
  grafico("g-rad", { type: "bar", data: { labels: r.aderencia_lojas.map((l) => l.loja.replace("Loja Exemplo ", "")), datasets: [{ label: "Aderência", data: r.aderencia_lojas.map((l) => l.aderencia), backgroundColor: r.aderencia_lojas.map((l) => (l.aderencia < 85 ? k.bad : k.m2)), borderRadius: 5, maxBarThickness: 22 }] }, options: { indexAxis: "y", scales: { x: { min: 0, max: 100, ticks: { callback: (v) => v + "%" } } }, plugins: { tooltip: { callbacks: { label: (x) => dec(x.raw) + "%" } } } } });

  return { acoes: { voltar: () => ctx.ir("raio-x"), dossie: () => ctx.ir("dossie", "n~" + id) } };
}
