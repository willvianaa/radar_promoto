"""Servidor de mock do front: serve front/ e imita /api/v1 (api/openapi.yaml) com as fixtures fictícias.

Não calcula regra de negócio: só filtra e agrega os números prontos das fixtures, para dar para desenvolver
as telas antes da API real. Sessão por cookie httpOnly, como no contrato. Aplica escopo, máscara de CPF e
visibilidade do humor por perfil (docs/05-matriz-permissoes.md).

Uso:  python front/mock/servidor.py [porta]      (padrão 8765)  -> http://127.0.0.1:8765
Usuários e senha de teste: tests/fixtures/front/usuarios.json
"""
from __future__ import annotations

import json
import mimetypes
import re
import secrets
import sys
from datetime import date
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

RAIZ = Path(__file__).resolve().parents[2]
FRONT = RAIZ / "front"
FIX = RAIZ / "tests" / "fixtures" / "front"

CPF_COMPLETO = {"rh", "dp", "compliance", "pp", "admin"}
HUMOR_TOTAL = {"rh"}                      # vê a opção (inclui "Doente")
HUMOR_ALERTA = {"gerencia_regional", "supervisor"}   # vê só o alerta de cuidado
HUMOR_AGREGADO = {"rh", "pp", "diretoria", "merch", "gerencia_regional", "supervisor"}
SEM_FALTAS = {"diretoria", "merch"}
SO_AGREGADO = {"diretoria"}
GERAM_DOSSIE = {"rh", "pp", "admin"}
MIN_GRUPO_HUMOR = 5
TERMOS_PROIBIDOS = ["detrator", "preguiçoso", "irresponsável", "desonesto", "relapso", "má-fé", "mentiu", "culpado", "fraude", "comprovado"]

SESSOES: dict[str, dict] = {}
DOSSIES: dict[str, dict] = {}
SEQ = {"n": 0}


def carregar():
    colabs = json.loads((FIX / "colaboradores.json").read_text(encoding="utf-8"))
    cfg = json.loads((FIX / "usuarios.json").read_text(encoding="utf-8"))
    return colabs, cfg


COLABS, CFG = carregar()
POR_ID = {c["resumo"]["id"]: c for c in COLABS}


def no_escopo(user: dict, c: dict) -> bool:
    esc = user["escopo"]
    r = c["resumo"]
    if esc == "nacional":
        return True
    tipo, _, val = esc.partition(":")
    if tipo == "regional":
        return r["uf"] in CFG["regionais"].get(val, [])
    if tipo == "equipe":
        return r["supervisor"] == val
    return False


def filtrar(user, q: dict) -> list[dict]:
    uf, sup = q.get("uf", [""])[0], q.get("supervisor", [""])[0]
    return [c for c in COLABS if no_escopo(user, c) and (not uf or c["resumo"]["uf"] == uf) and (not sup or c["resumo"]["supervisor"] == sup)]


def semanas_no_periodo(c: dict, ini: str, fim: str):
    # semana entra se qualquer dia dela cai no recorte
    out = []
    for s in c["_semanas"]:
        d0 = date.fromisoformat(s["semana_ini"])
        d1 = date.fromordinal(d0.toordinal() + 6)
        if d1.isoformat() >= ini and d0.isoformat() <= fim:
            out.append(s)
    return out


def contagem(lst):
    n = {"C": 0, "A": 0, "T": 0, "N": 0}
    for c in lst:
        n[c["resumo"]["nivel"]] += 1
    return n


def painel(user, q):
    ini = q.get("ini", [CFG["periodo"]["ini"]])[0]
    fim = q.get("fim", [CFG["periodo"]["fim"]])[0]
    lst = filtrar(user, q)
    por_sem: dict[str, dict] = {}
    for c in lst:
        for s in semanas_no_periodo(c, ini, fim):
            a = por_sem.setdefault(s["semana_ini"], {"semana_ini": s["semana_ini"], "contratadas": 0, "realizadas": 0, "programadas": 0, "respondidas": 0,
                                                     "expiradas": 0, "ocorrencias_jornada": 0, "_hd": 0, "_hn": 0})
            for k in ("contratadas", "realizadas", "programadas", "respondidas", "expiradas", "ocorrencias_jornada"):
                a[k] += s[k]
            a["_hd"] += s["humor_dias"]
            a["_hn"] += s["humor_negativos"]
    semanas = [por_sem[k] for k in sorted(por_sem)]
    ver_humor = user["perfil"] in HUMOR_AGREGADO and len(lst) >= MIN_GRUPO_HUMOR
    for a in semanas:
        hd, hn = a.pop("_hd"), a.pop("_hn")
        if ver_humor and hd:
            a["humor_negativo_pct"] = round(hn / hd * 100, 1)   # extensão pendente no contrato (ver notas)
    ct = sum(a["contratadas"] for a in semanas)
    rz = sum(a["realizadas"] for a in semanas)
    pg = sum(a["programadas"] for a in semanas)
    ex = sum(a["expiradas"] for a in semanas)
    dow = [0] * 7   # Dom..Sáb
    atrasos = autos = 0
    for c in lst:
        for d in c["raiox"]["jornada_dias"]:
            if ini <= d["data"] <= fim:
                if d["atraso_min"] > 15:
                    atrasos += 1
                    dow[(date.fromisoformat(d["data"]).weekday() + 1) % 7] += 1
                if d["checkout_auto"]:
                    autos += 1
                    dow[(date.fromisoformat(d["data"]).weekday() + 1) % 7] += 1
    kpis = {"aderencia": round(rz / ct * 100, 1) if ct else 0, "pesquisas_expiradas_pct": round(ex / pg * 100, 1) if pg else 0,
            "atrasos": atrasos, "checkout_auto": autos, "colaboradores": len(lst)}
    if ver_humor:
        hd = sum(s["humor_dias"] for c in lst for s in semanas_no_periodo(c, ini, fim))
        hn = sum(s["humor_negativos"] for c in lst for s in semanas_no_periodo(c, ini, fim))
        kpis["humor_negativo_pct"] = round(hn / hd * 100, 1) if hd else 0
    sups: dict[str, dict] = {}
    for c in lst:
        r = c["resumo"]
        s = sups.setdefault(r["supervisor"], {"supervisor": r["supervisor"], "C": 0, "A": 0, "T": 0})
        if r["nivel"] in ("C", "A", "T"):
            s[r["nivel"]] += 1
    n = contagem(lst)
    leitura = []
    if n["C"]:
        leitura.append(f"{n['C']} colaborador(es) em nível crítico: vários indícios graves ao mesmo tempo, que pedem conferência.")
    if kpis["aderencia"] < 85:
        leitura.append(f"Aderência de {str(kpis['aderencia']).replace('.', ',')}% no período, abaixo da Meta 1 (85%).")
    elif kpis["aderencia"] < 93:
        leitura.append(f"Aderência de {str(kpis['aderencia']).replace('.', ',')}%: acima da Meta 1 e abaixo da Meta 2 (93%).")
    if dow and max(dow):
        leitura.append("Maior concentração de ocorrências de jornada em " + ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"][dow.index(max(dow))] + ".")
    return {"periodo": {"ini": ini, "fim": fim}, "contagem": n, "kpis": kpis, "semanas": semanas, "dia_semana": dow,
            "risco_por_supervisor": sorted(sups.values(), key=lambda x: -(x["C"] * 3 + x["A"] * 2 + x["T"])), "leitura_automatica": leitura}


def radar(user, q):
    uf, sup = q.get("uf", [""])[0], q.get("supervisor", [""])[0]
    return [{**c["resumo"], "fatia": c["resumo"]["supervisor"] if (uf or sup) else c["resumo"]["uf"]} for c in filtrar(user, q)]


def ordem_risco(lst):
    return sorted(lst, key=lambda c: (-c["resumo"]["risco"], c["resumo"]["nome"]))


def pagina(lst, q, chave=lambda x: x):
    lim = int(q.get("limite", ["60"])[0])
    ini = int(q.get("cursor", ["0"])[0] or 0)
    itens = lst[ini:ini + lim]
    prox = str(ini + lim) if ini + lim < len(lst) else None
    return itens, prox


def alertas(user, q):
    ini = q.get("ini", [CFG["periodo"]["ini"]])[0]
    fim = q.get("fim", [CFG["periodo"]["fim"]])[0]
    nivel, tipo = q.get("nivel", [""])[0], q.get("tipo", [""])[0]
    ev = []
    for c in filtrar(user, q):
        for e in c["_eventos"]:
            if not (ini <= e["data"] <= fim):
                continue
            if e["tipo"] == "humor" and user["perfil"] not in HUMOR_TOTAL | HUMOR_ALERTA:
                continue
            if e["tipo"] == "falta" and user["perfil"] in SEM_FALTAS:
                continue
            ev.append({"colaborador": c["resumo"], **e})
    cont = {"C": 0, "A": 0, "T": 0, "N": 0}
    vistos = set()
    for e in ev:
        if (e["colaborador"]["id"]) not in vistos:
            vistos.add(e["colaborador"]["id"])
            cont[e["colaborador"]["nivel"]] += 1
    por_tipo, por_dia = {}, {}
    for e in ev:
        por_tipo[e["tipo"]] = por_tipo.get(e["tipo"], 0) + 1
        por_dia[e["data"]] = por_dia.get(e["data"], 0) + 1
    sel = [e for e in ev if (not nivel or e["colaborador"]["nivel"] == nivel) and (not tipo or e["tipo"] == tipo)]
    sel.sort(key=lambda e: (-e["severidade"], e["data"]), reverse=False)
    sel.sort(key=lambda e: (-e["severidade"], -date.fromisoformat(e["data"]).toordinal()))
    itens, prox = pagina(sel, q)
    return {"contagem": cont, "por_tipo": por_tipo, "por_dia": [{"data": d, "n": n} for d, n in sorted(por_dia.items())], "itens": itens, "proximo_cursor": prox}


def raio_x(user, cid, q):
    if user["perfil"] in SO_AGREGADO:
        return 403, {"codigo": "sem_permissao", "mensagem": "Seu perfil vê apenas dados agregados."}
    c = POR_ID.get(cid)
    if not c or not no_escopo(user, c):
        return 404, {"codigo": "nao_encontrado", "mensagem": "Colaborador fora do escopo ou inexistente."}
    ini = q.get("ini", [CFG["periodo"]["ini"]])[0]
    fim = q.get("fim", [CFG["periodo"]["fim"]])[0]
    r = json.loads(json.dumps(c["raiox"]))
    r["colaborador"].pop("cpf", None)
    if user["perfil"] in CPF_COMPLETO:
        r["colaborador"]["cpf"] = c["_cpf"]
    else:
        r["colaborador"]["cpf"] = r["colaborador"]["cpf_mascarado"]
    r["jornada_dias"] = [d for d in r["jornada_dias"] if ini <= d["data"] <= fim]
    r["carga"]["semanas"] = [s for s in r["carga"]["semanas"] if s["semana_ini"] <= fim and date.fromordinal(date.fromisoformat(s["semana_ini"]).toordinal() + 6).isoformat() >= ini]
    if user["perfil"] in HUMOR_TOTAL:
        pass
    elif user["perfil"] in HUMOR_ALERTA:
        h = r["humor"]
        r["humor"] = {"dias_registrados": h["dias_registrados"], "negativos_pct": h["negativos_pct"], "alerta_cuidado": h["alerta_cuidado"]}
    else:
        r.pop("humor", None)
        r["dimensoes"].pop("Humor", None)
        r["media_filtro"].pop("Humor", None)
        r["alertas"] = [a for a in r["alertas"] if a["tipo"] != "humor"]
    if user["perfil"] in SEM_FALTAS:
        r["faltas"] = None
    return 200, r


def texto_dossie(c: dict, ini: str, fim: str, relato: str | None) -> dict:
    r = c["raiox"]
    nome = c["resumo"]["nome"]
    blocos = []
    for a in r["alertas"][:5]:
        if a["tipo"] == "humor":
            continue
        blocos.append({"chave": a["tipo"], "titulo": a["titulo"], "texto": f"Os registros operacionais do período indicam: {a['detalhe']}", "conclusao": "procede_parcialmente" if relato else None})
    ader = r["carga"]["semanas"]
    ctx = None
    if r.get("humor"):
        ctx = ("Os registros de acompanhamento indicam variação de humor no período. Esta informação é contexto para cuidado e não fundamenta medida.")
    return {
        "intro": f"Este documento apresenta indícios identificados nos registros operacionais de {nome} entre {ini[8:10]}/{ini[5:7]}/{ini[:4]} e {fim[8:10]}/{fim[5:7]}/{fim[:4]}.",
        "objetivos": "Reunir, de forma objetiva, os indícios observados e o impacto na aderência, para apoio à decisão de DP e Compliance.",
        "blocos": blocos,
        "impacto": f"A aderência no período foi de {ader[-1]['aderencia']:.1f}% na última semana considerada, sobre as visitas contratadas.".replace(".", ","),
        "contexto_acompanhamento": ctx,
        "consideracoes_finais": "Sendo assim, os registros apresentam indícios que devem ser conferidos pelas áreas responsáveis antes de qualquer decisão.",
    }


def revisar(cont: dict) -> list[str]:
    avisos = []
    texto = " ".join([cont.get("intro") or "", cont.get("objetivos") or "", cont.get("impacto") or "", cont.get("contexto_acompanhamento") or "", cont.get("consideracoes_finais") or ""]
                     + [(b.get("texto") or "") for b in cont.get("blocos", [])]).lower()
    for t in TERMOS_PROIBIDOS:
        if t in texto:
            avisos.append(f"Termo não permitido no texto: “{t}”. Use “indícios” e descreva o registro.")
    if not (cont.get("consideracoes_finais") or "").startswith("Sendo assim,"):
        avisos.append("As considerações finais devem começar com “Sendo assim,”.")
    if re.search(r"\b(eu|nós|nos)\b", texto):
        avisos.append("O texto deve evitar primeira pessoa.")
    return avisos


def montar_dossie(d: dict, user: dict) -> dict:
    out = {k: v for k, v in d.items() if not k.startswith("_")}
    if user["perfil"] not in HUMOR_TOTAL | HUMOR_ALERTA and out["conteudo"].get("contexto_acompanhamento") is not None:
        out["conteudo"] = {**out["conteudo"], "contexto_acompanhamento": None}
    return out


PDF_MIN = (b"%PDF-1.1\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
           b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 300 120]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
           b"4 0 obj<</Length 62>>stream\nBT /F1 12 Tf 20 60 Td (Arquivo de mock - dados ficticios) Tj ET\nendstream endobj\n"
           b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n")


class H(BaseHTTPRequestHandler):
    server_version = "RadarMock/1"

    def log_message(self, fmt, *a):  # sem logar query nem corpo
        sys.stderr.write("[mock] %s %s\n" % (self.command, urlparse(self.path).path))

    # ---- utilidades ----
    def _json(self, status, corpo, cabecalhos=None):
        b = json.dumps(corpo, ensure_ascii=False).encode("utf-8") if corpo is not None else b""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (cabecalhos or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def _usuario(self):
        ck = SimpleCookie(self.headers.get("Cookie", ""))
        m = ck.get("rp_sessao")
        return SESSOES.get(m.value) if m else None

    def _corpo(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    # ---- estáticos ----
    def _estatico(self, caminho):
        rel = unquote(caminho.lstrip("/")) or "index.html"
        alvo = (FRONT / rel).resolve()
        if FRONT.resolve() not in alvo.parents and alvo != FRONT.resolve():
            return self._json(404, {"codigo": "nao_encontrado", "mensagem": "?"})
        if alvo.is_dir():
            alvo = alvo / "index.html"
        if not alvo.exists():
            return self._json(404, {"codigo": "nao_encontrado", "mensagem": "Arquivo não encontrado."})
        b = alvo.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", (mimetypes.guess_type(str(alvo))[0] or "application/octet-stream") + ("; charset=utf-8" if alvo.suffix in (".html", ".js", ".css", ".svg") else ""))
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(b)

    # ---- roteamento ----
    def do_GET(self):
        self._rota("GET")

    def do_POST(self):
        self._rota("POST")

    def do_PATCH(self):
        self._rota("PATCH")

    def _rota(self, metodo):
        u = urlparse(self.path)
        if not u.path.startswith("/api/v1"):
            return self._estatico(u.path) if metodo == "GET" else self._json(405, {"codigo": "metodo", "mensagem": "?"})
        p, q = u.path[len("/api/v1"):], parse_qs(u.query)
        if p == "/saude":
            return self._json(200, {"status": "ok"})
        if p == "/auth/login" and metodo == "POST":
            b = self._corpo()
            usr = next((x for x in CFG["usuarios"] if x["email"] == b.get("email")), None)
            if not usr or b.get("senha") != CFG["senha_teste"]:
                return self._json(401, {"codigo": "nao_autenticado", "mensagem": "E-mail ou senha inválidos."})
            tok = secrets.token_urlsafe(24)
            SESSOES[tok] = usr
            return self._json(200, usr, {"Set-Cookie": f"rp_sessao={tok}; Path=/; HttpOnly; SameSite=Strict"})
        user = self._usuario()
        if not user:
            return self._json(401, {"codigo": "nao_autenticado", "mensagem": "Sessão inexistente ou expirada."})
        if p == "/auth/logout" and metodo == "POST":
            ck = SimpleCookie(self.headers.get("Cookie", ""))
            SESSOES.pop(ck["rp_sessao"].value, None)
            return self._json(204, None, {"Set-Cookie": "rp_sessao=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict"})
        if p == "/auth/eu":
            return self._json(200, user)
        if p == "/filtros":
            lst = [c for c in COLABS if no_escopo(user, c)]
            ufs = sorted({c["resumo"]["uf"] for c in lst})
            sups = sorted({c["resumo"]["supervisor"] for c in lst})
            return self._json(200, {"ufs": ufs, "supervisores": [{"cpf_mascarado": "***.000.000-**", "nome": s} for s in sups],
                                    "periodo_disponivel": CFG["periodo"],
                                    "bases": [{"origem": o, "periodo": CFG["periodo"], "linhas": 1000, "atualizada_em": "2026-11-16T06:00:00-03:00"} for o in ("operacao", "atividades", "aderencia")]})
        if p == "/painel":
            return self._json(200, painel(user, q))
        if p == "/painel/radar":
            return self._json(200, radar(user, q))
        if p == "/painel/ranking":
            lst = ordem_risco(filtrar(user, q))
            itens, prox = pagina(lst, q)
            return self._json(200, {"itens": [c["resumo"] for c in itens], "total": len(lst), "proximo_cursor": prox})
        if p == "/alertas":
            return self._json(200, alertas(user, q))
        if p == "/colaboradores" and metodo == "GET":
            t = (q.get("q", [""])[0]).strip().lower()
            dig = re.sub(r"\D", "", t)
            lst = [c for c in COLABS if no_escopo(user, c) and (t in c["resumo"]["nome"].lower() or (dig and dig in re.sub(r"\D", "", c["_cpf"])))]
            itens, prox = pagina(sorted(lst, key=lambda c: c["resumo"]["nome"]), q)
            return self._json(200, {"itens": [c["resumo"] for c in itens], "total": len(lst), "proximo_cursor": prox})
        m = re.fullmatch(r"/colaboradores/([^/]+)/raio-x", p)
        if m:
            st, corpo = raio_x(user, unquote(m.group(1)), q)
            return self._json(st, corpo)
        if p == "/dossies":
            if metodo == "POST":
                if user["perfil"] not in GERAM_DOSSIE:
                    return self._json(403, {"codigo": "sem_permissao", "mensagem": "Seu perfil não gera rascunho de dossiê."})
                b = self._corpo()
                c = POR_ID.get(b.get("colaborador_id"))
                if not c or not no_escopo(user, c):
                    return self._json(404, {"codigo": "nao_encontrado", "mensagem": "Colaborador fora do escopo."})
                did = "d_" + secrets.token_hex(4)
                cont = texto_dossie(c, b["ini"], b["fim"], b.get("relato"))
                DOSSIES[did] = {"id": did, "numero": None, "status": "rascunho", "colaborador": c["resumo"], "periodo": {"ini": b["ini"], "fim": b["fim"]},
                                "parametro_versao": 1, "relato": b.get("relato"), "conteudo": cont, "avisos_revisao": revisar(cont), "arquivos": {}, "emitido_em": None}
                return self._json(201, montar_dossie(DOSSIES[did], user))
            lst = [d for d in DOSSIES.values() if no_escopo(user, POR_ID[d["colaborador"]["id"]])]
            return self._json(200, [{"numero": d["numero"] or d["id"], "status": d["status"], "colaborador": d["colaborador"]["nome"], "periodo": d["periodo"], "emitido_em": d["emitido_em"]} for d in lst])
        m = re.fullmatch(r"/dossies/(RP-\d{4}-\d{6})/arquivo", p)
        if m:
            d = next((x for x in DOSSIES.values() if x["numero"] == m.group(1)), None)
            if not d:
                return self._json(404, {"codigo": "nao_encontrado", "mensagem": "Dossiê não encontrado."})
            fmt = q.get("formato", ["pdf"])[0]
            ctype = "application/pdf" if fmt == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Disposition", "attachment; filename*=UTF-8''" + d["arquivos"][fmt].replace(" ", "%20").replace("ê", "%C3%AA"))
            self.send_header("Content-Length", str(len(PDF_MIN)))
            self.end_headers()
            self.wfile.write(PDF_MIN)
            return
        m = re.fullmatch(r"/dossies/([^/]+)(/emitir)?", p)
        if m:
            d = DOSSIES.get(unquote(m.group(1))) or next((x for x in DOSSIES.values() if x["numero"] == unquote(m.group(1))), None)
            if not d or not no_escopo(user, POR_ID[d["colaborador"]["id"]]):
                return self._json(404, {"codigo": "nao_encontrado", "mensagem": "Dossiê não encontrado."})
            if m.group(2):
                if user["perfil"] not in GERAM_DOSSIE:
                    return self._json(403, {"codigo": "sem_permissao", "mensagem": "Seu perfil não emite dossiê."})
                av = revisar(d["conteudo"])
                if av or d["status"] == "emitido":
                    return self._json(422, {"codigo": "revisao_bloqueou", "mensagem": "A revisão bloqueou a emissão.", "detalhes": av or ["Dossiê já emitido."]})
                SEQ["n"] += 1
                d.update(numero=f"RP-{date.today().year}-{SEQ['n']:06d}", status="emitido", emitido_em=date.today().isoformat() + "T12:00:00-03:00",
                         arquivos={"pdf": f"Dossiê - {d['colaborador']['nome']}.pdf", "xlsx": f"Dossiê - {d['colaborador']['nome']}.xlsx"})
                return self._json(200, montar_dossie(d, user))
            if metodo == "PATCH":
                if d["status"] == "emitido":
                    return self._json(409, {"codigo": "ja_emitido", "mensagem": "Dossiê já emitido."})
                d["conteudo"] = {**d["conteudo"], **self._corpo()}
                d["avisos_revisao"] = revisar(d["conteudo"])
            return self._json(200, montar_dossie(d, user))
        return self._json(404, {"codigo": "nao_encontrado", "mensagem": "Rota inexistente no mock."})


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Mock do Radar Promotor em http://127.0.0.1:{porta}  (usuários: tests/fixtures/front/usuarios.json)")
    ThreadingHTTPServer(("127.0.0.1", porta), H).serve_forever()


if __name__ == "__main__":
    main()
