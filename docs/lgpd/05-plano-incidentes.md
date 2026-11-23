# Plano de resposta a incidentes de segurança com dados pessoais (rascunho)

> Rascunho para o DPO e a TI. Segue o art. 48 da LGPD e o Regulamento de Comunicação de Incidente da ANPD (Resolução CD/ANPD nº 15/2024: comunicação em até **3 dias úteis** do conhecimento, quando houver risco ou dano relevante).

## 1. O que é incidente

Qualquer evento confirmado ou suspeito que afete a confidencialidade, integridade ou disponibilidade de dado pessoal. Exemplos neste projeto:
- CPF, nome, foto, GPS ou humor em commit, PR, issue, log, print ou chat;
- segredo (senha, token, `SEGREDO_SESSAO`, credencial do ingestor) exposto;
- acesso de perfil fora do escopo (ex.: supervisor vendo outra equipe; perfil vendo "Doente");
- dossiê ou export enviado a destinatário errado;
- perda, cifragem ou exclusão indevida de banco, backup ou fotos.

## 2. Papéis

| Papel | Quem | Responsabilidade |
|-------|------|------------------|
| Quem detecta | Qualquer pessoa ou sessão | Avisar no mesmo dia; **não copiar o dado** para o aviso |
| Coordenação | DPO | Avaliar risco, decidir comunicação, registrar |
| Técnico | TI / sessão Infra e LGPD e Segurança | Conter, investigar, corrigir |
| Dono do sistema | P&P | Decisões operacionais (suspender uso, ingestão) |
| Jurídico e RH | — | Comunicação aos titulares, aspectos trabalhistas |

## 3. Fluxo

1. **Detecção e aviso (mesmo dia)**: avisar o dono e o DPO (CLAUDE.md §2.1). Descrever o tipo de dado, onde, desde quando, sem reproduzir o valor.
2. **Contenção (imediata)**:
   - segredo exposto → **revogar e trocar** (a remoção do git não basta);
   - dado no repositório → remover, tornar o repositório privado se ainda for público, avaliar reescrita do histórico com o dono (BFG/`git filter-repo`) e pedir ao GitHub limpeza de cache/forks;
   - acesso indevido → desativar usuário/sessão, corrigir permissão;
   - arquivo enviado errado → pedir exclusão ao destinatário e registrar.
3. **Avaliação de risco (até 2 dias úteis)**: volume, tipo (sensível? CPF? GPS?), titulares afetados, probabilidade de uso indevido, medidas que reduzem o risco (ex.: dado criptografado).
4. **Comunicação (até 3 dias úteis do conhecimento, se risco ou dano relevante)**: ANPD pelo formulário oficial e titulares em linguagem simples (o que houve, quais dados, riscos, medidas, contato do DPO).
5. **Erradicação e recuperação**: corrigir a causa; restaurar de backup se necessário; reforçar controle (ex.: novo padrão no scanner do CI).
6. **Registro e lições aprendidas (até 15 dias)**: registro interno do incidente mantido por no mínimo 5 anos (mesmo sem comunicação à ANPD), com causa, impacto, medidas e responsáveis.

## 4. Controles preventivos ligados a este plano

- CI: varredura de CPF e segredos, gitleaks, pip-audit, bandit (`.github/workflows/seguranca.yml`).
- Logs sem CPF completo, humor individual ou motivo de falta.
- Auditoria append-only de leituras individuais e emissões.
- Backups criptografados com teste de restauração.

## 5. Contatos (preencher fora do repositório público)

DPO, TI, Jurídico e dono do sistema: manter a lista em local interno, não neste arquivo.
