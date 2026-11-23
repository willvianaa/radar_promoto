# Desempenho do motor de regras — linha de base

Meta (harness QA): painel < 2 s com 1.000 colaboradores × 60 dias; carga diária dentro da janela da madrugada.

## Como medir

```powershell
python -m tests.carga.medir                                   # 1.000 × 60, 3 repetições
python -m tests.carga.medir --colaboradores 250 --repeticoes 1
```

Dados 100% sintéticos (`tests/carga/gerador.py`, semente 2026, impressão `eef727176626b69d`).

## Volume da fixture (1.000 colaboradores × 60 dias)

visitas 224.589 · atividades 291.064 · humor 35.334 · fotos 187.170 · posições 187.170 · aderência 66.000 · faltas 156 · PDOH 1.000.

## Linha de base (22/11/2026)

Máquina de desenvolvimento Windows (Python 3.12.10, AMD64), com outras sessões rodando em paralelo: os números têm ruído e valem como ordem de grandeza.

| Cenário | Motor (`regras.motor.calcular`) |
|---|---|
| 1.000 × 60 (3 execuções) | 20,3 / 21,9 / 17,6 s — mediana **20,3 s** |
| 250 × 60 | 8,2 s |
| 1.000 × 60 com `norm_nome` em cache (experimento, não commitado) | **10,1 s** |

Geração dos dados sintéticos: ~18 s (só no teste).

## Leitura

- **Painel < 2 s: o motor sozinho não cumpre.** O cálculo completo de 1.000 × 60 leva ~20 s. Isso é aceitável para a carga diária (madrugada), mas o painel **não pode recalcular por requisição**: precisa ler resultados já gravados (tabelas de resultado/alertas pelo job diário). Ver achado A-01 em `achados.md`.
- **Gargalo medido** (cProfile, 250 × 60): ~75 % do tempo em `regras.util.norm_nome` (chamada ~335 mil vezes, uma por foto/humor/visita), mais o laço principal de `calcular`. Memoizar `norm_nome` reduz o tempo pela metade.
- Os 4 níveis aparecem na fixture (C 26 · A 100 · T 193 · N 681), então o volume exercita todos os ramos.

## Regressão de desempenho

`tests/carga/test_desempenho.py` falha se 100 × 30 passar de 60 s (teto folgado para o CI). Reexecutar a medição completa a cada mudança em `regras/` e atualizar esta tabela.
