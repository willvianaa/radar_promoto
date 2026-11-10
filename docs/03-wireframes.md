# 3. Wireframes

Wireframes de baixa fidelidade das três telas principais. Mostram conteúdo e organização, não o visual final. Todos os nomes e números são fictícios.

O que cada perfil vê em cada tela está em [05-matriz-permissoes.md](05-matriz-permissoes.md). Blocos de humor individual só aparecem para perfis autorizados.

## 3.1 Painel Geral

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ 2P RT  ›  RADAR PROMOTOR                                    Usuário: Ana Exemplo (P&P) ▾ │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ Visão:   [ CUIDAR ]   [■ AMBOS ■]   [ CORRIGIR ]                                         │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ Colaborador [nome ou matrícula    ]  Supervisor [▾]  Gerência [▾]  Regional [▾]  UF [▾]  │
│ Loja [▾]   Cliente/Marca [▾]   Período [01/09/2026] a [30/09/2026]   [Aplicar] [Limpar]  │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐              │
│ │ Índice de Humor│ │ Adesão         │ │ Dias Negativos │ │ Alertas Abertos│              │
│ │      68        │ │     88,4%      │ │     17,2%      │ │       23       │              │
│ │ ▼ 3 pts        │ │ ▲ 1,1 p.p.     │ │ ▲ 2,0 p.p.     │ │ ▲ 4            │              │
│ └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘              │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐              │
│ │ SLA Supervisor │ │ Aderência      │ │ Fotos Suspeitas│ │ Pesq. Expiradas│              │
│ │  1,6 dia útil  │ │     91,3%      │ │       41       │ │      312       │              │
│ │ ▼ 0,3          │ │ ▼ 0,8 p.p.     │ │ ▲ 6            │ │ ▲ 28           │              │
│ └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘              │
│   (tendência = comparação com o período anterior de mesma duração)                       │
├───────────────────────────────────────────────┬──────────────────────────────────────────┤
│ MATRIZ HUMOR × DESEMPENHO                     │ ALERTAS                    [Todos ▾]     │
│                                               │                                          │
│  Humor                                        │ Colaborador      Tipo        Etapa       │
│  ok    ┌──────────────┬──────────────┐        │ Humor (10 dias)              Dias aberto │
│        │ AZUL     38  │ VERDE   214  │        │ ──────────────────────────────────────── │
│        │ orientação   │ destaque     │        │ Joana M. Pereira Jornada     Aberto      │
│        ├──────────────┼──────────────┤        │ ●●●○●●●●●●                   1           │
│  em    │ VERMELHO 12  │ AMARELO  19  │        │ Pedro F. Lima    Cuidado     Conv. agend.│
│ alerta │ cuidado      │ esgotamento  │        │ ●●○○○●○○○●                   2           │
│        └──────────────┴──────────────┘        │ Rita E. Santos   Adesão      Aberto      │
│          baixo           alto   Desempenho    │ ●–––––●––●                   6           │
│                                               │ ...                                      │
│  CINZA (adesão < 85%): 27                     │ ● ok  ○ negativo  – sem registro         │
│  Clique num quadrante para listar as pessoas. │                         [Ver todos ›]    │
├───────────────────────────────────────────────┴──────────────────────────────────────────┤
│ RANKING     [■ Supervisor ■]  [ Loja ]  [ Regional ]                                     │
│                                                                                          │
│ Supervisor         Equipe  Humor  Adesão  Aderência  Pesq. resp.  Alertas  SLA           │
│ Carlos E. Souza      14     71    91,7%    89,9%       82,7%        3      1,0           │
│ Marta F. Rocha       11     64    86,0%    93,4%       90,1%        5      2,5           │
│ ...                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Comportamento:

- **Seletor de visão.** `CUIDAR` mostra só cards e listas de humor e cuidado. `CORRIGIR` mostra só os operacionais. `AMBOS` mostra tudo. O seletor só oferece as visões que o perfil pode ver.
- **Filtros globais.** Valem para todos os blocos da tela. Gerência regional e supervisor já entram com a própria regional ou equipe travada no filtro.
- **Cards.** Clicar num card abre a lista de colaboradores que compõem o número.
- **Matriz.** Clicar num quadrante filtra a lista de alertas e o ranking.
- **Fita de humor.** Para perfis sem acesso ao humor individual, a fita não aparece. O alerta mostra só "alerta de cuidado".
- **Ranking.** Agregado por supervisor, loja e regional. Não existe ranking individual de humor.

## 3.2 Ficha do Colaborador

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ ‹ Voltar ao painel                                             [ Emitir relatório ]      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ JOANA MODELO PEREIRA (fictícia)                    Matrícula 900001  ·  CLT              │
│ Promotora de Vendas · Regional Nordeste 1 · BA     Supervisor: Carlos Exemplo Souza      │
│ Escala: seg a sáb, 07:00–15:20, intervalo 12:00–13:00                                    │
│ Lojas: Loja Fictícia 01 · Loja Fictícia 02         Clientes: Marca A · Marca B           │
│ Período: [01/09/2026] a [30/09/2026]               Quadrante: AZUL                       │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ [■ Resumo ■] [ Jornada ] [ Pesquisas ] [ Aderência ] [ Humor ] [ Faltas ] [ Fotos ]      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ RESUMO                                                                                   │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│ │ Dias trab.   │ │ Pesq. resp.  │ │ Aderência    │ │ Conf. jornada│ │ Desempenho   │     │
│ │ 24 de 25     │ │ 82,7%        │ │ 89,1%        │ │ 62,5%        │ │ 81,2         │     │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │
│                                                                                          │
│ LINHA DO TEMPO UNIFICADA (ocorrências + humor)                                           │
│                                                                                          │
│  01/09 ter  ● Bem                                                                        │
│  03/09 qui  ● Bem       ▲ Atraso: check-in às 07:41                                      │
│  10/09 qui  ● Neutro    ◆ Foto com indício de duplicidade (Loja Fictícia 01)             │
│  12/09 sáb  ● Bem       ▲ Saída antecipada: check-out às 13:58                           │
│  18/09 sex  –           ■ Falta justificada                                              │
│  22/09 ter  ○ Cansado   ▲ Check-out automático · almoço sem registro                     │
│  ...                                                                                     │
│  ● humor ok  ○ humor negativo  – sem registro  ▲ jornada  ◆ foto  ■ falta                │
│                                                                                          │
│ GALERIA DE FOTOS SUSPEITAS                                                               │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                                                   │
│ │  [foto]  │ │  [foto]  │ │  [foto]  │   Cada foto: data, hora, loja, pesquisa,          │
│ │ 10/09    │ │ 17/09    │ │ 24/09    │   GPS da captura, distância até a loja,           │
│ │ Duplicada│ │ Duplicada│ │ Fora PDV │   motivo do indício e ID do registro.             │
│ └──────────┘ └──────────┘ └──────────┘   [Conferido] [Descartar indício]                 │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Conteúdo das abas:

| Aba | Conteúdo |
|-----|----------|
| Resumo | Cards do período, linha do tempo unificada e galeria de fotos suspeitas |
| Jornada | Tabela dia a dia: escala, check-in, check-out, atraso, saída antecipada, check-out automático, almoço, PDOH, tempo ocioso |
| Pesquisas | Programadas x respondidas x expiradas por semana, cliente, loja e tipo de serviço |
| Aderência | Aderência por loja e semana, com a meta de 93%, e aderência de rota (manhã x tarde) |
| Humor | Fita de humor, Índice, adesão, sequência negativa, queda brusca, alertas e conversas de cuidado. **Só perfis autorizados** |
| Faltas | Faltas, faltas justificadas, atestados e afastamentos. Motivo visível só para DP e RH |
| Fotos | Todos os indícios de foto, com metadados e situação da conferência |

Comportamento:

- Cada número é um link para os registros que o compõem (ID, fonte e data de extração).
- "Descartar indício" exige justificativa e fica na auditoria. O indício descartado não entra em documento.
- Para perfis sem acesso ao humor, a aba Humor não existe, a linha do tempo mostra só ocorrências e o quadrante não é exibido.

## 3.3 Emissão de relatório

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ EMITIR RELATÓRIO                                              Etapa 1 de 3: Parâmetros   │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│ a) Tipo de relatório                                                                     │
│    (●) Dossiê de Conduta                                                                 │
│    ( ) Relatório de Acompanhamento (Cuidado)                                             │
│    ( ) Relatório de Jornada (DP/Compliance)                                              │
│    ( ) Relatório Executivo (agregado)                                                    │
│                                                                                          │
│ b) Colaborador  [900001 – Joana Modelo Pereira       ]   Área solicitante [P&P ▾]        │
│    Período      [01/09/2026] a [30/09/2026]                                              │
│    (no Relatório Executivo: Equipe / Regional no lugar do colaborador)                   │
│                                                                                          │
│ c) RELATO A APURAR  (obrigatório)                                                        │
│    ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│    │ Supervisão relata saídas antes do horário, ruptura informada sem fundamento na   │  │
│    │ Loja Fictícia 01 e pesquisas não respondidas na última semana do mês.            │  │
│    └──────────────────────────────────────────────────────────────────────────────────┘  │
│    Origem do relato [Supervisão ▾]     Data do relato [02/10/2026]                       │
│                                                                                          │
│ ┌──────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ⚠ EMISSÃO BLOQUEADA (aparece só no quadrante VERMELHO)                               │ │
│ │ É necessário registrar a Conversa de Cuidado antes de emitir o Dossiê de Conduta.    │ │
│ │ [Ir para o alerta de cuidado]                                                        │ │
│ └──────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                              [Cancelar]  [Gerar rascunho]│
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ EMITIR RELATÓRIO                                              Etapa 2 de 3: Rascunho     │
│ RP-2026-000123 · v1 · RASCUNHO                                                           │
├───────────────────────────────────────────────┬──────────────────────────────────────────┤
│ PONTOS DO RELATO                              │ PRÉ-VISUALIZAÇÃO DO TEXTO (editável)     │
│                                               │                                          │
│ 1. Saídas antes do horário                    │ 1. Saídas antes do horário previsto      │
│    Conclusão [CONFIRMADO ▾]                   │ ┌──────────────────────────────────────┐ │
│    Indicador: 6 de 24 dias                    │ │ Os registros indicam check-out       │ │
│    [ver registros]                            │ │ anterior ao horário previsto em 6    │ │
│                                               │ │ dos 24 dias trabalhados...           │ │
│ 2. Ruptura sem fundamento – Loja Fictícia 01  │ └──────────────────────────────────────┘ │
│    Conclusão [PARCIALMENTE CONFIRMADO ▾]      │ [tabela] [gráfico]                       │
│    Indicador: 5 de 9 itens                    │                                          │
│                                               │ 2. Ruptura informada x estoque           │
│ 3. Pesquisas não respondidas – última semana  │ ...                                      │
│    Conclusão [CONFIRMADO ▾]                   │                                          │
│    Indicador: 15 de 42 expiradas              │ Blocos de achados: 3 de 5                │
│                                               │                                          │
│ OUTRAS OCORRÊNCIAS IDENTIFICADAS              │ REVISÃO AUTOMÁTICA                       │
│ [x] Fotos com indício de duplicidade (2)      │ ✔ Sem termos acusatórios                 │
│ [x] Almoço sem registro (4 dias)              │ ✔ Sem nomes de sistemas                  │
│ [ ] Atrasos (3 dias)                          │ ✔ Números conferem com a base            │
├───────────────────────────────────────────────┴──────────────────────────────────────────┤
│ [Salvar rascunho]   [Baixar prévia com marca RASCUNHO]            [Enviar para revisão ›]│
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ EMITIR RELATÓRIO                                              Etapa 3 de 3: Fluxo        │
│ RP-2026-000123 · v1                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────────┤
│  Rascunho ──► Em revisão ──► Aprovado ──► Emitido ──► Ciência registrada ──► Arquivado   │
│  Ana E.       Bruno E.       (pendente)                                                  │
│  05/10 09:12  05/10 14:30                                                                │
│                                                                                          │
│  Comentários da revisão: [                                                     ]         │
│                                                                                          │
│                          [Devolver ao rascunho]   [Aprovar]   [Emitir PDF e Excel]       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

Comportamento:

- **Relato a apurar.** Campo obrigatório. O relato é transcrito no documento como foi registrado.
- **Pontos do relato.** O sistema divide o relato em pontos e propõe a conclusão de cada um. O revisor pode alterar a conclusão; a alteração exige justificativa e fica na auditoria.
- **Texto pré-gerado.** Editável até a emissão. Os números dentro do texto são campos ligados à base e não podem ser digitados à mão.
- **Revisão automática.** Roda a cada edição. Qualquer item reprovado bloqueia o envio para revisão.
- **Limite de blocos.** No máximo 5 blocos de achados. Ocorrências correlacionadas são unidas.
- **Trava do quadrante VERMELHO.** O aviso aparece na etapa 1 e o botão de aprovação fica desabilitado até o registro da Conversa de Cuidado.
- **Emissão.** Gera PDF e Excel com o mesmo número, calcula o hash e torna o documento imutável. Qualquer mudança posterior cria a versão seguinte (`v2`).
- **Segregação de funções.** Quem gerou o rascunho não pode aprovar o próprio documento.
- **Relatório de Acompanhamento (Cuidado).** Só RH e supervisão da própria equipe podem gerar. Não traz ocorrências de conduta.
