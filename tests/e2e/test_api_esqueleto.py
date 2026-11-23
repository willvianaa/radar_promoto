"""Esqueleto e2e da API (api/openapi.yaml + docs/05-matriz-permissoes.md).

Cada teste é um contrato a verificar quando API e dados de teste existirem. Hoje todos são ignorados
sem ``E2E_BASE_URL``. Onde falta definição (ex.: id de colaborador de teste), o teste tem ``pytest.skip``
explícito para ser completado pela QA quando a API subir.
"""

import re
import time

import pytest

CPF_COMPLETO = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
CPF_MASCARADO = re.compile(r"\*\*\*\.\d{3}\.\d{3}-\*\*")


# ---------------------------------------------------------------- autenticação

def test_saude_sem_login(anonimo):
    assert anonimo.get("/saude").status_code == 200


@pytest.mark.parametrize("rota", ["/painel", "/painel/radar", "/painel/ranking", "/alertas", "/colaboradores",
                                  "/dossies", "/parametros", "/auditoria", "/auth/eu"])
def test_rotas_exigem_sessao(anonimo, rota):
    assert anonimo.get(rota).status_code == 401


def test_login_invalido_devolve_401(anonimo):
    r = anonimo.post("/auth/login", json={"email": "ninguem@exemplo.invalid", "senha": "x"})
    assert r.status_code == 401


# ---------------------------------------------------------------- CPF mascarado em listas

@pytest.mark.parametrize("perfil", ["RH", "SUPERVISOR"])
def test_cpf_nunca_completo_em_listas(como, perfil):
    c = como(perfil)
    for rota in ("/painel/ranking", "/colaboradores?q=a", "/painel/radar"):
        r = c.get(rota)
        assert r.status_code == 200, rota
        achou = bool(CPF_COMPLETO.search(r.text))  # booleano antes: o assert não imprime o CPF casado no log
        assert not achou, f"CPF completo em {rota} para {perfil}"


def test_lista_traz_cpf_mascarado_no_formato_padrao(como):
    r = como("RH").get("/painel/ranking")
    assert r.status_code == 200
    assert CPF_MASCARADO.search(r.text) or r.json().get("itens") == []


# ---------------------------------------------------------------- permissões por perfil (matriz §5.2)

@pytest.mark.parametrize("perfil", ["DIRETORIA", "DP", "COMPLIANCE", "PP", "MERCH"])
def test_humor_individual_fora_de_rh_e_supervisor_nao_aparece(como, perfil):
    pytest.skip("completar com o id de colaborador de teste da seed e o campo de humor do schema RaioX")


@pytest.mark.parametrize("perfil", ["DIRETORIA", "DP", "COMPLIANCE", "PP", "MERCH", "GERENCIA", "SUPERVISOR"])
def test_dias_doente_nao_vem_para_perfil_sem_permissao(como, perfil):
    c = como(perfil)
    for rota in ("/painel/ranking", "/colaboradores?q=a", "/painel/radar"):
        r = c.get(rota)
        assert r.status_code == 200, rota
        achou = "dias_doente" in r.text
        assert not achou, f"campo dias_doente presente em {rota} para {perfil}"


def test_opcao_doente_so_para_rh(como):
    pytest.skip("completar: Raio-X de colaborador de teste com humor 'Doente' lido por RH (vê) e por Supervisor (só alerta)")


@pytest.mark.parametrize("perfil", ["PP", "GERENCIA", "SUPERVISOR"])
def test_motivo_da_falta_oculto(como, perfil):
    pytest.skip("completar: Raio-X de colaborador de teste com falta e motivo; só RH e DP veem o motivo")


def test_cpf_completo_so_no_raio_x_e_dossie_de_perfil_autorizado(como):
    pytest.skip("completar: confirmar na matriz quais perfis veem CPF completo no Raio-X")


def test_escopo_gerencia_regional_e_supervisor_so_o_proprio(como):
    pytest.skip("completar: ids de colaboradores de teste fora do escopo devem dar 404 (openapi /raio-x)")


def test_leitura_individual_gera_auditoria(como):
    pytest.skip("completar: GET /colaboradores/{id}/raio-x como RH; /auditoria deve registrar leitura")


# ---------------------------------------------------------------- desempenho (meta do harness QA)

def test_painel_responde_em_menos_de_2s(como):
    c = como("RH")
    c.get("/painel")  # aquecimento
    t = time.perf_counter()
    r = c.get("/painel")
    dur = time.perf_counter() - t
    assert r.status_code == 200
    assert dur < 2.0, f"/painel levou {dur:.2f}s com a fixture de 1.000 × 60 (meta: < 2 s)"


# ---------------------------------------------------------------- dossiê

def test_dossie_marca_confidencial_e_numeracao(como):
    pytest.skip("completar: emitir dossiê de colaborador de teste; número RP-AAAA-NNNNNN, arquivo 'Dossiê - NOME.pdf'")


def test_dossie_sem_termos_proibidos(como):
    pytest.skip("completar: texto do dossiê sem detrator, preguiçoso, irresponsável, desonesto, relapso, má-fé, mentiu, culpado")
