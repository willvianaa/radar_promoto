import pytest

from documentos import RevisaoBloqueada, revisar
from documentos.revisao import garantir_revisao


def test_conteudo_limpo_passa(conteudo):
    assert revisar(conteudo, "Relato ficticio sem termos proibidos.") == []


def test_termo_proibido_em_bloco_aponta_o_campo(conteudo):
    conteudo["blocos"][1]["texto"] = "O colaborador é um detrator da equipe."
    achados = revisar(conteudo)
    assert [(a.campo, a.termo) for a in achados] == [("conteudo.blocos[2].texto", "detrat")]


@pytest.mark.parametrize("texto", ["Má-fé comprovada", "Ele MENTIU ao registrar", "uma fraude", "agiu de forma irresponsável"])
def test_detecta_variacoes_com_acento_e_caixa(conteudo, texto):
    conteudo["impacto"] = texto
    assert revisar(conteudo), texto


def test_nao_bloqueia_palavras_parecidas(conteudo):
    conteudo["impacto"] = "Há culpa compartilhada pela operação e registros de jornada."
    assert revisar(conteudo) == []


def test_nome_de_sistema_e_bloqueado(conteudo):
    conteudo["intro"] = "Dados extraídos de Postgres na rodada de hoje."
    assert [a.termo for a in revisar(conteudo)] == ["postgres"]


def test_relato_tambem_e_revisado(conteudo):
    achados = revisar(conteudo, "A supervisão diz que ele mentiu.")
    assert [(a.campo, a.termo) for a in achados] == [("relato", "mentiu")]


def test_garantir_revisao_bloqueia_sem_expor_trecho(conteudo):
    conteudo["impacto"] = "Trecho sensível com culpado no meio."
    with pytest.raises(RevisaoBloqueada) as erro:
        garantir_revisao(conteudo)
    assert "culpad" in str(erro.value)
    assert "Trecho sensível" not in str(erro.value)
