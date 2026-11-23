"""Gera as fixtures do mock do front a partir de api/openapi.yaml.

Tudo é FICTÍCIO: nomes inventados, CPFs inválidos de propósito (000.000.00x-9y), lojas de exemplo.
Saída: tests/fixtures/front/*.json (determinística: mesma semente, mesmo resultado).
Valida cada resposta contra os schemas do contrato (ver tests/front/test_mock_contrato.py).

Uso:  python front/mock/gerar.py
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "tests" / "fixtures" / "front"

SEMANA_INI = date(2026, 9, 7)  # segunda-feira
N_SEMANAS = 10
PERIODO = {"ini": SEMANA_INI.isoformat(), "fim": (SEMANA_INI + timedelta(days=N_SEMANAS * 7 - 1)).isoformat()}

# Estados e supervisores fictícios (regional "Sudeste" = SP, RJ, MG; "Sul" = PR; "Nordeste" = BA).
EQUIPES = {
    "SP": ["Supervisor Aurora Teste", "Supervisor Bento Exemplo"],
    "RJ": ["Supervisor Cecília Modelo"],
    "MG": ["Supervisor Davi Ficticio"],
    "PR": ["Supervisor Elisa Amostra"],
    "BA": ["Supervisor Fabio Demonstracao"],
}
REGIONAIS = {"Sudeste": ["SP", "RJ", "MG"], "Sul": ["PR"], "Nordeste": ["BA"]}
LOJAS = ["Loja Exemplo Centro", "Loja Exemplo Norte", "Loja Exemplo Sul", "Loja Exemplo Leste", "Loja Exemplo Oeste",
         "Loja Exemplo Praça", "Loja Exemplo Shopping", "Loja Exemplo Avenida"]
NOMES = ["Ana", "Bruno", "Carla", "Diego", "Elaine", "Fabio", "Gisele", "Heitor", "Iris", "Jonas", "Karen", "Lucas",
         "Marta", "Nilo", "Olga", "Paulo", "Quiteria", "Rafael", "Sonia", "Tiago", "Ursula", "Vitor", "Wanda", "Xavier"]
SOBRENOMES = ["Teste", "Exemplo", "Ficticio", "Modelo", "Amostra", "Demo", "Pilar", "Quadro", "Ensaio", "Simulado"]
TIPOS_PDV = ["VISITA", "VISITA", "VISITA", "NÃO OPERACIONAL"]

USUARIOS = [
    {"id": 1, "nome": "Dora Diretoria", "email": "diretoria@exemplo.teste", "perfil": "diretoria", "escopo": "nacional"},
    {"id": 2, "nome": "Rita RH", "email": "rh@exemplo.teste", "perfil": "rh", "escopo": "nacional"},
    {"id": 3, "nome": "Paulo PeP", "email": "pp@exemplo.teste", "perfil": "pp", "escopo": "nacional"},
    {"id": 4, "nome": "Glória Gerência", "email": "gerencia@exemplo.teste", "perfil": "gerencia_regional", "escopo": "regional:Sudeste"},
    {"id": 5, "nome": "Aurora Supervisora", "email": "supervisor@exemplo.teste", "perfil": "supervisor", "escopo": "equipe:Supervisor Aurora Teste"},
    {"id": 6, "nome": "Carlos Compliance", "email": "compliance@exemplo.teste", "perfil": "compliance", "escopo": "nacional"},
    {"id": 7, "nome": "Admin Teste", "email": "admin@exemplo.teste", "perfil": "admin", "escopo": "nacional"},
]
SENHA_TESTE = "senha-de-teste-nao-real"  # só vale no mock local

PESO_PERFIL = ["estavel"] * 18 + ["atencao"] * 8 + ["alto"] * 5 + ["critico"] * 3 + ["sobre"] * 2


def hhmm(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def mascarar(cpf: str) -> str:
    return "***." + cpf[4:11] + "-**"


def gerar() -> dict:
    rnd = random.Random(20260922)
    supervisores = [(uf, s) for uf, ss in EQUIPES.items() for s in ss]
    colabs = []
    for i in range(36):
        uf, sup = supervisores[i % len(supervisores)] if i < len(supervisores) * 2 else rnd.choice(supervisores)
        nome = f"{NOMES[i % len(NOMES)]} {rnd.choice(SOBRENOMES)} {chr(65 + i % 26)}."
        cpf = f"000.000.00{i % 10}-9{i // 10}"
        cid = "c_" + hashlib.sha1(f"mock-{i}".encode()).hexdigest()[:10]
        perfil = rnd.choice(PESO_PERFIL)
        colabs.append(_colaborador(rnd, i, cid, nome, cpf, uf, sup, perfil))
    return {"colaboradores": colabs}


def _colaborador(rnd: random.Random, i: int, cid: str, nome: str, cpf: str, uf: str, sup: str, perfil: str) -> dict:
    forca = {"estavel": 0.0, "atencao": 0.35, "alto": 0.6, "critico": 0.85, "sobre": 0.5}[perfil]
    inicio = rnd.choice([480, 480, 480, 420])  # jornada cadastrada: 08:00 ou "INÍCIO 07H"
    jornada = f"{hhmm(inicio)}–{hhmm(inicio + 570)}"
    lojas = rnd.sample(LOJAS, rnd.randint(2, 4))
    contr_base = rnd.randint(40, 56) if perfil == "sobre" else rnd.randint(18, 36)

    semanas, car_sem, pesq_sem = [], [], []
    for w in range(N_SEMANAS):
        ini = SEMANA_INI + timedelta(weeks=w)
        ct = max(6, int(contr_base + rnd.randint(-3, 3)))
        queda = (w / (N_SEMANAS - 1)) * (0.14 if perfil == "sobre" else 0.05 * forca)
        ader = max(0.4, min(1.0, 0.97 - forca * 0.18 - queda + rnd.uniform(-0.03, 0.03)))
        rz = int(round(ct * ader))
        prog = rnd.randint(18, 30)
        exp = int(round(prog * max(0.0, forca * 0.35 + rnd.uniform(-0.03, 0.04))))
        oc = int(round(forca * rnd.uniform(1, 4) + rnd.random()))
        humor_dias = rnd.randint(3, 5)
        humor_neg = min(humor_dias, int(round(humor_dias * min(1, forca * 0.9 + rnd.uniform(-0.1, 0.15)))))
        semanas.append({"semana_ini": ini.isoformat(), "contratadas": ct, "realizadas": rz, "programadas": prog,
                        "respondidas": prog - exp, "expiradas": exp, "ocorrencias_jornada": oc,
                        "humor_dias": humor_dias, "humor_negativos": humor_neg})
        car_sem.append({"semana_ini": ini.isoformat(), "lojas": len(lojas), "contratadas": ct, "realizadas": rz,
                        "aderencia": round(rz / ct * 100, 1)})
        pesq_sem.append({"semana": int(ini.isocalendar()[1]), "programadas": prog, "respondidas": prog - exp, "expiradas": exp})

    # jornada dia a dia (dias úteis)
    dias = []
    d = SEMANA_INI
    fim = date.fromisoformat(PERIODO["fim"])
    while d <= fim:
        if d.weekday() < 5 and rnd.random() > 0.04:
            atraso = max(0, int(rnd.gauss(forca * 22, 10))) if rnd.random() < 0.25 + forca * 0.4 else 0
            auto = rnd.random() < 0.05 + forca * 0.25
            cin = inicio + atraso
            visitas, t = [], cin + 5
            for _ in range(rnd.randint(2, 4)):
                tipo = rnd.choice(TIPOS_PDV)
                dur = rnd.randint(25, 75) if tipo != "NÃO OPERACIONAL" else 60
                visitas.append({"pdv": rnd.choice(lojas), "ini": hhmm(t), "fim": hhmm(t + dur), "tipo_pdv": tipo})
                t += dur + rnd.randint(10, 35)
            dias.append({"data": d.isoformat(), "checkin": hhmm(cin), "checkout": None if auto and rnd.random() < 0.3 else hhmm(min(t, inicio + 570)),
                         "checkout_auto": auto, "atraso_min": atraso if atraso > 15 else 0, "visitas": visitas})
        d += timedelta(days=1)

    soma_ct = sum(s["contratadas"] for s in semanas)
    soma_rz = sum(s["realizadas"] for s in semanas)
    prog = sum(s["programadas"] for s in semanas)
    exp = sum(s["expiradas"] for s in semanas)
    n_atr = sum(1 for x in dias if x["atraso_min"] > 15)
    n_auto = sum(1 for x in dias if x["checkout_auto"])
    hd = sum(s["humor_dias"] for s in semanas)
    hn = sum(s["humor_negativos"] for s in semanas)
    pct_ader = soma_rz / soma_ct * 100
    pct_exp = exp / prog * 100

    # alertas determinísticos (severidade 1–3) — regras do CLAUDE.md §4 só como forma; os limites aqui são ilustrativos
    alertas = []
    if pct_ader < 85:
        alertas.append(("ader", 3 if pct_ader < 75 else 2, "Aderência abaixo da Meta 1", f"Aderência de {pct_ader:.1f}% no período (Meta 1: 85%).".replace(".", ",")))
    if pct_exp > 12 and prog >= 20:
        alertas.append(("pesq", 3 if pct_exp > 20 else 2, "Pesquisas expiradas acima do limite", f"{exp} de {prog} programadas expiraram ({pct_exp:.1f}%).".replace(".", ",")))
    if n_atr >= 5:
        alertas.append(("jor", 3 if n_atr >= 10 else 2 if n_atr >= 7 else 1, "Atrasos recorrentes", f"{n_atr} dias com primeiro check-in após a tolerância de 15 min."))
    if n_auto >= 4:
        alertas.append(("auto", 2 if n_auto >= 8 else 1, "Check-outs automáticos", f"{n_auto} dias com check-out realizado pelo sistema."))
    fotos = []
    if perfil in ("alto", "critico") and rnd.random() < 0.8:
        for _ in range(rnd.randint(1, 3)):
            dd = SEMANA_INI + timedelta(days=rnd.randint(0, N_SEMANAS * 7 - 8))
            fotos.append({"data": dd.isoformat(), "loja": rnd.choice(lojas),
                          "motivos": rnd.sample(["imagem repetida", "captura a mais de 300 m da loja", "foto fora do horário da visita"], rnd.randint(1, 2)),
                          "url_assinada": "/assets/foto-ficticia.svg?exp=mock"})
        alertas.append(("foto", 3 if len(fotos) >= 3 else 2, "Fotos com indício", f"{len(fotos)} foto(s) com indício de repetição, distância ou horário."))
    if perfil == "critico" and rnd.random() < 0.6:
        alertas.append(("rota", 2, "Posição fora da cerca", "Registros de posição a mais de 200 m da loja em visitas do período."))
    media_ct = soma_ct / N_SEMANAS
    sobre = media_ct >= 44 and (car_sem[0]["aderencia"] - car_sem[-1]["aderencia"]) >= 5
    if sobre:
        alertas.append(("sobre", 3 if hn / hd > 0.35 else 2, "Possível sobrecarga",
                        f"Média de {media_ct:.0f} visitas contratadas por semana e queda de aderência de {car_sem[0]['aderencia']:.0f}% para {car_sem[-1]['aderencia']:.0f}% (sinal de cuidado, não de conduta).".replace(".", ",")))
    if hn / hd > 0.4:
        alertas.append(("humor", 1, "Humor negativo recorrente", f"Humor negativo em {hn / hd * 100:.0f}% dos dias com registro (contexto de acompanhamento).".replace(".", ",")))

    faltas = {"injustificadas": rnd.randint(0, 3) if forca > 0.5 else 0, "justificadas": rnd.randint(0, 2), "atestados": rnd.randint(0, 1)}
    if faltas["injustificadas"] >= 2:
        alertas.append(("falta", 2, "Faltas injustificadas", f"{faltas['injustificadas']} faltas injustificadas no período."))

    soma = sum(a[1] for a in alertas)
    n3 = sum(1 for a in alertas if a[1] == 3)
    nivel = "C" if (soma >= 9 or n3 >= 2) else "A" if soma >= 5 else "T" if soma >= 3 else "N"
    cl = lambda x: max(0, min(100, round(x)))  # noqa: E731
    dim = {
        "Aderência": cl(pct_ader), "Pesquisas": cl(100 - pct_exp * 4), "Pontualidade": cl(100 - n_atr / max(1, len(dias)) * 200),
        "Registro de jornada": cl(100 - n_auto / max(1, len(dias)) * 200), "Fotos": cl(100 - len(fotos) * 12),
        "Presença": cl(100 - faltas["injustificadas"] * 25 - faltas["justificadas"] * 6), "Humor": cl(100 - hn / hd * 100),
    }
    sem_humor = [v for k, v in dim.items() if k != "Humor"]
    risco = min(100, round(soma * 9 + (100 - sum(sem_humor) / len(sem_humor)) * 0.25))

    prod = rnd.uniform(0.52, 0.72) - forca * 0.1
    desl = rnd.uniform(0.12, 0.2)
    ocio = rnd.uniform(0.04, 0.1) + forca * 0.08
    pdoh = {"periodo": {"ini": "2026-11-02", "fim": "2026-11-15"}, "dias": 10, "produtivo_pct": round(prod * 100, 1), "deslocamento_pct": round(desl * 100, 1),
            "ocio_pct": round(ocio * 100, 1), "nao_registrado_pct": round(100 - (prod + desl + ocio) * 100, 1)}

    resumo = {"id": cid, "nome": nome, "cpf_mascarado": mascarar(cpf), "uf": uf, "supervisor": sup, "nivel": nivel,
              "score": soma, "risco": risco, "sobrecarga": sobre}
    eventos = []
    for tipo, sev, tit, desc in alertas:
        ndias = 1 if tipo in ("ader", "sobre", "humor") else rnd.randint(1, 3)
        for _ in range(ndias):
            dd = date.fromisoformat(PERIODO["fim"]) - timedelta(days=rnd.randint(0, 40))
            eventos.append({"tipo": tipo, "severidade": sev, "data": dd.isoformat(), "titulo": tit, "descricao": desc})
    media_dim = {k: cl(v + rnd.uniform(-6, 6)) for k, v in {"Aderência": 91, "Pesquisas": 82, "Pontualidade": 85, "Registro de jornada": 88, "Fotos": 95, "Presença": 96, "Humor": 78}.items()}
    humor = {"dias_registrados": hd, "negativos_pct": round(hn / hd * 100, 1), "sequencia_max": rnd.randint(1, 5) if hn else 0,
             "alerta_cuidado": hn / hd > 0.4, "opcoes": {"Cansado": hn // 2, "Sobrecarregado": hn // 3, "Doente": 1 if perfil == "critico" else 0, "Triste": 0}}

    return {
        "resumo": resumo, "_cpf": cpf, "_perfil_sintetico": perfil, "_semanas": semanas, "_eventos": eventos,
        "raiox": {
            "colaborador": {**resumo, "cpf": cpf, "jornada": jornada, "lojas": lojas},
            "dimensoes": dim, "media_filtro": media_dim,
            "alertas": [{"tipo": t, "severidade": s, "titulo": ti, "detalhe": de} for t, s, ti, de in alertas],
            "jornada_dias": dias, "pesquisas_semana": pesq_sem,
            "aderencia_lojas": [{"loja": lj, "contratadas": (c := max(4, soma_ct // len(lojas) // 2)), "realizadas": (r := int(c * min(1, pct_ader / 100 + rnd.uniform(-0.1, 0.06)))),
                                 "aderencia": round(r / c * 100, 1), "situacao": "abaixo da Meta 1" if r / c < 0.85 else "dentro da meta"} for lj in lojas],
            "carga": {"semanas": car_sem, "media_contratadas": round(media_ct, 1), "pdoh": pdoh if rnd.random() < 0.85 else None},
            "faltas": faltas, "fotos_indicio": fotos, "humor": humor,
        },
    }


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    base = gerar()
    (SAIDA / "colaboradores.json").write_text(json.dumps(base["colaboradores"], ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (SAIDA / "usuarios.json").write_text(json.dumps({"senha_teste": SENHA_TESTE, "regionais": REGIONAIS, "periodo": PERIODO, "usuarios": USUARIOS}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("fixtures gravadas em", SAIDA, "—", len(base["colaboradores"]), "colaboradores fictícios")


if __name__ == "__main__":
    main()
