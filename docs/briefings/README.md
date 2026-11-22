# Briefings das sessões

Um briefing por sessão: a ideia, por que existe, o que entrega, o que não faz, como se encaixa nas outras e como saber que terminou.
Toda sessão nova (filha ou mãe) ganha o seu briefing **antes** de começar; mudança de escopo atualiza o briefing por PR.

| Sessão | Modelo | Branch | Onda | Situação | Briefing |
|---|---|---|---|---|---|
| Mãe (arquitetura) | Opus | `docs/*` | 0 | Ativa | [00-mae.md](00-mae.md) |
| Infra e Docs | Haiku | `feat/infra` | 1 | Em andamento | [01-infra.md](01-infra.md) |
| Dados e regras | Sonnet | `feat/dados` | 1 | Em andamento | [02-dados.md](02-dados.md) |
| Ingestor | Sonnet | `feat/ingestor` | 2 | Aguardando onda 1 | [03-ingestor.md](03-ingestor.md) |
| Backend/API | Sonnet | `feat/api` | 2 | Aguardando onda 1 | [04-api.md](04-api.md) |
| Design/Front | Sonnet | `feat/front` | 3 | Aguardando onda 2 | [05-front.md](05-front.md) |
| Documentos | Haiku | `feat/documentos` | 3 | Aguardando onda 2 | [06-documentos.md](06-documentos.md) |
| Otimização e QA | Sonnet | `feat/qa` | 4 | Aguardando onda 3 | [07-qa.md](07-qa.md) |

Regras comuns a todos: `CLAUDE.md` (dados fictícios, nada real no repositório, PR pequeno, só o dono faz merge, contrato muda só por PR na mãe).
