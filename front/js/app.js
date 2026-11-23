/* Casca da aplicação: login, abas, filtros, roteamento por hash e tema. Só consome a API. */
import { $, esc, fD, hojeISO, addD, debounce } from "./util.js";
import { api, aoExpirar, ErroApi } from "./api.js";
import { S, lerTema, gravarTema, aplicarTema, temaAtual } from "./estado.js";
import { abasDoPerfil, NOME_PERFIL, podeRaioX } from "./perfis.js";
import { IC } from "./componentes.js";
import { limparGraficos } from "./graficos.js";
import * as login from "./telas/login.js";

const TELAS = {
  geral: () => import("./telas/geral.js"),
  alertas: () => import("./telas/alertas.js"),
  "raio-x": () => import("./telas/raiox.js"),
  dossie: () => import("./telas/dossie.js"),
};
let acoes = {};
let geracao = 0;

export const ctx = {
  S, api, esc,
  ir(aba, id) { location.hash = "#/" + aba + (id ? "/" + encodeURIComponent(id) : ""); },
  renderizar: () => rotear(),
  periodoTxt: () => fD(S.f.ini) + " a " + fD(S.f.fim),
  filtrosApi: () => ({ ini: S.f.ini, fim: S.f.fim, uf: S.f.uf, supervisor: S.f.supervisor }),
};

/* ---------- tema ---------- */
function iniciarTema() {
  aplicarTema(lerTema());
  const b = $("tema");
  const rotulo = () => { b.textContent = temaAtual() === "light" ? "Tema escuro" : "Tema claro"; };
  rotulo();
  b.onclick = () => { const n = temaAtual() === "light" ? "dark" : "light"; aplicarTema(n); gravarTema(n); rotulo(); rotear(); };
  matchMedia("(prefers-color-scheme: light)").addEventListener("change", () => { rotulo(); rotear(); });
}

/* ---------- casca ---------- */
function mostrarLogin(msg) {
  $("app").hidden = true; $("login").hidden = false;
  login.montar($("login"), { aoEntrar: iniciarSessao, msg });
}
async function sair() {
  try { await api.logout(); } catch { /* sessão já encerrada */ }
  S.usuario = null; S.opcoes = null; limparGraficos(); $("view").innerHTML = "";
  location.hash = "";
  mostrarLogin();
}
function pintarNav() {
  const abas = abasDoPerfil(S.usuario);
  const lk = (a, i) => `<a href="#/${a[0]}" class="${S.aba === a[0] ? "active" : ""}" ${S.aba === a[0] ? 'aria-current="page"' : ""}>${IC[a[0]]}${esc(a[1])}</a>`;
  $("nav").innerHTML = abas.map((a) => lk(a)).join("");
  $("tabs").innerHTML = abas.map((a, i) => lk(a, i)).join("");
  $("crumb").textContent = (abas.find((a) => a[0] === S.aba) || abas[0])[1];
  $("regchip").textContent = ctx.periodoTxt();
  $("usuario").textContent = S.usuario ? S.usuario.nome + " · " + (NOME_PERFIL[S.usuario.perfil] || S.usuario.perfil) : "";
}
function pintarFiltros() {
  const o = S.opcoes || { ufs: [], supervisores: [] }, f = S.f;
  const pd = o.periodo_disponivel;
  const anos = [...new Set([f.fim.slice(0, 4), f.ini.slice(0, 4), ...(pd ? [pd.ini.slice(0, 4), pd.fim.slice(0, 4)] : [])])].filter(Boolean).sort();
  const sel = (id, rot, ops, val, todos) => `<label class="f" for="f-${id}"><span>${rot}</span><select id="f-${id}" data-f="${id}"><option value="">${todos}</option>${ops.map((x) => `<option value="${esc(x.v)}"${x.v === val ? " selected" : ""}>${esc(x.t)}</option>`).join("")}</select></label>`;
  $("filtros").innerHTML =
    sel("uf", "UF", o.ufs.map((u) => ({ v: u, t: u })), f.uf, "Todas") +
    sel("supervisor", "Supervisor", o.supervisores.map((s) => ({ v: s.nome, t: s.nome })), f.supervisor, "Todos") +
    `<label class="f" for="f-ini"><span>Data início</span><input type="date" id="f-ini" data-f="ini" value="${f.ini}"></label>` +
    `<label class="f" for="f-fim"><span>Data fim</span><input type="date" id="f-fim" data-f="fim" value="${f.fim}"></label>` +
    `<label class="f" for="f-ano"><span>Ano</span><select id="f-ano" data-f="ano">${anos.map((a) => `<option${a === f.fim.slice(0, 4) ? " selected" : ""}>${a}</option>`).join("")}</select></label>` +
    (podeRaioX(S.usuario) ? `<label class="f grow" for="f-q"><span>Promotor (nome ou CPF)</span><input id="f-q" data-f="q" list="plist" placeholder="Digite o nome ou o CPF" autocomplete="off" inputmode="search"></label><datalist id="plist"></datalist>` : "");
}

const sugerir = debounce(async (txt) => {
  const dl = $("plist"); if (!dl || txt.trim().length < 2) return;
  try {
    const r = await api.colaboradores(txt.trim(), 10);
    dl.innerHTML = r.itens.map((c) => `<option value="${esc(c.nome)}">${esc(c.cpf_mascarado)}</option>`).join("");
    S.sugestoes = r.itens;
  } catch { /* silencioso */ }
}, 250);

async function abrirPromotorPorBusca(txt) {
  const t = txt.trim(); if (!t) return;
  let ach = (S.sugestoes || []).find((c) => c.nome === t);
  if (!ach) { try { ach = (await api.colaboradores(t, 1)).itens[0]; } catch { ach = null; } }
  if (ach) ctx.ir("raio-x", ach.id);
  else $("banner").innerHTML = '<div class="banner">Nenhum promotor encontrado para essa busca no seu escopo.</div>';
}

function ligarEventos() {
  $("burger").onclick = () => { const a = $("side").classList.toggle("open"); $("burger").setAttribute("aria-expanded", a); };
  $("scrim").onclick = () => $("side").classList.remove("open");
  $("sair").onclick = (e) => { e.preventDefault(); sair(); };
  document.addEventListener("click", (e) => {
    const a = e.target.closest("[data-acao]");
    if (a && acoes[a.dataset.acao]) acoes[a.dataset.acao](a, e);
    if (e.target.closest("#side a")) $("side").classList.remove("open");
  });
  document.addEventListener("keydown", (e) => {
    const a = e.target.closest && e.target.closest("[data-acao][tabindex]");
    if (a && (e.key === "Enter" || e.key === " ") && acoes[a.dataset.acao]) { e.preventDefault(); acoes[a.dataset.acao](a, e); }
  });
  $("filtros").addEventListener("change", (e) => {
    const k = e.target.dataset.f; if (!k) return;
    if (k === "ano") {
      S.f.ini = e.target.value + "-01-01"; S.f.fim = e.target.value + "-12-31";
      const p = S.opcoes && S.opcoes.periodo_disponivel;
      if (p) { if (S.f.fim > p.fim) S.f.fim = p.fim; if (S.f.ini < p.ini) S.f.ini = p.ini; }
    } else if (k === "q") { abrirPromotorPorBusca(e.target.value); e.target.value = ""; return; }
    else S.f[k] = e.target.value;
    if (S.f.ini > S.f.fim) [S.f.ini, S.f.fim] = [S.f.fim, S.f.ini];
    pintarFiltros(); rotear();
  });
  $("filtros").addEventListener("input", (e) => { if (e.target.dataset.f === "q") sugerir(e.target.value); });
  window.addEventListener("hashchange", rotear);
  aoExpirar(() => { if (S.usuario) { S.usuario = null; mostrarLogin("Sua sessão expirou. Entre novamente."); } });
}

/* ---------- roteamento ---------- */
async function rotear() {
  if (!S.usuario) return;
  const [, aba0, idRaw] = location.hash.split("/");
  const permitidas = abasDoPerfil(S.usuario).map((a) => a[0]);
  const aba = permitidas.includes(aba0) ? aba0 : "geral";
  S.aba = aba;
  const minha = ++geracao;
  limparGraficos(); acoes = {};
  pintarNav();
  $("banner").innerHTML = "";
  $("view").innerHTML = '<div class="nobase" role="status">Carregando…</div>';
  try {
    const tela = await TELAS[aba]();
    const r = await tela.mostrar(ctx, idRaw ? decodeURIComponent(idRaw) : null, () => minha === geracao);
    if (minha !== geracao) return;
    acoes = (r && r.acoes) || {};
  } catch (e) {
    if (minha !== geracao) return;
    if (e instanceof ErroApi && e.status === 401) return;
    const msg = e instanceof ErroApi && e.status === 403 ? "Seu perfil não tem acesso a esta informação."
      : e instanceof ErroApi && e.status === 404 ? "Registro não encontrado no seu escopo."
      : "Não foi possível carregar os dados agora.";
    $("view").innerHTML = `<div class="banner err" role="alert">${esc(msg)} <button class="btn sm sec" data-acao="repetir">Tentar de novo</button></div>`;
    acoes = { repetir: () => rotear() };
  }
}

/* ---------- sessão ---------- */
async function iniciarSessao(usuario) {
  S.usuario = usuario || await api.eu();
  $("login").hidden = true; $("app").hidden = false;
  S.opcoes = await api.filtros();
  const p = S.opcoes.periodo_disponivel;
  if (p && !S.f.ini) {
    S.f.fim = p.fim;
    S.f.ini = addD(p.fim, -29) > p.ini ? addD(p.fim, -29) : p.ini;
  }
  if (!S.f.ini) { S.f.fim = hojeISO(); S.f.ini = addD(S.f.fim, -29); }
  pintarFiltros();
  if (!location.hash) location.hash = "#/geral";
  rotear();
}

export async function iniciar() {
  iniciarTema();
  ligarEventos();
  try { await iniciarSessao(); }
  catch (e) { mostrarLogin(e instanceof ErroApi && e.status === 401 ? "" : "Não foi possível falar com o servidor."); }
}
