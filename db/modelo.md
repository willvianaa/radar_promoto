# Modelo do banco (Postgres 16)

Três esquemas. O DDL de referência está em `db/modelo.sql`; as migrações reais (Alembic) são do filho **Dados e regras** e devem seguir este contrato.

| Esquema | Para quê | Quem escreve |
|---|---|---|
| `raw` | Arquivo como recebido + linhas cruas (JSONB), imutável | Ingestor |
| `core` | Dados tratados e normalizados (fatos e dimensões) | Dados e regras |
| `app` | Usuários, perfis, parâmetros, resultados calculados, dossiês, auditoria | Dados e regras / Backend |

## raw
- `raw.carga` — uma linha por arquivo baixado: origem (`colaboradores|operacao|atividades|humor|fotos|faltas|aderencia|pdoh|estoque`), nome, SHA-256, período, linhas lidas/aceitas/descartadas, status (`ok|formato_alterado|erro`), `gerado_em_origem` (ex.: "Gerado em" do 2PRT), iniciada/terminada.
- `raw.linha` — `carga_id`, número da linha, `dados JSONB`. Nunca é alterada; reprocessar = nova carga.

## core
- `colaborador` — `cpf` (PK, só dígitos), nome, nome_norm, uf, cidade, supervisor_cpf, regional, ativo, admissao, jornada_texto, jornada_ini (min), jornada_fim (min), `cpf_pendente`.
- `supervisor`/hierarquia — derivada de `colaborador.supervisor_cpf` + tabela `regional`.
- `pdv` — id, nome (`UF / LOJA`), uf, tipo (`loja|nao_operacional|reuniao`), lat, lon.
- `visita` (fato) — cpf, data, pdv_id, checkin, checkout, checkout_auto, carga_id.
- `atividade` (fato) — id_origem (PK), cpf, data, pdv_id, cliente, tipo, status (`R|E|P`), justificada, fotos.
- `humor` (fato) — cpf, data, opcao, negativo (bool). **Acesso restrito** (view por perfil).
- `foto` (fato) — cpf, data, hora, pdv_id, id_atividade, caminho_storage, sha256, phash, lat, lon.
- `falta` (fato) — cpf, data, tipo (`I|J|A|F`), motivo (**coluna restrita a RH/DP**).
- `aderencia` (fato) — cpf (nulo = SEM COLABORADOR), loja, marca, uf, semana_ini (segunda ISO), contratadas, realizadas, realizadas_lim (= min(realizadas, contratadas)), ajustadas, semana_fechada (bool).
- `pdoh` (fato) — cpf, periodo_ini, periodo_fim, dias, seg_produtivo, seg_deslocamento, seg_ocio, seg_nao_registrado.
- `estoque` (fato) — cliente, pdv_id, produto, ean, data, estoque, ruptura.
- `feriado` — data, uf (nulo = nacional), descricao.

## app
- `usuario` — id, email, nome, perfil (`diretoria|rh|dp|compliance|pp|merch|gerencia_regional|supervisor|admin`), escopo_regional, escopo_supervisor_cpf, ativo, `senha_hash` (hash argon2; nulo = sem login por senha; migração 0003, até o SSO — Q-06). O `db/modelo.sql` é o DDL da migração 0001; mudanças posteriores entram só por migração nova.
- `parametro_versao` — id, vigente_desde, autor, justificativa, `valores JSONB`. Toda alteração cria versão nova; documento guarda a versão usada.
- `calculo` — id, periodo_ini, periodo_fim, parametro_versao_id, criado_em (um cálculo por execução diária e sob demanda).
- `indicador_colaborador` — calculo_id, cpf, dimensões (aderência, pesquisas, pontualidade, registro de jornada, fotos, presença, humor), carga_media, queda_ader_pp, score, nivel (`C|A|T|N`), risco (0–100).
- `alerta` — id, calculo_id, cpf, tipo (`jor|auto|pesq|exec|ader|falta|foto|rota|sobre|humor`), severidade (1–3), titulo, detalhe, data_ref.
- `dossie` — numero (`RP-AAAA-NNNNNN`, único), cpf, periodo, parametro_versao_id, relato, conteúdo editado (JSONB), status (`rascunho|emitido`), emitido_por, emitido_em, sha256_pdf, sha256_xlsx.
- `dossie_sequencia` — ano, ultimo (numeração sem reaproveitamento, com lock).
- `auditoria` — id, quando, usuario_id, acao, recurso, recurso_id, ip, detalhe JSONB. **Append-only** (sem UPDATE/DELETE, garantido por trigger e permissão).
- `ingestao_alerta` — carga_id, origem, motivo, aberto_em, resolvido_em.

## Parâmetros iniciais (`parametro_versao` nº 1)

```json
{
  "escala": {"ini": "08:00", "fim": "17:30"},
  "tolerancia_atraso_min": 15, "tolerancia_saida_min": 15, "saida_antecipada_ativa": false,
  "meta1": 85, "meta2": 93, "corte_ader_dossie": 93,
  "dist_foto_m": 300, "cerca_rota_m": 200,
  "humor_negativo": ["Cansado", "Sobrecarregado", "Triste", "Doente"],
  "limites": {"atraso": [4,7,10], "saida": [4,7,10], "checkout_auto": [5,8,10],
              "pesq_expiradas_pct": [20,30,45], "pesq_min": 20, "dias_sem_atividade": [0,2,4],
              "faltas_injust": [0,1,3], "fotos_indicio": [0,1,3], "visitas_pendentes": [0,1,10],
              "dias_fuga_rota": [0,3,10], "humor_pct": 40, "humor_seq": 3,
              "carga_semana": 44, "queda_ader_pp": 5},
  "nivel": {"critico_soma": 9, "critico_sev3": 2, "alto_soma": 5, "atencao_soma": 3}
}
```
Limites `[a,b,c]`: valor ≥ c → severidade 3; ≥ b → 2; ≥ a (e a > 0) → 1.
