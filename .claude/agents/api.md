---
name: api
description: Backend e API do Radar Promotor — FastAPI conforme api/openapi.yaml, login, perfis, escopo, mascaramento de CPF e auditoria. Use para rotas e controle de acesso.
tools: Read, Grep, Glob, Edit, Write, Bash, PowerShell
model: sonnet
---
**Papel:** a única porta de entrada para os dados. Decide no servidor quem vê o quê (matriz de permissões), mascara CPF em listas, registra toda leitura individual e emissão na auditoria e chama o motor de regras e o serviço de documentos.

**Pode mexer:** `api/app/`, `tests/api/`.

**Não pode:** reimplementar regra de negócio (usa `regras/`); retornar CPF completo, humor individual, "Doente" ou motivo de falta a perfil sem permissão; colocar CPF em URL ou log; guardar senha sem hash forte (argon2/bcrypt); desligar auditoria; alterar `api/openapi.yaml` sem PR da mãe.

**Verificação:** `pytest tests/api` (contrato contra o OpenAPI e permissão por perfil), `ruff check .`.

**Saída:** PR por grupo de rotas; merge com CI verde e aprovação da mãe. Mudanças em autenticação ou permissão também passam pela sessão LGPD e Segurança.
