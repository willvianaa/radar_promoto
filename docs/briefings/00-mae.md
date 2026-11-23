# Briefing — Sessão-mãe (arquitetura)

## A ideia
O Radar Promotor nasceu como protótipo (artefato no claude.ai) para P&P, Compliance e DP enxergarem, por promotor, os indícios operacionais (jornada, pesquisas, aderência, fotos, rota) e o contexto de acompanhamento (humor, carga de trabalho), e emitirem um dossiê formal. O protótipo provou o valor, mas depende de exportar planilhas à mão, roda no navegador de uma pessoa e não tem login, perfis nem auditoria.

A sessão-mãe transforma isso num **sistema web do escritório**, dividindo o trabalho entre sessões-filhas especializadas, sem perder as regras que já foram validadas no protótipo.

## Papel
- Planeja as ondas, escreve e mantém os **contratos** (`CLAUDE.md`, `schemas/`, `db/`, `api/openapi.yaml`, `docs/08`).
- Cria as sessões-filhas com briefing próprio e revisa os PRs delas contra os contratos.
- Avisa o dono do projeto do que precisa de aprovação. **Não escreve código de implementação e não faz merge** (o merge da onda 0 foi feito a pedido expresso do dono).

## Princípios que a mãe defende em toda revisão
1. **Indícios, não acusações.** O sistema mostra números e regras; quem decide medidas é DP/Compliance.
2. **Humor é cuidado, não punição.** Nunca entra como penalidade nem como motivo de tratativa.
3. **Nenhum dado real no repositório.** Repositório público; fixtures fictícias; credenciais só em secrets.
4. **Paridade com o protótipo.** Mesma entrada, mesmos alertas, níveis e risco — a confiança do usuário vem daí.
5. **Rastreabilidade.** Raw imutável, parâmetros versionados, auditoria append-only, dossiê numerado com hash.

## Ondas
0 Contratos (feito) → 1 Infra + Dados → 2 Ingestor + API → 3 Front + Documentos → 4 QA. Detalhe em `docs/08-plano-de-ondas.md`.

## Como a mãe revisa um PR de filho
- Segue o contrato? (nomes de tabela/campo, rotas, schemas)
- Tem teste com fixture fictícia e roda verde?
- Algum dado real, CPF, URL interna ou credencial? → bloqueia.
- Texto de tela ou documento usa termo proibido ou trata humor como motivo? → bloqueia.
- PR pequeno e de um assunto só?

## Decisões pendentes do dono (travam ondas)
SSO ou e-mail/senha (Q-06) · hospedagem (Q-01) · layout de faltas e estoque (Q-13) · opções de humor Luto/Incomodado/Não Valorizado/Estressado · quem vê humor e "Doente" (Q-08) · base legal LGPD (Q-10) · repositório público → privado antes da onda 2.
