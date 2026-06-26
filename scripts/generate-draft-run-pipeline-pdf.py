from __future__ import annotations

import re
from argparse import ArgumentParser
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs" / "architecture" / "DRAFT_RUN_PIPELINE_AS_IS.md"
DEFAULT_OUTPUT = ROOT / "docs" / "architecture" / "DRAFT_RUN_PIPELINE_AS_IS.pdf"
FONT_REGULAR = Path("C:/Windows/Fonts/arial.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_MONO = Path("C:/Windows/Fonts/consola.ttf")


def main() -> None:
    args = _parse_args()
    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    _register_fonts()
    markdown = source.read_text(encoding="utf-8")
    story = _build_story(markdown)
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="DraftRun Pipeline AS IS",
        author="Glavred",
    )
    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
    print(f"Generated {output}")


def _parse_args():
    parser = ArgumentParser(description="Generate a PDF from a DraftRun pipeline Markdown document.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="Markdown source path.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="PDF output path.")
    return parser.parse_args()


def _register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("DocRegular", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("DocBold", str(FONT_BOLD)))
    pdfmetrics.registerFont(TTFont("DocMono", str(FONT_MONO)))


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="DocBold",
            fontSize=22,
            leading=27,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="DocBold",
            fontSize=15,
            leading=19,
            spaceBefore=10,
            spaceAfter=7,
        ),
        "h3": ParagraphStyle(
            "h3",
            parent=base["Heading3"],
            fontName="DocBold",
            fontSize=12.5,
            leading=16,
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontName="DocRegular",
            fontSize=9.4,
            leading=13,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["BodyText"],
            fontName="DocRegular",
            fontSize=9.2,
            leading=12.5,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "code",
            parent=base["Code"],
            fontName="DocMono",
            fontSize=7.4,
            leading=9.2,
            backColor=colors.HexColor("#f4f1ea"),
            borderColor=colors.HexColor("#ddd6c8"),
            borderWidth=0.5,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "table": ParagraphStyle(
            "table",
            parent=base["BodyText"],
            fontName="DocRegular",
            fontSize=7.2,
            leading=9,
        ),
        "tableHeader": ParagraphStyle(
            "tableHeader",
            parent=base["BodyText"],
            fontName="DocBold",
            fontSize=7.2,
            leading=9,
            alignment=TA_CENTER,
        ),
    }


def _build_story(markdown: str) -> list:
    styles = _styles()
    story: list = []
    lines = markdown.splitlines()
    i = 0
    in_code = False
    code_language = ""
    code_lines: list[str] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        text = " ".join(line.strip() for line in paragraph_lines if line.strip())
        paragraph_lines.clear()
        if text:
            story.append(Paragraph(_inline(text), styles["body"]))

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                code = "\n".join(code_lines)
                if code_language == "mermaid":
                    story.append(MermaidDiagram(code))
                else:
                    story.append(Preformatted(code, styles["code"]))
                code_lines = []
                in_code = False
                code_language = ""
            else:
                flush_paragraph()
                in_code = True
                code_language = stripped[3:].strip()
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            flush_paragraph()
            story.append(Spacer(1, 2))
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and _is_table_separator(lines[i + 1]):
            flush_paragraph()
            table_lines = [stripped, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            story.append(_table(table_lines, styles))
            story.append(Spacer(1, 6))
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped[2:]), styles["h1"]))
            i += 1
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped[3:]), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped[4:]), styles["h3"]))
            i += 1
            continue
        if stripped in {"---", "***"}:
            flush_paragraph()
            story.append(PageBreak())
            i += 1
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(f"- {_inline(stripped[2:])}", styles["bullet"]))
            i += 1
            continue
        if re.match(r"^\d+\. ", stripped):
            flush_paragraph()
            story.append(Paragraph(_inline(stripped), styles["bullet"]))
            i += 1
            continue

        paragraph_lines.append(line)
        i += 1

    flush_paragraph()
    return story


class MermaidDiagram(Flowable):
    def __init__(self, code: str) -> None:
        super().__init__()
        self.code = code
        self.kind = self._detect_kind(code)
        self.width = 0
        self.height = 230 if self.kind == "sequence" else 245

    def wrap(self, available_width, available_height):
        self.width = available_width
        if self.kind == "flow_td":
            nodes, edges = _parse_flowchart(self.code)
            row_count = max(1, (len(_ordered_nodes(nodes, edges)) + 1) // 2)
            self.height = max(170, min(300, 42 + row_count * 36))
        elif self.kind == "flow_lr":
            self.height = 235
        else:
            self.height = 245
        return self.width, self.height + 8

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        self._draw_panel(canvas)
        if self.kind == "sequence":
            self._draw_sequence(canvas)
        elif self.kind == "flow_lr":
            self._draw_flow_lr(canvas)
        else:
            self._draw_flow_td(canvas)
        canvas.restoreState()

    def _detect_kind(self, code: str) -> str:
        first = code.strip().splitlines()[0].strip()
        if first == "sequenceDiagram":
            return "sequence"
        if first == "flowchart LR":
            return "flow_lr"
        return "flow_td"

    def _draw_panel(self, canvas) -> None:
        canvas.setFillColor(colors.HexColor("#fbfaf7"))
        canvas.setStrokeColor(colors.HexColor("#ddd6c8"))
        canvas.roundRect(0, 4, self.width, self.height, 8, fill=1, stroke=1)

    def _draw_sequence(self, canvas) -> None:
        participants: list[tuple[str, str]] = []
        messages: list[tuple[str, str, str, str]] = []
        for raw in self.code.splitlines():
            line = raw.strip()
            participant = re.match(r"participant\s+(\w+)\s+as\s+(.+)", line)
            if participant:
                participants.append((participant.group(1), participant.group(2)))
                continue
            message = re.match(r"(\w+)(-->>|->>)(\w+):\s+(.+)", line)
            if message:
                messages.append((message.group(1), message.group(3), message.group(4), message.group(2)))

        margin = 18
        top = self.height - 24
        bottom = 20
        column_width = (self.width - margin * 2) / max(1, len(participants))
        centers = {
            key: margin + column_width * index + column_width / 2
            for index, (key, _) in enumerate(participants)
        }

        canvas.setFont("DocBold", 7.5)
        for key, label in participants:
            x = centers[key]
            box_w = min(82, column_width - 8)
            canvas.setFillColor(colors.HexColor("#eee8dc"))
            canvas.setStrokeColor(colors.HexColor("#d2c7b6"))
            canvas.roundRect(x - box_w / 2, top - 18, box_w, 20, 6, fill=1, stroke=1)
            canvas.setFillColor(colors.HexColor("#2b2824"))
            canvas.drawCentredString(x, top - 11, _short(label, 18))
            canvas.setDash(2, 3)
            canvas.setStrokeColor(colors.HexColor("#c7bdad"))
            canvas.line(x, top - 20, x, bottom)
            canvas.setDash()

        y = top - 38
        step = max(15, min(19, (y - bottom) / max(1, len(messages))))
        for source, target, label, arrow_type in messages:
            if source not in centers or target not in centers:
                continue
            x1 = centers[source]
            x2 = centers[target]
            canvas.setStrokeColor(colors.HexColor("#6e665a"))
            canvas.setFillColor(colors.HexColor("#6e665a"))
            canvas.line(x1, y, x2, y)
            self._arrow_head(canvas, x1, x2, y)
            canvas.setFont("DocRegular", 6.6)
            canvas.setFillColor(colors.HexColor("#3a352f"))
            canvas.drawCentredString((x1 + x2) / 2, y + 3, _short(label, 48))
            y -= step

    def _draw_flow_td(self, canvas) -> None:
        nodes, edges = _parse_flowchart(self.code)
        order = _ordered_nodes(nodes, edges)
        margin_x = 18
        box_w = (self.width - margin_x * 2 - 18) / 2
        box_h = 24
        gap_y = 12
        top = self.height - 28
        positions: dict[str, tuple[float, float]] = {}

        split = (len(order) + 1) // 2
        columns = [order[:split], order[split:]]
        for col, column_nodes in enumerate(columns):
            x = margin_x + col * (box_w + 18)
            for row, key in enumerate(column_nodes):
                y = top - row * (box_h + gap_y)
                positions[key] = (x, y)
                self._node(canvas, x, y, box_w, box_h, nodes.get(key, key), active=key in {"L", "M"})

        for source, target in edges:
            if source not in positions or target not in positions:
                continue
            x1, y1 = positions[source]
            x2, y2 = positions[target]
            if abs(x1 - x2) < 1:
                self._down_arrow(canvas, x1 + box_w / 2, y1, y2 + box_h)
            else:
                self._elbow_arrow(canvas, x1 + box_w, y1 + box_h / 2, x2, y2 + box_h / 2)

    def _draw_flow_lr(self, canvas) -> None:
        nodes, edges = _parse_flowchart(self.code)
        left = ["A", "B", "C", "E", "F"]
        right = ["G", "H", "I", "J", "K", "L"]
        center = "D"
        margin_x = 18
        left_w = 132
        center_w = 112
        right_w = 130
        box_h = 24
        top = self.height - 32
        positions: dict[str, tuple[float, float, float]] = {}

        for index, key in enumerate(left):
            x = margin_x
            y = top - index * 34
            positions[key] = (x, y, left_w)
            self._node(canvas, x, y, left_w, box_h, nodes.get(key, key))

        center_x = self.width / 2 - center_w / 2
        center_y = self.height / 2 + 2
        positions[center] = (center_x, center_y, center_w)
        self._node(canvas, center_x, center_y, center_w, 34, nodes.get(center, center), active=True)

        for index, key in enumerate(right):
            x = self.width - margin_x - right_w
            y = top - index * 30
            positions[key] = (x, y, right_w)
            self._node(canvas, x, y, right_w, box_h, nodes.get(key, key))

        for source, target in edges:
            if source not in positions or target not in positions:
                continue
            x1, y1, w1 = positions[source]
            x2, y2, _ = positions[target]
            self._elbow_arrow(canvas, x1 + w1, y1 + box_h / 2, x2, y2 + box_h / 2)

    def _node(self, canvas, x: float, y: float, w: float, h: float, label: str, active: bool = False) -> None:
        canvas.setFillColor(colors.HexColor("#fffdf8") if not active else colors.HexColor("#f2eadc"))
        canvas.setStrokeColor(colors.HexColor("#d5ccbd") if not active else colors.HexColor("#b9aa94"))
        canvas.roundRect(x, y, w, h, 6, fill=1, stroke=1)
        canvas.setFont("DocBold", 7.3)
        canvas.setFillColor(colors.HexColor("#27231f"))
        lines = _wrap_words(label, max(10, int(w / 5.6)), 2)
        start_y = y + h / 2 + (len(lines) - 1) * 4 - 3
        for index, line in enumerate(lines):
            canvas.drawCentredString(x + w / 2, start_y - index * 8, line)

    def _arrow_head(self, canvas, x1: float, x2: float, y: float) -> None:
        direction = 1 if x2 >= x1 else -1
        canvas.line(x2, y, x2 - direction * 5, y + 3)
        canvas.line(x2, y, x2 - direction * 5, y - 3)

    def _down_arrow(self, canvas, x: float, y1: float, y2: float) -> None:
        canvas.setStrokeColor(colors.HexColor("#84796b"))
        canvas.line(x, y1, x, y2)
        canvas.line(x, y2, x - 3, y2 + 5)
        canvas.line(x, y2, x + 3, y2 + 5)

    def _elbow_arrow(self, canvas, x1: float, y1: float, x2: float, y2: float) -> None:
        canvas.setStrokeColor(colors.HexColor("#84796b"))
        mid = (x1 + x2) / 2
        canvas.line(x1, y1, mid, y1)
        canvas.line(mid, y1, mid, y2)
        canvas.line(mid, y2, x2, y2)
        canvas.line(x2, y2, x2 - 5, y2 + 3)
        canvas.line(x2, y2, x2 - 5, y2 - 3)


def _is_table_separator(line: str) -> bool:
    stripped = line.strip()
    return bool(re.fullmatch(r"\|?[\s:\-|]+\|?", stripped)) and "---" in stripped


def _table(lines: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [_cells(line) for line in lines if not _is_table_separator(line)]
    if not rows:
        return Table([[""]])
    max_cols = max(len(row) for row in rows)
    normalized = [row + [""] * (max_cols - len(row)) for row in rows]
    data = []
    for row_index, row in enumerate(normalized):
        style = styles["tableHeader"] if row_index == 0 else styles["table"]
        data.append([Paragraph(_inline(cell), style) for cell in row])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eee8dc")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f1d1a")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d8d0c1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _cells(line: str) -> list[str]:
    value = line.strip().strip("|")
    return [cell.strip() for cell in value.split("|")]


def _parse_flowchart(code: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    nodes: dict[str, str] = {}
    edges: list[tuple[str, str]] = []
    node_pattern = re.compile(r"(\w+)\[([^\]]+)\]")
    edge_pattern = re.compile(r"(\w+)(?:\[[^\]]+\])?\s*-->\s*(\w+)(?:\[[^\]]+\])?")
    for raw in code.splitlines():
        line = raw.strip()
        for key, label in node_pattern.findall(line):
            nodes[key] = label
        edge = edge_pattern.search(line)
        if edge:
            edges.append((edge.group(1), edge.group(2)))
    return nodes, edges


def _ordered_nodes(nodes: dict[str, str], edges: list[tuple[str, str]]) -> list[str]:
    if not edges:
        return list(nodes)
    targets = {target for _, target in edges}
    candidates = [source for source, _ in edges if source not in targets]
    current = candidates[0] if candidates else edges[0][0]
    order = [current]
    seen = {current}
    while True:
        next_nodes = [target for source, target in edges if source == current and target not in seen]
        if not next_nodes:
            break
        current = next_nodes[0]
        order.append(current)
        seen.add(current)
    for key in nodes:
        if key not in seen:
            order.append(key)
    return order


def _wrap_words(text: str, width: int, max_lines: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if not lines:
        lines = [text[:width]]
    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = _short(lines[-1], width)
    return lines


def _short(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return f"{text[: max(1, max_length - 1)]}..."


def _inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="DocMono">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def _footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("DocRegular", 7)
    canvas.setFillColor(colors.HexColor("#7d756a"))
    canvas.drawString(18 * mm, 9 * mm, "Glavred - DraftRun Pipeline")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


if __name__ == "__main__":
    main()
