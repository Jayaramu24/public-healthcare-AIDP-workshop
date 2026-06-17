from __future__ import annotations

import re
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "workshop_guide.md"
OUTPUT = ROOT / "workshop_guide.pdf"

INK = colors.HexColor("#182321")
MUTED = colors.HexColor("#566460")
DEEP = colors.HexColor("#143735")
ORACLE = colors.HexColor("#C83232")
CORAL = colors.HexColor("#E15F3F")
SOFT = colors.HexColor("#F4F8F6")
LINE = colors.HexColor("#D9E4DF")
GOLD = colors.HexColor("#B45309")


def inline_markdown(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" color="#143735">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def collect_headings(lines: list[str]) -> list[tuple[int, str]]:
    headings = []
    for line in lines:
        match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if match:
            headings.append((len(match.group(1)), match.group(2).strip()))
    return headings


def col_widths(column_count: int, available_width: float) -> list[float]:
    if column_count == 2:
        return [available_width * 0.34, available_width * 0.66]
    if column_count == 3:
        return [available_width * 0.30, available_width * 0.22, available_width * 0.48]
    if column_count == 4:
        return [available_width * 0.23, available_width * 0.22, available_width * 0.18, available_width * 0.37]
    return [available_width / column_count] * column_count


def make_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=29,
            leading=34,
            textColor=colors.white,
            alignment=TA_LEFT,
            spaceAfter=18,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#DCEAE5"),
            alignment=TA_LEFT,
            spaceAfter=28,
        ),
        "cover_meta": ParagraphStyle(
            "CoverMeta",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=DEEP,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=27,
            textColor=DEEP,
            spaceBefore=10,
            spaceAfter=14,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=DEEP,
            spaceBefore=16,
            spaceAfter=8,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=GOLD,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.6,
            leading=14,
            textColor=INK,
            spaceAfter=7,
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.1,
            leading=10.5,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8.1,
            leading=10.5,
            textColor=colors.white,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13,
            leftIndent=17,
            firstLineIndent=-9,
            bulletIndent=4,
            textColor=INK,
            spaceAfter=4,
        ),
        "toc": ParagraphStyle(
            "TOC",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=INK,
            leftIndent=12,
            spaceAfter=4,
        ),
        "callout": ParagraphStyle(
            "Callout",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=13,
            textColor=INK,
        ),
    }


def draw_page(canvas, doc) -> None:
    width, height = letter
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(DEEP)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setFillColor(ORACLE)
        canvas.rect(0.62 * inch, height - 1.02 * inch, 1.1 * inch, 0.12 * inch, fill=1, stroke=0)
        canvas.setFillColor(CORAL)
        canvas.rect(width - 2.25 * inch, 0, 2.25 * inch, height, fill=1, stroke=0)
        canvas.setFillColor(colors.Color(1, 1, 1, alpha=0.13))
        for idx in range(7):
            canvas.circle(width - 1.2 * inch, 1.2 * inch + idx * 0.95 * inch, 0.36 * inch, fill=1, stroke=0)
    else:
        canvas.setStrokeColor(ORACLE)
        canvas.setLineWidth(2)
        canvas.line(doc.leftMargin, height - 0.48 * inch, width - doc.rightMargin, height - 0.48 * inch)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(doc.leftMargin, height - 0.36 * inch, "Public Healthcare AIDP Workshop Guide")
        canvas.drawRightString(width - doc.rightMargin, height - 0.36 * inch, "Synthetic data only")
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 0.48 * inch, width - doc.rightMargin, 0.48 * inch)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 0.31 * inch, "Oracle AI Data Platform | Autonomous AI Lakehouse | Oracle Analytics Cloud")
        canvas.drawRightString(width - doc.rightMargin, 0.31 * inch, f"Page {doc.page}")
    canvas.restoreState()


def add_cover(story: list, styles: dict[str, ParagraphStyle]) -> None:
    story.append(Spacer(1, 1.55 * inch))
    story.append(Paragraph("Public Healthcare AIDP Workshop", styles["cover_title"]))
    story.append(
        Paragraph(
            "Execution team guide for a public healthcare lakehouse workshop using Oracle AI Data Platform, Autonomous AI Lakehouse, Oracle Analytics Cloud, spatial analytics, document chat, and optional real-time labs.",
            styles["cover_subtitle"],
        )
    )
    meta = [
        [Paragraph("Core labs<br/>3 hours", styles["cover_meta"]), Paragraph("Gold model<br/>Snowflake schema", styles["cover_meta"])],
        [Paragraph("Raw formats<br/>CSV, JSON, GeoJSON, DOCX", styles["cover_meta"]), Paragraph("Privacy<br/>Synthetic data only", styles["cover_meta"])],
    ]
    table = Table(meta, colWidths=[2.15 * inch, 2.15 * inch], rowHeights=[0.76 * inch, 0.76 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#DCEAE5")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(table)
    story.append(PageBreak())


def add_toc(story: list, styles: dict[str, ParagraphStyle], headings: list[tuple[int, str]]) -> None:
    story.append(Paragraph("Contents", styles["h1"]))
    for level, title in headings:
        if level == 2:
            story.append(Paragraph(inline_markdown(title), styles["toc"]))
        elif title.startswith("Objectives") or title.startswith("Expected Outcome"):
            continue
        else:
            story.append(Paragraph(f"&nbsp;&nbsp;{inline_markdown(title)}", styles["toc"]))
    story.append(PageBreak())


def add_table(story: list, rows: list[list[str]], styles: dict[str, ParagraphStyle], available_width: float) -> None:
    cleaned = []
    for ridx, row in enumerate(rows):
        style = styles["table_header"] if ridx == 0 else styles["small"]
        cleaned.append([Paragraph(inline_markdown(cell), style) for cell in row])
    table = Table(cleaned, colWidths=col_widths(len(rows[0]), available_width), repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DEEP),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
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
    story.append(Spacer(1, 9))


def parse_markdown_to_story(text: str, story: list, styles: dict[str, ParagraphStyle], available_width: float) -> None:
    lines = text.splitlines()
    idx = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline_markdown(" ".join(paragraph)), styles["body"]))
            paragraph = []

    while idx < len(lines):
        line = lines[idx].rstrip()
        if not line:
            flush_paragraph()
            idx += 1
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if level == 1:
                story.append(Paragraph(inline_markdown(title), styles["h1"]))
            elif level == 2:
                story.append(Paragraph(inline_markdown(title), styles["h2"]))
            else:
                story.append(Paragraph(inline_markdown(title), styles["h3"]))
            idx += 1
            continue

        if line.startswith("|"):
            flush_paragraph()
            table_lines = []
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                if not is_table_separator(lines[idx]):
                    table_lines.append(split_table_row(lines[idx]))
                idx += 1
            if table_lines:
                add_table(story, table_lines, styles, available_width)
            continue

        bullet = re.match(r"^-\s+(.+)$", line)
        numbered = re.match(r"^(\d+)\.\s+(.+)$", line)
        if bullet:
            flush_paragraph()
            story.append(Paragraph(inline_markdown(bullet.group(1)), styles["bullet"], bulletText="•"))
            idx += 1
            continue
        if numbered:
            flush_paragraph()
            story.append(Paragraph(inline_markdown(numbered.group(2)), styles["bullet"], bulletText=f"{numbered.group(1)}."))
            idx += 1
            continue

        paragraph.append(line)
        idx += 1

    flush_paragraph()


def build_pdf() -> None:
    styles = make_styles()
    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = collect_headings(lines)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.68 * inch,
        rightMargin=0.68 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.66 * inch,
        title="Public Healthcare AIDP Workshop Guide",
        author="Metro Public Health Authority Workshop Kit",
        subject="Oracle AI Data Platform and AI Lakehouse public healthcare workshop",
    )
    story = []
    add_cover(story, styles)
    add_toc(story, styles, headings)
    parse_markdown_to_story(text, story, styles, doc.width)
    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)


if __name__ == "__main__":
    build_pdf()
