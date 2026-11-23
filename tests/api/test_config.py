import pytest
from fastapi.testclient import TestClient

from api.app.config import Configuracao, ConfiguracaoInvalida
from api.app.main import app

FORTE_A = "a" * 40
FORTE_B = "b" * 40


def _cfg(**kw):
    return Configuracao(_env_file=None, **kw)


@pytest.mark.parametrize("env", ["desenvolvimento", "producao", "homologacao", ""])
def test_sem_segredo_nao_sobe(env):
    with pytest.raises(ConfiguracaoInvalida):
        _cfg(app_env=env).validar()


def test_padrao_e_restritivo(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    assert _cfg().app_env == "producao"
    with pytest.raises(ConfiguracaoInvalida):
        _cfg().validar()


def test_segredo_curto_e_recusado():
    with pytest.raises(ConfiguracaoInvalida):
        _cfg(app_env="producao", segredo_sessao="curto", segredo_id=FORTE_B).validar()
    with pytest.raises(ConfiguracaoInvalida):
        _cfg(app_env="producao", segredo_sessao=FORTE_A, segredo_id="curto").validar()


def test_segredos_devem_ser_diferentes():
    with pytest.raises(ConfiguracaoInvalida):
        _cfg(app_env="producao", segredo_sessao=FORTE_A, segredo_id=FORTE_A).validar()


def test_segredos_fortes_e_diferentes_sobem():
    cfg = _cfg(app_env="producao", segredo_sessao=FORTE_A, segredo_id=FORTE_B)
    cfg.validar()
    assert cfg.segredo != cfg.segredo_do_id


@pytest.mark.parametrize("env", ["teste", "ci"])
def test_teste_e_ci_dispensam_segredo(env):
    _cfg(app_env=env).validar()


def test_app_nao_sobe_sem_segredo(monkeypatch):
    from api.app import config

    monkeypatch.setenv("APP_ENV", "desenvolvimento")
    monkeypatch.delenv("SEGREDO_SESSAO", raising=False)
    monkeypatch.delenv("SEGREDO_ID", raising=False)
    config.configuracao.cache_clear()
    try:
        with pytest.raises(ConfiguracaoInvalida):
            with TestClient(app):
                pass
    finally:
        config.configuracao.cache_clear()
