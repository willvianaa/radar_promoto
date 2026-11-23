/* Tratamento de perfis. A regra de dados é do servidor: aqui só se decide o que MOSTRAR
   a partir do que a API devolveu ("o que a API não devolve não aparece") e quais atalhos oferecer. */
export const NOME_PERFIL = {
  diretoria: "Diretoria", rh: "RH", dp: "DP", compliance: "Compliance", pp: "P&P / Monitoramento",
  merch: "Merchandising e TD", gerencia_regional: "Gerência Regional", supervisor: "Supervisor", admin: "Administração",
};
/* Perfis que só veem dado agregado (sem Raio-X individual) — docs/05, §5.2. */
const SO_AGREGADO = new Set(["diretoria"]);
/* Perfis que geram rascunho de Dossiê de Conduta — docs/05, §5.3. Os demais só consultam e baixam. */
const GERAM_DOSSIE = new Set(["rh", "pp", "admin"]);

export const podeRaioX = (u) => !!u && !SO_AGREGADO.has(u.perfil);
export const podeGerarDossie = (u) => !!u && GERAM_DOSSIE.has(u.perfil);
export const abasDoPerfil = (u) => [
  ["geral", "Visão Geral"], ["alertas", "Alertas"],
  ...(podeRaioX(u) ? [["raio-x", "Raio-X"]] : []), ["dossie", "Dossiê"],
];
/* CPF completo só quando a API o entrega sem máscara. */
export const cpfCompleto = (cpf) => !!cpf && !cpf.includes("*");
