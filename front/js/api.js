/* Cliente da API (api/openapi.yaml). Sessão por cookie httpOnly: o front nunca vê nem guarda token. */
const BASE = "/api/v1";

export class ErroApi extends Error {
  constructor(status, corpo) {
    super((corpo && corpo.mensagem) || "Falha na requisição (" + status + ")");
    this.status = status; this.codigo = corpo && corpo.codigo; this.detalhes = (corpo && corpo.detalhes) || [];
  }
}

const eventos = new EventTarget();
export const aoExpirar = (fn) => eventos.addEventListener("expirou", fn);

function qs(params) {
  const p = new URLSearchParams();
  Object.entries(params || {}).forEach(([k, v]) => { if (v !== "" && v != null) p.set(k, v); });
  const s = p.toString();
  return s ? "?" + s : "";
}

async function req(metodo, caminho, { params, corpo, semRenovar } = {}) {
  const r = await fetch(BASE + caminho + qs(params), {
    method: metodo, credentials: "same-origin",
    headers: corpo ? { "Content-Type": "application/json", Accept: "application/json" } : { Accept: "application/json" },
    body: corpo ? JSON.stringify(corpo) : undefined,
  });
  if (r.status === 204) return null;
  let json = null;
  try { json = await r.json(); } catch { /* corpo vazio */ }
  if (r.status === 401 && !semRenovar) eventos.dispatchEvent(new Event("expirou"));
  if (!r.ok) throw new ErroApi(r.status, json);
  return json;
}
const get = (c, params) => req("GET", c, { params });

/** Período, UF, supervisor e busca viram query; vazios são omitidos. */
export const api = {
  login: (email, senha) => req("POST", "/auth/login", { corpo: { email, senha }, semRenovar: true }),
  logout: () => req("POST", "/auth/logout", { semRenovar: true }),
  eu: () => req("GET", "/auth/eu", { semRenovar: true }),
  filtros: () => get("/filtros"),
  painel: (f) => get("/painel", f),
  radar: (f) => get("/painel/radar", f),
  ranking: (f) => get("/painel/ranking", f),
  alertas: (f) => get("/alertas", f),
  colaboradores: (q, limite = 20) => get("/colaboradores", { q, limite }),
  raioX: (id, f) => get("/colaboradores/" + encodeURIComponent(id) + "/raio-x", { ini: f.ini, fim: f.fim }),
  criarDossie: (corpo) => req("POST", "/dossies", { corpo }),
  dossies: () => get("/dossies"),
  dossie: (id) => get("/dossies/" + encodeURIComponent(id)),
  salvarDossie: (id, conteudo) => req("PATCH", "/dossies/" + encodeURIComponent(id), { corpo: conteudo }),
  emitirDossie: (id) => req("POST", "/dossies/" + encodeURIComponent(id) + "/emitir"),
  urlArquivo: (numero, formato) => BASE + "/dossies/" + encodeURIComponent(numero) + "/arquivo?formato=" + formato,
};
