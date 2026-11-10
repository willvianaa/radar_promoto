# 7. Perguntas em aberto e premissas adotadas

Quando faltou informação, foi registrada uma premissa em vez de um dado inventado. As premissas valem só até a resposta da área responsável.

## 7.1 Perguntas em aberto

**Bloqueante** = precisa de resposta antes do início do MVP (Fase 1).

| Código | Pergunta | Quem responde | Bloqueante? |
|--------|----------|---------------|-------------|
| Q-01 | Qual é a stack do 2P RT (linguagem, banco de dados, front-end, hospedagem, forma de publicar novos módulos)? | TI | Sim |
| Q-02 | Há acesso à API da plataforma de monitoramento? Quais dados ela expõe (humor, fotos com metadados, eventos de Status Day), com quais limites de uso e credenciais? | TI + fornecedor | Não para o MVP (usa arquivos); sim para a Fase 2 |
| Q-03 | Quais são as opções reais da pesquisa de humor na abertura de jornada e a pontuação de cada uma? | RH + P&P | Sim |
| Q-04 | Quais são as tolerâncias e metas oficiais: atraso, saída antecipada, permanência mínima no PDV, tempo ocioso, distância da foto, meta de pesquisas respondidas, meta de alertas no SLA? | P&P | Sim |
| Q-05 | Quais são os pesos do Índice de Desempenho e o corte entre desempenho alto e baixo? | P&P + Diretoria | Sim |
| Q-06 | Qual é o provedor de SSO corporativo e como os perfis serão mapeados (grupos do diretório)? | TI | Sim |
| Q-07 | Quem, no P&P, é o dono nominal dos parâmetros? A alteração exige segunda aprovação? | P&P + Compliance | Não |
| Q-08 | Quais perfis podem ver o humor individual e a seção "Contexto de acompanhamento"? Supervisor e gerência regional veem a opção "Doente" ou só o alerta? Compliance vê a seção de contexto? | RH + DPO | Sim |
| Q-09 | Qual é a política de retenção e descarte por tipo de dado (humor, fotos, jornada, documentos emitidos, auditoria)? | DPO + DP + Compliance | Não para o MVP; sim antes da emissão formal |
| Q-10 | Qual é a base legal LGPD para o tratamento do humor, em especial do dado de saúde? Como e quando os promotores serão avisados? | DPO + RH + Jurídico | Sim |
| Q-11 | As regras de jornada (atraso, saída antecipada, intervalo) se aplicam a promotores PJ? | DP + Jurídico | Sim |
| Q-12 | Qual é a janela de disponibilidade exigida (horário comercial de qual fuso; inclui sábado)? | TI + áreas | Não |
| Q-13 | Em que formato chega o relatório de estoque do cliente/backoffice e com que frequência? O layout varia por cliente? | Merchandising + P&P | Não para o MVP |
| Q-14 | Quais são a tipografia, o logo e o padrão visual corporativos para os documentos? | Marketing / Diretoria | Não |
| Q-15 | O colaborador toma ciência do Dossiê de Conduta dentro do sistema ou só fora dele, pela liderança e pelo RH? | RH + Jurídico | Não para o MVP |
| Q-16 | Qual é a regional piloto e quais promotores entram no piloto? | Diretoria + P&P | Sim |
| Q-17 | Onde está cadastrada a escala de cada promotor hoje, e qual é a fonte oficial em caso de divergência? Há lojas em fuso diferente de `America/Sao_Paulo`? | DP + P&P | Sim |
| Q-18 | Como é definida hoje a aderência de rota (GPS manhã x tarde)? Qual é a fórmula usada no 2P RT? | P&P | Sim |
| Q-19 | Qual é a definição exata de PDOH (horas não registradas)? | P&P | Sim |
| Q-20 | Qual serviço de IA pode ser usado para fotos e texto, e onde os dados podem ser processados (restrições contratuais e de LGPD)? | TI + DPO | Não para o MVP; sim para as Fases 3 e 4 |
| Q-21 | Como é a fórmula da aderência de loja no 2P RT e quem mantém a meta de 93%? | P&P | Sim |
| Q-22 | Os calendários de feriados estaduais e municipais já existem em alguma base? | DP | Sim |

## 7.2 Premissas adotadas

| Código | Premissa | Onde é usada | Depende de |
|--------|----------|--------------|-----------|
| P-01 | A arquitetura é descrita por camada e responsabilidade, sem fixar produto, porque a stack do 2P RT não foi informada | Arquitetura | Q-01 |
| P-02 | Opções e pontos do humor: Feliz 100, Bem 75, Neutro 50, Cansado 25, Sobrecarregado 25, Triste 0, Doente 0 | KPI de Humor | Q-03 |
| P-03 | Registros negativos: Cansado, Sobrecarregado, Triste e Doente | Dias negativos, sequência negativa | Q-03 |
| P-04 | "Humor em alerta" = Índice de Humor do período abaixo de 50, ou sequência negativa ativa, ou queda brusca ativa | Matriz | Q-04 |
| P-05 | Dia trabalhado = dia previsto na escala com pelo menos um check-in, sem falta, atestado ou afastamento | Adesão, jornada | Q-17 |
| P-06 | Tolerância de 15 minutos para atraso e para saída antecipada | Jornada | Q-04 |
| P-07 | "Registros seguidos" = permanência menor que 10 minutos no PDV | Jornada | Q-04 |
| P-08 | Foto "fora do PDV" = captura a mais de 300 m da loja | Fotos | Q-04 |
| P-09 | Foto "duplicada" = distância de Hamming entre pHashes ≤ 5 | Fotos | Q-04 |
| P-10 | Pesos do desempenho: aderência 40%, pesquisas respondidas 40%, conformidade de jornada 20% | Índice de Desempenho | Q-05 |
| P-11 | Desempenho alto = índice ≥ 85; baixo = índice < 85 | Matriz | Q-05 |
| P-12 | Semana de segunda a domingo | Todas as visões semanais | Q-04 |
| P-13 | Dia útil do SLA = segunda a sexta, excluídos feriados nacionais | SLA do supervisor | Q-04 |
| P-14 | Indício de divergência de conteúdo só é exibido com score de confiança ≥ 0,80 | Agente de fotos | Q-04, Q-20 |
| P-15 | Tempo ocioso = intervalo maior que 60 minutos entre PDVs, descontado o almoço | Jornada | Q-04 |
| P-16 | Numeração `RP-AAAA-NNNNNN`, sequencial nacional por ano, comum a todos os tipos de relatório | Documentos | Compliance |
| P-17 | O P&P vê o quadrante da matriz e a situação da trava, mas não o humor dia a dia | Permissões | Q-08 |
| P-18 | Cada emissão gera duas renderizações (completa e sem contexto), com o mesmo número e versão e hashes próprios | Documentos, permissões | Q-08, Compliance |
| P-19 | Queda brusca = média dos últimos 7 dias trabalhados comparada com a média dos 60 dias anteriores | KPI de Humor | Q-04 |
| P-20 | "Almoço sem registro" = dia trabalhado sem check-in no PDV não operacional entre 12h e 13h, para qualquer escala | Jornada | Q-17 |
| P-21 | O quadrante CINZA (adesão < 85%) tem precedência sobre os demais | Matriz | RH + P&P |
| P-22 | A matriz exige no mínimo 10 dias trabalhados no período | Matriz | P&P |
| P-23 | Agregados de humor só são exibidos para grupos de 5 pessoas ou mais | Permissões | Q-08, DPO |
| P-24 | A ciência do colaborador não é colhida dentro do sistema; os campos de ciência do PDF cobrem emissor, aprovador, supervisor e RH | Documentos | Q-15 |
| P-25 | No MVP, os dados chegam por relatórios exportáveis e uploads; a API entra na Fase 2 | Plano de fases | Q-02 |
| P-26 | Fotos sem GPS não geram indício de conduta | Fotos | P&P |
| P-27 | O supervisor não gera Dossiê de Conduta sobre a própria equipe; registra o relato, e o P&P ou o RH gera | Permissões | RH + Compliance |

## 7.3 Pontos de atenção

1. **Humor e adesão.** Se os promotores entenderem que o humor pode ser usado contra eles, a adesão cai e o indicador perde valor. O aviso aos promotores (**Q-10**) e a restrição de acesso (**Q-08**) precisam estar resolvidos antes do piloto.
2. **Dado de saúde.** A opção "Doente" é dado sensível. O tratamento depende da base legal definida com o DPO. Sem essa definição, a opção não deve ser carregada no sistema.
3. **PJ.** Aplicar controle de jornada a prestadores PJ pode ter implicação trabalhista. A regra depende do Jurídico (**Q-11**).
4. **Estoque do cliente.** Estoque positivo em sistema não prova que o produto estava disponível na loja. Por isso o ponto é tratado como indício e a redação pede apuração junto à loja.
5. **IA de fotos.** O score é uma estimativa. Todo indício de divergência de conteúdo exige conferência humana antes de entrar em documento.
6. **Qualidade do cadastro.** Jornada e aderência dependem da escala e do roteiro corretos. Cadastro desatualizado gera falso indício. A fonte oficial precisa ser definida (**Q-17**).
7. **Dados reais fora do repositório.** Este repositório não deve receber dados reais de colaboradores, fotos, planilhas ou credenciais. O `.gitignore` já bloqueia os formatos mais comuns.
