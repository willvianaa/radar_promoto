# Radar Promotor (2P RT)

Especificação inicial do **Radar Promotor**, módulo da plataforma 2P RT que reúne o acompanhamento do colaborador (Módulo **CUIDAR**, com o KPI de Humor) e a apuração operacional e de conduta (Módulo **CORRIGIR**, com o Dossiê do Promotor).

> **Situação: especificação para aprovação inicial.**
> Este repositório contém apenas documentos. Não há código de produção nem alteração em bases de dados. Todos os nomes, matrículas, lojas e números dos exemplos são **fictícios**.

## Documentos para validação

| Nº | Entrega | Documento |
|----|---------|-----------|
| 1 | Diagrama em blocos da arquitetura e especificação técnica | [docs/01-arquitetura.md](docs/01-arquitetura.md) |
| 2 | Dicionário de KPIs e regras de negócio | [docs/02-dicionario-kpis.md](docs/02-dicionario-kpis.md) |
| 3 | Wireframes do Painel Geral, da Ficha do Colaborador e da tela de Emissão | [docs/03-wireframes.md](docs/03-wireframes.md) |
| 4 | Modelo do PDF e do Excel de um Dossiê de Conduta fictício | [docs/04-modelo-documentos.md](docs/04-modelo-documentos.md) |
| 5 | Matriz de permissões por perfil e governança | [docs/05-matriz-permissoes.md](docs/05-matriz-permissoes.md) |
| 6 | Plano de fases e plano de testes | [docs/06-plano-fases-e-testes.md](docs/06-plano-fases-e-testes.md) |
| 7 | Perguntas em aberto e premissas adotadas | [docs/07-premissas-e-perguntas.md](docs/07-premissas-e-perguntas.md) |

## Princípios não negociáveis

1. **O Humor jamais é motivo de punição.** Entra no dossiê só como contexto de acompanhamento e só para os perfis autorizados.
2. **O sistema aponta exclusivamente indícios.** Apuração, tratativa e decisão são sempre humanas.
3. **Rastreabilidade total.** Todo número tem fonte, data e ID de registro.
4. **Cálculos determinísticos.** Regras e KPIs em SQL/Python. A IA atua apenas na análise visual de fotos e na redação/revisão do texto.
5. **LGPD.** O status "Doente" é dado sensível de saúde e gera só um alerta de cuidado, sem detalhe para perfis não autorizados.
6. **Documento emitido é imutável.** Qualquer alteração gera nova versão numerada.

## Como ler as premissas

Sempre que faltou informação, o documento registra uma premissa em vez de inventar um dado. As premissas têm código (`P-01`, `P-02`, …) e as perguntas em aberto também (`Q-01`, `Q-02`, …). A lista completa está em [docs/07-premissas-e-perguntas.md](docs/07-premissas-e-perguntas.md). Os valores marcados com **(P-xx)** nos demais documentos dependem de confirmação.

## Próximo passo

Validação desta especificação pelas áreas (Diretoria, RH, DP, Compliance, P&P, Merchandising/TD, Supervisão e TI). O desenvolvimento do MVP só começa depois da aprovação e da resposta às perguntas marcadas como bloqueantes.

## Protótipo navegável

Em [prototipo/index.html](prototipo/index.html) há um protótipo das telas (Painel, Ficha do Colaborador e Emissão), com dados fictícios. Abra o arquivo no navegador. Ele serve para demonstração e validação: não é o sistema, não grava nada e não se conecta a nenhuma base.
