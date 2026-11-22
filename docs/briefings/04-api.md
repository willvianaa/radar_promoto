# Briefing — Backend/API (Sonnet · `feat/api` · onda 2)

## A ideia
Ser a única porta de entrada para os dados. Hoje qualquer pessoa com o link do protótipo vê tudo; no sistema, **quem pode ver o quê** (matriz de permissões) é decidido no servidor, o CPF sai mascarado nas listas e toda leitura individual e emissão fica registrada.

## Entrega
- FastAPI implementando `api/openapi.yaml` (painel, radar, ranking, alertas, Raio-X, dossiês, parâmetros, ingestão, auditoria).
- Login: e-mail e senha com hash até a decisão de SSO (Q-06); sessão em cookie httpOnly/Secure/SameSite.
- Perfis e escopo (nacional, regional, equipe) conforme `docs/05-matriz-permissoes.md`; humor e "Doente" só para perfis autorizados.
- Auditoria append-only; URLs assinadas e temporárias para fotos.

## Não faz
Não recalcula regra de negócio (chama o motor de Dados); não gera PDF (chama Documentos).

## Encaixe
Lê o que Dados grava; serve o Front; aciona Documentos na emissão.

## Pronto quando
Testes de contrato contra o OpenAPI e testes de permissão por perfil passando.

## Riscos
Matriz de permissões depende de decisões do RH/DPO (Q-08); mudar a API exige PR de contrato na mãe.
