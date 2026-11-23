# Briefings das sessões

Um briefing por sessão: a ideia, por que existe, o que entrega, o que não faz, como se encaixa nas outras e como saber que terminou.
Cada sessão também tem um **harness** em `.claude/agents/` (modelo, ferramentas, pastas que pode mexer, limites, verificação e saída).
Toda sessão nova ganha briefing e harness **antes** de começar; mudança de escopo atualiza os dois por PR.

| Sessão | Modelo | Branch | Situação | Briefing | Harness |
|---|---|---|---|---|---|
| Mãe (arquitetura) | Opus | `docs/*` | Ativa | [00-mae.md](00-mae.md) | — |
| Infra e Docs | Haiku | `feat/infra` | Ativa | [01-infra.md](01-infra.md) | `infra.md` |
| Dados e Regras | Sonnet | `feat/dados*` | Ativa | [02-dados.md](02-dados.md) | `dados.md` |
| Ingestor | Sonnet | `feat/ingestor` | Ativa | [03-ingestor.md](03-ingestor.md) | `ingestor.md` |
| Backend e API | Sonnet | `feat/api` | Ativa | [04-api.md](04-api.md) | `api.md` |
| Design e Front | Sonnet | `feat/front` | Ativa | [05-front.md](05-front.md) | `front.md` |
| Documentos | Haiku | `feat/documentos` | Ativa | [06-documentos.md](06-documentos.md) | `documentos.md` |
| Otimização e QA | Sonnet | `feat/qa` | Ativa | [07-qa.md](07-qa.md) | `qa.md` |
| LGPD e Segurança | Opus | `feat/lgpd-seguranca` | Ativa | [08-lgpd-seguranca.md](08-lgpd-seguranca.md) | `lgpd-seguranca.md` |

Nomes das sessões são simples (o nome da área), sem número de onda.
Regras comuns a todas: `CLAUDE.md` (dados fictícios, LGPD §2.1, PR pequeno, merge com CI verde e aprovação da mãe).
