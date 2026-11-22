# Briefing — Dados e regras (Sonnet · `feat/dados` · onda 1)

## A ideia
É o coração do sistema: levar para Python e Postgres, **com testes**, a lógica que hoje roda em JavaScript no protótipo — e que o escritório já validou olhando os resultados. Se esta peça divergir do protótipo, o usuário deixa de confiar no sistema; por isso a meta é **paridade**, não reinvenção.

## Por que Sonnet
Muita regra de negócio fina (jornada, aderência com teto, sobrecarga, níveis) e porte cuidadoso de código.

## Entrega
1. Migrações Alembic que reproduzem `db/modelo.sql` + parâmetros versão 1.
2. `regras/`: transformação raw → core por origem (nome normalizado, CPF herdado pelo nome, status R/E/P, almoço no PDV NÃO OPERACIONAL, realizadas limitadas ao contratado, semana fechada).
3. Motor de cálculo: dimensões (0–100), alertas com severidade, nível C/A/T/N, Índice de risco, sobrecarga (≥ 44 visitas/semana e queda ≥ 5 p.p.; humor reforça; PDOH é contexto), leitura cruzada com humor.
4. Testes com fixtures fictícias, incluindo um cenário de paridade calculado à mão.

## Fontes da lógica (só leitura)
`radar_v2/engine.js` (no repositório) e, fora do git, `radar_v3/build.py` e `radar_v3/parts/engine_tail.js`. Nunca usar `dados/` nem `radar_v3/tmp/` (dados reais).

## Não faz
Não baixa exports (é do Ingestor), não expõe API (é do Backend), não altera contratos.

## Encaixe
Recebe `raw.*` do Ingestor; grava `core.*` e `app.indicador_colaborador`/`app.alerta` que o Backend lê.

## Pronto quando
Migrações aplicam do zero; motor passa nos testes de borda (atraso com/sem jornada, check-out automático, feriado, almoço, pesquisas < 20, aderência com teto, semana em andamento, sobrecarga, níveis e risco) e no teste de paridade.

## Riscos
Sem Postgres local, parte das migrações fica sem validar até a Infra subir o compose; ambiguidades do protótipo devem virar pergunta no PR, não decisão silenciosa.
