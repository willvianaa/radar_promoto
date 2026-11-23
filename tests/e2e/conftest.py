"""Configuração do e2e. Roda só quando ``E2E_BASE_URL`` está definida; senão, tudo é ignorado.

Variáveis de ambiente (nunca no repositório, nunca em log):
  E2E_BASE_URL                 ex.: http://localhost:8000/api/v1 (ambiente local ou de homologação)
  E2E_<PERFIL>_EMAIL / _SENHA  usuários de TESTE por perfil: DIRETORIA, RH, DP, COMPLIANCE, PP, MERCH,
                               GERENCIA, SUPERVISOR (criados pela seed de dados fictícios)
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE_URL = os.environ.get("E2E_BASE_URL", "").rstrip("/")
PERFIS = ("DIRETORIA", "RH", "DP", "COMPLIANCE", "PP", "MERCH", "GERENCIA", "SUPERVISOR")


def pytest_collection_modifyitems(config, items):
    if BASE_URL:
        return
    skip = pytest.mark.skip(reason="E2E_BASE_URL não definida (API e Front ainda não disponíveis neste ambiente)")
    for item in items:
        if "tests/e2e" in str(item.fspath).replace("\\", "/") or "tests\\e2e" in str(item.fspath):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def anonimo() -> httpx.Client:
    with httpx.Client(base_url=BASE_URL, timeout=10, follow_redirects=False) as c:
        yield c


@pytest.fixture(scope="session")
def como():
    """``como("RH")`` devolve um cliente autenticado com o usuário de teste do perfil (ou pula o teste)."""
    clientes: dict[str, httpx.Client] = {}

    def _como(perfil: str) -> httpx.Client:
        if perfil in clientes:
            return clientes[perfil]
        email = os.environ.get(f"E2E_{perfil}_EMAIL")
        senha = os.environ.get(f"E2E_{perfil}_SENHA")
        if not email or not senha:
            pytest.skip(f"credenciais de teste do perfil {perfil} não configuradas")
        c = httpx.Client(base_url=BASE_URL, timeout=10)
        r = c.post("/auth/login", json={"email": email, "senha": senha})
        assert r.status_code == 200, f"login de teste do perfil {perfil} falhou ({r.status_code})"
        clientes[perfil] = c
        return c

    yield _como
    for c in clientes.values():
        c.close()
