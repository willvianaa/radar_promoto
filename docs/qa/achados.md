# Achados de QA (priorizados)

Prioridade: **P1** bloqueia uso real · **P2** corrigir antes da Fase 1 · **P3** melhoria.
Cada achado nomeia a sessão dona; QA não corrige código de outra área.

| ID | Prio | Área dona | Achado | Evidência | Status |
|---|---|---|---|---|---|
| A-01 | P2 | Dados e Regras (`regras/`) / Backend e API | O motor leva ~20 s para 1.000 × 60 dias; a meta de painel < 2 s só é possível lendo resultados pré-calculados. ~75 % do tempo está em `util.norm_nome` (sem cache). Memoizar corta a ~10 s. | `docs/qa/desempenho.md` | Aberto — avisar dados e api |
| A-02 | P2 | Dados e Regras (`regras/util.py`, `regras/transformacao.py`) | Origem com valor inválido derruba o lote: `parse_data` lança `ValueError` em data impossível (`31/02/2026`); `transforma_aderencia` lança em semana ISO 0 ou 54; `parse_hora` aceita `25:99` (=1599 min). Uma linha ruim aborta a transformação inteira em vez de ser descartada e contada. | `tests/regressao/test_bordas.py` (xfail strict) | Aberto — avisar dados e mãe |
| A-03 | P3 | Dados e Regras (`regras/motor.py`) | `DiaJornada.lojas` conta PDV REUNIÃO como loja; CLAUDE.md §4.1 diz que reunião não conta como loja atendida. | `test_reuniao_nao_conta_como_loja_atendida` (xfail strict) | Aberto — confirmar a intenção com a mãe |
