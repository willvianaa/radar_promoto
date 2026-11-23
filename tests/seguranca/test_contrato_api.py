"""Contrato da API (api/openapi.yaml) sem dado pessoal ou sensível em URL (CLAUDE.md §2.1 e §3).

Query string e caminho vão para logs de proxy, histórico do navegador e cabeçalho Referer. Por
isso nenhum parâmetro de caminho ou de query pode carregar CPF, humor, motivo, senha ou token.
Exceções já conhecidas ficam listadas aqui, com o risco correspondente de docs/lgpd/00-diagnostico.md;
um parâmetro novo fora da lista reprova o teste.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parents[2]
CONTRATO = yaml.safe_load((RAIZ / "api" / "openapi.yaml").read_text(encoding="utf-8"))
METODOS = {"get", "post", "put", "patch", "delete"}

SENSIVEIS = ("cpf", "humor", "doente", "motivo", "senha", "password", "token", "segredo", "secret")

# (local, nome) aceitos por decisão registrada. Mudou? Atualize o diagnóstico junto.
EXCECOES_URL = {
    # R5: busca por "nome ou parte do CPF" na query. Pendente de decisão da sessão-mãe (contrato).
    ("query", "q"),
    # Nome do supervisor como filtro: dado pessoal de baixo risco (função, não do colaborador avaliado).
    ("query", "supervisor"),
}

# Onde o CPF pode aparecer sem máscara: só no Raio-X individual (CLAUDE.md §3).
CPF_COMPLETO_PERMITIDO = {"components.schemas.RaioX.properties.colaborador.allOf.1"}


def _resolver(obj):
    if isinstance(obj, dict) and "$ref" in obj:
        alvo = CONTRATO
        for parte in obj["$ref"].lstrip("#/").split("/"):
            alvo = alvo[parte]
        return alvo
    return obj


def _parametros():
    for caminho, ops in CONTRATO["paths"].items():
        comuns = ops.get("parameters", [])
        for metodo, op in ops.items():
            if metodo not in METODOS:
                continue
            for p in [*comuns, *op.get("parameters", [])]:
                p = _resolver(p)
                yield caminho, metodo, p


def _propriedades(obj, trilha=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "properties" and isinstance(v, dict):
                for nome in v:
                    yield ".".join(trilha), nome
            yield from _propriedades(v, (*trilha, str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _propriedades(v, (*trilha, str(i)))


def test_contrato_tem_parametros():
    assert len(list(_parametros())) > 10


def test_nenhum_parametro_de_url_com_dado_sensivel():
    problemas = []
    for caminho, metodo, p in _parametros():
        local, nome = p.get("in"), p.get("name", "")
        if local not in ("query", "path", "header"):
            continue
        if (local, nome) in EXCECOES_URL:
            continue
        # Pelo nome do parâmetro: a descrição pode citar o termo para proibi-lo ("nunca o CPF").
        if any(s in nome.lower() for s in SENSIVEIS):
            problemas.append(f"{metodo.upper()} {caminho}: {local} '{nome}'")
    assert not problemas, "dado sensível na URL: " + "; ".join(problemas)


def test_excecoes_ainda_existem():
    # Se a exceção sumiu do contrato (ex.: R5 resolvido), tire-a da lista para não acobertar outra.
    atuais = {(p.get("in"), p.get("name")) for _, _, p in _parametros()}
    assert EXCECOES_URL <= atuais


@pytest.mark.parametrize("caminho", [c for c in CONTRATO["paths"] if "{" in c])
def test_identificador_no_caminho_nunca_e_cpf(caminho):
    for nome in [s.strip("{}") for s in caminho.split("/") if s.startswith("{")]:
        assert "cpf" not in nome.lower()
    for _, _, p in _parametros():
        if p.get("in") == "path" and p.get("name") == "id":
            assert "opaco" in p.get("description", "").lower()


def test_cpf_completo_so_no_raio_x():
    onde = {trilha for trilha, nome in _propriedades(CONTRATO) if nome == "cpf"}
    assert onde <= CPF_COMPLETO_PERMITIDO, f"campo 'cpf' sem máscara fora do Raio-X: {sorted(onde - CPF_COMPLETO_PERMITIDO)}"


def test_listas_usam_cpf_mascarado():
    assert any(nome == "cpf_mascarado" for _, nome in _propriedades(CONTRATO["components"]["schemas"]["ColaboradorResumo"]))


def test_senha_so_no_corpo_do_login():
    onde = {trilha.split(".content")[0] for trilha, nome in _propriedades(CONTRATO["paths"]) if nome == "senha"}
    assert onde == {"/auth/login.post.requestBody"}
    corpo = CONTRATO["paths"]["/auth/login"]["post"]["requestBody"]["content"]
    assert set(corpo) == {"application/json"}


def test_sessao_por_cookie_e_nao_por_query():
    for nome, esquema in CONTRATO["components"]["securitySchemes"].items():
        assert esquema.get("in") != "query", f"esquema '{nome}' põe credencial na URL"


def test_humor_individual_e_opcional_no_raio_x():
    # Perfis sem acesso ao contexto de acompanhamento recebem o Raio-X sem humor (matriz de permissões).
    humor = CONTRATO["components"]["schemas"]["RaioX"]["properties"]["humor"]
    assert humor.get("nullable") is True
    assert "humor" not in CONTRATO["components"]["schemas"]["RaioX"].get("required", [])


def test_documentacao_interativa_desligada():
    from api.app.main import app

    assert app.docs_url is None and app.redoc_url is None
