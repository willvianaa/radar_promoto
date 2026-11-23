# regras/ — transformação raw → core e motor de cálculo

Python 3.12, sem E/S e sem dependências além da biblioteca padrão. Determinístico: mesma entrada + mesma versão de parâmetros = mesmo resultado.

| Módulo | O que faz |
|---|---|
| `parametros.py` | Parâmetros da versão nº 1 (`db/modelo.md`) e a regra de limites `[a,b,c]` |
| `transformacao.py` | Uma função por origem: linhas cruas (`raw.linha.dados`) → registros do core. CPF (herança por nome), status R/E/P, almoço, jornada cadastrada, teto por linha, semana fechada, marcas quinzenais |
| `motor.py` | `calcular(base, parametros, ini, fim)` → dimensões, alertas e severidades, nível C/A/T/N, Índice de risco, sobrecarga e leitura cruzada com humor |
| `tipos.py` | Registros em memória que espelham as tabelas do core |
| `util.py` | Nome normalizado, CPF, datas/horas, distância, formatação pt-BR |

## Decisões que seguem o CLAUDE.md onde o protótipo difere

1. **Humor soma, como no protótipo (§4.4/§4.7 atualizados).** "Humor negativo recorrente" = 1 ponto; "Possível sobrecarga" = 2, ou 3 quando carga de visitas e humor negativo aparecem juntos. A dimensão Humor fica fora da média de dimensões do Índice de risco, e o humor não fundamenta conclusão do dossiê.
2. **Almoço (§4.1).** `NÃO OPERACIONAL` sai antes de qualquer cálculo (não é visita, não vira primeiro check-in nem dia trabalhado). `REUNIÃO` conta na jornada, mas não como loja atendida.
3. **Aderência (§4.3).** Realizadas limitadas ao contratado em cada linha (colaborador × loja × marca × semana) e agrupadas por UF + loja + marca; só semanas fechadas entram (carga, queda, alertas). O protótipo somava as marcas de uma loja e não limitava a linha.
4. **Semana fechada** = o domingo da semana é anterior a "hoje" (decidido na transformação, gravado em `core.aderencia.semana_fechada`).
5. **Chave do colaborador (§3).** CPF da origem → CPF do cadastro pelo nome normalizado (homônimos não herdam) → `N:` + nome normalizado com `cpf_pendente`.
