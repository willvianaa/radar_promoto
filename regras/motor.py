"""Motor de cálculo: dimensões, alertas, severidades, nível, Índice de risco, sobrecarga e leitura
cruzada com humor. Porte do protótipo (``radar_v2/engine.js`` + patches da v3), ajustado ao CLAUDE.md.

Determinístico e sem E/S: ``calcular(base, parametros, ini, fim)`` devolve um resultado por colaborador.

Humor (CLAUDE.md §4.4 e §4.7): "Humor negativo recorrente" soma 1 ponto; "Possível sobrecarga" soma 2, ou 3
quando carga de visitas e humor negativo aparecem juntos. O Índice de risco é min(100, soma das severidades × 10); as dimensões
são informativas (o humor é uma delas) e não entram nessa conta. O humor não fundamenta conclusão do dossiê (isso é do gerador de documentos).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from . import util
from .parametros import parametros_padrao, severidade
from .tipos import Base, Foto, Visita
from .util import arredonda, fmt_pct, plural

TIPOS_ALERTA = ("jor", "auto", "pesq", "exec", "ader", "falta", "foto", "rota", "sobre", "humor")
DIMENSOES = ("aderencia", "pesquisas", "pontualidade", "registro_jornada", "fotos", "presenca", "humor")


@dataclass
class Alerta:
    tipo: str
    severidade: int  # 1 baixa, 2 média, 3 alta
    titulo: str
    detalhe: str
    data_ref: date | None = None
    # Dado de saúde (LGPD art. 11): fica fora do texto; a API só entrega a perfis autorizados.
    dias_doente: int | None = None


@dataclass
class DiaJornada:
    data: date
    checkin: int
    checkout: int | None
    auto: bool
    atraso: int
    saida: int
    humor_negativo: bool
    lojas: int

    @property
    def desvio(self) -> bool:
        return bool(self.atraso or self.saida or self.auto)


@dataclass
class Resultado:
    cpf: str
    nome: str
    uf: str
    supervisor: str
    cpf_pendente: bool
    dimensoes: dict[str, int | None]
    carga_media: float | None
    queda_ader_pp: float | None
    score: int
    nivel: str  # C | A | T | N
    risco: int  # 0-100
    alertas: list[Alerta]
    cruzada: list[str]
    sobrecarga: bool
    dias: list[DiaJornada] = field(default_factory=list)
    aderencia_pct: float | None = None


def nivel_de(soma: int, n_sev3: int, p: dict) -> str:
    n = p["nivel"]
    if soma >= n["critico_soma"] or n_sev3 >= n["critico_sev3"]:
        return "C"
    if soma >= n["alto_soma"]:
        return "A"
    if soma >= n["atencao_soma"]:
        return "T"
    return "N"


def _cl(x: float) -> int:
    return max(0, min(100, arredonda(x)))


def _media(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def calcular(
    base: Base, parametros: dict | None, ini: date, fim: date
) -> list[Resultado]:
    """Calcula todos os colaboradores com registro no período [ini, fim].

    Só linhas de aderência com ``semana_fechada`` entram (a semana em andamento não gera alerta).
    """
    p = parametros or parametros_padrao()
    lim = p["limites"]
    esc_ini, esc_fim = (_hhmm(p["escala"]["ini"]), _hhmm(p["escala"]["fim"]))
    neg_set = {util.norm_nome(x) for x in p["humor_negativo"]}

    def no_periodo(d: date) -> bool:
        return ini <= d <= fim

    visitas = [v for v in base.visitas if no_periodo(v.data) and v.tipo_pdv != "nao_operacional"]  # almoço fora
    atividades = [a for a in base.atividades if no_periodo(a.data)]
    humores = [h for h in base.humor if no_periodo(h.data)]
    fotos = [f for f in base.fotos if no_periodo(f.data)]
    faltas = [f for f in base.faltas if no_periodo(f.data)]
    posicoes = [x for x in base.posicoes if no_periodo(x.data)]
    seg_ini = util.segunda_da_semana(ini)
    aderencia = [
        a for a in base.aderencia
        if a.cpf and seg_ini <= a.semana_ini <= fim and a.semana_fechada  # semana em andamento fora
    ]
    pdoh = [x for x in base.pdoh if x.periodo_ini <= fim and x.periodo_fim >= ini]
    tem_faltas = bool(faltas)
    tem_visitas = bool(visitas)

    # quem entra: todo CPF com algum registro no período
    cad = {c.cpf: c for c in base.colaboradores}
    cpfs: dict[str, None] = {}
    for fonte in (visitas, atividades, aderencia, humores, faltas, fotos, posicoes):
        for r in fonte:
            cpfs.setdefault(r.cpf, None)

    por_cpf: dict[str, dict[str, list]] = {}

    def idx(nome, lista):
        d = defaultdict(list)
        for r in lista:
            d[r.cpf].append(r)
        por_cpf[nome] = d

    for nome, lista in (("v", visitas), ("a", atividades), ("h", humores), ("f", fotos),
                        ("fl", faltas), ("ad", aderencia), ("pd", pdoh), ("po", posicoes)):
        idx(nome, lista)

    # imagem repetida: o mesmo hash em visitas diferentes (colaborador × dia × loja)
    usos: dict[str, set] = defaultdict(set)
    for f in fotos:
        usos[f.sha256].add((f.cpf, f.data, util.norm_nome(f.pdv)))

    saida_ativa = bool(p["saida_antecipada_ativa"])
    tol_atr, tol_sai = p["tolerancia_atraso_min"], p["tolerancia_saida_min"]
    res = []
    for cpf in cpfs:
        c = cad.get(cpf)
        nome = c.nome if c else (cpf[2:] if cpf.startswith("N:") else util.mascara_cpf(cpf))
        uf = (c.uf if c else "") or ""
        esc = (c.jornada_ini, c.jornada_fim) if c and c.jornada_ini is not None else (esc_ini, esc_fim)

        def feriado(d: date, uf=uf) -> bool:
            return (d, None) in base.feriados or (d, uf) in base.feriados

        # ---- humor
        hm: dict[date, bool] = {}
        doente_dias = set()
        for h in por_cpf["h"].get(cpf, []):
            hm[h.data] = hm.get(h.data, False) or (util.norm_nome(h.opcao) in neg_set)
            if util.norm_nome(h.opcao) == "DOENTE":
                doente_dias.add(h.data)
        hd = sorted(hm)
        seq = cur = n_neg = 0
        seq_fim = None
        for d in hd:
            if hm[d]:
                n_neg += 1
                cur += 1
                if cur > seq:
                    seq, seq_fim = cur, d
            else:
                cur = 0
        h_pct = n_neg / len(hd) if hd else None

        # ---- jornada
        vd: dict[date, list[Visita]] = defaultdict(list)
        for v in por_cpf["v"].get(cpf, []):
            vd[v.data].append(v)
        dias: list[DiaJornada] = []
        for d in sorted(vd):
            vs = sorted(vd[d], key=lambda v: v.checkin)
            last = vs[-1]
            man = [v for v in vs if not v.checkout_auto and v.checkout is not None]
            lo = max((v.checkout for v in man), default=None)
            first = vs[0].checkin
            fer = feriado(d)
            atraso = first - esc[0] if (not fer and first > esc[0] + tol_atr) else 0
            saida = esc[1] - lo if (saida_ativa and not fer and not last.checkout_auto and lo is not None
                                    and lo < esc[1] - tol_sai) else 0
            dias.append(DiaJornada(d, first, None if last.checkout_auto else lo, any(v.checkout_auto for v in vs),
                                   atraso, saida, hm.get(d) is True, len({v.pdv for v in vs if v.tipo_pdv == "loja"})))
        trab = len(dias)
        n_atr = sum(1 for x in dias if x.atraso)
        n_sai = sum(1 for x in dias if x.saida)
        n_auto = sum(1 for x in dias if x.auto)

        # ---- pesquisas
        ps = por_cpf["a"].get(cpf, [])
        prog = len(ps)
        exp = sum(1 for a in ps if a.status == "E")
        pct_exp = exp / prog if prog else None
        sem_p: dict[date, list[int]] = defaultdict(lambda: [0, 0, 0])  # semana → [prog, resp, exp]
        dia_p: dict[date, list[int]] = defaultdict(lambda: [0, 0, 0])
        for a in ps:
            for acc in (sem_p[util.segunda_da_semana(a.data)], dia_p[a.data]):
                acc[0] += 1
                acc[1] += a.status == "R"
                acc[2] += a.status == "E"
        sem_exec = sorted(d for d, (pg, rs, _) in dia_p.items() if pg > 0 and rs == 0 and d in vd and not feriado(d))

        # ---- aderência (semanas fechadas; realizadas limitadas ao contratado em cada linha)
        grupos: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])
        semanas: dict[date, dict] = {}
        for a in por_cpf["ad"].get(cpf, []):
            g = grupos[(a.uf, a.loja, a.marca)]
            g[0] += a.contratadas
            g[1] += a.realizadas_lim
            s = semanas.setdefault(a.semana_ini, {"ct": 0, "rz": 0, "lojas": set()})
            s["ct"] += a.contratadas
            s["rz"] += a.realizadas_lim
            if a.contratadas > 0:
                s["lojas"].add(a.loja)
        baixo = []
        for (_uf, loja, marca), (ct, rz) in grupos.items():
            x = rz / ct if ct else None
            if x is None:
                continue
            st = "severa" if x * 100 < p["meta1"] else "abaixo" if x * 100 < p["meta2"] else "ok"
            if st != "ok":
                baixo.append({"loja": loja, "marca": marca, "ct": ct, "rz": rz, "pend": max(0, ct - rz), "pct": x, "st": st})
        ct_tot = sum(g[0] for g in grupos.values())
        rz_tot = sum(g[1] for g in grupos.values())
        ad_pct = rz_tot / ct_tot if ct_tot else None
        pend_baixo = sum(b["pend"] for b in baixo)
        aw = [(d, s["ct"], s["rz"], len(s["lojas"]), s["rz"] / s["ct"] if s["ct"] else None)
              for d, s in sorted(semanas.items())]
        carga_media = _media(w[1] for w in aw) if aw else None
        queda = (aw[0][4] - aw[-1][4]) if len(aw) >= 2 and aw[0][4] is not None and aw[-1][4] is not None else 0.0
        queda_pp = queda * 100 if aw else None
        max_lojas = max((w[3] for w in aw), default=0)

        # ---- faltas
        fl = sorted(por_cpf["fl"].get(cpf, []), key=lambda f: f.data)
        f_i = sum(1 for f in fl if f.tipo == "I")
        f_j = sum(1 for f in fl if f.tipo == "J")
        f_a = sum(1 for f in fl if f.tipo == "A")

        # ---- fotos
        fot_ind: list[tuple[Foto, list[str]]] = []
        fotos_p = por_cpf["f"].get(cpf, [])
        for f in fotos_p:
            m = []
            if len(usos[f.sha256]) > 1:
                m.append("Imagem repetida em outra visita")
            if None not in (f.lat, f.lon, f.pdv_lat, f.pdv_lon):
                ds = util.haversine_m(f.lat, f.lon, f.pdv_lat, f.pdv_lon)
                if ds > p["dist_foto_m"]:
                    m.append(f"Captura a {round(ds)} m da loja")
            if tem_visitas and f.hora is not None and f.data in vd:
                nl = util.norm_nome(f.pdv)
                at = [v for v in vd[f.data] if util.norm_nome(v.pdv) == nl]
                if at and not any(f.hora >= v.checkin - 5 and (v.checkout is None or v.checkout_auto or f.hora <= v.checkout + 5)
                                  for v in at):
                    m.append("Fora do horário da visita")
            if m:
                fot_ind.append((f, m))

        # ---- rota
        rt = [x for x in por_cpf["po"].get(cpf, []) if x.dist_m > p["cerca_rota_m"]]
        rt_dias = len({x.data for x in rt})
        rt_max = max((x.dist_m for x in rt), default=0)

        # ---- PDOH (contexto de sobrecarga)
        pds = por_cpf["pd"].get(cpf, [])
        pd = None
        if pds:
            tot = {k: sum(getattr(x, k) for x in pds) for k in
                   ("seg_produtivo", "seg_deslocamento", "seg_ocio", "seg_nao_registrado")}
            soma = sum(tot.values())
            if soma > 0:
                pd = {**tot, "tot": soma}

        lojas_atend = {a.pdv for a in ps if a.pdv} | {v.pdv for v in por_cpf["v"].get(cpf, []) if v.tipo_pdv == "loja"} \
            | {b["loja"] for b in baixo}
        n_lojas = len({x for x in lojas_atend if x})

        # ================= alertas
        A: list[Alerta] = []

        def add(tipo, sev, tit, det, data_ref=None, A=A, dias_doente=None):
            A.append(Alerta(tipo, sev, tit, det, data_ref, dias_doente))

        s = severidade(n_atr, lim["atraso"])
        if s:
            add("jor", s, "Atrasos no check-in",
                f"{plural(n_atr, 'dia', 'dias')} com check-in após a tolerância, em {trab} dias trabalhados",
                max((x.data for x in dias if x.atraso), default=None))
        s = severidade(n_sai, lim["saida"])
        if s:
            add("jor", s, "Saídas antecipadas", f"{plural(n_sai, 'dia', 'dias')} com check-out antes do fim da jornada",
                max((x.data for x in dias if x.saida), default=None))
        s = severidade(n_auto, lim["checkout_auto"])
        if s:
            add("auto", s, "Check-out automático", f"{n_auto} de {trab} dias sem check-out manual",
                max((x.data for x in dias if x.auto), default=None))
        if prog >= lim["pesq_min"]:
            s = severidade((pct_exp or 0) * 100, lim["pesq_expiradas_pct"])
            if s:
                add("pesq", s, "Pesquisas expiradas", f"{exp} de {prog} pesquisas ({fmt_pct(pct_exp)})")
        s = severidade(len(sem_exec), lim["dias_sem_atividade"])
        if s:
            add("exec", s, "Dias sem atividades",
                f"{plural(len(sem_exec), 'dia', 'dias')} com atividades programadas e nenhuma respondida", sem_exec[-1])
        s = severidade(f_i, lim["faltas_injust"])
        if s:
            add("falta", s, "Faltas injustificadas",
                plural(f_i, "falta", "faltas") + (f" e {plural(f_a, 'atestado', 'atestados')}" if f_a else ""),
                max((f.data for f in fl if f.tipo == "I"), default=None))
        s = severidade(len(fot_ind), lim["fotos_indicio"])
        if s:
            motivos = sorted({_generico(m) for _, ms in fot_ind for m in ms})
            add("foto", s, "Fotos com indício",
                f"{plural(len(fot_ind), 'foto', 'fotos')} de {len(fotos_p)} analisadas ({'; '.join(motivos).lower()})",
                max(f.data for f, _ in fot_ind))
        if baixo:
            s = max(2 if any(b["st"] == "severa" for b in baixo) else 1, severidade(pend_baixo, lim["visitas_pendentes"]))
            n_l = len({b["loja"] for b in baixo})
            add("ader", s, "Impacto na aderência",
                f"{plural(n_l, 'loja', 'lojas')} abaixo da meta, "
                f"com {plural(pend_baixo, 'visita pendente', 'visitas pendentes')} do contratado")
        s = severidade(rt_dias, lim["dias_fuga_rota"])
        if s:
            add("rota", s, "Fuga de rota",
                f"{len(rt)} posições fora da cerca de {p['cerca_rota_m']} m em {plural(rt_dias, 'dia', 'dias')} "
                f"(maior distância: {round(rt_max)} m)", max(x.data for x in rt))

        # sobrecarga e humor: contexto de cuidado, nunca de conduta
        h_neg = len(hd) >= 5 and ((h_pct or 0) * 100 >= lim["humor_pct"] or seq >= lim["humor_seq"])
        imp = ((prog >= lim["pesq_min"] and (pct_exp or 0) * 100 > lim["pesq_expiradas_pct"][0])
               or n_atr >= lim["atraso"][0] or bool(baixo) or len(sem_exec) >= 2)
        carga_alta = (len(aw) >= 2 and carga_media >= lim["carga_semana"] and queda * 100 >= lim["queda_ader_pp"])
        pd_txt = (f"PDOH: {fmt_pct(pd['seg_produtivo'] / pd['tot'], 0)} produtivo, {fmt_pct(pd['seg_ocio'] / pd['tot'], 0)} "
                  f"ócio e {fmt_pct(pd['seg_nao_registrado'] / pd['tot'], 0)} sem registro.") if pd else ""
        cg_txt = (f"Média de {arredonda(carga_media)} visitas contratadas por semana (até {plural(max_lojas, 'loja', 'lojas')}) "
                  f"e aderência de {fmt_pct(aw[0][4], 0)} para {fmt_pct(aw[-1][4], 0)} nas semanas fechadas.") if carga_alta else ""
        h_txt = (f"Humor negativo em {fmt_pct(h_pct, 0)} dos dias (maior sequência: {plural(seq, 'dia', 'dias')})"
                 + (f", junto com queda de desempenho e {plural(n_lojas, 'loja atendida', 'lojas atendidas')}"
                    if imp and not carga_alta else "")
                 + ".") if h_neg else ""
        if (h_neg and imp) or carga_alta:
            sev = 3 if (h_neg and carga_alta) else 2
            add("sobre", sev, "Possível sobrecarga",
                " ".join(x for x in (cg_txt, h_txt, pd_txt) if x), seq_fim if h_neg else None)
        elif h_neg:
            add("humor", 1, "Humor negativo recorrente",
                f"Humor negativo em {fmt_pct(h_pct, 0)} dos dias com registro (maior sequência: {plural(seq, 'dia', 'dias')})",
                seq_fim, dias_doente=len(doente_dias) or None)
        A.sort(key=lambda a: -a.severidade)

        # ================= leitura cruzada com humor (contexto, não motivo de medida)
        cz: list[str] = []
        if hd:
            an = sum(1 for x in dias if x.atraso and x.humor_negativo)
            if n_atr and an:
                cz.append(f"{an} dos {plural(n_atr, 'atraso', 'atrasos')} ocorreram em dias com humor negativo")
            sn = sum(1 for x in dias if x.saida and x.humor_negativo)
            if sn:
                cz.append(f"{sn} das {plural(n_sai, 'saída antecipada', 'saídas antecipadas')} ocorreram em dias com humor negativo")
            if exp >= 5:
                semana, (_, _, w_exp) = sorted(sem_p.items(), key=lambda kv: (-kv[1][2], kv[0]))[0]
                nw = sum(1 for d in hd if util.segunda_da_semana(d) == semana and hm[d])
                if nw >= 2 and w_exp >= exp * 0.35:
                    cz.append(f"a semana {util.semana_iso(semana)} concentra {w_exp} das {exp} pesquisas expiradas "
                              f"e teve {nw} dias com humor negativo")

        # ================= nível, dimensões e risco
        soma = sum(a.severidade for a in A)
        n3 = sum(1 for a in A if a.severidade == 3)
        nivel = nivel_de(soma, n3, p)
        dim = {
            "aderencia": None if ad_pct is None else _cl(ad_pct * 100),
            "pesquisas": None if pct_exp is None else _cl(100 - pct_exp * 400),
            "pontualidade": _cl(100 - (n_atr + n_sai) / trab * 200) if trab else None,
            "registro_jornada": _cl(100 - n_auto / trab * 200) if trab else None,
            "fotos": _cl(100 - len(fot_ind) / len(fotos_p) * 500) if fotos_p else None,
            "presenca": _cl(100 - f_i * 25 - f_j * 6) if tem_faltas else None,
            "humor": None if not hd else _cl(100 - (h_pct or 0) * 100),
        }
        risco = min(100, soma * 10)  # Índice de risco simples: soma das severidades × 10, teto 100

        res.append(Resultado(
            cpf=cpf, nome=nome, uf=uf, supervisor=c.supervisor if c else "", cpf_pendente=cpf.startswith("N:"),
            dimensoes=dim, carga_media=carga_media, queda_ader_pp=queda_pp, score=soma, nivel=nivel, risco=risco,
            alertas=A, cruzada=cz, sobrecarga=any(a.tipo == "sobre" for a in A), dias=dias, aderencia_pct=ad_pct,
        ))
    ordem = {"C": 0, "A": 1, "T": 2, "N": 3}
    res.sort(key=lambda r: (ordem[r.nivel], -r.score, -r.risco, r.nome))
    return res


def _hhmm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def _generico(motivo: str) -> str:
    """'Captura a 412 m da loja' → 'Captura a X m da loja' (agrupa motivos iguais)."""
    return re.sub(r"\d+ m", "X m", motivo)
