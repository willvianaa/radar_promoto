from .fakes import SENHA

URL = "/api/v1/auth"


def test_login_ok_define_cookie_seguro(client):
    r = client.post(f"{URL}/login", json={"email": "rh@ficticio.example.com", "senha": SENHA})
    assert r.status_code == 200
    assert r.json() == {"id": 1, "nome": "Rita RH", "email": "rh@ficticio.example.com", "perfil": "rh", "escopo": "nacional"}
    cookie = r.headers["set-cookie"].lower()
    assert "rp_sessao=" in cookie and "httponly" in cookie and "secure" in cookie and "samesite=strict" in cookie


def test_login_senha_errada_e_email_inexistente_dao_a_mesma_resposta(client):
    a = client.post(f"{URL}/login", json={"email": "rh@ficticio.example.com", "senha": "errada"})
    b = client.post(f"{URL}/login", json={"email": "ninguem@ficticio.example.com", "senha": "errada"})
    assert a.status_code == b.status_code == 401
    assert a.json() == b.json()
    assert a.json()["codigo"] == "credenciais_invalidas"


def test_usuario_inativo_nao_entra(client):
    assert client.post(f"{URL}/login", json={"email": "off@ficticio.example.com", "senha": SENHA}).status_code == 401


def test_bloqueio_apos_falhas_repetidas(client):
    for _ in range(5):
        client.post(f"{URL}/login", json={"email": "rh@ficticio.example.com", "senha": "x"})
    r = client.post(f"{URL}/login", json={"email": "rh@ficticio.example.com", "senha": SENHA})
    assert r.status_code == 429


def test_eu_exige_sessao(client):
    assert client.get(f"{URL}/eu").status_code == 401


def test_eu_devolve_escopo_por_perfil(login):
    c = login("ger@ficticio.example.com")
    assert c.get(f"{URL}/eu").json()["escopo"] == "regional:Sul"
    c = login("sup@ficticio.example.com")
    assert c.get(f"{URL}/eu").json()["escopo"] == "equipe:SARA SUPERVISORA"


def test_cookie_adulterado_e_recusado(client):
    client.cookies.set("rp_sessao", "adulterado")
    assert client.get(f"{URL}/eu").status_code == 401


def test_logout_encerra(login):
    c = login("rh@ficticio.example.com")
    assert c.post(f"{URL}/logout").status_code == 204
    c.cookies.clear()
    assert c.get(f"{URL}/eu").status_code == 401


def test_usuario_desligado_perde_acesso_com_sessao_aberta(login, repo):
    c = login("rh@ficticio.example.com")
    repo.usuarios[1].ativo = False
    assert c.get(f"{URL}/eu").status_code == 401


def test_auditoria_de_login_sem_dado_pessoal(login, client, repo):
    client.post(f"{URL}/login", json={"email": "rh@ficticio.example.com", "senha": "errada"})
    login("rh@ficticio.example.com")
    assert [a["acao"] for a in repo.auditoria] == ["login_falha", "login"]
    assert "ficticio.example.com" not in str(repo.auditoria)


def test_erro_de_validacao_nao_ecoa_o_valor(client):
    r = client.post(f"{URL}/login", json={"email": "nao-e-email", "senha": "segredo-xyz"})
    assert r.status_code == 422
    assert "segredo-xyz" not in r.text and "nao-e-email" not in r.text
