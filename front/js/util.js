/* Utilidades puras: escape, formatação pt-BR, datas ISO. Nada aqui guarda dado. */
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
export const $ = (id) => document.getElementById(id);
export const num = (n) => (n == null ? "—" : Number(n).toLocaleString("pt-BR"));
export const dec = (n, d = 1) => (n == null ? "—" : Number(n).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d }));
export const pc = (v, d = 1) => (v == null ? "—" : dec(v, d) + "%");
export const plural = (n, um, varios) => `${num(n)} ${n === 1 ? um : varios}`;
export const p2 = (n) => String(n).padStart(2, "0");
/** AAAA-MM-DD -> dd/mm/aaaa (só na tela) */
export const fD = (iso) => (iso ? iso.slice(8, 10) + "/" + iso.slice(5, 7) + "/" + iso.slice(0, 4) : "—");
export const fDc = (iso) => (iso ? iso.slice(8, 10) + "/" + iso.slice(5, 7) : "—");
const DIAS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
export const dow = (iso) => DIAS[new Date(iso + "T12:00:00").getDay()];
export const addD = (iso, n) => { const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };
export const hojeISO = () => new Date().toLocaleDateString("sv-SE", { timeZone: "America/Sao_Paulo" });
export function isoWeek(iso) {
  const d = new Date(iso + "T12:00:00Z"); const dia = (d.getUTCDay() + 6) % 7;
  d.setUTCDate(d.getUTCDate() - dia + 3);
  const p = new Date(Date.UTC(d.getUTCFullYear(), 0, 4));
  return 1 + Math.round(((d - p) / 864e5 - 3 + ((p.getUTCDay() + 6) % 7)) / 7);
}
export const semLbl = (iso) => "S" + isoWeek(iso);
export const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
export const soma = (a, f = (x) => x) => a.reduce((s, x) => s + (f(x) || 0), 0);
export function debounce(fn, ms = 300) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
