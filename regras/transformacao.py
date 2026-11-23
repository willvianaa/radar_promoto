"""Transformação raw → core, uma função por origem.

Entrada: linhas cruas (``raw.linha.dados``) como dicionários com os nomes de coluna da origem
(ver ``schemas/``). Os nomes de coluna são comparados normalizados (sem acento, maiúsculas).
Saída: registros de ``regras.tipos``. Nenhuma função faz E/S nem registra dado pessoal em log.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import date, timedelta

from . import util
from .tipos import (
    Aderencia,
    Atividade,
    Colaborador,
    Falta,
    Foto,
    Humor,
    Pdoh,
    Posicao,
    Visita,
)

DURACAO_JORNADA_MIN = 9 * 60 + 30  # fim = início + 9h30 (CLAUDE.md §4.1)
MARCAS_QUINZENAIS = ("WD-40", "WD40", "BOTAFOGO")  # contrato só em semana par (§4.3)


class Linha:
    """Acesso a uma linha crua por nome de coluna normalizado."""

    def __init__(self, dados: dict):
        self._d = {util.norm_nome(k): v for k, v in dados.items()}

    def get(self, *nomes: str):
        for n in nomes:
            v = self._d.get(util.norm_nome(n))
            if v is not None and v != "":
                return v
        return None

    def txt(self, *nomes: str) -> str:
        v = self.get(*nomes)
        return "" if v is None else str(v).strip()


# ---------------------------------------------------------------- identificação

def tipo_pdv(nome: str) -> str:
    n = util.norm_nome(nome)
    if "NAO OPERACIONAL" in n:
        return "nao_operacional"
    if "REUNIAO" in n:
        return "reuniao"
    return "loja"


class Cadastro:
    """Índice do cadastro de colaboradores para herdar CPF pelo nome normalizado (§3)."""

    def __init__(self, colaboradores: Iterable[Colaborador] = ()):
        self.por_cpf: dict[str, Colaborador] = {}
        self._por_nome: dict[str, set[str]] = {}
        for c in colaboradores:
            if c.cpf_pendente:
                continue
            self.por_cpf[c.cpf] = c
            self._por_nome.setdefault(c.nome_norm, set()).add(c.cpf)

    def cpf_por_nome(self, nome: str) -> str:
        """CPF do cadastro para o nome; '' se não há ou se há homônimos (ambíguo)."""
        cpfs = self._por_nome.get(util.norm_nome(nome), set())
        return next(iter(cpfs)) if len(cpfs) == 1 else ""

    def resolver(self, nome: str, cpf_origem=None) -> tuple[str, bool]:
        """(chave, cpf_pendente). Ordem: CPF da origem → CPF do cadastro pelo nome → 'N:'+nome."""
        cpf = util.normaliza_cpf(cpf_origem)
        if cpf:
            return cpf, False
        cpf = self.cpf_por_nome(nome)
        if cpf:
            return cpf, False
        return "N:" + util.norm_nome(nome), True


def jornada_do_texto(texto: str) -> tuple[int | None, int | None]:
    """'INÍCIO 07H' → (420, 990). Sem jornada reconhecida → (None, None) = escala padrão."""
    m = re.search(r"INICIO (\d{1,2})H", util.norm_nome(texto))
    if not m:
        return None, None
    ini = int(m.group(1)) * 60
    return ini, ini + DURACAO_JORNADA_MIN


# ---------------------------------------------------------------- origens

def transforma_colaboradores(linhas: Iterable[dict]) -> list[Colaborador]:
    out: dict[str, Colaborador] = {}
    for d in linhas:
        r = Linha(d)
        nome = r.txt("NOME DO COLABORADOR")
        if not nome:
            continue
        cpf = util.normaliza_cpf(r.get("CPF"))
        ini, fim = jornada_do_texto(r.txt("JORNADA"))
        c = Colaborador(
            cpf=cpf or "N:" + util.norm_nome(nome),
            nome=nome,
            nome_norm=util.norm_nome(nome),
            uf=util.norm_nome(r.txt("UF"))[:2],
            cidade=r.txt("CIDADE"),
            supervisor=r.txt("COLABORADOR SUPERIOR"),
            ativo=util.norm_nome(r.txt("USUARIO ATIVO")) not in ("NAO", "N", "0", "FALSE"),
            jornada_texto=r.txt("JORNADA"),
            jornada_ini=ini,
            jornada_fim=fim,
            cpf_pendente=not cpf,
        )
        out[c.cpf] = c
    # supervisor_cpf: o supervisor também é colaborador cadastrado, quando o nome bate
    cad = Cadastro(out.values())
    for c in out.values():
        c.supervisor_cpf = cad.cpf_por_nome(c.supervisor) or None
    return list(out.values())


def transforma_operacao(linhas: Iterable[dict], cad: Cadastro) -> tuple[list[Visita], int]:
    """Visitas (uma por linha com HORA ENTRADA) e quantas linhas foram descartadas.

    PDV NÃO OPERACIONAL (almoço) e REUNIÃO ficam no core com o ``tipo_pdv`` próprio; é o motor que
    os tira de visita/ócio/deslocamento. Linhas sem HORA ENTRADA (visita não iniciada) e duplicadas
    pela chave única são descartadas.
    """
    visitas, descartadas, vistos = [], 0, set()
    for d in linhas:
        r = Linha(d)
        nome = r.txt("COLABORADOR")
        ent = r.get("HORA ENTRADA")
        data = util.parse_data(r.get("DATA DO ROTEIRO")) or util.parse_data(ent)
        cin = util.parse_hora(ent)
        if not nome or data is None or cin is None:
            descartadas += 1
            continue
        pdv = r.txt("PONTO DE VENDA")
        cout = util.parse_hora(r.get("HORA SAIDA"))
        sis = util.norm_nome(r.txt("CHECKOUT SISTEMA"))
        auto = sis in ("SIM", "S") or bool(re.search(r"SISTEMA|AUTOM", sis))
        cpf, _ = cad.resolver(nome)
        chave = (cpf, pdv, data, cin, cout)
        if chave in vistos:
            descartadas += 1
            continue
        vistos.add(chave)
        visitas.append(Visita(cpf, data, pdv, tipo_pdv(pdv), cin, cout, auto))
    return visitas, descartadas


_RE_EXPIRADA = re.compile(r"EXPIR|NAO REALIZ|NAO RESPOND|PERDID|NAO EXECUT")
_RE_RESPONDIDA = re.compile(r"RESPOND|REALIZ|CONCLU|FINALIZ|EXECUT|CRITIC")


def status_pesquisa(texto: str) -> str:
    """R respondida/realizada, E expirada/não realizada, P pendente (E tem precedência sobre R)."""
    t = util.norm_nome(texto)
    if _RE_EXPIRADA.search(t):
        return "E"
    if _RE_RESPONDIDA.search(t):
        return "R"
    return "P"


def transforma_atividades(linhas: Iterable[dict], cad: Cadastro) -> list[Atividade]:
    out: dict[str, Atividade] = {}
    for d in linhas:
        r = Linha(d)
        nome = r.txt("Responsável")
        data = util.parse_data(r.get("Solicitação"))
        if not nome or data is None:
            continue
        form = r.txt("Formulário")
        m = re.match(r"^\[(.*?)\]\s*(.*)$", form)
        cliente, tipo = (m.group(1), m.group(2)) if m else ("", form)
        idv = r.txt("ID") or f"{util.norm_nome(nome)}|{data}|{form}|{r.txt('PDV')}"
        fotos = util.parse_num(r.get("Total de Fotos"))
        just = util.norm_nome(r.txt("Justificada?"))
        cpf, _ = cad.resolver(nome)
        out[idv] = Atividade(
            idv, cpf, data, r.txt("PDV"), cliente, tipo, status_pesquisa(r.txt("Status")),
            justificada=None if not just else just in ("SIM", "S"),
            fotos=None if fotos is None else int(fotos),
        )
    return list(out.values())


def transforma_humor(linhas: Iterable[dict], cad: Cadastro, negativos: Iterable[str]) -> list[Humor]:
    neg = {util.norm_nome(x) for x in negativos}
    out: dict[tuple[str, date], Humor] = {}
    for d in linhas:
        r = Linha(d)
        nome, data, op = r.txt("NOME DO COLABORADOR"), util.parse_data(r.get("DATA")), r.txt("HUMOR")
        if not nome or data is None or not op:
            continue
        cpf, _ = cad.resolver(nome)
        out[(cpf, data)] = Humor(cpf, data, op, util.norm_nome(op) in neg)
    return list(out.values())


def tipo_falta(tipo: str, motivo: str = "") -> str:
    """I injustificada, J justificada, A atestado, F afastamento."""
    t = util.norm_nome(tipo + " " + motivo)
    if "ATESTADO" in t:
        return "A"
    if "AFASTAMENTO" in t:
        return "F"
    if re.search(r"INJUSTIF|NAO JUSTIF|SEM JUSTIF", t):
        return "I"
    if "JUSTIF" in t or motivo:
        return "J"
    return "I"


def transforma_faltas(linhas: Iterable[dict], cad: Cadastro) -> list[Falta]:
    out: dict[tuple[str, date, str], Falta] = {}
    for d in linhas:
        r = Linha(d)
        nome, data = r.txt("Colaborador"), util.parse_data(r.get("Data"))
        if data is None or not (nome or r.get("CPF")):
            continue
        cpf, _ = cad.resolver(nome, r.get("CPF"))
        motivo = r.txt("Motivo")
        t = tipo_falta(r.txt("Tipo"), "" if r.txt("Tipo") else motivo)
        dias = int(util.parse_num(r.get("Dias")) or 1) if t == "F" else 1
        for i in range(max(1, dias)):
            dia = data + timedelta(days=i)
            out[(cpf, dia, t)] = Falta(cpf, dia, t, motivo)
    return list(out.values())


def transforma_aderencia(
    linhas: Iterable[dict], cad: Cadastro, hoje: date, descartes: list[int] | None = None
) -> list[Aderencia]:
    """Uma linha por colaborador × loja × marca × semana.

    ``semana_fechada`` = a semana (segunda a domingo) terminou antes de ``hoje``. Marcas quinzenais
    (WD-40, Botafogo) têm contrato só em semana ISO par: em semana ímpar o contratado é 0.

    Linha inválida (semana ISO 0/54, ano impossível, campo ausente) não derruba o lote: é descartada e,
    se ``descartes`` for passado, o número da linha (a partir de 0) é acrescentado a ele
    (``linhas_descartadas`` da carga).
    """
    out = []
    for n, d in enumerate(linhas):
        r = Linha(d)
        ano, sem = util.parse_num(r.get("ANO")), util.parse_num(r.get("SEMANA"))
        ct, rz = util.parse_num(r.get("CONTRATADAS")), util.parse_num(r.get("REALIZADAS"))
        loja = r.txt("LOJA")
        seg = None
        if ano is not None and sem is not None and ct is not None and loja:
            try:
                seg = util.segunda_da_semana_iso(int(ano), int(sem))
            except (ValueError, OverflowError):
                seg = None
        if seg is None:
            if descartes is not None:
                descartes.append(n)
            continue
        marca = r.txt("MARCA")
        if int(sem) % 2 == 1 and any(q in util.norm_nome(marca) for q in MARCAS_QUINZENAIS):
            ct = 0
        nome = r.txt("COLABORADOR")
        sem_colab = not nome or util.norm_nome(nome) == "SEM COLABORADOR"
        cpf = None if sem_colab else cad.resolver(nome)[0]
        uf = util.norm_nome(r.txt("UF"))[:2] or util.norm_nome(loja)[:2]
        aj = util.parse_num(r.get("AJUSTADAS"))
        out.append(Aderencia(
            cpf, loja, marca, uf, seg, int(ct), int(rz or 0),
            semana_fechada=seg + timedelta(days=6) < hoje,
            ajustadas=None if aj is None else int(aj),
        ))
    return out


def transforma_pdoh(
    por_categoria: dict[str, Iterable[dict]], cad: Cadastro, periodo_ini: date, periodo_fim: date
) -> list[Pdoh]:
    """Junta os quatro rankings (prod, desl, ocio, hnr) em uma linha por colaborador e período."""
    campo = {"prod": "seg_produtivo", "desl": "seg_deslocamento", "ocio": "seg_ocio", "hnr": "seg_nao_registrado"}
    acc: dict[str, Pdoh] = {}
    for cat, linhas in por_categoria.items():
        if cat not in campo:
            raise ValueError(f"categoria PDOH desconhecida: {cat}")
        for d in linhas:
            r = Linha(d)
            nome = r.txt("Colaborador")
            seg = util.parse_num(r.get("Segundos"))
            if not nome or seg is None:
                continue
            cpf, _ = cad.resolver(nome)
            p = acc.setdefault(cpf, Pdoh(cpf, periodo_ini, periodo_fim))
            setattr(p, campo[cat], getattr(p, campo[cat]) + int(seg))
            p.dias = max(p.dias, int(util.parse_num(r.get("Dias")) or 0))
    return list(acc.values())


def transforma_fotos(linhas: Iterable[dict], cad: Cadastro) -> list[Foto]:
    """Manifesto das fotos. ``SHA256`` (e ``PHASH``) vêm do ingestor; sem hash a foto não entra."""
    out = []
    for d in linhas:
        r = Linha(d)
        nome, data = r.txt("Colaborador"), util.parse_data(r.get("Data"))
        sha = r.txt("SHA256", "Hash").lower()
        if not nome or data is None or not sha:
            continue
        ph = r.get("PHASH")
        out.append(Foto(
            cad.resolver(nome)[0], data, util.parse_hora(r.get("Hora")), r.txt("PDV"),
            r.txt("ID da pesquisa") or None, sha,
            phash=int(ph) if ph not in (None, "") else None,
            lat=util.parse_num(r.get("Latitude")), lon=util.parse_num(r.get("Longitude")),
            pdv_lat=util.parse_num(r.get("Latitude da loja")), pdv_lon=util.parse_num(r.get("Longitude da loja")),
            atividade_tipo=r.txt("Formulário"),
        ))
    return out


def transforma_posicoes(linhas: Iterable[dict], cad: Cadastro) -> list[Posicao]:
    out = []
    for d in linhas:
        r = Linha(d)
        nome, data = r.txt("Colaborador"), util.parse_data(r.get("Data"))
        dist = util.parse_num(r.get("Distância", "DISTANCIA"))
        if not nome or data is None or dist is None:
            continue
        out.append(Posicao(cad.resolver(nome)[0], data, util.parse_hora(r.get("Hora")), r.txt("PDV"), dist))
    return out
