"""PDF formal do dossiê (CLAUDE.md §5). Layout de A4 retrato, com as cores da identidade RT.

Cada página traz logo, CONFIDENCIAL no topo e, no rodapé, número, página, código de
verificação e a frase de indícios. A saída é determinística: mesma entrada e mesma
data de emissão geram o mesmo arquivo, então o SHA-256 gravado confere.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab import rl_config
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from documentos.conteudo import rotulo_conclusao
from documentos.modelos import DadosDossie, Grafico, Tabela
from documentos.numeracao import FUSO

# Sem ano/data automáticos nos metadados: o mesmo dossiê gera o mesmo arquivo.
rl_config.invariant = 1

W, H = A4
LM = RM = 18 * mm
TM = 30 * mm
BM = 30 * mm
LARGURA = W - LM - RM

LOGO = Path(__file__).parent / "templates" / "rt-intelligence.png"
NAVY = colors.HexColor("#10263B")
ORANGE = colors.HexColor("#F4562A")
GREY = colors.HexColor("#56697E")
LIGHT = colors.HexColor("#E6EBF1")
ZEBRA = colors.HexColor("#F5F7FA")
GRADE = colors.HexColor("#BFC8D2")
PALETA = (NAVY, ORANGE, GREY, colors.HexColor("#8FA3B8"))

FRASE_RODAPE = "Este relatório apresenta indícios baseados em registros operacionais"
NOMES_SECOES = (
    "Identificação",
    "Introdução e objetivos",
    "Relato a apurar",
    "Relatos identificados",
    "Impacto na aderência e na operação",
    "Contexto de acompanhamento",
    "Considerações finais",
)


def _estilos() -> dict[str, ParagraphStyle]:
    return {
        "titulo": ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=15, leading=19,
                                 alignment=TA_CENTER, textColor=NAVY, spaceAfter=2),
        "subtitulo": ParagraphStyle("subtitulo", fontName="Helvetica", fontSize=9, leading=12,
                                    alignment=TA_CENTER, textColor=GREY, spaceAfter=8),
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=11, leading=14,
                             textColor=NAVY, spaceBefore=10, spaceAfter=4),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
                             textColor=NAVY, spaceBefore=6, spaceAfter=3),
        "corpo": ParagraphStyle("corpo", fontName="Helvetica", fontSize=9, leading=12.5,
                                alignment=TA_JUSTIFY, spaceAfter=4),
        "conclusao": ParagraphStyle("conclusao", fontName="Helvetica-Bold", fontSize=8.5,
                                    leading=11, textColor=NAVY, spaceAfter=4),
        "cel": ParagraphStyle("cel", fontName="Helvetica", fontSize=8, leading=10),
        "cel_rotulo": ParagraphStyle("cel_rotulo", fontName="Helvetica-Bold", fontSize=8,
                                     leading=10, textColor=NAVY),
        "cab": ParagraphStyle("cab", fontName="Helvetica-Bold", fontSize=8, leading=10,
                              textColor=colors.white),
    }


def _p(texto: object, estilo: ParagraphStyle) -> Paragraph:
    valor = "" if texto is None else str(texto)
    return Paragraph(escape(valor).replace("\n", "<br/>"), estilo)


def _tabela_chave_valor(linhas: list[tuple[str, str]], st: dict[str, ParagraphStyle]) -> Table:
    dados = [[_p(r, st["cel_rotulo"]), _p(v, st["cel"])] for r, v in linhas]
    tb = Table(dados, colWidths=[46 * mm, LARGURA - 46 * mm])
    tb.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT),
                ("GRID", (0, 0), (-1, -1), 0.25, GRADE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return tb


def _tabela_bloco(tabela: Tabela, st: dict[str, ParagraphStyle]) -> Table:
    cabecalho = [_p(c, st["cab"]) for c in tabela.colunas]
    corpo = [[_p(v, st["cel"]) for v in linha] for linha in tabela.linhas]
    largura_coluna = LARGURA / len(tabela.colunas)
    tb = Table([cabecalho, *corpo], colWidths=[largura_coluna] * len(tabela.colunas), repeatRows=1)
    tb.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
                ("GRID", (0, 0), (-1, -1), 0.25, GRADE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return tb


def _grafico(grafico: Grafico) -> Drawing:
    altura = 170
    d = Drawing(LARGURA, altura)
    bc = VerticalBarChart()
    bc.x = 34
    bc.y = 26
    bc.width = LARGURA - 60
    bc.height = altura - 40
    bc.data = [list(s.valores) for s in grafico.series]
    bc.categoryAxis.categoryNames = list(grafico.categorias)
    bc.categoryAxis.labels.fontName = "Helvetica"
    bc.categoryAxis.labels.fontSize = 7
    bc.valueAxis.valueMin = 0
    maximo = max(max(s.valores) for s in grafico.series)
    bc.valueAxis.valueMax = max(maximo * 1.15, 1)
    bc.valueAxis.labels.fontName = "Helvetica"
    bc.valueAxis.labels.fontSize = 7
    bc.groupSpacing = 6
    bc.barSpacing = 1
    for i in range(len(grafico.series)):
        bc.bars[i].fillColor = PALETA[i % len(PALETA)]
        bc.bars[i].strokeColor = None
    d.add(bc)
    if len(grafico.series) > 1:
        legenda = Legend()
        legenda.fontName = "Helvetica"
        legenda.fontSize = 7
        legenda.x = 34
        legenda.y = 4
        legenda.columnMaximum = len(grafico.series)
        legenda.deltax = 110
        legenda.colorNamePairs = [
            (PALETA[i % len(PALETA)], s.nome) for i, s in enumerate(grafico.series)
        ]
        d.add(legenda)
    return d


def _historia(
    conteudo: dict[str, Any],
    dados: DadosDossie,
    contexto_visivel: bool,
    st: dict[str, ParagraphStyle],
) -> list[Any]:
    fluxo: list[Any] = [
        _p("DOSSIÊ DE ANÁLISE OPERACIONAL", st["titulo"]),
        _p("RT Intelligence", st["subtitulo"]),
        _tabela_chave_valor(
            [
                ("Documento nº", dados.numero),
                ("Emissão", dados.emitido_em.astimezone(FUSO).strftime("%d/%m/%Y às %H:%M")),
                ("Emissor", dados.emissor),
                ("Versão dos parâmetros", str(dados.parametro_versao)),
            ],
            st,
        ),
    ]

    contexto_texto = conteudo.get("contexto_acompanhamento") if contexto_visivel else None
    nomes = [n for n in NOMES_SECOES if n != "Contexto de acompanhamento" or contexto_texto]
    numero = {nome: i for i, nome in enumerate(nomes, start=1)}

    def titulo(nome: str) -> Paragraph:
        return _p(f"{numero[nome]}. {nome}", st["h1"])

    # 1. Identificação
    fluxo.append(titulo("Identificação"))
    linhas = [("Colaborador", dados.colaborador), ("CPF", dados.cpf)]
    if dados.uf:
        linhas.append(("UF", dados.uf))
    if dados.supervisor:
        linhas.append(("Supervisor", dados.supervisor))
    linhas.append(
        (
            "Período analisado",
            f"{dados.periodo_ini:%d/%m/%Y} a {dados.periodo_fim:%d/%m/%Y}",
        )
    )
    fluxo.append(_tabela_chave_valor(linhas, st))

    # 2. Introdução e objetivos
    fluxo.append(titulo("Introdução e objetivos"))
    for chave in ("intro", "objetivos"):
        if conteudo.get(chave):
            fluxo.append(_p(conteudo[chave], st["corpo"]))

    # 3. Relato a apurar
    fluxo.append(titulo("Relato a apurar"))
    fluxo.append(
        _p(dados.relato or "Não há relato vinculado a este dossiê.", st["corpo"])
    )

    # 4. Relatos identificados
    fluxo.append(titulo("Relatos identificados"))
    blocos = conteudo.get("blocos") or []
    if not blocos:
        fluxo.append(_p("Não há relatos identificados a apresentar.", st["corpo"]))
    for i, bloco in enumerate(blocos, start=1):
        fluxo.append(
            _p(f"{numero['Relatos identificados']}.{i} {bloco['titulo']}", st["h2"])
        )
        fluxo.append(_p(bloco["texto"], st["corpo"]))
        rotulo = rotulo_conclusao(bloco.get("conclusao"))
        if rotulo:
            fluxo.append(_p(f"Conclusão: {rotulo}", st["conclusao"]))
        tabela = dados.tabelas.get(bloco["chave"])
        if tabela is not None:
            fluxo.append(_tabela_bloco(tabela, st))
            fluxo.append(Spacer(1, 4))
            if tabela.grafico is not None:
                fluxo.append(_grafico(tabela.grafico))
        fluxo.append(Spacer(1, 6))

    # 5. Impacto
    fluxo.append(titulo("Impacto na aderência e na operação"))
    fluxo.append(_p(conteudo.get("impacto") or "Sem impacto a registrar.", st["corpo"]))

    # 6. Contexto de acompanhamento (só perfis autorizados)
    if contexto_texto:
        fluxo.append(titulo("Contexto de acompanhamento"))
        fluxo.append(_p(contexto_texto, st["corpo"]))

    # 7. Considerações finais
    fluxo.append(titulo("Considerações finais"))
    fluxo.append(_p(conteudo["consideracoes_finais"], st["corpo"]))
    return fluxo


def _cabecalho(canv: canvas.Canvas, _doc: Any) -> None:
    canv.saveState()
    altura_logo = 40 * mm * 182 / 760
    canv.drawImage(
        str(LOGO),
        LM,
        H - 12 * mm - altura_logo,
        width=40 * mm,
        height=altura_logo,
        mask="auto",
        preserveAspectRatio=True,
    )
    canv.setFont("Helvetica-Bold", 9)
    canv.setFillColor(GREY)
    canv.drawRightString(W - RM, H - 12 * mm - altura_logo + 2, "CONFIDENCIAL")
    canv.setStrokeColor(GRADE)
    canv.setLineWidth(0.4)
    canv.line(LM, H - 24 * mm, W - RM, H - 24 * mm)
    canv.restoreState()


def _classe_canvas(numero: str, codigo: str, comprimir: bool):
    class _Canvas(canvas.Canvas):
        """Guarda as páginas para escrever 'Página X de Y' no rodapé."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs["pageCompression"] = comprimir
            super().__init__(*args, **kwargs)
            self._paginas: list[dict[str, Any]] = []

        def showPage(self) -> None:
            self._paginas.append(dict(self.__dict__))
            self._startPage()

        def save(self) -> None:
            total = len(self._paginas)
            for n, estado in enumerate(self._paginas, start=1):
                self.__dict__.update(estado)
                self._rodape(n, total)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def _rodape(self, n: int, total: int) -> None:
            self.saveState()
            self.setFillColor(GREY)
            self.setFont("Helvetica", 7.5)
            self.drawString(LM, BM - 10 * mm, f"{numero}  ·  Página {n} de {total}")
            self.drawRightString(W - RM, BM - 10 * mm, f"Código de verificação: {codigo}")
            self.setFont("Helvetica", 7)
            self.drawCentredString(W / 2, BM - 16 * mm, FRASE_RODAPE + ".")
            self.restoreState()

    return _Canvas


def montar_pdf(
    conteudo: dict[str, Any],
    dados: DadosDossie,
    *,
    contexto_visivel: bool,
    codigo_verificacao: str,
    comprimir: bool = True,
) -> bytes:
    buf = BytesIO()
    doc = BaseDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=LM,
        rightMargin=RM,
        topMargin=TM,
        bottomMargin=BM,
        title=f"Dossiê de Análise Operacional {dados.numero}",
        author="RT Intelligence",
        subject=dados.numero,
        creator="RT Intelligence",
    )
    frame = Frame(LM, BM, LARGURA, H - TM - BM, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="dossie", frames=[frame], onPage=_cabecalho)])
    st = _estilos()
    doc.build(
        _historia(conteudo, dados, contexto_visivel, st),
        canvasmaker=_classe_canvas(dados.numero, codigo_verificacao, comprimir),
    )
    return buf.getvalue()
