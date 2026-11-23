"""Tipos de entrada e saída da geração do dossiê."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime

from documentos.numeracao import NUMERO_RE


@dataclass(frozen=True)
class Serie:
    nome: str
    valores: tuple[float, ...]


@dataclass(frozen=True)
class Grafico:
    """Gráfico de barras de um bloco. Categorias e séries devem ter o mesmo tamanho."""

    categorias: tuple[str, ...]
    series: tuple[Serie, ...]

    def __post_init__(self) -> None:
        if not self.categorias or not self.series:
            raise ValueError("gráfico sem categorias ou séries")
        for s in self.series:
            if len(s.valores) != len(self.categorias):
                raise ValueError(f"série '{s.nome}' com tamanho diferente das categorias")


@dataclass(frozen=True)
class Tabela:
    """Tabela de apoio de um bloco. Valores já formatados (datas dd/mm/aaaa, percentuais)."""

    colunas: tuple[str, ...]
    linhas: tuple[tuple[object, ...], ...]
    grafico: Grafico | None = None

    def __post_init__(self) -> None:
        for linha in self.linhas:
            if len(linha) != len(self.colunas):
                raise ValueError("linha com número de colunas diferente do cabeçalho")


@dataclass(frozen=True)
class ParametroAplicado:
    nome: str
    valor: str
    versao: int
    vigente_desde: date


@dataclass(frozen=True)
class DadosDossie:
    """Identificação e rastreio do documento. O texto vem em `conteudo`, não aqui."""

    numero: str
    emitido_em: datetime
    emissor: str
    colaborador: str
    cpf: str
    periodo_ini: date
    periodo_fim: date
    parametro_versao: int
    parametros: tuple[ParametroAplicado, ...]
    uf: str | None = None
    supervisor: str | None = None
    relato: str | None = None
    tabelas: Mapping[str, Tabela] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not NUMERO_RE.match(self.numero):
            raise ValueError("número fora do padrão RP-AAAA-NNNNNN")
        if self.emitido_em.tzinfo is None:
            raise ValueError("emitido_em precisa ter fuso")


@dataclass(frozen=True)
class Arquivos:
    numero: str
    codigo_verificacao: str
    nome_pdf: str
    pdf: bytes
    sha256_pdf: str
    nome_xlsx: str
    xlsx: bytes
    sha256_xlsx: str
