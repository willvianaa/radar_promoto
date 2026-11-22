"""Cenário FICTÍCIO de paridade. Nomes inventados e CPFs inválidos de propósito (CLAUDE.md §2).

Gera linhas cruas no formato dos exports (nomes de coluna de ``schemas/``), sem CPF na operação, nas
pesquisas e no humor: o CPF vem do cadastro pelo nome normalizado, como no sistema real.

Período do cálculo: 01/09/2026 a 25/09/2026. "Hoje": 23/09/2026 (a semana 39, de 21 a 27/09, está em andamento).
Feriado: 07/09/2026 (nacional) e 16/09/2026 (só BA).

Pessoas:
  Joana Modelo Pereira  000.000.001-91  BA  escala padrão     → ver ESPERADO["Joana"]
  Pedro Fictício Lima   000.000.002-82  BA  "INÍCIO 07H"       → sobrecarga por carga, reforçada por humor
  Caio Teste Almeida    000.000.003-73  CE  escala padrão     → nível crítico
  Dora Sem Cadastro     (sem CPF)       —   escala padrão     → chave provisória
"""

from __future__ import annotations

from datetime import date

HOJE = date(2026, 9, 23)
INI = date(2026, 9, 1)
FIM = date(2026, 9, 25)
FERIADOS = {(date(2026, 9, 7), None), (date(2026, 9, 16), "BA")}

JOANA, PEDRO, CAIO = "00000000191", "00000000282", "00000000373"
DORA = "N:DORA SEM CADASTRO"

L1, L2, L3 = "BA / LOJA FICTICIA 01", "BA / LOJA FICTICIA 02", "BA / LOJA FICTICIA 03"
ALMOCO = "BA / NÃO OPERACIONAL"


def d(dia: int) -> str:
    return f"{dia:02d}/09/2026"


def h(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def cadastro() -> list[dict]:
    base = {"USUARIO ATIVO": "SIM"}
    return [
        {**base, "NOME DO COLABORADOR": "Joana Modelo Pereira", "CPF": "000.000.001-91", "COLABORADOR SUPERIOR": "Marta Fictícia Rocha", "UF": "BA", "JORNADA": ""},
        {**base, "NOME DO COLABORADOR": "Pedro Fictício Lima", "CPF": "000.000.002-82", "COLABORADOR SUPERIOR": "Marta Fictícia Rocha", "UF": "BA", "JORNADA": "INÍCIO 07H"},
        {**base, "NOME DO COLABORADOR": "Caio Teste Almeida", "CPF": "000.000.003-73", "COLABORADOR SUPERIOR": "Paulo Modelo Dias", "UF": "CE", "JORNADA": ""},
    ]


def _visita(nome, dia, pdv, ent, sai, auto="NÃO", uf="BA"):
    return {
        "DATA DO ROTEIRO": d(dia), "COLABORADOR": nome, "COLABORADOR SUPERIOR": "x", "ESTADO": uf,
        "PONTO DE VENDA": pdv, "HORA ENTRADA": h(ent), "HORA SAIDA": h(sai), "CHECKOUT SISTEMA": auto,
    }


def operacao() -> list[dict]:
    rows = []
    # Joana: dias de trabalho 14,15,16(feriado BA),17,18,21,22,23,24; dia 25 só almoço
    primeiro = {14: 510, 15: 510, 16: 520, 17: 510, 18: 510, 22: 495, 23: 480, 24: 480}
    for dia, ent in primeiro.items():
        rows.append(_visita("Joana Modelo Pereira", dia, L1, ent, 690))
        rows.append(_visita("Joana Modelo Pereira", dia, ALMOCO, 720, 780))
        auto = "SIM" if dia in (23, 24) else "NÃO"
        rows.append(_visita("Joana Modelo Pereira", dia, L2, 790, 1050, auto))
    # dia 21: reunião às 08:00 (conta na jornada, não é loja), loja 01 a partir das 09:00
    rows.append(_visita("Joana Modelo Pereira", 21, "BA / REUNIÃO", 480, 540))
    rows.append(_visita("Joana Modelo Pereira", 21, L1, 540, 690))
    rows.append(_visita("Joana Modelo Pereira", 21, ALMOCO, 720, 780))
    rows.append(_visita("Joana Modelo Pereira", 21, L2, 790, 1050))
    rows.append(_visita("Joana Modelo Pereira", 25, ALMOCO, 720, 780))  # só almoço: não é dia trabalhado
    # Pedro: jornada cadastrada 07:00 → tolerância até 07:15; 21,22,23 chegam 07:40
    for dia in (14, 15, 17, 18, 21, 22, 23, 24):
        ent = 460 if dia in (21, 22, 23) else 430
        rows.append(_visita("Pedro Fictício Lima", dia, L3, ent, 1050))
    # Caio: 10 dias de 08:30 com check-out automático (1–4, 8–11, 14, 15/09)
    for dia in (1, 2, 3, 4, 8, 9, 10, 11, 14, 15):
        rows.append(_visita("Caio Teste Almeida", dia, "CE / LOJA FICTICIA 09", 510, 1050, "SIM", uf="CE"))
    # Dora: sem cadastro
    rows.append(_visita("Dora Sem Cadastro", 14, "BA / LOJA FICTICIA 05", 480, 1050))
    # linha sem hora de entrada: descartada
    rows.append({**_visita("Pedro Fictício Lima", 25, L3, 0, 0), "HORA ENTRADA": ""})
    return rows


def _pesq(idv, nome, dia, status, pdv):
    return {"ID": idv, "Formulário": "[MARCA A] Preço", "PDV": pdv, "Responsável": nome,
            "Colaborador superior": "x", "Solicitação": f"{d(dia)} 08:00", "Status": status}


def atividades() -> list[dict]:
    rows, n = [], 0

    def add(nome, dia, status, pdv):
        nonlocal n
        n += 1
        rows.append(_pesq(f"A{n:04d}", nome, dia, status, pdv))

    # Joana: 25 programadas, 5 expiradas (16: 2, 18: 1, 24: 2)
    for dia in (14, 15, 17, 21, 22, 23):
        for _ in range(3):
            add("Joana Modelo Pereira", dia, "Respondido", L1)
    add("Joana Modelo Pereira", 18, "Respondido", L1)
    add("Joana Modelo Pereira", 18, "Respondido", L1)
    add("Joana Modelo Pereira", 18, "Expirado", L1)
    for dia in (16, 24):
        add("Joana Modelo Pereira", dia, "Expirado", L1)
        add("Joana Modelo Pereira", dia, "Expirado", L1)
    # Pedro: 20 programadas, todas respondidas
    for i in range(20):
        add("Pedro Fictício Lima", (14, 15, 17, 18, 21, 22, 23, 24)[i % 8], "Respondido", L3)
    return rows


def humor() -> list[dict]:
    def r(nome, dia, op):
        return {"NOME DO COLABORADOR": nome, "DATA": d(dia), "HUMOR": op}

    joana = dict(zip((14, 15, 16, 17, 18, 21, 22, 23, 24),
                     ("Cansado", "Triste", "Sobrecarregado", "Feliz", "Bem", "Motivado", "Feliz", "Bem", "Feliz"), strict=True))
    pedro = dict(zip((14, 15, 17, 18, 21, 22, 23, 24),
                     ("Feliz", "Bem", "Motivado", "Cansado", "Cansado", "Triste", "Sobrecarregado", "Cansado"), strict=True))
    return [r("Joana Modelo Pereira", k, v) for k, v in joana.items()] + [r("Pedro Fictício Lima", k, v) for k, v in pedro.items()]


def faltas() -> list[dict]:
    return [
        {"CPF": "000.000.001-91", "Colaborador": "Joana Modelo Pereira", "Data": d(10), "Tipo": "Justificada", "Motivo": "motivo fictício"},
        {"CPF": "000.000.003-73", "Colaborador": "Caio Teste Almeida", "Data": d(17), "Tipo": "Injustificada", "Motivo": ""},
    ]


def aderencia() -> list[dict]:
    def r(marca, loja, nome, sem, ct, rz):
        return {"MARCA": marca, "LOJA": loja, "SUPERVISOR": "x", "UF": "BA", "COLABORADOR": nome,
                "CONTRATADAS": ct, "REALIZADAS": rz, "AJUSTADAS": rz, "SEMANA": sem, "ANO": 2026}

    j = "Joana Modelo Pereira"
    rows = [
        r("MARCA A", L1, j, 36, 10, 9), r("MARCA B", L1, j, 36, 4, 6),   # B: realizadas acima do contrato (teto por linha)
        r("MARCA A", L1, j, 37, 10, 10), r("MARCA B", L1, j, 37, 4, 4),
        r("MARCA A", L1, j, 38, 10, 7), r("MARCA B", L1, j, 38, 4, 4),
        r("MARCA A", L1, j, 39, 10, 0), r("MARCA B", L1, j, 39, 4, 0),   # semana em andamento: fora
    ]
    p = "Pedro Fictício Lima"
    rows += [r("MARCA A", L3, p, 36, 46, 46), r("MARCA A", L3, p, 37, 46, 44),
             r("MARCA A", L3, p, 38, 46, 40), r("MARCA A", L3, p, 39, 46, 0),
             r("MARCA A", L3, "SEM COLABORADOR", 38, 8, 0)]
    return rows


def pdoh() -> dict[str, list[dict]]:
    def r(seg):
        return [{"Colaborador": "Pedro Fictício Lima", "Superior": "x", "UF": "BA", "Segundos": seg, "Dias": 8}]

    return {"prod": r(21600), "desl": r(7200), "ocio": r(3600), "hnr": r(3600)}


def fotos() -> list[dict]:
    def f(dia, hora, n, pdv=L1):
        return {"Colaborador": "Joana Modelo Pereira", "Data": d(dia), "Hora": h(hora), "PDV": pdv,
                "ID da pesquisa": f"A{n:04d}", "Arquivo": f"f{n}.jpg", "SHA256": f"{n:064x}"}

    rows = [f(dia, 540, i) for i, dia in enumerate((14, 15, 17, 18, 21, 22, 23, 24), start=1)]
    rows.append(f(17, 1020, 9))   # fora do horário: no dia 17 a loja 01 só foi visitada até 11:30
    rows.append(f(18, 600, 10))   # dentro da visita
    return rows
