# 8. Plano de ondas e sessões-filhas

Do protótipo (artefato) para o sistema web do escritório. A sessão-mãe planeja, mantém os contratos,
revisa os PRs dos filhos e avisa o dono do projeto do que precisa de aprovação. **Só o dono faz merge.**

## 8.1 Ondas

| Onda | Entra | Sai (critério de pronto) |
|---|---|---|
| 0 | PR de contratos (este) | CLAUDE.md, `schemas/`, `db/`, `api/openapi.yaml` e este plano aprovados e com merge em `main` |
| 1 | Infra e Docs · Dados e regras | `docker compose up` sobe Postgres + API vazia; CI roda lint e testes; banco migrado conforme `db/modelo.sql`; motor de regras com paridade ao protótipo nos fixtures |
| 2 | Ingestor · Backend/API | Carga diária automática das origens confirmadas, com parada por formato; API do OpenAPI com login, perfis, escopo, mascaramento e auditoria |
| 3 | Design/Front · Documentos | 4 abas funcionando contra a API; PDF e Excel do dossiê gerados no servidor com numeração RP-AAAA-NNNNNN |
| 4 | Otimização e QA | Regressão contra dossiês anonimizados, testes de permissão, desempenho (painel < 2 s com 1.000 colaboradores × 60 dias), revisão de segurança |

## 8.2 Sessões-filhas

Todas seguem o `CLAUDE.md`. Branch `feat/<área>`, PRs pequenos, fixtures fictícias, sem dado real.

| Filho | Modelo | Branch | Escopo | Não faz | Pronto quando |
|---|---|---|---|---|---|
| Infra e Docs | Haiku | `feat/infra` | Dockerfile, docker-compose (Postgres, API, worker), GitHub Actions (lint, testes, build), agendamento diário do ingestor (cron no worker, 05:00 America/Sao_Paulo), README, `.env.example` sem valores | Não cria secrets reais | CI verde; `docker compose up` local funciona |
| Dados e regras | Sonnet | `feat/dados` | Migrações (Alembic) do `db/modelo.sql`; carga raw → core; motor de KPIs, alertas, nível, Índice de risco, sobrecarga e leitura cruzada com humor, portando a lógica do protótipo (`radar_v2/engine.js`, `radar_v3/parts/engine_tail.js`); parâmetros versionados | Não lê export direto da origem | Testes de paridade: para os fixtures, mesmos alertas, níveis e riscos que o protótipo |
| Ingestor | Sonnet | `feat/ingestor` | Playwright com usuário de serviço; download dos exports da plataforma de monitoramento e do 2PRT (só filtros e Exportar); fatiamento ≤ 10 mil linhas; validação contra `schemas/`; parada e `ingestao_alerta` se mudar formato; grava `raw.carga`/`raw.linha` | **Não contorna captcha ou 2FA**; nunca clica Atualizar/Gerar Aderência | Rodada completa contra um ambiente simulado (páginas fake nos testes) e contra a origem real em homologação |
| Backend/API | Sonnet | `feat/api` | FastAPI conforme `api/openapi.yaml`; login (e-mail/senha com hash até definir SSO); perfis e escopo da matriz de permissões; mascaramento de CPF; log de auditoria append-only; URLs assinadas de foto | Não reimplementa regra de negócio (chama o motor) | Testes de contrato (schemathesis) e de permissão por perfil |
| Design/Front | Sonnet | `feat/front` | 4 abas: Visão Geral (com Radar da operação), Alertas, Raio-X, Dossiê; identidade do Monitor Regional / RT; responsivo; tema claro e escuro; consome só a API | Não acessa banco | Paridade visual com o protótipo v3 aprovada pelo dono; Lighthouse acessibilidade ≥ 90 |
| Documentos | Haiku | `feat/documentos` | PDF formal e Excel do dossiê no servidor (padrão do `CLAUDE.md` §5), numeração RP-AAAA-NNNNNN com lock, hash SHA-256, nome "Dossiê - NOME" | Não decide texto (recebe o conteúdo pronto) | Documento de fixture idêntico ao modelo aprovado; revisão de termos proibidos |
| Otimização e QA | Sonnet | `feat/qa` | Regressão contra dossiês anonimizados (anonimização feita fora do repo), testes de borda (feriado, semana em andamento, CPF ausente, almoço), desempenho, revisão de segurança (OWASP, LGPD) | Não guarda dossiê real no repo | Relatório de QA com achados priorizados |

## 8.3 Dependências e ordem

```
Contratos ──┬─> Infra e Docs ──────────────┐
            └─> Dados e regras ──┬─> Backend/API ──┬─> Design/Front ──┐
                                 └─> Ingestor ─────┘   Documentos ────┴─> QA
```

## 8.4 O que precisa da aprovação do dono

- Merge de todo PR.
- Mudança de contrato (schemas, banco, API, regras do CLAUDE.md).
- Criação do usuário de serviço e dos secrets (o dono cria; nenhum agente recebe a senha em chat).
- Repositório: hoje é **público**. Recomendado torná-lo privado antes da Onda 2 (regras internas, nomes de origem nos schemas).
- Decisões em aberto que bloqueiam ondas: SSO (Q-06), hospedagem (Q-01), layout de faltas e estoque (Q-13), opções de humor pendentes, quem vê humor/“Doente” (Q-08), base legal LGPD (Q-10).
