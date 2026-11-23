"""Gerador de dados SINTÉTICOS em volume real para QA de carga e desempenho.

Tudo é fictício e determinístico por semente (mesma semente + mesmos argumentos = mesma ``Base``).
Nomes são combinações de sílabas inventadas; CPFs começam em ``000`` e têm dígitos verificadores
inválidos de propósito (CLAUDE.md §2). Nenhum dado real entra aqui, nem como inspiração de valores.

Uso::

    from tests.carga.gerador import gerar_base
    base, meta = gerar_base(n_colaboradores=1000, dias=60, semente=2026)

Perfis (distribuição aproximada) controlam quais alertas aparecem, para o volume exercitar os
ramos do motor: ``normal`` (maioria), ``atrasado``, ``expirador``, ``baixa_aderencia``,
``sobrecarga`` (carga alta + queda + humor negativo), ``foto_suspeita``, ``fuga_rota``, ``faltoso``.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date, timedelta

from regras.tipos import (
    Aderencia, Atividade, Base, Colaborador, Falta, Foto, Humor, Pdoh, Posicao, Visita,
)
from regras.util import norm_nome, segunda_da_semana

SILABAS = ["ma", "ri", "to", "ne", "la", "vo", "de", "su", "ki", "pa", "lo", "be", "zu", "fa", "ro", "ti", "ga", "no", "ve", "cu"]
UFS = ["BA", "CE", "PE", "SP", "MG", "RJ", "PR", "RS", "GO", "PA"]
MARCAS = ["MARCA A", "MARCA B", "MARCA C", "MARCA D"]  # MARCA D é quinzenal (como WD-40 e Botafogo)
TIPOS_ATIV = ["Preço", "Ruptura", "Validade", "Exposição"]
HUMOR_POS = ["Feliz", "Animado", "Tranquilo", "Motivado"]
HUMOR_NEG = ["Cansado", "Sobrecarregado", "Triste", "Doente"]
PERFIS = [("normal", 0.70), ("atrasado", 0.06), ("expirador", 0.06), ("baixa_aderencia", 0.06),
          ("sobrecarga", 0.04), ("foto_suspeita", 0.03), ("fuga_rota", 0.02), ("faltoso", 0.03)]
FERIADOS_NACIONAIS_MMDD = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25)]
TABELAS = ("colaboradores", "visitas", "atividades", "humor", "fotos", "faltas", "aderencia", "pdoh", "posicoes")


@dataclass
class Meta:
    semente: int
    n_colaboradores: int
    dias: int
    ini: date
    fim: date
    hoje: date
    perfis: dict[str, int]
    contagens: dict[str, int]
    impressao: str  # hash do conteúdo, para provar determinismo


def hash_i(s: str) -> int:
    """Hash estável (o ``hash`` embutido muda a cada execução)."""
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:4], "big")


def _cpf_ficticio(i: int) -> str:
    """CPF começando em 000 com dígitos verificadores inválidos de propósito."""
    corpo = [0, 0, 0] + [int(c) for c in f"{i:06d}"]
    ds: list[int] = []
    for n in (9, 10):
        seq = corpo + ds
        soma = sum(v * (n + 1 - k) for k, v in enumerate(seq))
        dv = (soma * 10 % 11) % 10
        ds.append((dv + 1) % 10)  # +1: nunca bate com o verdadeiro
    return "".join(map(str, corpo + ds))


def _nome(rng: random.Random, usados: set[str]) -> str:
    while True:
        partes = ["".join(rng.choice(SILABAS) for _ in range(rng.randint(2, 3))).capitalize() for _ in range(3)]
        nome = " ".join(partes)
        if nome not in usados:
            usados.add(nome)
            return nome


def _escolhe_perfil(rng: random.Random) -> str:
    x, acc = rng.random(), 0.0
    for nome, p in PERFIS:
        acc += p
        if x < acc:
            return nome
    return "normal"


def _impressao(base: Base) -> str:
    h = hashlib.sha256()
    for nome in TABELAS:
        for r in getattr(base, nome):
            h.update(repr(r).encode())
    h.update(repr(sorted(base.feriados, key=lambda x: (x[0], x[1] or ""))).encode())
    return h.hexdigest()[:16]


def gerar_base(n_colaboradores: int = 1000, dias: int = 60, semente: int = 2026,
               fim: date = date(2026, 9, 25), hoje: date | None = None) -> tuple[Base, Meta]:
    """Gera uma ``Base`` coerente com ``n_colaboradores`` × ``dias`` (dias corridos até ``fim``)."""
    rng = random.Random(semente)
    ini = fim - timedelta(days=dias - 1)
    hoje = hoje or fim - timedelta(days=2)
    base = Base()
    nacionais = {(date(a, m, d), None) for a in {ini.year, fim.year} for m, d in FERIADOS_NACIONAIS_MMDD}
    base.feriados = {f for f in nacionais if ini <= f[0] <= fim}
    base.feriados.add((ini + timedelta(days=dias // 3), UFS[0]))  # um feriado estadual

    lista_dias = [ini + timedelta(days=i) for i in range(dias)]
    uteis = [d for d in lista_dias if d.weekday() < 5 and (d, None) not in base.feriados]
    semanas = sorted({segunda_da_semana(d) for d in lista_dias})
    seg_hoje = segunda_da_semana(hoje)

    usados: set[str] = set()
    perfis_cont: dict[str, int] = {}
    n_lojas = max(50, n_colaboradores // 4)
    lojas = [f"{UFS[i % len(UFS)]} / LOJA FICTICIA {i:04d}" for i in range(n_lojas)]
    supervisores = [f"Supervisor Ficticio {i:03d}" for i in range(max(1, n_colaboradores // 25))]

    for i in range(n_colaboradores):
        cpf = _cpf_ficticio(i + 1)
        nome = _nome(rng, usados)
        perfil = _escolhe_perfil(rng)
        perfis_cont[perfil] = perfis_cont.get(perfil, 0) + 1
        uf = UFS[i % len(UFS)]
        cedo = rng.random() < 0.2
        base.colaboradores.append(Colaborador(
            cpf=cpf, nome=nome, nome_norm=norm_nome(nome), uf=uf, cidade=f"Cidade {i % 40}",
            supervisor=supervisores[i % len(supervisores)], jornada_texto="INÍCIO 07H" if cedo else "",
            jornada_ini=420 if cedo else None, jornada_fim=990 if cedo else None))
        meus_pdv = [lojas[(i * 3 + k) % n_lojas] for k in range(rng.randint(3, 6))]
        ini_jorn = 420 if cedo else 480

        negativo_p = 0.55 if perfil == "sobrecarga" else 0.08
        for d in uteis:
            if perfil == "faltoso" and rng.random() < 0.12:
                base.faltas.append(Falta(cpf, d, rng.choice(["I", "I", "J", "A"])))
                continue
            if rng.random() < 0.03:  # ausência sem registro
                continue
            if rng.random() < 0.85:
                opc = rng.choice(HUMOR_NEG) if rng.random() < negativo_p else rng.choice(HUMOR_POS)
                base.humor.append(Humor(cpf, d, opc, opc in HUMOR_NEG))
            atraso = rng.randint(20, 90) if (perfil == "atrasado" and rng.random() < 0.4) else rng.randint(-10, 12)
            t = ini_jorn + atraso
            n_vis = rng.randint(3, 6)
            pdvs = [rng.choice(meus_pdv) for _ in range(n_vis)]
            auto = rng.random() < 0.04
            for k, pdv in enumerate(pdvs):
                dur = rng.randint(25, 70)
                base.visitas.append(Visita(cpf, d, pdv, "loja", t, t + dur, auto and k == n_vis - 1))
                h = hash_i(pdv)
                pdv_lat, pdv_lon = -12.9 - (h % 1000) / 1000, -38.5 - (h % 777) / 1000
                if perfil == "foto_suspeita" and rng.random() < 0.3:
                    sha, lat, lon = f"rep{i:05d}", pdv_lat + 0.01, pdv_lon  # ~1,1 km da loja
                else:
                    sha = f"s{rng.getrandbits(48):012x}"
                    lat, lon = pdv_lat + rng.uniform(-0.0008, 0.0008), pdv_lon + rng.uniform(-0.0008, 0.0008)
                base.fotos.append(Foto(cpf, d, t + dur // 2, pdv, None, sha, None, lat, lon, pdv_lat, pdv_lon, "Exposição"))
                dist = rng.uniform(250, 900) if (perfil == "fuga_rota" and rng.random() < 0.15) else rng.uniform(5, 150)
                base.posicoes.append(Posicao(cpf, d, t + 5, pdv, dist))
                t += dur + rng.randint(10, 30)
                if k == 1 and rng.random() < 0.9:  # almoço no PDV NÃO OPERACIONAL
                    base.visitas.append(Visita(cpf, d, f"{uf} / NÃO OPERACIONAL", "nao_operacional", t, t + 60, False))
                    t += 60
            prob_exp = 0.35 if perfil == "expirador" else 0.03
            for k in range(rng.randint(4, 10)):
                st = "E" if rng.random() < prob_exp else ("P" if rng.random() < 0.02 else "R")
                base.atividades.append(Atividade(f"{cpf}-{d:%m%d}-{k}", cpf, d, pdvs[k % n_vis], MARCAS[k % 4],
                                                 TIPOS_ATIV[k % 4], st, None, 1))

        carga = 60 if perfil == "sobrecarga" else rng.randint(20, 40)
        for si, seg in enumerate(semanas):
            fechada = seg < seg_hoje
            base_ader = {"baixa_aderencia": 0.7, "sobrecarga": 1.0 - 0.15 * si / max(1, len(semanas)),
                         "normal": 0.97}.get(perfil, 0.95)
            marcas = MARCAS[:2] + ([MARCAS[3]] if seg.isocalendar()[1] % 2 == 0 else [])  # D só em semana par
            for loja in meus_pdv[:3]:
                for marca in marcas:
                    ct = max(1, carga // 6)
                    rz = min(ct + 2, max(0, round(ct * min(1.0, base_ader + rng.uniform(-0.1, 0.1)))))
                    if not fechada:
                        rz //= 2
                    base.aderencia.append(Aderencia(cpf, loja, marca, uf, seg, ct, rz, fechada))

        tot = len(uteis) * 8 * 3600
        prod, desl, ocio = (int(tot * rng.uniform(a, b)) for a, b in ((0.45, 0.7), (0.1, 0.2), (0.02, 0.15)))
        base.pdoh.append(Pdoh(cpf, ini, fim, len(uteis), prod, desl, ocio, max(0, tot - prod - desl - ocio)))

    contagens = {k: len(getattr(base, k)) for k in TABELAS}
    return base, Meta(semente, n_colaboradores, dias, ini, fim, hoje, perfis_cont, contagens, _impressao(base))
