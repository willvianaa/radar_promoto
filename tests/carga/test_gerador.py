"""Garantias do gerador sintético (volume pequeno, rápido para o CI)."""

import re

from regras import motor
from tests.carga.gerador import _cpf_ficticio, gerar_base


def _valido(cpf: str) -> bool:
    n = [int(c) for c in cpf]
    for t in (9, 10):
        dv = (sum(v * (t + 1 - k) for k, v in enumerate(n[:t])) * 10 % 11) % 10
        if dv != n[t]:
            return False
    return True


def test_deterministico_por_semente():
    _, a = gerar_base(30, 14, semente=1)
    _, b = gerar_base(30, 14, semente=1)
    _, c = gerar_base(30, 14, semente=2)
    assert a.impressao == b.impressao
    assert a.impressao != c.impressao


def test_cpfs_ficticios_e_invalidos():
    base, _ = gerar_base(200, 7, semente=3)
    cpfs = [c.cpf for c in base.colaboradores]
    assert len(set(cpfs)) == 200
    assert all(re.fullmatch(r"000\d{8}", c) and not _valido(c) for c in cpfs)
    assert not any(_valido(_cpf_ficticio(i)) for i in range(1, 2000))


def test_nomes_unicos_e_volumes():
    base, meta = gerar_base(100, 30, semente=4)
    assert len({c.nome for c in base.colaboradores}) == 100
    assert meta.contagens["visitas"] > 100 * 15
    assert sum(meta.perfis.values()) == 100


def test_motor_roda_e_exercita_varios_alertas():
    base, meta = gerar_base(300, 45, semente=5)
    res = motor.calcular(base, None, meta.ini, meta.fim)
    assert len(res) > 250
    tipos = {a.tipo for r in res for a in r.alertas}
    assert {"jor", "pesq", "ader", "falta", "foto", "rota"} <= tipos
    assert {r.nivel for r in res} >= {"N", "T"}
