/* Estado só em memória. CPF, humor e qualquer dado de colaborador NUNCA vão para localStorage/sessionStorage.
   O único item persistido é a preferência de tema (não sensível). */
export const S = {
  usuario: null,          // { nome, perfil, escopo } vindo de /auth/eu
  f: { ini: "", fim: "", uf: "", supervisor: "", q: "" },
  opcoes: null,           // /filtros
  aba: "geral",
  alt: { nivel: "", tipo: "" },   // filtros da aba Alertas
};

export function lerTema() { try { return localStorage.getItem("rp-tema"); } catch { return null; } }
export function gravarTema(t) { try { localStorage.setItem("rp-tema", t); } catch { /* ignora */ } }
export function aplicarTema(t) { if (t) document.documentElement.dataset.theme = t; else delete document.documentElement.dataset.theme; }
export function temaAtual() {
  const t = document.documentElement.dataset.theme;
  return t || (matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
}
