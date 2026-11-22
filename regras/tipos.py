"""Registros do core em memória (espelham as tabelas de db/modelo.sql que o motor lê)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Colaborador:
    cpf: str  # só dígitos; 'N:'+nome_norm quando cpf_pendente
    nome: str
    nome_norm: str
    uf: str = ""
    cidade: str = ""
    supervisor: str = ""  # nome do supervisor (exibição)
    supervisor_cpf: str | None = None
    ativo: bool = True
    jornada_texto: str = ""
    jornada_ini: int | None = None  # minutos desde 00:00
    jornada_fim: int | None = None
    cpf_pendente: bool = False


@dataclass
class Visita:
    cpf: str
    data: date
    pdv: str
    tipo_pdv: str  # loja | nao_operacional | reuniao
    checkin: int  # minutos
    checkout: int | None
    checkout_auto: bool


@dataclass
class Atividade:
    id_origem: str
    cpf: str
    data: date
    pdv: str
    cliente: str
    tipo: str
    status: str  # R | E | P
    justificada: bool | None = None
    fotos: int | None = None


@dataclass
class Humor:
    cpf: str
    data: date
    opcao: str
    negativo: bool


@dataclass
class Foto:
    cpf: str
    data: date
    hora: int | None
    pdv: str
    id_atividade: str | None
    sha256: str
    phash: int | None = None
    lat: float | None = None
    lon: float | None = None
    pdv_lat: float | None = None
    pdv_lon: float | None = None
    atividade_tipo: str = ""


@dataclass
class Falta:
    cpf: str
    data: date
    tipo: str  # I | J | A | F
    motivo: str = ""  # restrito a RH/DP; o motor nunca o repassa a textos de alerta


@dataclass
class Aderencia:
    cpf: str | None  # None = SEM COLABORADOR
    loja: str
    marca: str
    uf: str
    semana_ini: date  # segunda-feira ISO
    contratadas: int
    realizadas: int
    semana_fechada: bool
    ajustadas: int | None = None

    @property
    def realizadas_lim(self) -> int:
        """Realizadas limitadas ao contratado na linha (coluna gerada do banco)."""
        return min(self.realizadas, self.contratadas)


@dataclass
class Pdoh:
    cpf: str
    periodo_ini: date
    periodo_fim: date
    dias: int = 0
    seg_produtivo: int = 0
    seg_deslocamento: int = 0
    seg_ocio: int = 0
    seg_nao_registrado: int = 0


@dataclass
class Posicao:
    """Posição em relação à loja. Ainda sem tabela no core (ver PR)."""

    cpf: str
    data: date
    hora: int | None
    pdv: str
    dist_m: float


@dataclass
class Base:
    """Tudo que o motor lê, já no formato core."""

    colaboradores: list[Colaborador] = field(default_factory=list)
    visitas: list[Visita] = field(default_factory=list)
    atividades: list[Atividade] = field(default_factory=list)
    humor: list[Humor] = field(default_factory=list)
    fotos: list[Foto] = field(default_factory=list)
    faltas: list[Falta] = field(default_factory=list)
    aderencia: list[Aderencia] = field(default_factory=list)
    pdoh: list[Pdoh] = field(default_factory=list)
    posicoes: list[Posicao] = field(default_factory=list)
    feriados: set[tuple[date, str | None]] = field(default_factory=set)  # (data, uf | None = nacional)
