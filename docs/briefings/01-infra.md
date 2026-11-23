# Briefing — Infra e Docs (Haiku · `feat/infra` · onda 1)

## A ideia
Dar ao projeto um "chão" onde todas as outras sessões pisam: subir o sistema com um comando, testar cada PR automaticamente e rodar o ingestor todo dia sem ninguém lembrar. Sem isso, cada filho montaria o ambiente do seu jeito e os PRs não seriam comparáveis.

## Por que Haiku
Trabalho bem definido e mecânico (Docker, YAML de CI, README), com pouco julgamento de negócio.

## Entrega
- `docker-compose.yml`: Postgres 16, `api` (FastAPI, Python 3.12, rota `/api/v1/saude`), `worker` com cron do ingestor às 05:00 America/Sao_Paulo (placeholder até a onda 2).
- `Dockerfile`(s) e `.env.example` só com nomes de variáveis.
- GitHub Actions: ruff, pytest, build das imagens, validação de `schemas/*.json` e de `api/openapi.yaml`.
- `README.md`: subir local, estrutura de pastas, fluxo de PR.

## Não faz
Não cria secrets reais, não escolhe hospedagem (pendente Q-01), não altera contratos.

## Encaixe
Base para Dados (migrações rodam no Postgres do compose), Backend (serviço `api`), Ingestor (serviço `worker`) e QA (CI).

## Pronto quando
CI verde em PR; `docker compose up` sobe Postgres e `/api/v1/saude` responde 200 (ou relato claro do que não pôde ser validado nesta máquina).

## Riscos
Docker pode não estar instalado no computador do escritório; hospedagem ainda indefinida — manter tudo portátil.
