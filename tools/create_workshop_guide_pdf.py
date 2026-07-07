from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass, field
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.html"
OUTPUT = ROOT / "workshop_guide.pdf"

INK = colors.HexColor("#232323")
MUTED = colors.HexColor("#5E6670")
LINE = colors.HexColor("#D9DDE3")
ORACLE = colors.HexColor("#C74634")
ORACLE_SOFT = colors.HexColor("#FBE9E5")
BLUE = colors.HexColor("#245EA6")
BLUE_SOFT = colors.HexColor("#EDF5FF")
GREEN = colors.HexColor("#167C52")
GREEN_SOFT = colors.HexColor("#EEF8F2")
AMBER = colors.HexColor("#946200")
AMBER_SOFT = colors.HexColor("#FFF7DF")
DARK = colors.HexColor("#252629")
CODE_BG = colors.HexColor("#F6F8FA")

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "header", "nav", "aside", "footer"}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)


class TreeBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag.lower() not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx].tag == tag:
                del self.stack[idx:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(unescape(data))

    def handle_entityref(self, name: str) -> None:
        self.stack[-1].children.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.stack[-1].children.append(unescape(f"&#{name};"))


def find_first(node: Node, tag: str) -> Node | None:
    if node.tag == tag:
        return node
    for child in node.children:
        if isinstance(child, Node):
            found = find_first(child, tag)
            if found:
                return found
    return None


def direct_children(node: Node, tag: str | None = None) -> list[Node]:
    return [child for child in node.children if isinstance(child, Node) and (tag is None or child.tag == tag)]


def sanitize(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u00a0": " ",
        "\u00b7": " | ",
        "\u2022": "*",
        "\u2192": "->",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return "".join(ch if ord(ch) < 128 else " " for ch in text)


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", sanitize(text)).strip()


def plain_text(node: Node | str) -> str:
    if isinstance(node, str):
        return sanitize(node)
    if node.tag in SKIP_TAGS:
        return ""
    if node.tag == "br":
        return "\n"
    return "".join(plain_text(child) for child in node.children)


def inline_markup(node: Node | str) -> str:
    if isinstance(node, str):
        return escape(compact(node))
    if node.tag in SKIP_TAGS:
        return ""
    if node.tag == "br":
        return "<br/>"
    inner = " ".join(part for part in (inline_markup(child) for child in node.children) if part)
    inner = re.sub(r"\s+", " ", inner).strip()
    if not inner:
        return ""
    if node.tag in {"strong", "b"}:
        return f"<b>{inner}</b>"
    if node.tag == "code":
        return f'<font name="Courier" color="#245EA6">{inner}</font>'
    if node.tag == "a":
        return f'<font color="#1A5A96">{inner}</font>'
    return inner


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=33,
            textColor=colors.white,
            alignment=TA_LEFT,
            spaceAfter=16,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=12.5,
            leading=18,
            textColor=colors.HexColor("#E8EEF4"),
            alignment=TA_LEFT,
            spaceAfter=28,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.2,
            leading=12,
            textColor=DARK,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            textColor=DARK,
            spaceBefore=6,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=DARK,
            spaceBefore=15,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=AMBER,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.3,
            textColor=INK,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.6,
            leading=9.6,
            textColor=INK,
        ),
        "caption": ParagraphStyle(
            "Caption",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.2,
            textColor=MUTED,
            alignment=TA_LEFT,
        ),
        "toc": ParagraphStyle(
            "TOC",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13.5,
            textColor=INK,
            leftIndent=10,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.8,
            leading=12.2,
            leftIndent=17,
            firstLineIndent=-9,
            bulletIndent=4,
            textColor=INK,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "Code",
            parent=base["Code"],
            fontName="Courier",
            fontSize=6.8,
            leading=8.4,
            textColor=INK,
            backColor=CODE_BG,
            borderColor=LINE,
            borderWidth=0.35,
            borderPadding=5,
            splitLongWords=True,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.6,
            leading=9.8,
            textColor=colors.white,
        ),
    }


def draw_page(canvas, doc) -> None:
    width, height = letter
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(DARK)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setFillColor(ORACLE)
        canvas.rect(0.62 * inch, height - 1.02 * inch, 1.1 * inch, 0.12 * inch, fill=1, stroke=0)
        canvas.setFillColor(colors.Color(1, 1, 1, alpha=0.12))
        for idx in range(8):
            canvas.circle(width - 1.35 * inch, 1.0 * inch + idx * 0.85 * inch, 0.33 * inch, fill=1, stroke=0)
    else:
        canvas.setStrokeColor(ORACLE)
        canvas.setLineWidth(2)
        canvas.line(doc.leftMargin, height - 0.48 * inch, width - doc.rightMargin, height - 0.48 * inch)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7.2)
        canvas.drawString(doc.leftMargin, height - 0.35 * inch, "Public Healthcare AIDP Workshop")
        canvas.drawRightString(width - doc.rightMargin, height - 0.35 * inch, "Screenshot-based execution guide")
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 0.48 * inch, width - doc.rightMargin, 0.48 * inch)
        canvas.drawString(doc.leftMargin, 0.31 * inch, "Oracle AI Data Platform | Autonomous AI Lakehouse | Oracle Analytics Cloud")
        canvas.drawRightString(width - doc.rightMargin, 0.31 * inch, f"Page {doc.page}")
    canvas.restoreState()


def add_cover(story: list, styles: dict[str, ParagraphStyle]) -> None:
    story.append(Spacer(1, 1.45 * inch))
    story.append(Paragraph("Public Healthcare AIDP Workshop", styles["cover_title"]))
    story.append(
        Paragraph(
            "Screenshot-based execution guide for MPHA claims analytics, AIDP medallion processing, AI Lakehouse star schema publishing, OAC dashboards, ML risk scoring, and AI agent labs.",
            styles["cover_subtitle"],
        )
    )
    meta = [
        [Paragraph("Core labs<br/>Setup to dashboard", styles["cover_meta"]), Paragraph("Gold model<br/>Claims star schema", styles["cover_meta"])],
        [Paragraph("Inputs<br/>CSV, JSONL, GeoJSON, DOCX", styles["cover_meta"]), Paragraph("Evidence<br/>Screenshots embedded", styles["cover_meta"])],
    ]
    table = Table(meta, colWidths=[2.25 * inch, 2.25 * inch], rowHeights=[0.74 * inch, 0.74 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#DCEAE5")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(table)
    story.append(PageBreak())


def collect_headings(node: Node) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for child in node.children:
        if isinstance(child, Node):
            if child.tag in {"h1", "h2"}:
                result.append((1 if child.tag == "h1" else 2, compact(plain_text(child))))
            result.extend(collect_headings(child))
    return result


def add_toc(story: list, styles: dict[str, ParagraphStyle], headings: list[tuple[int, str]]) -> None:
    story.append(Paragraph("Contents", styles["h1"]))
    for level, title in headings:
        if not title:
            continue
        prefix = "" if level == 1 else "&nbsp;&nbsp;"
        story.append(Paragraph(prefix + escape(title), styles["toc"]))
    story.append(PageBreak())


def resolve_image(src: str) -> Path | None:
    if not src or src.startswith(("http://", "https://", "data:")):
        return None
    path = (ROOT / src).resolve()
    if path.exists() and path.is_file():
        return path
    return None


def add_image(story: list, image_path: Path, caption: str, available_width: float, styles: dict[str, ParagraphStyle]) -> None:
    with PILImage.open(image_path) as img:
        px_w, px_h = img.size
    max_width = available_width
    max_height = 4.9 * inch
    scale = min(max_width / px_w, max_height / px_h)
    width = px_w * scale
    height = px_h * scale
    flow_img = Image(str(image_path), width=width, height=height)
    flow_img.hAlign = "CENTER"
    caption_text = caption or image_path.name
    frame = Table(
        [[flow_img], [Paragraph(escape(sanitize(caption_text)), styles["caption"])]],
        colWidths=[width],
        hAlign="CENTER",
    )
    frame.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.45, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("LINEBELOW", (0, 0), (0, 0), 0.35, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (0, 0), 0),
                ("BOTTOMPADDING", (0, 0), (0, 0), 0),
                ("LEFTPADDING", (0, 1), (0, 1), 7),
                ("RIGHTPADDING", (0, 1), (0, 1), 7),
                ("TOPPADDING", (0, 1), (0, 1), 6),
                ("BOTTOMPADDING", (0, 1), (0, 1), 6),
            ]
        )
    )
    story.append(Spacer(1, 8))
    story.append(frame)
    story.append(Spacer(1, 9))


def wrap_code(text: str, width: int = 96) -> str:
    lines: list[str] = []
    for line in sanitize(text).splitlines():
        if not line:
            lines.append("")
        elif len(line) <= width:
            lines.append(line)
        else:
            lines.extend(textwrap.wrap(line, width=width, break_long_words=True, break_on_hyphens=False))
    return "\n".join(lines)


def table_col_widths(count: int, available_width: float) -> list[float]:
    if count <= 0:
        return [available_width]
    if count == 2:
        return [available_width * 0.34, available_width * 0.66]
    if count == 3:
        return [available_width * 0.26, available_width * 0.32, available_width * 0.42]
    return [available_width / count] * count


def add_html_table(story: list, node: Node, styles: dict[str, ParagraphStyle], available_width: float) -> None:
    rows: list[list[Node]] = []
    for tr in [n for n in iter_nodes(node) if n.tag == "tr"]:
        cells = [c for c in direct_children(tr) if c.tag in {"th", "td"}]
        if cells:
            rows.append(cells)
    if not rows:
        return
    max_cols = max(len(row) for row in rows)
    data = []
    for row_idx, row in enumerate(rows):
        style = styles["table_header"] if row_idx == 0 else styles["small"]
        values = [Paragraph(inline_markup(cell) or "&nbsp;", style) for cell in row]
        while len(values) < max_cols:
            values.append(Paragraph("", style))
        data.append(values)
    table = Table(data, colWidths=table_col_widths(max_cols, available_width), repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 8))


def iter_nodes(node: Node) -> Iterable[Node]:
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from iter_nodes(child)


def render_list(story: list, node: Node, styles: dict[str, ParagraphStyle], ordered: bool) -> None:
    index = 1
    for li in direct_children(node, "li"):
        marker = f"{index}." if ordered else "*"
        story.append(Paragraph(inline_markup(li), styles["bullet"], bulletText=marker))
        index += 1


def render_figure(story: list, node: Node, styles: dict[str, ParagraphStyle], available_width: float) -> None:
    img_nodes = [child for child in direct_children(node, "img")]
    if not img_nodes:
        return
    img = img_nodes[0]
    caption_node = next((child for child in direct_children(node, "figcaption")), None)
    caption = compact(plain_text(caption_node)) if caption_node else compact(img.attrs.get("alt", ""))
    image_path = resolve_image(img.attrs.get("src", ""))
    if image_path:
        add_image(story, image_path, caption, available_width, styles)
    else:
        story.append(Paragraph(f"Screenshot unavailable: {escape(compact(img.attrs.get('alt', 'image')))}", styles["body"]))


def render_node(story: list, node: Node, styles: dict[str, ParagraphStyle], available_width: float, first_lab_seen: list[bool]) -> None:
    if node.tag in SKIP_TAGS or "anchor-alias" in node.attrs.get("class", ""):
        return

    if node.tag == "section":
        node_id = node.attrs.get("id", "")
        if node_id.startswith("lab") or node_id in {"challenge", "assets", "closeout"}:
            if first_lab_seen[0]:
                story.append(PageBreak())
            first_lab_seen[0] = True
        for child in node.children:
            if isinstance(child, Node):
                render_node(story, child, styles, available_width, first_lab_seen)
        return

    if node.tag in {"h1", "h2", "h3"}:
        text = inline_markup(node)
        if text:
            story.append(Paragraph(text, styles[node.tag]))
        return

    if node.tag == "p":
        text = inline_markup(node)
        if text:
            story.append(Paragraph(text, styles["body"]))
        return

    if node.tag in {"ul", "ol"}:
        render_list(story, node, styles, ordered=node.tag == "ol")
        return

    if node.tag == "table":
        add_html_table(story, node, styles, available_width)
        return

    if node.tag == "figure":
        render_figure(story, node, styles, available_width)
        return

    if node.tag == "pre":
        code = compact("") if False else sanitize(plain_text(node)).strip()
        if code:
            story.append(Preformatted(wrap_code(code), styles["code"], maxLineLength=100))
            story.append(Spacer(1, 8))
        return

    # Divs, spans, articles, and other layout nodes are structural in the HTML.
    for child in node.children:
        if isinstance(child, Node):
            render_node(story, child, styles, available_width, first_lab_seen)


def build_pdf() -> None:
    styles = make_styles()
    parser = TreeBuilder()
    parser.feed(SOURCE.read_text(encoding="utf-8"))
    main = find_first(parser.root, "main")
    if main is None:
        raise RuntimeError("Could not find <main> in index.html")

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.58 * inch,
        rightMargin=0.58 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.66 * inch,
        title="Public Healthcare AIDP Workshop Guide",
        author="Metro Public Health Authority Workshop Kit",
        subject="Oracle AI Data Platform and AI Lakehouse public healthcare workshop",
    )
    story: list = []
    add_cover(story, styles)
    add_toc(story, styles, collect_headings(main))
    render_node(story, main, styles, doc.width, [False])
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)


if __name__ == "__main__":
    build_pdf()
