# Radar Promotor (RT Intelligence)

Sistema web do Radar Promotor: análise operacional de promotores de campo (jornada, pesquisas, aderência, humor, fotos e dossiê formal).

> **Dados reais nunca entram no repositório.** O repositório é público. Testes usam só dados fictícios em `tests/fixtures/`. Credenciais ficam em `.env` (fora do git) ou nos secrets do ambiente.

Regras de negócio, contratos e plano de trabalho estão em [CLAUDE.md](CLAUDE.md) (fonte da verdade) e em [docs/08-plano-de-ondas.md](docs/08-plano-de-ondas.md).

## Como subir localmente

Pré-requisitos: Docker com Compose v2 e Git.

```powershell
git clone https://github.com/willvianaa/radar_promoto.git
cd radar_promoto
copy .env.example .env
# edite o .env e preencha POSTGRES_DB, POSTGRES_USER e POSTGRES_PASSWORD (valores fictícios para dev)
docker compose up --build
```

Quando subir:

- Postgres 16 em `127.0.0.1:5432`. O serviço `migrate` aplica as migrações (`alembic upgrade head`) antes da API e do worker; rodar de novo não altera nada.
- API em `http://127.0.0.1:8000/api/v1/saude` → `{"status": "ok"}`.
- Worker: agendador do ingestor, execução diária às 05:00 (America/Sao_Paulo). Hoje é um placeholder: não lê nenhuma origem.

Sem Docker, para rodar só os testes e a API:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
uvicorn api.app.main:app --port 8000
```

## Estrutura de pastas

| Pasta | Conteúdo | Quem entrega |
|---|---|---|
| `api/` | Contrato da API (`openapi.yaml`) e código FastAPI (`api/app/`) | Contratos; feat/api |
| `db/` | Modelo do banco (`modelo.sql`, fonte da verdade) e notas | Contratos; feat/dados (migrações) |
| `schemas/` | Formato de cada export, uma linha por arquivo (`*.schema.json`) | Contratos; feat/ingestor |
| `ingestor/` | Agendador do worker e, depois, o ingestor (Playwright) | feat/infra (agendador); feat/ingestor |
| `regras/` | Motor de KPIs, alertas, nível e Índice de risco | feat/dados |
| `front/` | Interface web (consome só a API) | feat/front |
| `docs/` | Especificação (01 a 08) | Contratos |
| `tests/` | Testes automatizados | Todas as sessões |
| `tests/fixtures/` | Dados fictícios para testes | Todas as sessões |
| `scripts/` | Utilitários do repositório (ex.: validação dos contratos) | feat/infra |
| `docker/` | Dockerfiles da API e do worker | feat/infra |
| `.github/workflows/` | CI (lint, testes, contratos, build) | feat/infra |

Pastas de código ainda vazias têm um `README.md` com o escopo. Os demais arquivos (`radar_v2/`, `radar_v3/`, `prototipo/`, `ferramentas/`, `sistema/`) são o protótipo anterior e ficam como referência.

## Testes e CI

Rode localmente antes de abrir PR:

```powershell
ruff check .
ruff format --check .
pytest
python scripts/validar_contratos.py
```

O workflow `.github/workflows/ci.yml` roda: lint (ruff), testes (pytest), validação de `schemas/*.json` e `api/openapi.yaml`, e build das imagens com `docker compose up` do Postgres e da API checando `/api/v1/saude`. Nenhum secret é necessário: o CI usa valores fictícios.

## Fluxo de trabalho (PR)

1. Toda mudança entra por PR. Ninguém faz merge sozinho: o dono do projeto aprova e faz o merge.
2. Cada área trabalha na sua branch `feat/<área>` (ex.: `feat/infra`, `feat/dados`) a partir da `main`.
3. PRs pequenos e frequentes, um assunto por PR.
4. Todo PR descreve: o que muda, como testar, qual contrato segue e riscos. Testes verdes antes de pedir revisão.
5. Mudança de contrato (`schemas/`, `db/`, `api/openapi.yaml`, regras do `CLAUDE.md`) sai em PR próprio, antes do código que depende dele.
6. Commits e PRs em português.

## Configuração

Variáveis estão listadas em [.env.example](.env.example), **só com nomes**. Os valores vão para o `.env` local (não versionado) ou para os secrets do ambiente. Nenhum valor real deve aparecer em código, teste, log ou documentação.

## Documentação

| Nº | Entrega | Documento |
|----|---------|-----------|
| 1 | Arquitetura | [docs/01-arquitetura.md](docs/01-arquitetura.md) |
| 2 | Dicionário de KPIs e regras | [docs/02-dicionario-kpis.md](docs/02-dicionario-kpis.md) |
| 3 | Wireframes | [docs/03-wireframes.md](docs/03-wireframes.md) |
| 4 | Modelo do dossiê | [docs/04-modelo-documentos.md](docs/04-modelo-documentos.md) |
| 5 | Matriz de permissões | [docs/05-matriz-permissoes.md](docs/05-matriz-permissoes.md) |
| 6 | Plano de fases e testes | [docs/06-plano-fases-e-testes.md](docs/06-plano-fases-e-testes.md) |
| 7 | Premissas e perguntas em aberto | [docs/07-premissas-e-perguntas.md](docs/07-premissas-e-perguntas.md) |
| 8 | Plano de ondas e sessões-filhas | [docs/08-plano-de-ondas.md](docs/08-plano-de-ondas.md) |
