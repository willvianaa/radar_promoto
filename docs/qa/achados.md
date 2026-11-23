# Achados de QA (priorizados)

Prioridade: **P1** bloqueia uso real · **P2** corrigir antes da Fase 1 · **P3** melhoria.
Cada achado nomeia a sessão dona; QA não corrige código de outra área.

| ID | Prio | Área dona | Achado | Evidência | Status |
|---|---|---|---|---|---|
| A-01 | P2 | Dados e Regras (`regras/`) / Backend e API | O motor leva ~20 s para 1.000 × 60 dias; a meta de painel < 2 s só é possível lendo resultados pré-calculados. ~75 % do tempo está em `util.norm_nome` (sem cache). Memoizar corta a ~10 s. | `docs/qa/desempenho.md` | Aberto — avisar dados e api |
