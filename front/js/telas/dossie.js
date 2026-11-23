/* Dossiê de Análise Operacional: folha A4 editável (rascunho), avisos de revisão, emissão e download.
   Padrão formal do CLAUDE.md §5: título, emissor RT Intelligence, CONFIDENCIAL em todas as páginas, numeração RP-AAAA-NNNNNN,
   "indícios", sem primeira pessoa; considerações finais começam com "Sendo assim,".
   O texto e a revisão vêm da API; aqui só se edita, mostra e emite. */
import { $, esc, fD, hojeISO, debounce, semLbl, pc, dec, num } from "../util.js";
import { hero, nb } from "../componentes.js";
import { podeGerarDossie, cpfCompleto } from "../perfis.js";
import { ErroApi } from "../api.js";

const CONC = { procede: "Procede", procede_parcialmente: "Procede parcialmente", nao_procede: "Não procede", sem_dados: "Sem dados suficientes" };
const LOGO = "assets/rt-intelligence.png";

/* ---------- tabelas de apoio de cada bloco, montadas com o Raio-X do mesmo período ---------- */
const tab = (cab, linhas) => linhas.length ? `<table class="tb"><thead><tr>${cab.map((c) => `<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>${linhas.map((l) => `<tr>${l.map((c) => `<td>${esc(c)}</td>`).join("")}</tr>`).join("")}</tbody></table>` : "";
function barras(itens) {
  if (!itens.length) return "";
  const mx = Math.max(1, ...itens.map((i) => i.v));
  return `<div class="gr" role="img" aria-label="Gráfico do bloco">${itens.map((i) => `<div class="gr-l"><span>${esc(i.l)}</span><i style="width:${Math.max(2, i.v / mx * 100)}%"></i><b>${esc(i.t)}</b></div>`).join("")}</div>`;
}
function apoio(chave, r) {
  if (!r) return "";
  switch (chave) {
    case "jor": {
      const l = r.jornada_dias.filter((d) => d.atraso_min > 0);
      return tab(["Data", "Primeiro check-in", "Atraso (min)"], l.map((d) => [fD(d.data), d.checkin, d.atraso_min]));
    }
    case "auto": {
      const l = r.jornada_dias.filter((d) => d.checkout_auto);
      return tab(["Data", "Check-in", "Check-out"], l.map((d) => [fD(d.data), d.checkin, d.checkout ? d.checkout + " (automático)" : "não registrado"]));
    }
    case "pesq":
      return tab(["Semana", "Programadas", "Respondidas", "Expiradas"], r.pesquisas_semana.map((w) => ["S" + w.semana, w.programadas, w.respondidas, w.expiradas]))
        + barras(r.pesquisas_semana.map((w) => ({ l: "S" + w.semana, v: w.expiradas, t: w.expiradas + " exp." })));
    case "ader":
      return tab(["Loja", "Contratadas", "Realizadas", "Aderência", "Situação"], r.aderencia_lojas.map((l) => [l.loja, l.contratadas, l.realizadas, pc(l.aderencia), l.situacao]))
        + barras(r.aderencia_lojas.map((l) => ({ l: l.loja.replace("Loja Exemplo ", ""), v: l.aderencia, t: pc(l.aderencia) })));
    case "sobre":
      return tab(["Semana", "Lojas", "Contratadas", "Realizadas", "Aderência"], r.carga.semanas.map((w) => [semLbl(w.semana_ini), w.lojas, w.contratadas, w.realizadas, pc(w.aderencia)]))
        + barras(r.carga.semanas.map((w) => ({ l: semLbl(w.semana_ini), v: w.aderencia, t: pc(w.aderencia, 0) })));
    case "foto":
      return tab(["Data", "Loja", "Motivos do indício"], r.fotos_indicio.map((x) => [fD(x.data), x.loja, x.motivos.join("; ")]));
    case "falta":
      return r.faltas ? tab(["Injustificadas", "Justificadas", "Atestados"], [[r.faltas.injustificadas, r.faltas.justificadas, r.faltas.atestados]]) : "";
    default: return "";
  }
}

/* ---------- campo editável: textarea na tela, texto fixo na impressão ---------- */
const campo = (k, v, ro, linhas = 3) => `<div class="ed"><textarea data-k="${k}" rows="1" data-min="${linhas}" ${ro ? "readonly" : ""} aria-label="${esc(k)}">${esc(v || "")}</textarea><div class="pr-txt">${esc(v || "")}</div></div>`;

function folha(d, r, ro, usuario) {
  const c = d.conteudo, col = d.colaborador;
  const cpf = r ? r.colaborador.cpf : col.cpf_mascarado;
  let n = 2;
  const sec = (t) => `<div class="sec">${++n}. ${t}</div>`;
  const blocos = (c.blocos || []).map((b, i) => `<div class="bloco"><div class="bl-t"><b>${i + 1}. ${esc(b.titulo)}</b>${d.relato ? `<select data-conc="${i}" ${ro ? "disabled" : ""} aria-label="Conclusão do ponto ${i + 1}"><option value="">Conclusão do ponto…</option>${Object.entries(CONC).map(([k, v]) => `<option value="${k}"${b.conclusao === k ? " selected" : ""}>${v}</option>`).join("")}</select>` : ""}</div>${campo("b" + i, b.texto, ro, 3)}${apoio(b.chave, r)}</div>`).join("");
  return `<article class="a4" id="folha" aria-label="Dossiê de Análise Operacional">
    <header class="a4-top"><img src="${LOGO}" alt="RT Intelligence" class="a4-logo"><div class="a4-meta">${d.numero ? `Documento nº <b>${esc(d.numero)}</b>` : "Nº gerado na emissão"}<br>Emissão: ${fD(d.emitido_em ? d.emitido_em.slice(0, 10) : hojeISO())}<br><b>CONFIDENCIAL</b></div></header>
    <div class="a4-tit"><h3>DOSSIÊ DE ANÁLISE OPERACIONAL</h3><div>${esc(col.nome)} · ${fD(d.periodo.ini)} a ${fD(d.periodo.fim)}</div></div>
    <div class="sec">1. Identificação</div>
    <div class="idt"><span><b>Nome:</b> ${esc(col.nome)}</span><span><b>CPF:</b> ${esc(cpf)}</span><span><b>Supervisor:</b> ${esc(col.supervisor)}</span><span><b>UF:</b> ${esc(col.uf)}</span>
      ${r ? `<span class="w2"><b>Jornada:</b> ${esc(r.colaborador.jornada || "não cadastrada")}</span><span class="w2"><b>Lojas:</b> ${esc((r.colaborador.lojas || []).join("; ") || "—")}</span>` : ""}
      <span><b>Período analisado:</b> ${fD(d.periodo.ini)} a ${fD(d.periodo.fim)}</span><span><b>Versão dos parâmetros:</b> ${esc(d.parametro_versao)}</span></div>
    <div class="sec">2. Introdução e objetivos</div>${campo("intro", c.intro, ro, 4)}${campo("objetivos", c.objetivos, ro, 3)}
    ${d.relato ? `${sec("Relato a apurar")}<blockquote class="relato">“${esc(d.relato)}”</blockquote>` : ""}
    ${(c.blocos || []).length ? `${sec("Relatos identificados")}${blocos}` : `${sec("Relatos identificados")}<p class="vazio">Nenhum indício encontrado no período.</p>`}
    ${sec("Impacto na aderência e na operação")}${campo("impacto", c.impacto, ro, 3)}
    ${c.contexto_acompanhamento != null ? `${sec("Contexto de acompanhamento")}${campo("contexto_acompanhamento", c.contexto_acompanhamento, ro, 3)}<p class="nota">Informação de acompanhamento e cuidado; não fundamenta conclusão nem medida.</p>` : ""}
    ${sec("Considerações finais")}${campo("consideracoes_finais", c.consideracoes_finais, ro, 4)}
    <footer class="a4-foot"><span>RT Intelligence</span><span>Este relatório apresenta indícios baseados em registros operacionais. Quem decide medidas são DP e Compliance.</span><span>CONFIDENCIAL</span></footer>
  </article>`;
}

const avisosHtml = (av) => av && av.length
  ? av.map((a) => `<div class="av err"><i>!</i><span>${esc(a)}</span></div>`).join("")
  : '<div class="av ok"><i>✓</i><span>Nenhum aviso de revisão. O texto segue o padrão formal.</span></div>';

/* ---------- lista de dossiês ---------- */
async function lista(ctx, vivo) {
  const l = await ctx.api.dossies();
  if (!vivo()) return {};
  $("view").innerHTML = hero("RT Intelligence", "Dossiês de Análise Operacional", "Para criar um rascunho, abra o Raio-X do promotor e escolha “Gerar dossiê”. O texto é montado com os dados do período e revisado antes da emissão.") +
    `<section class="card"><div class="hd"><h2>Dossiês no seu escopo</h2><small class="muted">${l.length}</small></div>${l.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Número</th><th>Colaborador</th><th>Período</th><th>Situação</th><th>Emissão</th></tr></thead><tbody>${l.map((d) => `<tr class="click" data-acao="abrir" data-v="${esc(d.numero)}" tabindex="0"><td><b>${esc(d.numero)}</b></td><td>${esc(d.colaborador)}</td><td>${fD(d.periodo.ini)} a ${fD(d.periodo.fim)}</td><td><span class="pill ${d.status === "emitido" ? "p-good" : "p-warn"}">${d.status === "emitido" ? "Emitido" : "Rascunho"}</span></td><td>${d.emitido_em ? fD(d.emitido_em.slice(0, 10)) : "—"}</td></tr>`).join("")}</tbody></table></div>` : nb("Nenhum dossiê ainda.")}</section>`;
  return { acoes: { abrir: (el) => ctx.ir("dossie", el.dataset.v) } };
}

/* ---------- novo rascunho (a partir do Raio-X) ---------- */
async function novo(ctx, colabId, vivo) {
  const f = ctx.filtrosApi();
  const r = await ctx.api.raioX(colabId, f);
  if (!vivo()) return {};
  $("view").innerHTML = hero("Dossiê de Análise Operacional", esc(r.colaborador.nome), `Período do filtro: ${ctx.periodoTxt()}. O rascunho é montado pelas regras a partir dos registros operacionais e pode ser editado na folha antes da emissão.`) +
    `<section class="card"><h2>Relato a apurar <small>opcional</small></h2><textarea class="inp" id="relato" rows="4" maxlength="2000" placeholder="Ex.: a supervisão relata atrasos recorrentes e pesquisas não respondidas."></textarea><small class="muted">Se informado, cada ponto do dossiê recebe uma conclusão (procede, procede parcialmente, não procede, sem dados).</small><div class="row"><button class="btn big" data-acao="criar">Montar rascunho</button><button class="btn sec" data-acao="cancelar">Cancelar</button></div><div id="msg"></div></section>`;
  return {
    acoes: {
      cancelar: () => ctx.ir("raio-x", colabId),
      criar: async (el) => {
        el.disabled = true;
        try {
          const d = await ctx.api.criarDossie({ colaborador_id: colabId, ini: f.ini, fim: f.fim, relato: $("relato").value.trim() || undefined });
          ctx.ir("dossie", d.id);
        } catch (e) { el.disabled = false; $("msg").innerHTML = `<div class="banner err">${esc(e instanceof ErroApi ? e.message : "Não foi possível montar o rascunho.")}</div>`; }
      },
    },
  };
}

export async function mostrar(ctx, id, vivo) {
  if (!id) return lista(ctx, vivo);
  if (id.startsWith("n~")) return novo(ctx, id.slice(2), vivo);
  let d = await ctx.api.dossie(id);
  let r = null;
  try { r = await ctx.api.raioX(d.colaborador.id, { ini: d.periodo.ini, fim: d.periodo.fim }); } catch { /* perfil sem Raio-X: a folha usa só o dossiê */ }
  if (!vivo()) return {};
  const pode = podeGerarDossie(ctx.S.usuario);
  const ro = () => d.status === "emitido" || !pode;

  const pintar = () => {
    $("view").innerHTML =
      hero("RT Intelligence", "Dossiê de Análise Operacional", d.status === "emitido" ? `Documento <b>${esc(d.numero)}</b> emitido e congelado.` : "O texto foi montado com os dados do período e pode ser editado direto na folha. A emissão numera, congela e gera o PDF e o Excel.") +
      `<div class="dos"><div class="a4-wrap" id="a4wrap">${folha(d, r, ro(), ctx.S.usuario)}</div>
      <div class="aside">
        <section class="card"><h2>${d.status === "emitido" ? "Arquivos emitidos" : "Emitir"}</h2>
          ${d.status === "emitido"
            ? `<div class="small muted">${esc(d.arquivos.pdf || "")}</div><a class="btn big" href="${ctx.api.urlArquivo(d.numero, "pdf")}" download>Baixar PDF</a><a class="btn sec" href="${ctx.api.urlArquivo(d.numero, "xlsx")}" download>Baixar Excel</a>`
            : pode ? `<div class="small muted">O número RP-AAAA-NNNNNN é atribuído na emissão.</div><button class="btn big" data-acao="emitir" ${d.avisos_revisao.length ? 'aria-disabled="true"' : ""}>Emitir dossiê</button><div id="st" class="small muted" role="status"></div>` : '<div class="small muted">Seu perfil consulta e baixa dossiês emitidos, mas não emite.</div>'}
          <button class="btn sec" data-acao="imprimir">Visualizar impressão (A4)</button><button class="btn sec" data-acao="lista">Todos os dossiês</button></section>
        ${d.relato ? `<section class="card"><h2>Relato a apurar</h2><div class="small muted">${esc(d.relato)}</div></section>` : ""}
        <section class="card"><h2>Revisão do texto</h2><div id="avisos" class="chk">${avisosHtml(d.avisos_revisao)}</div><small class="muted">A revisão confere termos não permitidos, primeira pessoa e o início das considerações finais.</small></section>
      </div></div>`;
    ajustar();
    ligarCampos();
  };

  const ajustar = () => {
    const w = $("a4wrap"), a = $("folha"); if (!w || !a) return;
    const z = Math.min(1, (w.clientWidth - 2) / 794);
    a.style.zoom = z < 1 ? z : "";
    w.querySelectorAll("textarea").forEach((t) => { t.style.height = "auto"; t.style.height = t.scrollHeight + 2 + "px"; });
  };
  const salvar = debounce(async () => {
    $("avisos") && ($("avisos").style.opacity = ".5");
    try {
      const nd = await ctx.api.salvarDossie(d.id, d.conteudo);
      d = nd; $("avisos").innerHTML = avisosHtml(nd.avisos_revisao); $("avisos").style.opacity = "";
      const be = document.querySelector('[data-acao="emitir"]'); if (be) be.setAttribute("aria-disabled", nd.avisos_revisao.length ? "true" : "false");
    } catch (e) { $("avisos").innerHTML = `<div class="av err"><i>!</i><span>${esc(e instanceof ErroApi ? e.message : "Não foi possível salvar o rascunho.")}</span></div>`; $("avisos").style.opacity = ""; }
  }, 700);
  const ligarCampos = () => {
    const w = $("a4wrap");
    w.addEventListener("input", (e) => {
      const t = e.target; if (!t.dataset.k) return;
      t.style.height = "auto"; t.style.height = t.scrollHeight + 2 + "px";
      t.nextElementSibling.textContent = t.value;
      const k = t.dataset.k;
      if (k[0] === "b" && /^b\d+$/.test(k)) d.conteudo.blocos[+k.slice(1)].texto = t.value; else d.conteudo[k] = t.value;
      salvar();
    });
    w.addEventListener("change", (e) => {
      if (e.target.dataset.conc == null) return;
      d.conteudo.blocos[+e.target.dataset.conc].conclusao = e.target.value || null; salvar();
    });
  };
  const aoRedimensionar = () => ajustar();
  window.addEventListener("resize", aoRedimensionar, { once: false });
  pintar();

  return {
    acoes: {
      lista: () => ctx.ir("dossie"),
      imprimir: () => window.print(),
      emitir: async (el) => {
        if (el.getAttribute("aria-disabled") === "true") { $("st").textContent = "Resolva os avisos de revisão antes de emitir."; return; }
        if (!confirm("Emitir o dossiê? O texto será congelado e o número, atribuído.")) return;
        el.disabled = true; $("st").textContent = "Emitindo…";
        try { d = await ctx.api.emitirDossie(d.id); pintar(); }
        catch (e) { el.disabled = false; $("st").innerHTML = e instanceof ErroApi ? esc(e.message) + (e.detalhes.length ? "<br>" + e.detalhes.map(esc).join("<br>") : "") : "Não foi possível emitir."; }
      },
    },
  };
}
