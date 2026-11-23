"""Geração do dossiê formal: PDF, Excel, numeração RP-AAAA-NNNNNN e SHA-256.

Uso pela API:
    numero = proximo_numero(conexao, ano_de_emissao(agora))   # dentro da transação
    arquivos = gerar_dossie(conteudo, perfil, DadosDossie(numero=numero, ...))
"""

from documentos.conteudo import PERFIS_COM_CONTEXTO, ConteudoInvalido, contexto_permitido
from documentos.gerador import gerar_dossie
from documentos.modelos import (
    Arquivos,
    DadosDossie,
    Grafico,
    ParametroAplicado,
    Serie,
    Tabela,
)
from documentos.numeracao import ano_de_emissao, formatar_numero, proximo_numero
from documentos.revisao import Achado, RevisaoBloqueada, revisar

__all__ = [
    "PERFIS_COM_CONTEXTO",
    "Achado",
    "Arquivos",
    "ConteudoInvalido",
    "DadosDossie",
    "Grafico",
    "ParametroAplicado",
    "RevisaoBloqueada",
    "Serie",
    "Tabela",
    "ano_de_emissao",
    "contexto_permitido",
    "formatar_numero",
    "gerar_dossie",
    "proximo_numero",
    "revisar",
]
