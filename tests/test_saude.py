from fastapi.testclient import TestClient

from api.app.main import app


def test_saude_responde_200():
    resposta = TestClient(app).get("/api/v1/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
