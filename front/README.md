# front/

Interface web responsiva do Radar Promotor (sessão Design e Front). **Sem build**: HTML + módulos JS + CSS,
servidos como estático pela API. Consome somente a API (`api/openapi.yaml`); não acessa o banco e não calcula regra.

## Estrutura

```
front/
  index.html            casca, CSP e Chart.js com SRI
  css/tokens.css        identidade RT / Monitor Regional, tema escuro e claro
  css/base.css          layout, componentes, responsivo (375 px a desktop)
  css/telas.css         estilos das abas
  js/main.js            ponto de entrada
  js/app.js             login, abas, filtros, roteamento por hash, tema
  js/api.js             cliente da API (cookie de sessão httpOnly; nenhum token no JS)
  js/estado.js          estado em memória (só o tema vai ao localStorage)
  js/perfis.js          o que mostrar por perfil (a regra de dados é do servidor)
  js/componentes.js     pílulas, KPI, sparkline, tipos de alerta
  js/graficos.js        wrapper do Chart.js com cores do tema
  js/telas/*.js         uma tela por aba (geral, alertas, raiox, dossie) e login
  vendor/               Chart.js 4.4.7 local (versão fixa) + hash SRI em chart-4.4.7.sri.txt
  mock/gerar.py         gera as fixtures fictícias a partir do contrato
  mock/servidor.py      serve o front e imita /api/v1 com as fixtures
```

## Rodar com o mock (dados fictícios)

```powershell
python front/mock/gerar.py        # só se quiser regenerar as fixtures
python front/mock/servidor.py     # http://127.0.0.1:8765
```

Usuários e senha de teste (fictícios, só valem no mock) ficam em `tests/fixtures/front/usuarios.json`:
`diretoria@`, `rh@`, `pp@`, `gerencia@`, `supervisor@`, `compliance@`, `admin@exemplo.teste`.

Testes: `pytest tests/front`.

## Regras que o front cumpre

- CPF, humor e token **nunca** em `localStorage`/`sessionStorage`; estado só em memória. Só a preferência de tema é salva.
- CPF aparece como a API entrega (mascarado em listas; completo só no Raio-X/dossiê para perfis autorizados).
- O que a API não devolve não aparece (ex.: sem `humor` no Raio-X, a seção some). Humor é sempre "contexto de acompanhamento".
- Textos de tela no padrão "indícios"; nada de termos acusatórios.
- Script de terceiros só com versão fixa e SRI; CSP restritiva no `index.html` (a API também deve enviar o cabeçalho).
- Datas ISO na API; `dd/mm/aaaa` só na tela. Fuso America/Sao_Paulo.

## Pendências de contrato (abrir PR na branch da sessão-mãe)

Anotadas em `docs/` da sessão-mãe; o front tolera a ausência de cada campo:

1. `Painel.semanas[].humor_negativo_pct` (agregado, só perfis com acesso e grupo mínimo de 5) para o gráfico de humor.
2. Formato do objeto `RaioX.humor` (hoje livre): o front lê `alerta_cuidado`, `negativos_pct`, `dias_registrados`, `sequencia_max` e, só para o RH, `opcoes`.
3. `Evento` sem severidade agregada por tipo em `/alertas` (`por_tipo` só traz contagem).
