# Diagnóstico inicial de LGPD e Segurança

Sessão LGPD e Segurança · 22/11/2026 · base: `main` em `1b76705`.
Nenhum valor encontrado é reproduzido aqui: só arquivo, commit e tipo do achado.

## Resumo dos riscos

| # | Risco | Nível | Ação recomendada | Responsável |
|---|-------|-------|------------------|-------------|
| R1 | Repositório **público** com protótipos, regras e contratos de um sistema que trata dados pessoais e de saúde | **Alto** | Tornar o repositório privado antes da onda 2 (qualquer ingestão real). Ativar *secret scanning* e *push protection* do GitHub | Dono (configuração da conta, as sessões não alteram) |
| R2 | Protótipo `radar_v2/` e `sistema/` gravam as bases carregadas (CPF, nome, humor, operação) no **banco do artefato no claude.ai** (`window.claude.use("db")`), compartilhado com quem abre o artefato, hospedado por terceiro e fora do Brasil | **Alto** | Apagar as bases reais do artefato (botão de limpar mês) ou o artefato; não carregar dado real em protótipo; registrar como operação de tratamento até a remoção; avaliar transferência internacional (art. 33) com o DPO | Dono + DPO |
| R3 | Base legal do humor e da opção "Doente" (dado de saúde, art. 11) indefinida (Q-10) | **Alto** | Não entrar em uso real com "Doente" visível até a decisão; RIPD em rascunho para o DPO | DPO, RH, Jurídico |
| R4 | Dependências com vulnerabilidades conhecidas: `starlette 0.41.3` (via `fastapi==0.115.6`, 7 avisos PYSEC-2026) e `pytest 8.3.4` (1 aviso) | **Médio** | Subir para `fastapi==0.165.0` (traz `starlette 1.10.0`) e `pytest==9.0.3`. Testado localmente: 78 testes passam e `pip-audit` fica limpo | Infra (dona dos `requirements`); PR de correção da sessão LGPD |
| R5 | Contrato `api/openapi.yaml`: parâmetro `q` de `/colaboradores` aceita "parte do CPF" **na query string** (vai para logs de proxy, histórico do navegador e auditoria em texto) | **Médio** | Trocar a busca por CPF para `POST` com corpo, ou exigir no servidor que `q` numérico nunca seja registrado em log; teste em `tests/seguranca/` | Sessão-mãe (contrato) + API |
| R6 | Protótipos carregam bibliotecas de CDN sem SRI; `xlsx 0.18.5` (SheetJS) tem vulnerabilidades públicas (poluição de protótipo e ReDoS ao ler planilhas) e `chart.js` sem versão fixa | **Médio** | No front definitivo: dependências locais e fixas, `integrity` nos scripts, SheetJS ≥ 0.20.2 ou leitura de planilha só no servidor | Front |
| R7 | Ausência de controles automáticos no CI (segredos, CPF, dependências, SAST) | **Médio** | Workflow `seguranca.yml` (próximo PR): scanner de CPF/segredos, gitleaks, `pip-audit`, `bandit` | LGPD + Infra |
| R8 | Três padrões de CPF fora da convenção de fixtures (`000.000.00x-xx`): `radar_v2/engine.js` linha 175 (commit `ed2afea`) e `sistema/index.html` linha 470 (commit `db4b54c`), ambos com dígitos verificadores **inválidos** e nomes fictícios; `tests/test_transformacao.py` linha 29 (commit `4af252f`), 11 dígitos com verificador válido em teste de normalização | **Baixo** | **Corrigido na árvore** (PR #15). Os valores antigos **continuam no histórico do git**, visível a qualquer pessoa enquanto o repositório for público. Sem indício de dado real; não proponho reescrever o histórico de ninguém. O risco residual é coberto por R1 (tornar o repositório privado). O CI varre o HEAD e só o que cada PR acrescenta (PR #26), para não reprovar PRs limpos por conteúdo antigo | LGPD (feito); dono (R1) |
| R9 | Pasta local `dados/` (dados reais) | **Baixo** | Confirmado: `dados/`, `uploads/`, `exports/`, `*.xlsx`, `*.csv`, `*.pdf`, imagens, `.env*` estão no `.gitignore` e no `.dockerignore`. A pasta não foi aberta | — |

## Varredura de segredos e CPF

Script: `.github/scripts/varrer_dados_pessoais.py` (modo árvore e `--historico`, 27 commits, todos os blobs).

- **Segredos:** nenhum achado (chaves privadas, tokens AWS/GitHub/Google/Slack/IA, JWT, URL com credencial, senha atribuída em código). `.env.example` só tem variáveis vazias; o CI usa valores fictícios.
- **CPF:** só os três achados de R8. Os demais CPFs são fictícios `000.000.00x-xx`.
- **Nomes:** os dados de demonstração usam nomes marcados como fictícios ("Exemplo", "Fictícia").

## Dependências e SAST

- `pip-audit -r requirements-dev.txt`: 8 avisos em 2 pacotes (R4).
- `bandit -r api regras ingestor ferramentas db scripts`: nenhum achado.

## Pontos positivos

- Compose publica Postgres e API só em `127.0.0.1`; imagens rodam como usuário não-root.
- Cookie de sessão previsto `httpOnly`, `Secure`, `SameSite=Strict`; docs da API desligados.
- Auditoria append-only e coluna `motivo` restrita a RH/DP já previstas em `db/modelo.md`.

## Situação em 22/11

- R4, R7 e R8: tratados nos PRs #15 e #26 (na `main`).
- Documentos LGPD em rascunho: `01` a `06` nesta pasta. **Base legal, prazos e visibilidade são propostas; quem decide são DPO, RH e Jurídico (Q-08, Q-09, Q-10).**
- Pendente: testes de segurança em `tests/seguranca/` (mascaramento, nada sensível em log/URL), e R1, R2, R3, R5 e R6 com os responsáveis indicados.

## Situação em 23/11 (retomada na conta da empresa)

- **Testes de segurança** em `tests/seguranca/`: mascaramento de CPF, textos de alerta e logs sem CPF, humor individual ou motivo de falta, contrato da API sem dado sensível na URL (exceções R5 e filtro de supervisor listadas no teste) e autoteste da varredura do CI (detecta e nunca imprime o valor).
- **R10 (novo, Médio) — "Doente" em texto livre de alerta:** o detalhe do alerta "Humor negativo recorrente" (`regras/motor.py`) conta os dias marcados como "Doente". O texto do alerta aparece para perfis que não podem ver dado de saúde (CLAUDE.md §2.1 e §4.4). Proposta: o motor guarda a contagem em campo estruturado e a API decide por perfil (`ver_doente`). Responsáveis: Dados (motor) e API. **Corrigido no PR #32**; coberto por `tests/seguranca/test_textos_e_logs.py`.
- **R2 atualizado — republicação do protótipo `radar_v3` na conta da empresa:** o código no repositório não tem dado real, mas o protótipo grava as bases carregadas no banco do artefato e mostra humor individual (inclusive "Doente") e CPF a quem abre o link, sem perfil nem auditoria. Na conta da empresa o contrato corporativo melhora a situação, mas continua valendo: publicar só para o grupo restrito da matriz, não publicar `radar_v3/fotos/` junto com a página, registrar a operação no `03-registro-operacoes.md` e apagar os dados da conta pessoal assim que a nova estiver conferida. Decisão do dono e do DPO.
- R1 (repositório público) continua aberto.
