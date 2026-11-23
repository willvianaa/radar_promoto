# Registro das operações de tratamento — art. 37 (rascunho)

> Rascunho para o DPO manter atualizado. Bases legais e prazos são **propostas** (Q-09, Q-10).

| # | Operação | Dados | Titulares | Base legal proposta | Sistema / local | Operador | Compartilhamento | Retenção proposta | Medidas |
|---|---------|-------|-----------|--------------------|-----------------|----------|------------------|-------------------|---------|
| OP-01 | Ingestão diária de exports | Cadastro, operação, atividades, humor, fotos, aderência, PDOH | Colaboradores de campo | Art. 7º II, V, IX; art. 11 II "a" (a decidir) | Ingestor → `raw` | Hospedagem; plataforma de monitoramento (origem) | Nenhum | `raw`: 90 dias | Usuário de serviço; sem contornar captcha/2FA; descarte de colunas fora do schema; SHA-256 da carga |
| OP-02 | Upload de faltas/atestados | Tipo e motivo da falta | Colaboradores | Art. 7º II, V; art. 11 II "a" se houver CID | API → `raw`/`core` | Hospedagem | Nenhum | 5 anos | Só perfil DP; validação contra schema; motivo restrito a RH/DP |
| OP-03 | Normalização e cálculo de indícios | Todos os de OP-01/02 | Colaboradores | Idem OP-01 | Motor de regras (`core`, `app`) | Hospedagem | Nenhum | Indicadores: 2 anos | Regras determinísticas e versionadas |
| OP-04 | Consulta em painel e Raio-X | Conforme perfil | Colaboradores | Art. 7º IX | API/front | Hospedagem | Interno, por perfil | — | RBAC + escopo no servidor; CPF mascarado em listas; auditoria de leitura individual |
| OP-05 | Emissão de dossiê | Indícios, identificação, contexto (perfis autorizados) | Colaboradores | Art. 7º VI, IX | Gerador de documentos + storage | Hospedagem | DP/Compliance; fora da empresa só por decisão das áreas | 5 anos após emissão | Numeração RP, hash, marca CONFIDENCIAL, marca d'água, revisão de linguagem |
| OP-06 | Autenticação e autorização | E-mail, nome, perfil, hash de senha | Usuários internos | Art. 7º V, IX | API | Hospedagem; SSO (Q-06) | Nenhum | Ativo + 1 ano | argon2; cookie seguro; bloqueio de tentativas |
| OP-07 | Trilha de auditoria | Usuário, ação, recurso (id opaco), IP | Usuários internos | Art. 7º II, IX; art. 37 | `app.auditoria` | Hospedagem | Compliance | 5 anos | Append-only (trigger), sem CPF/humor/motivo |
| OP-08 | Backups | Cópia do banco e do storage | Todos | Idem origem | Backup criptografado | Hospedagem | Nenhum | 35 dias rotativos | Criptografia em repouso; teste de restauração |
| OP-09 | **Protótipo no artefato do claude.ai** (transitório) | Bases carregadas (CPF, nome, humor, operação) | Colaboradores | Nenhuma formalizada | Banco do artefato (terceiro, fora do Brasil) | Anthropic (plataforma) | Quem abre o artefato | **Encerrar já** | Apagar as bases e não carregar dado real; avaliar art. 33 com o DPO |
