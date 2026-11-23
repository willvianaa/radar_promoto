# Briefing — LGPD e Segurança (Opus · `feat/lgpd-seguranca` · todas as ondas)

## A ideia
O Radar Promotor trata dados pessoais de centenas de colaboradores (nome, CPF, jornada, GPS, fotos) e um dado de saúde (humor "Doente"), e produz um documento que pode embasar medidas de RH. Um vazamento ou um uso indevido expõe pessoas e a RT (multas da ANPD, ações trabalhistas, imagem). Esta sessão existe para que a proteção de dados seja **parte do projeto desde o começo**, e não uma revisão no final.

## Por que Opus
Exige julgamento jurídico-técnico (bases legais, proporcionalidade, riscos) e revisão crítica do trabalho de todas as outras sessões.

## Entrega
1. **Diagnóstico inicial** do estado atual: repositório público, protótipo com dados reais no banco do artefato, pasta `dados/` local, histórico do git (varredura de CPF e segredos), dependências.
2. **Documentos LGPD** em `docs/lgpd/`: mapa de dados (que dado, de onde, para quê, quem vê, quanto tempo), RIPD, registro das operações de tratamento, proposta de política de retenção (Q-09), plano de resposta a incidentes, modelo de aviso aos colaboradores. As decisões de base legal e prazos ficam com DPO, RH e Jurídico; a sessão propõe.
3. **Controles no CI:** secret scanning, varredura de padrões de CPF, `pip-audit`, `bandit`.
4. **Testes de segurança** em `tests/seguranca/`: permissão por perfil, mascaramento, ausência de dado sensível em log e URL.
5. **Revisão de PRs** que tocam dado pessoal, autenticação, permissão, log, storage ou infraestrutura, com comentário "Revisão LGPD/Segurança: OK" ou "BLOQUEADO: motivo".

## Não faz
Não acessa nem copia dado real; não decide base legal nem retenção sozinha; não afrouxa controle para PR passar.

## Encaixe
Transversal: atua junto com Infra (CI e ambiente), API (login, perfis, auditoria), Ingestor (credenciais e minimização), Documentos (marca CONFIDENCIAL e seção de contexto) e QA (testes de permissão).

## Pronto quando
Diagnóstico entregue com riscos priorizados; documentos LGPD em rascunho para o DPO; controles de segurança rodando no CI; nenhum PR sensível entrando sem revisão.

## Riscos já conhecidos
- Repositório **público**: tornar privado antes da onda 2.
- O protótipo atual guarda dados reais (CPF, humor, operação) no banco do artefato no claude.ai.
- Base legal do humor e da opção "Doente" ainda não definida (Q-10).
