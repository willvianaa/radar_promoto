# LEIA-ME PRIMEIRO — Radar Promotor (RT Intelligence · Planejamento e Produtividade)

Este arquivo é o ponto de partida para continuar o projeto em **outra conta do Claude** (por exemplo, a conta empresarial da RT). Ele resume tudo o que foi feito, como a equipe de sessões está organizada e o que falta.

---

## 1. Como começar na conta nova (3 passos)

1. Abra o app do Claude com a conta da empresa → aba **Code**.
2. Abra esta pasta (`radar_promotor`).
3. Cole a mensagem da seção **2** abaixo. Ela recria a **sessão-mãe**, que por sua vez recria as **sessões-filhas**.

---

## 2. Mensagem para colar na primeira sessão (vira a sessão-mãe)

```
Você é a sessão-mãe (arquitetura) do sistema RADAR PROMOTOR da RT. Antes de tudo, leia:
LEIA-ME-PRIMEIRO.md, CLAUDE.md, docs/08-plano-de-ondas.md, docs/briefings/README.md,
.claude/agents/README.md e docs/lgpd/00-diagnostico.md.

Seu papel: planejar, manter os contratos (CLAUDE.md, schemas/, db/, api/openapi.yaml),
revisar os PRs das sessões-filhas e me avisar do que precisa da minha aprovação. Não escreva
código de implementação nas áreas das filhas.

Depois de ler, (1) me diga em que pé está o projeto e o que está pendente, e (2) recrie as
8 sessões-filhas, uma por área, cada uma com nome simples, o modelo do seu harness
(.claude/agents/<área>.md) e um brief baseado no briefing dela (docs/briefings/). Ao criar
cada filha, me diga o papel dela no sistema. Regras de PR e merge: CLAUDE.md §1.
```

---

## 3. A equipe de sessões

| Sessão | Modelo | Harness | Briefing | Papel |
|---|---|---|---|---|
| **Mãe (arquitetura)** | Opus | — | `docs/briefings/00-mae.md` | Planeja, mantém contratos, revisa e aprova PRs |
| Infra e Docs | Haiku | `.claude/agents/infra.md` | `01-infra.md` | Docker, CI, agendamento 05:00, README |
| Dados e Regras | Sonnet | `.claude/agents/dados.md` | `02-dados.md` | Migrações, motor de alertas, nível, risco, sobrecarga |
| Ingestor | Sonnet | `.claude/agents/ingestor.md` | `03-ingestor.md` | Robô que baixa exports (Involves, 2PRT) e valida |
| Backend e API | Sonnet | `.claude/agents/api.md` | `04-api.md` | FastAPI, login, perfis, CPF mascarado, auditoria |
| Design e Front | Sonnet | `.claude/agents/front.md` | `05-front.md` | As 4 abas do sistema web |
| Documentos | Haiku | `.claude/agents/documentos.md` | `06-documentos.md` | PDF/Excel do dossiê, numeração RP-AAAA-NNNNNN |
| Otimização e QA | Sonnet | `.claude/agents/qa.md` | `07-qa.md` | Regressão, bordas, desempenho, e2e |
| LGPD e Segurança | Opus | `.claude/agents/lgpd-seguranca.md` | `08-lgpd-seguranca.md` | LGPD, varredura de CPF/segredos, revisão de PRs sensíveis |

Regra de trabalho (CLAUDE.md §1): tudo por PR; merge com **CI verde** + comentário **"Aprovado pela sessão-mãe"**; PR que toca dado pessoal, login, permissão, log ou infra também precisa de **"Revisão LGPD/Segurança: OK"**.

---

## 4. Onde está cada coisa

| O quê | Onde |
|---|---|
| Regras de negócio e LGPD | `CLAUDE.md` |
| Formato dos exports | `schemas/` |
| Banco de dados | `db/modelo.md`, `db/modelo.sql`, `db/migrations/` |
| Contrato da API | `api/openapi.yaml` |
| Motor de regras (sistema web) | `regras/` |
| API | `api/app/` |
| Robô de coleta | `ingestor/` |
| Testes | `tests/` |
| Protótipo usado na apresentação | `radar_v3/` (gerar com `python radar_v3/build.py`) |
| Plano e briefings | `docs/08-plano-de-ondas.md`, `docs/briefings/` |
| Documentos LGPD | `docs/lgpd/` |
| Migração entre contas | `docs/MIGRACAO.md` |

**Fora do Git (copiar à parte, por meio aprovado pela TI):** pasta `dados/` (exports reais) e `radar_v3/fotos/` (fotos com indício). Nunca subir para o GitHub.

---

## 5. Estado em 23/11/2026

**Protótipo (`radar_v3`)** — funcionando com dados reais (654 promotores, 27/10 a 09/11/2026), publicado como página do Claude na conta pessoal. Abas: Visão Geral (radar, parâmetros com detalhe ao clicar, níveis, fotos com indício), Alertas (gráficos, cards por promotor, análise de **Humor** × desempenho), Raio-X (jornada, calendário, carga de trabalho, humor do Involves, fotos), Dossiê (PDF/Excel com fotos). Na conta nova é preciso **republicar** e **recarregar os dados** (link muda).

**Sistema web (repositório)** — na `main`: contratos, harness, LGPD, Docker/CI, migrações, motor de regras (humor soma pontos, mais rápido), varredura de CPF/segredos, documentos LGPD, gerador de dados de QA.

**PRs abertos quando este arquivo foi escrito** (conferir no GitHub):
- #13 e #14 — contrato `senha_hash` e base da API (aprovados; LGPD OK; faltava confirmar o merge)
- #11 e #17 — Ingestor: validador, gravação em raw e fluxos Playwright (aprovados; LGPD OK)
- #20, #21, #22 — QA: casos de borda, plano de regressão, e2e (#20 entra depois do #25)
- #25 — Dados: linha ruim não derruba o lote; reunião não conta como loja (aprovado)
- #27 — Documentos: PDF/Excel do dossiê no servidor (aguardando revisão)
- #16 e branch `feat/front-geral` — Front (PR da `feat/front-geral` ainda não aberto)
- #28 — protótipo no repositório + este arquivo + guia de migração

---

## 6. Decisões tomadas pelo dono (aplicar nos contratos)

- **Meta de aderência única: 93%** (sem Meta 1 / Meta 2). → atualizar `CLAUDE.md` §4.3 e `db/modelo.md`.
- **Risco simples:** risco = soma das severidades dos alertas × 10, até 100. → atualizar `CLAUDE.md` §4.7 e o motor (`regras/`).
- **Humor soma pontos** no nível e no risco (já em `CLAUDE.md` §4.4).
- **Respostas negativas de humor:** Cansado, Sobrecarregado, Triste, Doente, **Luto, Incomodado, Estressado e Não Valorizado**. → atualizar `CLAUDE.md` §4.4 e o motor.
- **"Sobrecarga" e "Humor" são tipos de alerta separados.**
- Sessões abrem PR e fazem merge com CI verde e aprovação da mãe (`CLAUDE.md` §1).

---

## 7. O que falta (por dono)

| Pendência | Quem decide/faz |
|---|---|
| Tornar o repositório **privado** (R1) | Dono |
| Apagar os dados reais guardados na conta pessoal do Claude depois de migrar (R2) | Dono |
| API do Involves **ou** usuário de serviço só leitura (sem 2FA) | TI |
| Servidor/hospedagem e login corporativo (SSO) | TI |
| Base legal do humor, prazos de guarda, quem vê o quê | DPO, RH, Jurídico |
| Layout de faltas (DP) e de estoque (cliente) | DP, Merchandising |
| Schemas das planilhas **Pesquisa x Dia** e **Contrato** (Google Sheets; links com o dono) | Mãe (PR de contrato) + Ingestor |
| Jornadas vêm da aba de colaboradores (já coberto em `schemas/colaboradores`) | — |
| Piloto de 30 dias em uma regional | Diretoria |

---

## 8. Ferramentas usadas neste computador

- Python 3.12 (`C:\Users\RT-151\AppData\Local\Programs\Python\Python312\python.exe`); sem `node` e sem `gh`.
- PRs abertos pelo GitHub no Chrome, com a conta do dono logada.
- Rotina do 2PRT (exportação de aderência/PDOH) documentada na pasta `backup - will\2PRT_rotina` (fora deste repositório).
