# Relatório de Impacto à Proteção de Dados Pessoais — RIPD (rascunho)

> **Rascunho técnico para o DPO.** Estrutura alinhada ao art. 38 da LGPD e ao modelo da ANPD. Base legal, prazos e decisões de visibilidade são **propostas** (Q-08, Q-09, Q-10) e precisam da assinatura do DPO, do RH e do Jurídico antes do piloto.

## 1. Identificação

- **Controladora:** RT (empregadora dos colaboradores de campo).
- **Operadores:** hospedagem/infraestrutura (a contratar), plataforma de monitoramento de campo (origem dos dados), provedor de SSO (Q-06). Todos com cláusula de proteção de dados.
- **Encarregado (DPO):** a indicar.
- **Sistema:** Radar Promotor (RT Intelligence).

## 2. Necessidade do RIPD

Tratamento de dado sensível (saúde: humor "Doente"), monitoramento sistemático de empregados (jornada, GPS, fotos), pontuação de risco e documento que pode embasar medida trabalhista. É alto risco.

## 3. Descrição do tratamento

- **Natureza:** coleta automática diária de exports da plataforma de monitoramento e uploads do DP; normalização; regras determinísticas de indícios; painel; dossiê formal.
- **Escopo:** centenas de colaboradores de campo, nacional; histórico de até 5 anos (proposta).
- **Contexto:** relação de emprego (assimetria de poder). O titular não escolhe participar da operação; o humor é respondido na abertura de jornada.
- **Finalidade única:** gestão operacional, acompanhamento e cuidado da equipe de campo e apuração de indícios (CLAUDE.md §2.1). Proibido ranking público, marketing ou outra finalidade.
- Mapa completo: `01-mapa-de-dados.md`.

## 4. Base legal proposta (decisão: DPO, RH, Jurídico — Q-10)

| Tratamento | Base proposta | Observação |
|-----------|---------------|-----------|
| Cadastro, jornada, visitas | Art. 7º, II (obrigação legal: controle de jornada) e V (execução do contrato de trabalho) | Aplicação a PJ depende do Jurídico (Q-11) |
| Pesquisas, aderência, fotos, GPS (indícios) | Art. 7º, IX (legítimo interesse) | Exige teste de balanceamento (seção 6) e transparência (aviso) |
| Dossiê | Art. 7º, VI (exercício regular de direitos em processo) e IX | Apresenta indícios; decisão é humana (DP e Compliance) |
| Humor (exceto "Doente") | Art. 7º, IX, só para cuidado | Nunca fundamenta medida (§4.4) |
| Humor "Doente" | Art. 11, II, "a" (obrigação legal/regulatória — saúde e segurança do trabalho) **ou** não coletar | **Recomendação desta sessão:** não carregar a opção "Doente" no sistema até a decisão; avaliar trocar por "Alerta de cuidado" sem a opção específica. Consentimento (art. 11, I) é frágil na relação de emprego |
| Auditoria | Art. 7º, II e IX; art. 37 | Prestação de contas |

## 5. Partes envolvidas e consulta

DPO, RH, DP, Compliance, Jurídico, P&P, TI. **Recomendação:** ouvir uma amostra de supervisores e promotores sobre o aviso antes do piloto (aceitação do humor, ponto de atenção 7.3.1).

## 6. Necessidade e proporcionalidade

- **Mínimo necessário:** só as colunas dos `schemas/`; descarte do resto na ingestão; GPS reduzido à distância depois de 12 meses (proposta).
- **Exatidão:** cadastro desatualizado gera falso indício (ponto 7.3.6). Mitigação: fonte oficial definida (Q-17), conferência humana antes de dossiê.
- **Teste de legítimo interesse:** finalidade legítima (integridade da operação e cuidado com a equipe); necessidade (sem alternativa menos invasiva para verificar execução em campo); balanceamento: indícios nunca são conclusão, decisão humana, contraditório pelos canais do RH, humor sem uso punitivo, acesso restrito por escopo.
- **Decisão automatizada (art. 20):** nível e risco são **priorização**, não decisão. Nenhuma medida é aplicada pelo sistema. O titular pode pedir revisão por pessoa natural.
- **Transparência:** aviso aos colaboradores (`06-aviso-colaboradores.md`) antes do piloto.

## 7. Riscos aos titulares

| # | Risco | Prob. | Impacto | Nível |
|---|-------|-------|---------|-------|
| T1 | Vazamento de CPF, GPS, fotos ou humor (repositório público, protótipo em artefato, falha de acesso) | Média | Alto | **Alto** |
| T2 | Uso do humor/saúde para punir ou discriminar | Média | Alto | **Alto** |
| T3 | Medida trabalhista com base em indício falso (cadastro errado, GPS impreciso) | Média | Alto | **Alto** |
| T4 | Acesso além do necessário (supervisor vendo outra equipe, perfil vendo "Doente") | Média | Médio | Médio |
| T5 | Monitoramento excessivo e efeito inibidor (vigilância contínua por GPS) | Média | Médio | Médio |
| T6 | Retenção além do prazo | Alta | Baixo | Médio |
| T7 | Transferência internacional sem salvaguarda (nuvem, IA de fotos — Q-20) | Baixa | Médio | Baixo |
| T8 | **Risco aceito pelo dono (24/11/2026):** o protótipo `radar_v3` mostra **nome** de quem marcou humor "Doente" e de quem teve atestado médico (detalhe de Humor e de Ausências), contra a regra provisória do `CLAUDE.md` §2.1 | Alta | Alto | **Alto** |

## 8. Medidas de mitigação

| Risco | Medidas (técnicas e organizacionais) | Status |
|-------|--------------------------------------|--------|
| T1 | Repositório privado; nenhum dado real no git (CI varre CPF e segredos); TLS 1.2+; criptografia em repouso (banco, backup, fotos); segredos em cofre; sessão segura; plano de incidentes | CI ativo (PR #15); repositório ainda público |
| T2 | Humor fora de qualquer texto acusatório (§4.4, Revisor bloqueia); "Doente" só RH; agregados ≥ 5 pessoas; aviso explícito de não uso punitivo | Regras no motor e matriz; "Doente" pendente de Q-10 |
| T3 | Linguagem de indício; conferência humana de fotos; decisão de DP/Compliance; parâmetros versionados e reproduzíveis; contraditório | Previsto (§5, §4.7) |
| T4 | RBAC + escopo no servidor; CPF mascarado em listas; auditoria de toda leitura individual; revisão periódica de acessos | Base da API em revisão (PR #14) |
| T5 | Uso do GPS só pontual (foto e check-in), sem rastreamento contínuo; redução à distância após 12 meses | Proposta |
| T6 | Política de retenção com descarte automático registrado | `04-politica-retencao.md` (proposta) |
| T7 | Hospedagem no Brasil preferencial; cláusulas-padrão se houver transferência; IA só após Q-20 | Pendente |
| T8 | Página do protótipo compartilhada só com o grupo restrito da matriz; sem texto livre do motivo da ausência na tela (pode conter CID ou diagnóstico); dado da planilha sempre escapado no HTML; registrar a operação no `03-registro-operacoes.md`; reavaliar quando o DPO decidir Q-08/Q-10. No sistema web continua valendo a matriz de permissões (`ver_doente`) | **Aceito pelo dono, pendente do DPO** |

## 9. Risco residual e parecer

Com as medidas implementadas, o risco residual estimado é **médio**, condicionado a: (a) repositório privado antes de qualquer dado real; (b) decisão de Q-10 sobre "Doente"; (c) aviso aos colaboradores entregue antes do piloto; (d) remoção dos dados reais do protótipo no artefato; (e) parecer do DPO sobre o risco T8, aceito pelo dono em 24/11/2026 (nomes visíveis em "Doente" e atestado médico no protótipo).

**Parecer do DPO:** _pendente_ · **Aprovação RH/Jurídico:** _pendente_ · **Revisão:** a cada mudança relevante ou anualmente.
