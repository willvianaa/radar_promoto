from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event, text

from documentos import ano_de_emissao, formatar_numero, proximo_numero


def test_formato_do_numero():
    assert formatar_numero(2026, 1) == "RP-2026-000001"
    assert formatar_numero(2026, 999_999) == "RP-2026-999999"
    with pytest.raises(ValueError):
        formatar_numero(2026, 0)


def test_ano_usa_fuso_de_sao_paulo():
    # 2027-01-01 02:30 UTC ainda é 31/12/2026 em São Paulo
    assert ano_de_emissao(datetime(2027, 1, 1, 2, 30, tzinfo=timezone.utc)) == 2026
    with pytest.raises(ValueError):
        ano_de_emissao(datetime(2026, 1, 1))


@pytest.fixture
def engine(tmp_path):
    motor = create_engine(
        f"sqlite:///{tmp_path / 'seq.db'}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    @event.listens_for(motor, "begin")
    def _escrita_serializada(conexao):
        # Em Postgres a linha do ano é travada pelo UPSERT; aqui o SQLite trava o banco inteiro.
        conexao.exec_driver_sql("BEGIN IMMEDIATE")

    with motor.begin() as c:
        c.execute(text("CREATE TABLE dossie_sequencia (ano INTEGER PRIMARY KEY, ultimo INTEGER NOT NULL DEFAULT 0)"))
    return motor


def test_emissoes_concorrentes_sem_buraco_nem_repeticao(engine):
    def emitir(_):
        with engine.begin() as c:
            return proximo_numero(c, 2026, tabela="dossie_sequencia")

    with ThreadPoolExecutor(max_workers=8) as pool:
        numeros = list(pool.map(emitir, range(40)))

    assert sorted(numeros) == [formatar_numero(2026, n) for n in range(1, 41)]


def test_rollback_nao_deixa_buraco(engine):
    with engine.connect() as c:
        transacao = c.begin()
        desfeito = proximo_numero(c, 2026, tabela="dossie_sequencia")
        transacao.rollback()
    with engine.begin() as c:
        proximo = proximo_numero(c, 2026, tabela="dossie_sequencia")
    assert desfeito == proximo == "RP-2026-000001"


def test_anos_tem_sequencias_separadas(engine):
    with engine.begin() as c:
        assert proximo_numero(c, 2026, tabela="dossie_sequencia") == "RP-2026-000001"
        assert proximo_numero(c, 2027, tabela="dossie_sequencia") == "RP-2027-000001"
        assert proximo_numero(c, 2026, tabela="dossie_sequencia") == "RP-2026-000002"


def test_nome_de_tabela_invalido_e_recusado(engine):
    with engine.begin() as c, pytest.raises(ValueError):
        proximo_numero(c, 2026, tabela="x; drop table y")
