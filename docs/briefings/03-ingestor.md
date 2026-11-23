# Briefing — Ingestor (Sonnet · `feat/ingestor` · onda 2)

## A ideia
Acabar com o "exporta planilha, converte, sobe no artefato" feito à mão. Um robô (Playwright, usuário de serviço) entra nas origens todo dia de madrugada, baixa os mesmos exports que a equipe baixa hoje, confere o formato e guarda o arquivo como recebido. Se a origem mudar, ele **para e avisa** em vez de gravar número errado.

## Entrega
- Fluxos de download: plataforma de monitoramento (cadastro, operação, atividades, humor, fotos) e 2PRT (aderência Todos/Descontos, PDOH).
- Fatiamento por período para nunca passar de 10 mil linhas por export.
- Validação contra `schemas/` (cabeçalho nas 15 primeiras linhas, colunas obrigatórias, tipos); `formato_alterado` → nada gravado + `app.ingestao_alerta`.
- Gravação em `raw.carga` (com SHA-256 e "Gerado em" da origem) e `raw.linha`.
- Upload controlado para faltas e estoque (layouts provisórios).

## Limites inegociáveis
- **Não contorna captcha nem 2FA**; se aparecer, para e alerta.
- No 2PRT, só filtros e "Exportar XLSX". Nunca "Atualizar Aderência" nem "Gerar Aderência"; "Recalcular" → Cancelar. Volta filtros ao padrão.
- Credenciais só em secrets; o dono cria o usuário de serviço.

## Encaixe
Depende da Infra (worker + cron) e entrega para Dados (raw → core).

## Pronto quando
Rodada completa contra páginas simuladas nos testes e, em homologação, contra as origens reais com conferência dos totais da tela.

## Riscos
Mudanças de layout das origens; limites de sessão/login; necessidade de usuário de serviço sem 2FA (decisão da TI).
