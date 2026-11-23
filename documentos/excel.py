"""Excel de apoio do dossiê: uma aba por informação, sem células mescladas.

Os números e textos são os mesmos do PDF. A aba de contexto só existe para perfis
autorizados (o arquivo é montado sem ela, não apenas oculta).
"""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from documentos.conteudo import rotulo_conclusao
from documentos.modelos import DadosDossie, Tabela
from documentos.numeracao import FUSO

NAVY = "FF10263B"
CABECALHO = PatternFill(fill_type="solid", fgColor=NAVY)
FONTE_CABECALHO = Font(bold=True, color="FFFFFFFF")
FONTE_TITULO = Font(bold=True, size=12, color=NAVY)
QUEBRA = Alignment(wrap_text=True, vertical="top")
_CARACTERES_PROIBIDOS_NOME_ABA = re.compile(r"[\\/*?:\[\]]")


def _celula(valor: object) -> object:
    return "" if valor is None else valor


def _escrever_cabecalho(
    ws: Any, colunas: tuple[str, ...] | list[str], larguras: list[int], linha: int = 1
) -> None:
    for i, nome in enumerate(colunas, start=1):
        c = ws.cell(row=linha, column=i, value=nome)
        c.fill = CABECALHO
        c.font = FONTE_CABECALHO
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = larguras[i - 1]
    ws.freeze_panes = f"A{linha + 1}"


def _escrever_linha(ws: Any, linha_idx: int, valores: tuple[object, ...] | list[object]) -> None:
    for i, valor in enumerate(valores, start=1):
        c = ws.cell(row=linha_idx, column=i)
        c.value = _celula(valor)
        if isinstance(c.value, str):
            # Texto nunca vira fórmula, mesmo que comece com "=", "+", "-" ou "@".
            c.data_type = "s"
        c.alignment = QUEBRA


def _aba_tabela(wb: Workbook, colunas: tuple[str, ...], linhas: list[tuple[object, ...]],
                nome: str, larguras: list[int] | None = None) -> Any:
    ws = wb.create_sheet(nome)
    larguras = larguras or [22] * len(colunas)
    _escrever_cabecalho(ws, colunas, larguras)
    for n, linha in enumerate(linhas, start=2):
        _escrever_linha(ws, n, linha)
    if linhas:
        ws.auto_filter.ref = f"A1:{get_column_letter(len(colunas))}{len(linhas) + 1}"
    return ws


def _nome_aba(rotulo: str, usados: set[str]) -> str:
    base = _CARACTERES_PROIBIDOS_NOME_ABA.sub(" ", rotulo).strip()[:28] or "Aba"
    nome, i = base, 2
    while nome.lower() in {u.lower() for u in usados}:
        nome = f"{base[:26]} {i}"
        i += 1
    usados.add(nome)
    return nome


def montar_excel(
    conteudo: dict[str, Any],
    dados: DadosDossie,
    *,
    contexto_visivel: bool,
    codigo_verificacao: str,
) -> bytes:
    wb = Workbook()
    emitido = dados.emitido_em.astimezone(FUSO)
    wb.properties.title = f"Dossiê de Análise Operacional {dados.numero}"
    wb.properties.creator = "RT Intelligence"
    wb.properties.created = emitido.replace(tzinfo=None)
    wb.properties.modified = emitido.replace(tzinfo=None)

    # Identificação
    ws = wb.active
    ws.title = "Identificação"
    ws.cell(row=1, column=1, value="RT Intelligence · Dossiê de Análise Operacional").font = FONTE_TITULO
    _escrever_cabecalho(ws, ("Campo", "Valor"), [30, 70], linha=2)
    ident: list[tuple[object, ...]] = [
        ("Documento nº", dados.numero),
        ("Emissão", emitido.strftime("%d/%m/%Y %H:%M")),
        ("Emissor", dados.emissor),
        ("Classificação", "CONFIDENCIAL"),
        ("Código de verificação", codigo_verificacao),
        ("Colaborador", dados.colaborador),
        ("CPF", dados.cpf),
    ]
    if dados.uf:
        ident.append(("UF", dados.uf))
    if dados.supervisor:
        ident.append(("Supervisor", dados.supervisor))
    ident.append(("Período analisado", f"{dados.periodo_ini:%d/%m/%Y} a {dados.periodo_fim:%d/%m/%Y}"))
    ident.append(("Versão dos parâmetros", dados.parametro_versao))
    for n, (campo, valor) in enumerate(ident, start=3):
        ws.cell(row=n, column=1, value=campo).font = Font(bold=True, color=NAVY)
        _escrever_linha(ws, n, (campo, valor))
    ws.freeze_panes = None

    # Relatos
    blocos = conteudo.get("blocos") or []
    linhas_relatos = [
        (i, b["titulo"], rotulo_conclusao(b.get("conclusao")) or "", b["texto"])
        for i, b in enumerate(blocos, start=1)
    ]
    _aba_tabela(wb, ("Nº", "Ponto", "Conclusão", "Texto"), linhas_relatos, "Relatos",
                [6, 40, 22, 90])

    usados = {ws.title for ws in wb.worksheets}
    for i, b in enumerate(blocos, start=1):
        tabela: Tabela | None = dados.tabelas.get(b["chave"])
        if tabela is None:
            continue
        nome = _nome_aba(f"Bloco {i} - {b['titulo']}", usados)
        _aba_tabela(wb, tabela.colunas, [tuple(linha) for linha in tabela.linhas], nome)

    if contexto_visivel and conteudo.get("contexto_acompanhamento"):
        _aba_tabela(wb, ("Contexto de acompanhamento",),
                    [(conteudo["contexto_acompanhamento"],)], "Contexto", [100])

    _aba_tabela(
        wb,
        ("Parâmetro", "Valor aplicado", "Versão", "Vigência desde"),
        [(p.nome, p.valor, p.versao, p.vigente_desde.strftime("%d/%m/%Y")) for p in dados.parametros],
        "Parâmetros",
        [40, 30, 10, 18],
    )

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()

