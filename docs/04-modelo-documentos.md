# 4. Modelo dos documentos: Dossiê de Conduta fictício

Modelo do PDF (página a página) e do Excel (aba a aba) de um Dossiê de Conduta.

> **Todos os dados deste modelo são fictícios**: colaboradora, matrícula, supervisor, lojas, marcas, datas e números foram criados só para mostrar o padrão do documento.

## 4.1 Caso fictício usado no modelo

| Campo | Valor |
|-------|-------|
| Nº do documento | RP-2026-000123 · versão 1 |
| Tipo | Dossiê de Conduta |
| Colaboradora | Joana Modelo Pereira · matrícula 900001 · CLT · Promotora de Vendas |
| Regional / UF | Regional Nordeste 1 · BA |
| Supervisor | Carlos Exemplo Souza |
| Escala | Segunda a sábado, 07:00 às 15:20, intervalo das 12:00 às 13:00 |
| Lojas | Loja Fictícia 01 · Loja Fictícia 02 |
| Clientes | Marca A · Marca B |
| Período analisado | 01/09/2026 a 30/09/2026 |
| Dias previstos / trabalhados | 25 previstos (feriado em 07/09) · 24 trabalhados · 1 falta justificada (18/09) |
| Relato a apurar | "Supervisão relata saídas antes do horário, ruptura informada sem fundamento na Loja Fictícia 01 e pesquisas não respondidas na última semana do mês." |

## 4.2 Regras de redação aplicadas

- Linguagem formal, impessoal e objetiva, em terceira pessoa. Sem saudações e sem tom de e-mail.
- Sem cores no texto. Cor só em gráficos, com legenda.
- Sem adjetivos sobre o colaborador. Os termos "detrator" e equivalentes acusatórios são proibidos.
- Vocabulário obrigatório: "indícios", "registros indicam", "necessitam ser apurados".
- No corpo do relatório, sem nomes de sistemas ou fornecedores. Usa-se "registros operacionais" ou "plataforma de monitoramento". A origem técnica fica só no Anexo C.
- No Dossiê de Conduta entram apenas desvios e lacunas. Metas atingidas e aderência positiva ficam de fora.
- No máximo 5 blocos de achados, unindo informações correlacionadas. Cada bloco traz o fato, o número e a tabela ou gráfico que o sustenta, sem rótulos como "Análise:" ou "Comprovação:".
- No máximo 1 gráfico por bloco (barras ou linhas).

## 4.3 PDF, página a página

Layout: A4 retrato, tipografia corporativa (**Q-14**), tabelas com cabeçalho repetido entre páginas.

**Rodapé de todas as páginas:**

```
RP-2026-000123 · v1        Página X de Y        Código de verificação: 7F3A-91C2-D05E-48B6
Este relatório apresenta indícios baseados em registros operacionais; a apuração e a decisão
cabem às áreas responsáveis.
```

### Página 1 – Capa

```
┌─────────────────────────────────────────────────────────────────────┐
│ [LOGO]                                  CONFIDENCIAL – USO INTERNO  │
│                                                                     │
│                                                                     │
│                         RADAR PROMOTOR                              │
│                        DOSSIÊ DE CONDUTA                            │
│                                                                     │
│                                                                     │
│   Documento nº        RP-2026-000123                                │
│   Versão              1                                             │
│   Emissão             06/10/2026 às 10:42                           │
│   Emissor             Ana Exemplo – P&P                             │
│   Área solicitante    Supervisão – Regional Nordeste 1              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ rodapé                                                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Página 2 – Identificação, objeto da apuração e síntese

**1. Identificação**

| Campo | Informação |
|-------|-----------|
| Colaboradora | Joana Modelo Pereira |
| Matrícula | 900001 |
| Vínculo / cargo | CLT · Promotora de Vendas |
| Regional / UF | Regional Nordeste 1 · BA |
| Supervisor | Carlos Exemplo Souza |
| Escala | Segunda a sábado, 07:00 às 15:20, intervalo das 12:00 às 13:00 |
| Lojas e clientes atendidos | Loja Fictícia 01 (Marca A, Marca B) · Loja Fictícia 02 (Marca A) |
| Período analisado | 01/09/2026 a 30/09/2026 (25 dias previstos, 24 dias trabalhados) |

**2. Objeto da apuração**

> Relato registrado em 02/10/2026 pela Supervisão: "Supervisão relata saídas antes do horário, ruptura informada sem fundamento na Loja Fictícia 01 e pesquisas não respondidas na última semana do mês."

**3. Síntese dos achados** (no máximo meia página)

| Nº | Ponto do relato | Conclusão | Indicador-chave |
|----|-----------------|-----------|-----------------|
| 1 | Saídas antes do horário | CONFIRMADO PELOS REGISTROS | Check-out antes do horário previsto em 6 de 24 dias trabalhados |
| 2 | Ruptura informada sem fundamento na Loja Fictícia 01 | PARCIALMENTE CONFIRMADO | 5 de 9 itens informados como ruptura constavam com estoque positivo |
| 3 | Pesquisas não respondidas na última semana do mês | CONFIRMADO PELOS REGISTROS | 15 de 42 pesquisas expiradas na semana de 21/09 a 26/09 |

### Página 3 – Achados detalhados: bloco 1

**4. Achados detalhados**

**4.1 Saídas antes do horário previsto**

Os registros operacionais indicam check-out anterior ao horário previsto na escala (15:20) em 6 dos 24 dias trabalhados no período, considerada a tolerância de 15 minutos. A antecipação média foi de 1h18 e o total acumulado foi de 7h47. Em 3 desses dias o check-out foi registrado automaticamente pela plataforma de monitoramento, sem registro manual de encerramento, e em 4 deles não houve registro de intervalo no ponto não operacional entre 12:00 e 13:00.

| Data | Dia | Último check-out | Antecipação | Tipo de check-out | Intervalo registrado |
|------|-----|------------------|-------------|-------------------|----------------------|
| 05/09/2026 | Sábado | 14:02 | 1h18 | Manual | Sim |
| 12/09/2026 | Sábado | 13:58 | 1h22 | Manual | Não |
| 15/09/2026 | Terça | 14:21 | 0h59 | Manual | Sim |
| 22/09/2026 | Terça | 13:47 | 1h33 | Automático | Não |
| 24/09/2026 | Quinta | 14:10 | 1h10 | Automático | Não |
| 26/09/2026 | Sábado | 13:55 | 1h25 | Automático | Não |

Nos dias com check-out automático, o horário da tabela é o do último registro de atividade.

*[Gráfico de barras: minutos de antecipação por data. Legenda: check-out manual / check-out automático.]*

### Página 4 – Achados detalhados: blocos 2 e 3

**4.2 Ruptura informada e estoque da loja**

Na Loja Fictícia 01, 9 itens foram informados como ruptura nas pesquisas do período. O confronto com o relatório de estoque fornecido pelo cliente indica que 5 desses itens constavam com estoque positivo na mesma data, 2 constavam com estoque zerado e, para 2, não havia relatório de estoque da data. Os 5 registros divergentes necessitam ser apurados junto à loja, uma vez que o estoque em sistema pode não corresponder ao estoque disponível para exposição.

| Data | Marca | Item | Resposta na pesquisa | Estoque no relatório do cliente | Situação |
|------|-------|------|----------------------|---------------------------------|----------|
| 08/09/2026 | Marca A | Item A-01 | Ruptura | 36 un. | Divergente |
| 08/09/2026 | Marca A | Item A-02 | Ruptura | 0 un. | Coerente |
| 14/09/2026 | Marca A | Item A-03 | Ruptura | 48 un. | Divergente |
| 14/09/2026 | Marca B | Item B-01 | Ruptura | 24 un. | Divergente |
| 21/09/2026 | Marca A | Item A-01 | Ruptura | 12 un. | Divergente |
| 21/09/2026 | Marca B | Item B-02 | Ruptura | 0 un. | Coerente |
| 25/09/2026 | Marca A | Item A-04 | Ruptura | Sem relatório | Sem dados |
| 25/09/2026 | Marca B | Item B-01 | Ruptura | Sem relatório | Sem dados |
| 28/09/2026 | Marca B | Item B-03 | Ruptura | 60 un. | Divergente |

**4.3 Pesquisas programadas e não respondidas**

No período, 168 pesquisas foram programadas, 139 foram respondidas (82,7%) e 29 expiraram. A semana de 21/09 a 26/09 concentrou 15 das 29 pesquisas expiradas: das 42 programadas, 27 foram respondidas (64,3%). Das 29 expiradas no período, 26 ocorreram em dias trabalhados e 3 na data da falta justificada (18/09).

| Semana | Período | Programadas | Respondidas | Expiradas | % respondidas |
|--------|---------|-------------|-------------|-----------|---------------|
| S36 | 01/09 a 05/09 | 35 | 33 | 2 | 94,3% |
| S37 | 08/09 a 12/09 | 35 | 32 | 3 | 91,4% |
| S38 | 14/09 a 19/09 | 40 | 36 | 4 | 90,0% |
| S39 | 21/09 a 26/09 | 42 | 27 | 15 | 64,3% |
| S40 | 28/09 a 30/09 | 16 | 11 | 5 | 68,8% |
| **Total** | | **168** | **139** | **29** | **82,7%** |

*[Gráfico de barras empilhadas por semana. Legenda: respondidas / expiradas.]*

### Página 5 – Outras ocorrências e contexto de acompanhamento

**5. Outras ocorrências identificadas**

Além dos pontos do relato, os registros do período indicam:

| Ocorrência | Quantidade | Datas | Referência |
|------------|-----------|-------|-----------|
| Check-in após o horário previsto (tolerância de 15 min) | 3 dias | 03/09 (07:41), 16/09 (07:38), 23/09 (08:05) | Anexo B, tabela de jornada |
| Fotos com indício de duplicidade (mesma imagem em visitas distintas) | 2 fotos | 10/09 e 17/09, Loja Fictícia 01 | Anexo A, fotos 1 e 2 |
| Foto capturada a mais de 300 m da loja | 1 foto | 24/09, Loja Fictícia 01 (640 m) | Anexo A, foto 3 |
| Aderência da Loja Fictícia 01 abaixo da meta de 93% | 86,4% | 38 de 44 visitas previstas | Anexo B, tabela de aderência |

A Loja Fictícia 02 não consta neste documento por apresentar aderência igual ou superior à meta.

**6. Contexto de acompanhamento** *(seção impressa somente para perfis autorizados)*

| Item | Informação |
|------|-----------|
| Quadrante na matriz Humor × Desempenho | AZUL (humor sem alerta, desempenho abaixo do corte) |
| Índice de Desempenho | 81,2 (aderência 89,1% · pesquisas respondidas 82,7% · conformidade de jornada 62,5%) |
| Índice de Humor no período | 71,6 |
| Adesão ao registro de humor | 91,7% (22 de 24 dias trabalhados) |
| Alertas de cuidado no período | Nenhum |
| Conversas de cuidado registradas | Nenhuma |

As informações desta seção têm finalidade exclusiva de acompanhamento e não constituem fundamento para medida disciplinar.

### Página 6 – Considerações finais e campos de ciência

**7. Considerações finais**

Sendo assim, os registros do período de 01/09/2026 a 30/09/2026 apresentam indícios de encerramento antecipado da jornada, de divergência entre rupturas informadas e o estoque da Loja Fictícia 01 e de pesquisas não respondidas concentradas na semana de 21/09 a 26/09, os quais necessitam ser apurados. Recomenda-se o acompanhamento da liderança direta, com apoio de Treinamento e Desenvolvimento e de Merchandising quanto à execução das pesquisas e ao registro de ruptura, e a verificação, junto à loja, da disponibilidade física dos itens apontados.

**8. Ciência**

| Papel | Nome | Data | Assinatura |
|-------|------|------|-----------|
| Emissor | Ana Exemplo – P&P | 06/10/2026 | |
| Revisor / aprovador | Bruno Exemplo – P&P | 06/10/2026 | |
| Supervisor | Carlos Exemplo Souza | | |
| RH | | | |

### Páginas 7 e 8 – Anexo A: book de fotos

Duas fotos por linha, até quatro por página. Cada foto com a legenda completa.

```
┌───────────────────────────────┐  ┌───────────────────────────────┐
│                               │  │                               │
│            [FOTO 1]           │  │            [FOTO 2]           │
│                               │  │                               │
├───────────────────────────────┤  ├───────────────────────────────┤
│ Data/hora: 10/09/2026 10:14   │  │ Data/hora: 17/09/2026 09:52   │
│ Loja: Loja Fictícia 01        │  │ Loja: Loja Fictícia 01        │
│ Pesquisa: Abastecimento –     │  │ Pesquisa: Abastecimento –     │
│           Marca A             │  │           Marca A             │
│ Motivo do indício: imagem     │  │ Motivo do indício: imagem     │
│ idêntica à foto 2             │  │ idêntica à foto 1             │
│ ID: FT-000000001              │  │ ID: FT-000000002              │
└───────────────────────────────┘  └───────────────────────────────┘
┌───────────────────────────────┐
│            [FOTO 3]           │
├───────────────────────────────┤
│ Data/hora: 24/09/2026 11:03   │
│ Loja: Loja Fictícia 01        │
│ Pesquisa: Ponto extra –       │
│           Marca B             │
│ Motivo do indício: captura a  │
│ 640 m da loja                 │
│ ID: FT-000000003              │
└───────────────────────────────┘
```

### Páginas 9 a 11 – Anexo B: tabelas completas

- **B.1 Jornada dia a dia:** os 25 dias previstos, com escala, primeiro check-in, último check-out, atraso, saída antecipada, tipo de check-out, intervalo registrado e observação (feriado, falta justificada).
- **B.2 Pesquisas:** por semana, loja, cliente e tipo de serviço.
- **B.3 Aderência:** por loja e semana, com a meta. Só lojas abaixo de 93%.

  | Semana | Loja | Previstas | Realizadas | Aderência | Meta |
  |--------|------|-----------|-----------|-----------|------|
  | S36 | Loja Fictícia 01 | 10 | 9 | 90,0% | 93% |
  | S37 | Loja Fictícia 01 | 8 | 8 | 100,0% | 93% |
  | S38 | Loja Fictícia 01 | 10 | 9 | 90,0% | 93% |
  | S39 | Loja Fictícia 01 | 10 | 7 | 70,0% | 93% |
  | S40 | Loja Fictícia 01 | 6 | 5 | 83,3% | 93% |
  | **Total** | | **44** | **38** | **86,4%** | **93%** |

- **B.4 Ruptura x estoque:** tabela completa do bloco 4.2.
- **B.5 Faltas e afastamentos:** 18/09/2026, falta justificada. O motivo não é impresso.

As tabelas quebram entre páginas com o cabeçalho repetido.

### Página 12 – Anexo C: rastreabilidade

Único lugar do documento em que a origem técnica é citada.

| Indicador | Fonte técnica | Registros (IDs) | Data de extração | Versão dos parâmetros |
|-----------|---------------|-----------------|------------------|-----------------------|
| Jornada (check-in e check-out) | Plataforma de monitoramento – visitas | VS-000000101 a VS-000000164 | 01/10/2026 03:10 | v3 |
| Pesquisas | Plataforma de monitoramento – pesquisas | PQ-000000001 a PQ-000000168 | 01/10/2026 03:10 | v3 |
| Fotos | Plataforma de monitoramento – fotos | FT-000000001 a FT-000000003 | 01/10/2026 03:10 | v3 |
| Aderência | Base do 2P RT | AD-2026-S36 a AD-2026-S40 | 01/10/2026 03:25 | v3 |
| Estoque | Upload do backoffice do cliente | UP-000000045, UP-000000052 | 02/10/2026 14:02 | v3 |
| Faltas | Upload do DP | UP-000000049 | 01/10/2026 09:30 | v3 |
| Relato | Registro da supervisão | RL-000000087 | 02/10/2026 16:20 | — |

Template do documento: Dossiê de Conduta v1.0. Hash do documento: impresso por extenso nesta página.

No documento real, o nome do sistema de origem aparece nesta tabela.

## 4.4 Versão para perfis sem acesso ao contexto de acompanhamento

A seção 6 (Contexto de acompanhamento) só é impressa para perfis autorizados. Para os demais, o documento sai sem essa seção. Premissa adotada (**P-18**): cada emissão gera duas renderizações do mesmo documento, **completa** e **sem contexto**, com o mesmo número e versão, cada uma com o próprio hash gravado em `relatorios`. O sistema entrega a renderização de acordo com o perfil de quem baixa.

## 4.5 Excel, aba a aba

Arquivo: `RP-2026-000123_v1.xlsx`. Mesmo número do PDF e mesma consulta de origem, para os dois baterem número a número.

Formatação geral: cabeçalho congelado, filtros ativos, datas em `dd/mm/aaaa`, horas em `hh:mm`, percentuais em formato percentual, **sem células mescladas nas abas de dados**, aba Capa protegida.

| Nº | Aba | Colunas | Conteúdo no caso fictício |
|----|-----|---------|---------------------------|
| 1 | **Capa** (protegida) | Campo · Valor | Nº, versão, tipo, classificação, emissão, emissor, aprovador, área solicitante, colaboradora, matrícula, período, relato, código de verificação, versão do template, versão dos parâmetros |
| 2 | **Síntese** | Nº · Ponto do relato · Conclusão · Indicador-chave · Aba de referência | 3 linhas, iguais ao quadro da página 2 do PDF |
| 3 | **Jornada** | Data · Dia da semana · Situação do dia · Escala início · Escala fim · Primeiro check-in · Último check-out · Atraso (min) · Saída antecipada (min) · Check-out automático (S/N) · Intervalo registrado (S/N) · ID da visita | 30 linhas (uma por dia do período); 6 saídas antecipadas, 3 atrasos, 3 check-outs automáticos, 4 dias sem intervalo registrado |
| 4 | **Pesquisas** | Semana · Data programada · Loja · Cliente · Tipo de serviço · Situação · Data da resposta · Dia trabalhado (S/N) · ID da pesquisa | 168 linhas; 139 respondidas, 29 expiradas |
| 5 | **Aderência** | Semana · Loja · Visitas previstas · Visitas realizadas · Aderência · Meta | 5 linhas (Loja Fictícia 01); total 38 de 44 = 86,4% |
| 6 | **Fotos** | ID da foto · Data · Hora · Loja · Pesquisa · Motivo do indício · Distância até a loja (m) · Score (quando IA) · Situação da conferência · Link para a imagem | 3 linhas |
| 7 | **Ruptura x Estoque** | Data · Loja · Marca · Item · Resposta na pesquisa · Estoque no relatório do cliente · Situação · ID da resposta · ID do upload | 9 linhas; 5 divergentes, 2 coerentes, 2 sem dados |
| 8 | **Faltas e Afastamentos** | Data início · Data fim · Tipo · Justificada (S/N) · ID do registro | 1 linha (18/09/2026). Sem coluna de motivo |
| 9 | **Humor** (só perfis autorizados) | Data · Registro (S/N) · Pontuação · Negativo (S/N) · Alerta | 24 linhas; adesão 91,7%; índice 71,6. Para perfis não autorizados, a aba não existe no arquivo |
| 10 | **Rastreabilidade** | Aba · Indicador · ID do registro · Fonte · Data de extração · ID do lote | Uma linha por registro usado no documento |
| 11 | **Parâmetros** | Parâmetro · Valor aplicado · Versão · Vigência desde | Tolerância 15 min, corte de aderência 93%, distância de foto 300 m, pesos 40/40/20, corte de desempenho 85 etc. |

Regras do Excel:

- Os totais do PDF são conferidos contra as abas antes da emissão. Diferença bloqueia a emissão.
- A aba Humor é removida do arquivo para perfis não autorizados; não é apenas ocultada.
- O link da aba Fotos aponta para a imagem dentro do sistema e exige login e permissão.
- Cada download fica registrado na auditoria.

## 4.6 Diferenças dos outros tipos de relatório

| Tipo | Diferenças em relação ao Dossiê de Conduta |
|------|--------------------------------------------|
| Relatório de Acompanhamento (Cuidado) | Só RH e supervisão. Traz humor, alertas, conversas de cuidado e planos de ação. Não traz ocorrências de conduta nem conclusão sobre relato de conduta |
| Relatório de Jornada (DP/Compliance) | Só jornada, faltas, atestados e afastamentos. Sem humor, sem fotos de execução |
| Relatório Executivo (agregado) | Por equipe ou regional. Só dados agregados: matriz, rankings, tendências. Sem dado individual de humor |

O relato a apurar, a numeração, o fluxo de aprovação, o rodapé e a rastreabilidade valem para todos os tipos.
