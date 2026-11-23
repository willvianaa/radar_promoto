import pytest
from fastapi.testclient import TestClient

from api.app import rotas_auth
from api.app.deps import get_repo
from api.app.main import app

from .fakes import SENHA, RepoMem


@pytest.fixture
def repo():
    return RepoMem()


@pytest.fixture
def client(repo):
    rotas_auth._falhas.clear()
    app.dependency_overrides[get_repo] = lambda: repo
    yield TestClient(app, base_url="https://testserver")
    app.dependency_overrides.clear()


@pytest.fixture
def login(client):
    def _login(email: str):
        r = client.post("/api/v1/auth/login", json={"email": email, "senha": SENHA})
        assert r.status_code == 200, r.text
        return client

    return _login
