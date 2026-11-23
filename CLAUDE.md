# CLAUDE.md — Radar Promotor (RT Intelligence)

Regras obrigatórias para qualquer sessão (humana ou agente) que trabalhe neste repositório.
Os contratos em `schemas/`, `db/` e `api/` são a fonte da verdade. Mudou um contrato? Abra PR
na branch da sessão-mãe (`docs/contratos` ou sucessora) antes de mudar o código que depende dele.

## 1. Fluxo de trabalho

- Toda mudança entra por PR, nunca por push direto na `main`.
- **Autorização do dono (22/11/2026):** a sessão-mãe e as sessões-filhas abrem seus próprios PRs e fazem o merge pelo GitHub, usando a conta do dono no Chrome. Condições para o merge:
  1. CI verde (todos os checks);
  2. aprovação da sessão-mãe registrada no PR (comentário "Aprovado pela sessão-mãe"); PR da própria mãe que mude contrato ou regra de negócio exige confirmação do dono no chat;
  3. merge pelo botão do PR (nunca `push --force` na `main`), apagando a branch só se não houver mais trabalho nela.
- Sem login no GitHub, captcha, 2FA ou pedido de senha: parar e avisar o dono. Nenhuma sessão digita senha nem altera configurações da conta ou do repositório.
- Cada sessão-filha trabalha na branch `feat/<área>` e abre PRs pequenos e frequentes (um assunto por PR).
- PR sempre com: o que muda, como testar, contrato que segue, riscos. Testes verdes antes de pedir revisão.
- Commits e PRs em português.

## 2. Dados e segurança (inegociável)

- **Nenhum dado real** entra no repositório: nome, CPF, foto, planilha, export, print, log com dados de colaborador. O repositório é público.
- Testes usam só dados fictícios em `tests/fixtures/` (nomes inventados, CPFs inválidos de propósito, ex.: `000.000.001-91`).
- Credenciais, tokens e URLs internas só em *secrets* (GitHub Actions / `.env` fora do git). Nunca em código, teste ou log.
- O ingestor usa usuário de serviço. **Não contorna captcha nem 2FA**: se a origem pedir, para e alerta.
- Logs da aplicação não registram CPF completo, humor individual nem motivo de falta.

## 3. Identificação do colaborador

- A chave do colaborador é o **CPF** (não existe matrícula no sistema). Sem CPF na origem, herda o CPF do mesmo nome normalizado (maiúsculas, sem acento, espaços simples) vindo do cadastro; sem cadastro, a chave provisória é o nome normalizado e o registro fica marcado `cpf_pendente`.
- Em **listas, tabelas, rankings e exports agregados** o CPF aparece mascarado: `***.456.789-**`.
- CPF completo só no Raio-X individual e no dossiê, para perfis autorizados (ver `docs/05-matriz-permissoes.md`).

## 4. Regras de negócio

### 4.1 Jornada
- Escala padrão **08:00–17:30**. Se o colaborador tem jornada cadastrada (ex.: "INÍCIO 07H"), vale a cadastrada; a duração é mantida (fim = início + 9h30).
- Tolerância de **15 min** para atraso (primeiro check-in) e **15 min** para saída antecipada (último check-out manual).
- Saída antecipada só é calculada quando houver o fim de jornada confiável; enquanto não houver, fica desligada (parâmetro `saida_antecipada_ativa = false`).
- Check-out feito pelo sistema ("Realizado pelo sistema") = **check-out automático**; não conta como saída.
- Feriados (tabela de parâmetros) não geram atraso nem saída.
- **Almoço:** o tempo no PDV `NÃO OPERACIONAL` é intervalo de almoço. Não conta como visita, nem como ócio, nem como deslocamento, e não gera alerta. PDVs `REUNIÃO` também não contam como loja atendida.

### 4.2 Pesquisas
- Status normalizado: `R` respondida/realizada, `E` expirada/não realizada, `P` pendente.
- Alerta de pesquisas expiradas só com no mínimo 20 programadas no período.
- "Dia sem atividades" = dia com programadas e nenhuma respondida, em dia com visita e fora de feriado.

### 4.3 Aderência (2PRT)
- Aderência = realizadas ÷ contratadas, com **realizadas limitadas ao contratado em cada linha** (colaborador × loja × marca × semana).
- Mês: soma das semanas por UF + Loja + Marca e só então aplica o teto (o excesso de um grupo não compensa o déficit de outro).
- **Meta 1 = 85%**, **Meta 2 = 93%**. Corte de aderência para o dossiê: 93%.
- WD-40 e Botafogo são quinzenais (contrato só em semana par).
- A semana em andamento **não entra em alertas** (o contrato vem inteiro e o realizado parcial).
- Semana = ISO, segunda a domingo. O 2PRT não tem filtro regional.

### 4.4 Humor
- Humor é **contexto de acompanhamento, nunca motivo de medida**. Não entra no Índice de risco como penalidade, não gera alerta de conduta sozinho e não aparece em texto acusatório.
- Opções negativas: Cansado, Sobrecarregado, Triste, Doente (Luto, Incomodado, Não Valorizado e Estressado: pendentes de decisão do RH).
- "Doente" é dado sensível (LGPD): visibilidade conforme a matriz de permissões.
- Humor negativo recorrente + queda de desempenho = **possível sobrecarga** (sinal de cuidado, não de conduta).

### 4.5 Sobrecarga
- Indício de sobrecarga: média ≥ 44 visitas contratadas por semana **e** queda de aderência ≥ 5 p.p. entre a primeira e a última semana fechada. Humor negativo recorrente reforça; PDOH (produtivo, deslocamento, ócio, horas não registradas) é contexto.

### 4.6 Fotos e rota
- Indícios de foto: imagem repetida (hash/pHash), captura a mais de 300 m da loja, foto fora do horário da visita.
- Fuga de rota: posição a mais de 200 m da loja (cerca).

### 4.7 Alertas e Índice de risco
- Cada alerta tem severidade 1 (baixa), 2 (média) ou 3 (alta), pelos limites versionados em `parametros` (valores iniciais em `db/modelo.md`).
- Nível do colaborador: **Crítico** se soma ≥ 9 ou dois alertas de severidade 3; **Alto** se soma ≥ 5; **Atenção** se soma ≥ 3; senão Estável.
- Índice de risco (0–100) = `min(100, soma_sev × 9 + (100 − média das dimensões sem humor) × 0,25)`.
- Toda regra é determinística e reproduzível: mesma entrada + mesma versão de parâmetros = mesmo resultado.

## 5. Dossiê (padrão formal)

- Título: **DOSSIÊ DE ANÁLISE OPERACIONAL**, emissor **RT Intelligence**, marca **CONFIDENCIAL** em todas as páginas.
- Numeração **RP-AAAA-NNNNNN** (sequencial anual, nunca reaproveitada). Arquivo: `Dossiê - NOME.pdf` / `.xlsx`.
- Sem saudação, sem primeira pessoa, sem adjetivos de juízo. **Não cita nomes de sistemas ou fornecedores** (escrever "registros operacionais", "plataforma de monitoramento").
- Sempre "indícios"; nunca "comprovado", "culpado", "fraude". Termos proibidos: detrator, preguiçoso, irresponsável, desonesto, relapso, má-fé, mentiu, culpado.
- Estrutura: 1. Identificação · 2. Introdução e objetivos · (Relato a apurar) · Relatos identificados (até 5 blocos, com tabela e gráfico) · Impacto na aderência e na operação · Contexto de acompanhamento (humor, só perfis autorizados) · Considerações finais, que começam com **"Sendo assim,"**.
- O dossiê apresenta indícios; quem decide medidas são DP e Compliance.

## 6. Técnica

- Python 3.12 + FastAPI, Postgres 16, front web responsivo (tema claro e escuro, identidade do Monitor Regional), Docker.
- Fuso **America/Sao_Paulo** em tudo. Datas ISO no banco e na API; `dd/mm/aaaa` só na tela e nos documentos.
- Limite de **10 mil registros por export** na origem: o ingestor fatia por período.
- Documentação existente: `docs/01` a `docs/07` (especificação inicial). Onde conflitar com este arquivo, vale este arquivo.
