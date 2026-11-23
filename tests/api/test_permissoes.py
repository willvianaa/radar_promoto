import pytest

from api.app.auditoria import Auditoria
from api.app.deps import monta_sessao
from api.app.permissoes import Escopo, formata_cpf, humor_visivel, mascara_cpf, no_escopo
from api.app.seguranca import id_opaco

from .fakes import RepoMem

PERFIS = {u.perfil: monta_sessao(u).acesso for u in RepoMem().usuarios.values() if u.ativo}


def test_mascara_cpf():
    assert mascara_cpf("12345678901") == "***.456.789-**"
    assert mascara_cpf("N:FULANO DE TAL") == "***.***.***-**"
    assert formata_cpf("00000000191") == "000.000.001-91"


@pytest.mark.parametrize("perfil,esperado", [
    ("rh", True), ("dp", True), ("compliance", True), ("pp", True),
    ("diretoria", False), ("merch", False), ("gerencia_regional", False), ("supervisor", False), ("admin", False),
])
def test_cpf_completo(perfil, esperado):
    assert PERFIS[perfil].ver_cpf_completo() is esperado


@pytest.mark.parametrize("perfil,opcao,esperado", [
    ("rh", "Doente", "Doente"), ("rh", "Cansado", "Cansado"),
    ("supervisor", "Cansado", "Cansado"), ("supervisor", "Doente", "Alerta de cuidado"),
    ("gerencia_regional", "Cansado", "Alerta de cuidado"), ("gerencia_regional", "Doente", "Alerta de cuidado"),
    ("pp", "Doente", "Alerta de cuidado"),
    ("diretoria", "Cansado", None), ("dp", "Doente", None), ("compliance", "Cansado", None),
    ("merch", "Cansado", None), ("admin", "Doente", None),
])
def test_humor_por_perfil(perfil, opcao, esperado):
    assert humor_visivel(PERFIS[perfil], opcao) == esperado


def test_motivo_de_falta_so_rh_e_dp():
    assert {p for p, a in PERFIS.items() if a.ver_motivo_falta()} == {"rh", "dp"}


def test_raio_x_nao_e_para_diretoria_nem_admin():
    assert not PERFIS["diretoria"].ver_raio_x() and not PERFIS["admin"].ver_raio_x()
    assert PERFIS["supervisor"].ver_raio_x()


def test_parametros_so_pp_altera():
    assert {p for p, a in PERFIS.items() if a.alterar_parametros()} == {"pp"}


def test_auditoria_completa_so_compliance():
    assert PERFIS["compliance"].auditoria() == "completa"
    assert PERFIS["rh"].auditoria() == PERFIS["pp"].auditoria() == "propria"
    assert PERFIS["supervisor"].auditoria() is None


def test_upload_por_perfil():
    assert PERFIS["dp"].pode_upload("faltas") and not PERFIS["rh"].pode_upload("faltas")
    assert PERFIS["pp"].pode_upload("estoque") and not PERFIS["dp"].pode_upload("estoque")
    assert not PERFIS["pp"].pode_upload("colaboradores")


def test_escopo():
    assert no_escopo(Escopo("nacional"), "Norte", "1")
    assert no_escopo(Escopo("regional", "Sul"), "Sul", "1")
    assert not no_escopo(Escopo("regional", "Sul"), "Norte", "1")
    assert no_escopo(Escopo("equipe", "00000000191"), "Sul", "00000000191")
    assert not no_escopo(Escopo("equipe", "00000000191"), "Sul", "00000000272")
    # sem vínculo cadastrado: não vê nada
    assert not no_escopo(Escopo("regional", ""), "Sul", "1")
    assert not no_escopo(Escopo("equipe", ""), "Sul", None)


def test_id_opaco_estavel_e_sem_cpf():
    a = id_opaco(b"k", "00000000191")
    assert a == id_opaco(b"k", "00000000191")
    assert a != id_opaco(b"k", "00000000272") and a != id_opaco(b"outra", "00000000191")
    assert "00000000191" not in a and a.startswith("c_")


def test_auditoria_recusa_dado_pessoal_e_acao_desconhecida():
    aud = Auditoria(RepoMem(), "127.0.0.1")
    with pytest.raises(ValueError):
        aud.registrar(1, "leitura_raio_x", "colaborador", "c_x", {"cpf": "00000000191"})
    with pytest.raises(ValueError):
        aud.registrar(1, "inventada", "x")
    aud.registrar(1, "leitura_raio_x", "colaborador", "c_x", {"periodo": "2026-01"})
    assert len(aud.repo.auditoria) == 1
