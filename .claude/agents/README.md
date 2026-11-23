# Harness das sessões

Cada sessão do Radar Promotor roda com um **harness** próprio: o arquivo `<área>.md` desta pasta.
O harness define, para aquela sessão:

| Item | Para quê |
|---|---|
| `model` | Modelo usado (custo × complexidade) |
| `tools` | Ferramentas que a sessão pode usar (o resto fica bloqueado) |
| **Papel** | O que a sessão é no sistema |
| **Pode mexer** | Pastas e arquivos que são dela |
| **Não pode** | Limites duros (dados, segurança, contratos, origens) |
| **Verificação** | Comandos que precisam passar antes do PR |
| **Saída** | O que o PR deve conter e quando pode haver merge |

Os arquivos seguem o formato de subagente do Claude Code (frontmatter `name`, `description`, `tools`, `model`),
então também podem ser chamados como subagentes. Regras comuns: `CLAUDE.md`. Fluxo de PR e merge: `CLAUDE.md` §1.

| Sessão | Harness | Modelo |
|---|---|---|
| Infra e Docs | `infra.md` | Haiku |
| Dados e Regras | `dados.md` | Sonnet |
| Ingestor | `ingestor.md` | Sonnet |
| Backend e API | `api.md` | Sonnet |
| Design e Front | `front.md` | Sonnet |
| Documentos | `documentos.md` | Haiku |
| LGPD e Segurança | `lgpd-seguranca.md` | Opus |
| Otimização e QA | `qa.md` | Sonnet |
