# Plano de regressão contra dossiês históricos

Objetivo (docs/06 §6.2): provar que o sistema dá **os mesmos números** que os dossiês manuais já concluídos. Toda divergência é explicada e registrada: erro do motor → corrige-se o motor; erro do dossiê manual → registra-se a evidência. Os casos viram testes permanentes.

## Regra de ouro

**Nenhum dossiê, planilha, print ou export real entra no repositório** (CLAUDE.md §2; o repositório é público). A anonimização é feita **fora do repositório, pelo dono**. Só o resultado anonimizado, no formato abaixo, vira fixture em `tests/regressao/fixtures/`.

## 1. Seleção (o dono)

- 5 a 10 dossiês concluídos, de períodos fechados, cobrindo: nível Crítico, Alto, Atenção e Estável; ao menos um com humor negativo recorrente; um com feriado no período; um com semana em andamento no corte; um com colaborador sem CPF na origem; um com marca quinzenal (WD-40/Botafogo).
- Vínculos CLT e PJ, mais de uma UF, mais de uma jornada cadastrada.

## 2. Anonimização (o dono, fora do repositório)

Trabalhar numa pasta local **fora** do clone do repositório (ex.: `C:\Anonimizacao\`), nunca versionada nem sincronizada com nuvem pública.

1. **Pseudonimizar pessoas.** Para cada colaborador, gerar `P001`, `P002`… e um nome inventado (`Pessoa Fictícia 001`). Guardar a tabela de correspondência só na pasta local (nunca no repositório).
2. **CPF:** substituir por CPF fictício inválido de propósito, mantendo **a mesma ordem e o mesmo agrupamento** (`000.000.001-91`, `000.000.002-82`…). Casos sem CPF na origem continuam sem CPF.
3. **Homônimos reais** continuam homônimos (mesmo nome fictício, CPFs diferentes), pois são caso de borda.
4. **Lojas/PDVs e marcas:** trocar por `BA / LOJA FICTICIA 01`…, `MARCA A`…; manter os PDVs `NÃO OPERACIONAL` e `REUNIÃO` com o nome original (não identificam ninguém).
5. **Supervisor:** `Supervisor Fictício 01`…
6. **Datas:** deslocar **todas** as datas por um mesmo número de dias, de modo que o dia da semana e os feriados relativos se mantenham (deslocar em múltiplos de 7; ajustar feriados da tabela). Horas, durações e contagens ficam **idênticas**.
7. **Fotos:** não levar imagens. Levar só `sha256` substituído por identificador (`foto-001`; fotos repetidas mantêm o mesmo identificador) e as distâncias já calculadas em metros.
8. **Coordenadas GPS:** não levar. Levar só a distância à loja (m) por posição.
9. **Texto livre e motivo de falta:** remover; manter apenas o tipo (I, J, A, F).
10. **Humor:** manter a opção (a regra depende dela); sem vínculo a pessoa real após o passo 1.
11. **Revisão de reidentificação:** procurar no pacote final, por busca de texto, qualquer nome, CPF, loja, e-mail ou telefone reais da tabela de correspondência. Zero ocorrências. Depois, enviar a revisão para a sessão LGPD e Segurança (PR com o comentário "Revisão LGPD/Segurança: OK" antes do merge).

## 3. Formato do resultado anonimizado (vira fixture)

Um diretório por caso: `tests/regressao/fixtures/caso_NN/`

| Arquivo | Conteúdo |
|---|---|
| `entrada/*.csv` | Linhas cruas anonimizadas, **com os nomes de coluna dos `schemas/`** (colaboradores, operacao, atividades, humor, faltas, aderencia, pdoh, fotos). UTF-8, separador `,`, datas `dd/mm/aaaa`. |
| `parametros.json` | Versão de parâmetros usada no dossiê (ou `{}` para a v1 de `db/modelo.md`). |
| `contexto.json` | `{"periodo_ini": "AAAA-MM-DD", "periodo_fim": "AAAA-MM-DD", "hoje": "AAAA-MM-DD", "feriados": [["AAAA-MM-DD", null]]}` já com as datas deslocadas. |
| `esperado.json` | Números do dossiê manual por pessoa (ver abaixo). |
| `divergencias.md` | Só quando houver: cada diferença conhecida, a causa e quem estava certo (motor ou dossiê), com evidência anonimizada. |
| `LEIAME.md` | Origem do caso (ex.: "dossiê concluído em mês fechado"), **sem** data real, nome real ou identificador do documento original. |

`esperado.json`:

```json
{
  "pessoas": {
    "00000000191": {
      "nivel": "C",
      "score": 9,
      "risco": 71,
      "alertas": {"jor": 2, "pesq": 3, "ader": 2},
      "aderencia_pct": 0.87,
      "dias_trabalhados": 18,
      "atrasos": 7,
      "checkout_auto": 3,
      "faltas_injustificadas": 1
    }
  }
}
```

`alertas` mapeia tipo → severidade (1, 2 ou 3). Campos que o dossiê manual não trouxer ficam de fora (não são comparados).

## 4. Execução e comparação

Teste parametrizado (a criar quando houver a primeira fixture): para cada `caso_NN`, transformar `entrada/` com `regras.transformacao`, rodar `regras.motor.calcular` e comparar com `esperado.json`.

- Inteiros (nível, score, severidades, contagens): igualdade exata.
- Percentuais: tolerância 0,5 ponto percentual, **a menos que** a regra de arredondamento (meio para cima, `util.arredonda`) explique a diferença.
- Índice de risco: igualdade exata (regra determinística, CLAUDE.md §4.7).
- Pessoa no esperado ausente do resultado, ou vice-versa, é divergência.

## 5. Tratamento das divergências

1. Reproduzir à mão a conta do campo divergente com a regra do CLAUDE.md.
2. Motor errado → achado em `docs/qa/achados.md` para Dados e Regras (PR na branch dela); o teste fica `xfail(strict=True)` até a correção.
3. Dossiê manual errado ou regra diferente na época → registrar em `divergencias.md` com a evidência e marcar o campo como "ignorado" no `esperado.json`.
4. Dúvida de regra de negócio → perguntar ao dono (nunca decidir sozinha).

## 6. Critério de saída (Fase 1)

Regressão sem divergência não explicada nos casos selecionados; todas as divergências explicadas estão registradas; casos mantidos como testes permanentes.

## 7. Enquanto não há fixtures reais

O teste de regressão usa o cenário sintético já existente em `tests/fixtures/cenario.py` e a suíte de paridade (`tests/test_paridade.py`). Nada neste plano exige dado real no repositório.
