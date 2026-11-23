import hashlib
import io
import re
from openpyxl import load_workbook

import pytest

from documentos import ConteudoInvalido, DadosDossie, RevisaoBloqueada, gerar_dossie
from documentos.pdf import montar_pdf


def _paginas(pdf: bytes) -> int:
    return len(re.findall(rb"/Type\s*/Page\b", pdf))


def test_gera_arquivos_com_nomes_e_hashes(conteudo, dados):
    arquivos = gerar_dossie(conteudo, "rh", dados)

    assert arquivos.nome_pdf == "Dossiê - Colaborador Ficticio Um.pdf"
    assert arquivos.nome_xlsx == "Dossiê - Colaborador Ficticio Um.xlsx"
    assert arquivos.pdf.startswith(b"%PDF")
    assert arquivos.sha256_pdf == hashlib.sha256(arquivos.pdf).hexdigest()
    assert arquivos.sha256_xlsx == hashlib.sha256(arquivos.xlsx).hexdigest()
    assert arquivos.numero == "RP-2026-000001"


def test_pdf_e_deterministico(conteudo, dados):
    primeiro = gerar_dossie(conteudo, "rh", dados)
    segundo = gerar_dossie(conteudo, "rh", dados)
    assert primeiro.sha256_pdf == segundo.sha256_pdf
    assert primeiro.codigo_verificacao == segundo.codigo_verificacao


def test_pdf_tem_confidencial_em_todas_as_paginas(conteudo, dados):
    pdf = montar_pdf(conteudo, dados, contexto_visivel=True, codigo_verificacao="0000-0000-0000-0000",
                     comprimir=False)
    paginas = _paginas(pdf)
    assert paginas >= 2
    assert pdf.count(b"CONFIDENCIAL") == paginas
    assert pdf.count(b"baseados em registros operacionais") == paginas
    assert pdf.count(b"RP-2026-000001") >= paginas
    assert b"Sendo assim," in pdf


def test_contexto_so_para_perfil_autorizado(conteudo, dados):
    com = montar_pdf(conteudo, dados, contexto_visivel=True, codigo_verificacao="X", comprimir=False)
    sem = montar_pdf(conteudo, dados, contexto_visivel=False, codigo_verificacao="X", comprimir=False)
    assert b"Contexto de acompanhamento" in com
    assert b"Contexto de acompanhamento" not in sem


def test_gerar_sem_permissao_remove_contexto_do_excel(conteudo, dados):
    autorizado = gerar_dossie(conteudo, "rh", dados)
    sem_permissao = gerar_dossie(conteudo, "dp", dados)

    nomes_com = load_workbook(io.BytesIO(autorizado.xlsx)).sheetnames
    nomes_sem = load_workbook(io.BytesIO(sem_permissao.xlsx)).sheetnames
    assert "Contexto" in nomes_com
    assert "Contexto" not in nomes_sem
    assert "Contexto" not in sem_permissao.xlsx.decode("latin-1")


def test_excel_tem_abas_esperadas_sem_mesclagem(conteudo, dados):
    arquivos = gerar_dossie(conteudo, "rh", dados)
    wb = load_workbook(io.BytesIO(arquivos.xlsx))
    assert wb.sheetnames[:2] == ["Identificação", "Relatos"]
    assert "Parâmetros" in wb.sheetnames
    assert any(nome.startswith("Bloco 1") for nome in wb.sheetnames)
    for ws in wb.worksheets:
        assert not ws.merged_cells.ranges
    parametros = wb["Parâmetros"]
    assert parametros.max_row == 1 + len(dados.parametros)


def test_revisao_bloqueia_antes_de_gerar(conteudo, dados):
    conteudo["impacto"] = "O colaborador agiu com má-fé."
    with pytest.raises(RevisaoBloqueada):
        gerar_dossie(conteudo, "rh", dados)


def test_conteudo_fora_do_contrato_e_recusado(conteudo, dados):
    conteudo["consideracoes_finais"] = "Os registros indicam encerramento antecipado."
    with pytest.raises(ConteudoInvalido, match="Sendo assim"):
        gerar_dossie(conteudo, "rh", dados)


def test_mais_de_cinco_blocos_e_recusado(conteudo, dados):
    bloco = dict(conteudo["blocos"][0])
    conteudo["blocos"] = [dict(bloco, chave=f"b{i}") for i in range(6)]
    with pytest.raises(ConteudoInvalido, match="no máximo 5"):
        gerar_dossie(conteudo, "rh", dados)


def test_numero_fora_do_padrao_e_recusado(dados):
    with pytest.raises(ValueError):
        DadosDossie(**{**dados.__dict__, "numero": "RP-26-1"})


def test_nome_do_arquivo_sem_caracteres_proibidos(conteudo, dados):
    dados_com_nome = DadosDossie(**{**dados.__dict__, "colaborador": 'Colaborador: "Teste" / Um'})
    arquivos = gerar_dossie(conteudo, "rh", dados_com_nome)
    assert arquivos.nome_pdf == "Dossiê - Colaborador Teste Um.pdf"
