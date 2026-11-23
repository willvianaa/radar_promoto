# Mapa de dados pessoais (rascunho)

> **Rascunho para o DPO, RH e Jurídico.** Os perfis seguem `docs/05-matriz-permissoes.md`. Retenção e base legal são **propostas** e só valem depois da decisão das áreas (Q-09 retenção, Q-10 base legal, Q-08 visibilidade). Nenhum dado real aparece neste documento.

Titulares: promotores e supervisores de campo (colaboradores CLT e, a confirmar, PJ — Q-11) e usuários internos do sistema.

## 1. Dados de colaboradores

| Dado | Origem | Onde fica | Finalidade | Quem vê (servidor aplica) | Retenção proposta |
|------|--------|-----------|-----------|---------------------------|-------------------|
| Nome | Cadastro (export) | `core.colaborador` | Identificar o titular em telas e dossiê | Todos os perfis no seu escopo; Diretoria só agregado | Vínculo + 5 anos |
| CPF | Cadastro e demais exports | `core.colaborador.cpf` (chave) e chaves estrangeiras | Chave única do colaborador (CLAUDE.md §3) | **Mascarado** em listas para todos. Completo no Raio-X e no dossiê só para RH, DP, Compliance e P&P (provisório, Q-08) | Vínculo + 5 anos |
| UF, cidade, regional, supervisor | Cadastro | `core.colaborador` | Escopo de acesso e agregações | Conforme escopo | Vínculo + 5 anos |
| Jornada cadastrada | Cadastro | `core.colaborador` | Calcular atraso e saída (CLAUDE.md §4.1) | RH, DP, Compliance, P&P, Gerência (regional), Supervisor (equipe) | Vínculo + 5 anos |
| Visitas (check-in/out, PDV) | Operação | `core.visita` | Jornada, aderência, indícios | Idem jornada | 5 anos |
| Atividades/pesquisas | Atividades | `core.atividade` | Execução, aderência | RH, Compliance, P&P, Merch/TD, Gerência, Supervisor | 2 anos |
| Aderência 2PRT | Aderência | `core.aderencia` | KPI de aderência e sobrecarga | Idem pesquisas | 2 anos |
| PDOH (produtivo, deslocamento, ócio) | PDOH | `core.pdoh` | Contexto de carga | Idem pesquisas | 2 anos |
| **Posição GPS** (foto e visita) | Fotos/operação | `core.foto.lat/lon` | Indício de foto fora da loja e fuga de rota (§4.6) | RH, Compliance, P&P, Merch/TD, Gerência, Supervisor | **12 meses**; depois só a distância calculada |
| **Fotos** | Plataforma de monitoramento | Storage criptografado (`caminho_storage`) + hash/pHash | Indícios de foto repetida, fora de horário ou de local | Idem GPS; link exige login | **12 meses**, salvo foto citada em dossiê emitido (segue o dossiê) |
| Faltas (tipo) | Faltas (upload DP) | `core.falta` | Presença, faltas injustificadas | RH, DP, Compliance; demais sem motivo | 5 anos |
| Motivo da falta / atestado | Faltas | `core.falta.motivo` (restrita) | Gestão de pessoal | **Só RH e DP** | 5 anos (legislação trabalhista; confirmar com DP) |
| **Humor** (opção diária) | Pesquisa de humor | `core.humor` (view por perfil) | Cuidado e acompanhamento, **nunca medida** (§4.4) | Detalhe: RH e Supervisor (equipe); "Alerta de cuidado": Gerência e P&P; Diretoria só agregado ≥ 5 pessoas | **12 meses** |
| **Humor "Doente"** (saúde, art. 11) | Pesquisa de humor | `core.humor` | Cuidado | **Só RH**; demais veem "Alerta de cuidado". Fora de uso real até Q-10 | **6 meses** |
| Indicadores, alertas, nível, risco | Calculados | `app.indicador_colaborador`, `app.alerta` | Priorizar acompanhamento | Conforme matriz | 2 anos (recalculáveis) |
| Dossiê (PDF/XLSX, conteúdo) | Emitido | `app.dossie` + storage | Apurar indícios (decisão é de DP/Compliance) | Matriz 5.2/5.3 | 5 anos após a emissão, ou o fim do processo relacionado, se for maior |

## 2. Dados de usuários internos

| Dado | Onde fica | Finalidade | Retenção proposta |
|------|-----------|-----------|-------------------|
| E-mail, nome, perfil, escopo | `app.usuario` | Autenticação e autorização | Enquanto ativo + 1 ano |
| Hash de senha (argon2) até o SSO | `app.usuario.senha_hash` | Login | Apagar ao migrar para SSO ou ao desligar |
| Trilha de auditoria (usuário, ação, recurso, IP) | `app.auditoria` (append-only) | Rastreabilidade e prestação de contas (art. 37) | 5 anos |

## 3. O que **não** é coletado

Tudo o que não está nos `schemas/` é descartado na ingestão (mínimo necessário). Não há coleta de endereço residencial, telefone, dados bancários, biometria, raça, religião ou outro dado sensível além do humor "Doente".

## 4. Fluxo resumido

Origens (exports e uploads) → `raw` (imutável, retenção curta proposta: **90 dias**) → `core` (normalizado) → `app` (cálculos, dossiês, auditoria) → telas e documentos filtrados por perfil.
