# 5. Matriz de permissões e governança

Controle de acesso por perfil (RBAC). A permissão é aplicada no servidor (API) e vale também para os arquivos exportados. Nenhum cliente externo tem acesso.

Os pontos marcados com **(P-xx)** ou **(Q-xx)** dependem de confirmação. Ver [07-premissas-e-perguntas.md](07-premissas-e-perguntas.md).

## 5.1 Escopo de dados por perfil

| Perfil | Escopo |
|--------|--------|
| Diretoria | Nacional, agregado |
| RH | Nacional |
| DP | Nacional |
| Compliance | Nacional |
| P&P / Monitoramento | Nacional |
| Merchandising e TD | Nacional |
| Gerência / Coordenação Regional | Só a própria regional |
| Supervisor | Só a própria equipe |

## 5.2 O que cada perfil vê

Legenda: **✔** vê · **Agr.** só agregado (sem dado individual) · **Alerta** vê só que existe um alerta de cuidado, sem a opção de humor escolhida · **—** não vê.

| Dado | Diretoria | RH | DP | Compliance | P&P | Merch. / TD | Gerência Regional | Supervisor |
|------|-----------|----|----|-----------|-----|-------------|-------------------|-----------|
| Painel – visão CUIDAR | Agr. | ✔ | — | — | Agr. | Agr. | ✔ (regional) | ✔ (equipe) |
| Painel – visão CORRIGIR | Agr. | ✔ | Jornada e faltas | ✔ | ✔ | ✔ | ✔ (regional) | ✔ (equipe) |
| Matriz Humor × Desempenho | Agr. | ✔ | — | — | ✔ (quadrante) | Agr. | ✔ (regional) | ✔ (equipe) |
| Rankings (supervisor, loja, regional) | ✔ | ✔ | — | — | ✔ | ✔ | ✔ (regional) | Própria equipe |
| Humor individual (dia a dia, fita) | — | ✔ | — | — | — | — | Alerta (**Q-08**) | ✔ (equipe) |
| Opção "Doente" | — | ✔ | — | — | — | — | Alerta | Alerta (**Q-08**) |
| Alertas de cuidado | Agr. | ✔ | — | — | Alerta | Agr. | ✔ (regional) | ✔ (equipe) |
| Conversas de cuidado e plano de ação | — | ✔ | — | — | Só a situação (feita / pendente) | Plano de ação | ✔ (regional) | ✔ (equipe) |
| Jornada (dia a dia) | — | ✔ | ✔ | ✔ | ✔ | — | ✔ (regional) | ✔ (equipe) |
| Faltas, atestados, afastamentos | — | ✔ | ✔ | ✔ | Sem o motivo | — | Sem o motivo | Sem o motivo |
| Motivo da falta / atestado | — | ✔ | ✔ | — | — | — | — | — |
| Pesquisas e aderência | Agr. | ✔ | — | ✔ | ✔ | ✔ | ✔ (regional) | ✔ (equipe) |
| Fotos e indícios de fotos | — | ✔ | — | ✔ | ✔ | ✔ | ✔ (regional) | ✔ (equipe) |
| Ruptura x estoque | — | ✔ | — | ✔ | ✔ | ✔ | ✔ (regional) | ✔ (equipe) |
| Dossiês emitidos | ✔ | ✔ | Só Relatório de Jornada | ✔ | ✔ | Sem a seção de contexto | ✔ (regional) | ✔ (equipe) |
| Seção "Contexto de acompanhamento" do dossiê | — | ✔ | — | ✔ (**Q-08**) | — | — | ✔ (regional) | ✔ (equipe) |
| Trilha de auditoria | — | Dos próprios documentos | — | ✔ completa | Dos próprios documentos | — | — | — |
| Parâmetros das regras | Leitura | Leitura | Leitura | Leitura | ✔ | Leitura | Leitura | — |

O P&P vê o quadrante e a situação da trava porque precisa deles para gerar o Dossiê de Conduta, mas não vê o humor dia a dia (**P-17**).

## 5.3 O que cada perfil gera, aprova e exporta

Legenda: **G** gera rascunho · **R** revisa · **A** aprova e emite · **E** exporta (PDF/Excel) · **—** sem permissão.

| Ação | Diretoria | RH | DP | Compliance | P&P | Merch. / TD | Gerência Regional | Supervisor |
|------|-----------|----|----|-----------|-----|-------------|-------------------|-----------|
| Dossiê de Conduta | E | G · R · A · E | — | E | G · R · A · E | E (sem contexto) | E (regional) | E (equipe) |
| Relatório de Acompanhamento (Cuidado) | — | G · R · A · E | — | — | — | — | E (regional) | G · E (equipe) |
| Relatório de Jornada | — | G · R · A · E | G · R · A · E | G · E | G · R · E | — | E (regional) | — |
| Relatório Executivo | E | G · A · E | — | E | G · R · A · E | E | G · E (regional) | — |
| Registrar relato a apurar | — | ✔ | — | ✔ | ✔ | ✔ | ✔ | ✔ |
| Registrar Conversa de Cuidado | — | ✔ | — | — | — | — | ✔ (regional) | ✔ (equipe) |
| Registrar plano de ação (TD/Merch.) | — | ✔ | — | — | — | ✔ | ✔ | ✔ |
| Conferir ou descartar indício de foto | — | — | — | — | ✔ | ✔ | — | — |
| Registrar ciência em documento | — | ✔ | ✔ | — | — | — | ✔ | ✔ |
| Alterar parâmetros | — | — | — | — | ✔ (dono) | — | — | — |
| Upload de escalas, atestados, afastamentos | — | — | ✔ | — | — | — | — | — |
| Upload de estoque do cliente | — | — | — | — | ✔ | ✔ | — | — |
| Pedir reprocessamento | — | — | — | — | ✔ | — | — | — |

Regras de segregação:

- Quem gera o rascunho não aprova o próprio documento.
- O supervisor não gera Dossiê de Conduta sobre a própria equipe; registra o relato, e o P&P ou o RH gera.
- Alteração de parâmetro exige justificativa e fica no histórico. A necessidade de segunda aprovação está em aberto (**Q-07**).

## 5.4 Regras nos arquivos exportados

- O PDF e o Excel são gerados de acordo com o perfil de quem baixa.
- Perfis sem acesso ao contexto recebem o PDF sem a seção "Contexto de acompanhamento" e o Excel **sem a aba Humor** (a aba é removida, não ocultada).
- Todo PDF baixado leva marca d'água com o nome do usuário e a data do download.
- O link das fotos no Excel exige login e respeita a permissão.

## 5.5 Requisitos de governança

| Requisito | Especificação |
|-----------|---------------|
| SSO | Login corporativo único. O perfil vem do grupo do usuário no diretório corporativo (**Q-06**) |
| Log imutável | Registra consultas, edições, emissões e downloads: usuário, perfil, data e hora, ação, registro acessado e origem. Só inclusão; sem edição nem exclusão |
| Marca d'água | Nome do usuário e data em todo PDF baixado |
| Retenção e descarte | Prazos por tipo de dado e de documento, com descarte automático registrado em log. Prazos a definir com DPO, DP e Compliance (**Q-09**) |
| Base legal LGPD | Documentada com o DPO antes do piloto, com atenção ao dado de saúde ("Doente") e ao uso em contexto trabalhista (**Q-10**) |
| Aviso aos promotores | Comunicado transparente sobre o uso da pesquisa de humor: para que serve, quem vê e a garantia de que não é usada para punição (**Q-10**) |
| Acesso externo | Nenhum acesso para clientes externos. Documento enviado para fora da empresa só por decisão das áreas responsáveis, fora do sistema |
| Revisão de acessos | Revisão periódica dos perfis pelo dono de cada área, com registro |
| Desligamento | Usuário desligado perde o acesso pelo SSO. Dados de colaborador desligado seguem a política de retenção |

## 5.6 Proteções específicas do Humor

- Não existe ranking individual de humor em nenhuma tela ou relatório.
- O humor nunca aparece como ocorrência nem como achado em Dossiê de Conduta.
- O agente Revisor bloqueia a emissão de texto que use o humor como fundamento de medida.
- Agregados de humor só são exibidos para grupos com número mínimo de pessoas, para não identificar indivíduos. Mínimo proposto: 5 (**P-23**).
- A opção "Doente" só é exibida ao RH. Os demais perfis autorizados veem "alerta de cuidado".
