# Briefing — Design/Front (Sonnet · `feat/front` · onda 3)

## A ideia
Manter a experiência que o escritório já aprovou no protótipo (logo de radar, Radar da operação, alertas em gráficos, Raio-X, dossiê editável) agora alimentada pela API, com login e funcionando bem no celular. O usuário não deve sentir que "trocou de sistema".

## Entrega
- 4 abas: **Visão Geral** (hero, Radar da operação por UF/supervisor, prioridade Crítico/Alto/Atenção, KPIs, gráficos de aderência, pesquisas, humor agregado, dia da semana, ranking), **Alertas** (caixas de prioridade, cards por tipo, alertas por dia, feed), **Raio-X** (identificação com CPF conforme perfil, 7 dimensões, alertas, carga de trabalho com PDOH, calendário, assinatura de jornada, fotos), **Dossiê** (folha editável, avisos de revisão, emitir).
- Filtros: UF, Supervisor, data início/fim, Ano, promotor por nome ou CPF.
- Identidade do Monitor Regional / RT, responsivo, tema claro e escuro.

## Não faz
Não acessa banco nem calcula regra; tudo vem da API.

## Encaixe
Consome o Backend; o botão Emitir chama a API que aciona Documentos.

## Pronto quando
Paridade visual com o protótipo v3 aprovada pelo dono; acessibilidade ≥ 90 no Lighthouse; funciona em 375 px.

## Riscos
Volume do radar com centenas de pontos (já resolvido no protótipo com fatias e pontos pequenos); textos de tela devem seguir o padrão "indícios".
