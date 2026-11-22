-- Radar Promotor — DDL de referência (contrato). As migrações reais (Alembic) devem produzir este modelo.
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS app;

-- ---------- raw ----------
CREATE TABLE raw.carga (
  id               bigserial PRIMARY KEY,
  origem           text NOT NULL CHECK (origem IN ('colaboradores','operacao','atividades','humor','fotos','faltas','aderencia','pdoh','estoque')),
  arquivo          text NOT NULL,
  sha256           char(64) NOT NULL,
  periodo_ini      date,
  periodo_fim      date,
  gerado_em_origem timestamptz,
  linhas_lidas     int NOT NULL DEFAULT 0,
  linhas_aceitas   int NOT NULL DEFAULT 0,
  linhas_descartadas int NOT NULL DEFAULT 0,
  status           text NOT NULL CHECK (status IN ('ok','formato_alterado','erro')),
  iniciada_em      timestamptz NOT NULL DEFAULT now(),
  terminada_em     timestamptz,
  UNIQUE (origem, sha256)
);
CREATE TABLE raw.linha (
  carga_id bigint NOT NULL REFERENCES raw.carga(id),
  n        int NOT NULL,
  dados    jsonb NOT NULL,
  PRIMARY KEY (carga_id, n)
);

-- ---------- core ----------
CREATE TABLE core.regional (id serial PRIMARY KEY, nome text UNIQUE NOT NULL);
CREATE TABLE core.colaborador (
  cpf            varchar(11) PRIMARY KEY,           -- só dígitos; chave provisória 'N:'+nome_norm quando cpf_pendente
  nome           text NOT NULL,
  nome_norm      text NOT NULL,
  uf             char(2),
  cidade         text,
  supervisor_cpf varchar(11),
  regional_id    int REFERENCES core.regional(id),
  ativo          boolean NOT NULL DEFAULT true,
  admissao       date,
  jornada_texto  text,
  jornada_ini    smallint,                          -- minutos desde 00:00
  jornada_fim    smallint,
  cpf_pendente   boolean NOT NULL DEFAULT false
);
CREATE INDEX ON core.colaborador (nome_norm);
CREATE TABLE core.pdv (
  id   serial PRIMARY KEY, nome text UNIQUE NOT NULL, uf char(2),
  tipo text NOT NULL DEFAULT 'loja' CHECK (tipo IN ('loja','nao_operacional','reuniao')),
  lat double precision, lon double precision
);
CREATE TABLE core.feriado (data date NOT NULL, uf char(2), descricao text, PRIMARY KEY (data, uf));
CREATE TABLE core.visita (
  id bigserial PRIMARY KEY, cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf), data date NOT NULL,
  pdv_id int NOT NULL REFERENCES core.pdv(id), checkin time NOT NULL, checkout time, checkout_auto boolean NOT NULL,
  carga_id bigint REFERENCES raw.carga(id), UNIQUE (cpf, pdv_id, data, checkin)
);
CREATE TABLE core.atividade (
  id_origem text PRIMARY KEY, cpf varchar(11) REFERENCES core.colaborador(cpf), data date NOT NULL,
  pdv_id int REFERENCES core.pdv(id), cliente text, tipo text, status char(1) NOT NULL CHECK (status IN ('R','E','P')),
  justificada boolean, fotos int, carga_id bigint REFERENCES raw.carga(id)
);
CREATE TABLE core.humor (
  cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf), data date NOT NULL, opcao text NOT NULL,
  negativo boolean NOT NULL, carga_id bigint REFERENCES raw.carga(id), PRIMARY KEY (cpf, data)
);
CREATE TABLE core.foto (
  id bigserial PRIMARY KEY, cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf), data date NOT NULL, hora time,
  pdv_id int REFERENCES core.pdv(id), id_atividade text, caminho_storage text NOT NULL, sha256 char(64) NOT NULL,
  phash bigint, lat double precision, lon double precision, carga_id bigint REFERENCES raw.carga(id)
);
CREATE INDEX ON core.foto (phash);
CREATE TABLE core.falta (
  cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf), data date NOT NULL,
  tipo char(1) NOT NULL CHECK (tipo IN ('I','J','A','F')), motivo text,   -- motivo: só RH/DP
  carga_id bigint REFERENCES raw.carga(id), PRIMARY KEY (cpf, data, tipo)
);
CREATE TABLE core.aderencia (
  id bigserial PRIMARY KEY, cpf varchar(11) REFERENCES core.colaborador(cpf),   -- nulo = SEM COLABORADOR
  loja text NOT NULL, marca text NOT NULL, uf char(2), semana_ini date NOT NULL,
  contratadas int NOT NULL, realizadas int NOT NULL,
  realizadas_lim int GENERATED ALWAYS AS (LEAST(realizadas, contratadas)) STORED,
  ajustadas int, semana_fechada boolean NOT NULL, carga_id bigint REFERENCES raw.carga(id)
);
CREATE INDEX ON core.aderencia (cpf, semana_ini);
CREATE TABLE core.pdoh (
  cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf), periodo_ini date NOT NULL, periodo_fim date NOT NULL,
  dias smallint, seg_produtivo int NOT NULL DEFAULT 0, seg_deslocamento int NOT NULL DEFAULT 0,
  seg_ocio int NOT NULL DEFAULT 0, seg_nao_registrado int NOT NULL DEFAULT 0, carga_id bigint REFERENCES raw.carga(id),
  PRIMARY KEY (cpf, periodo_ini, periodo_fim)
);
CREATE TABLE core.estoque (
  cliente text NOT NULL, pdv_id int NOT NULL REFERENCES core.pdv(id), produto text NOT NULL, ean text, data date NOT NULL,
  estoque numeric, ruptura boolean, carga_id bigint REFERENCES raw.carga(id), PRIMARY KEY (cliente, pdv_id, produto, data)
);

-- ---------- app ----------
CREATE TABLE app.usuario (
  id serial PRIMARY KEY, email text UNIQUE NOT NULL, nome text NOT NULL,
  perfil text NOT NULL CHECK (perfil IN ('diretoria','rh','dp','compliance','pp','merch','gerencia_regional','supervisor','admin')),
  escopo_regional_id int REFERENCES core.regional(id), escopo_supervisor_cpf varchar(11), ativo boolean NOT NULL DEFAULT true
);
CREATE TABLE app.parametro_versao (
  id serial PRIMARY KEY, vigente_desde timestamptz NOT NULL, autor_id int REFERENCES app.usuario(id),
  justificativa text NOT NULL, valores jsonb NOT NULL
);
CREATE TABLE app.calculo (
  id bigserial PRIMARY KEY, periodo_ini date NOT NULL, periodo_fim date NOT NULL,
  parametro_versao_id int NOT NULL REFERENCES app.parametro_versao(id), criado_em timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE app.indicador_colaborador (
  calculo_id bigint NOT NULL REFERENCES app.calculo(id), cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf),
  dimensoes jsonb NOT NULL, carga_media numeric, queda_ader_pp numeric,
  score smallint NOT NULL, nivel char(1) NOT NULL CHECK (nivel IN ('C','A','T','N')), risco smallint NOT NULL CHECK (risco BETWEEN 0 AND 100),
  PRIMARY KEY (calculo_id, cpf)
);
CREATE TABLE app.alerta (
  id bigserial PRIMARY KEY, calculo_id bigint NOT NULL REFERENCES app.calculo(id), cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf),
  tipo text NOT NULL CHECK (tipo IN ('jor','auto','pesq','exec','ader','falta','foto','rota','sobre','humor')),
  severidade smallint NOT NULL CHECK (severidade BETWEEN 1 AND 3), titulo text NOT NULL, detalhe text NOT NULL, data_ref date
);
CREATE TABLE app.dossie_sequencia (ano smallint PRIMARY KEY, ultimo int NOT NULL DEFAULT 0);
CREATE TABLE app.dossie (
  numero text PRIMARY KEY CHECK (numero ~ '^RP-\d{4}-\d{6}$'), cpf varchar(11) NOT NULL REFERENCES core.colaborador(cpf),
  periodo_ini date NOT NULL, periodo_fim date NOT NULL, parametro_versao_id int NOT NULL REFERENCES app.parametro_versao(id),
  relato text, conteudo jsonb NOT NULL, status text NOT NULL CHECK (status IN ('rascunho','emitido')),
  criado_por int NOT NULL REFERENCES app.usuario(id), emitido_por int REFERENCES app.usuario(id), emitido_em timestamptz,
  sha256_pdf char(64), sha256_xlsx char(64)
);
CREATE TABLE app.auditoria (
  id bigserial PRIMARY KEY, quando timestamptz NOT NULL DEFAULT now(), usuario_id int REFERENCES app.usuario(id),
  acao text NOT NULL, recurso text NOT NULL, recurso_id text, ip inet, detalhe jsonb
);
CREATE FUNCTION app.bloqueia_alteracao() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'auditoria é somente inclusão'; END $$;
CREATE TRIGGER auditoria_imutavel BEFORE UPDATE OR DELETE ON app.auditoria FOR EACH ROW EXECUTE FUNCTION app.bloqueia_alteracao();
CREATE TABLE app.ingestao_alerta (
  id bigserial PRIMARY KEY, carga_id bigint REFERENCES raw.carga(id), origem text NOT NULL, motivo text NOT NULL,
  aberto_em timestamptz NOT NULL DEFAULT now(), resolvido_em timestamptz
);
