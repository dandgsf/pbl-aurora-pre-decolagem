"""Gera um PDF do relatório em Markdown com suporte a imagens."""

from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as ReportImage,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILE = PROJECT_ROOT / "report" / "relatorio_operacional.md"
OUTPUT_FILE = PROJECT_ROOT / "report" / "relatorio_operacional.pdf"
PAGE_WIDTH, PAGE_HEIGHT = A4
IMAGE_PATTERN = re.compile(r"!\[(?P<alt>.*)\]\((?P<path>.+)\)")
URL_PATTERN = re.compile(r"^https?://\S+$")


def append_table_block(story, table_lines, table_style):
    if not table_lines:
        return
    story.append(Preformatted("\n".join(table_lines), table_style))
    story.append(Spacer(1, 8))
    table_lines.clear()


def append_code_block(story, code_lines, code_style):
    if not code_lines:
        return
    story.append(Preformatted("\n".join(code_lines), code_style))
    story.append(Spacer(1, 8))
    code_lines.clear()


def scaled_image(image_path):
    image = ReportImage(str(image_path))
    max_width = PAGE_WIDTH - 80
    max_height = PAGE_HEIGHT * 0.48
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight, 1)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


def main():
    styles = getSampleStyleSheet()
    body_style = styles["BodyText"]
    body_style.leading = 14
    body_style.spaceAfter = 6
    body_style.fontName = "Helvetica"

    code_style = ParagraphStyle(
        "CodeBlock",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=10,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=8,
    )
    table_style = ParagraphStyle(
        "TableBlock",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7,
        leading=9,
        spaceAfter=8,
    )
    caption_style = ParagraphStyle(
        "Caption",
        parent=body_style,
        alignment=1,
        fontSize=9,
        leading=11,
        spaceAfter=12,
    )

    document = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    story = []
    table_lines = []
    code_lines = []
    in_code_block = False

    for raw_line in SOURCE_FILE.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()

        if in_code_block:
            if stripped.startswith("```"):
                append_code_block(story, code_lines, code_style)
                in_code_block = False
            else:
                code_lines.append(raw_line)
            continue

        if stripped.startswith("```"):
            append_table_block(story, table_lines, table_style)
            in_code_block = True
            continue

        if stripped.startswith("|"):
            table_lines.append(raw_line)
            continue

        append_table_block(story, table_lines, table_style)

        if not stripped:
            story.append(Spacer(1, 6))
            continue

        image_match = IMAGE_PATTERN.fullmatch(stripped)
        if image_match:
            image_path = (SOURCE_FILE.parent / image_match.group("path")).resolve()
            if image_path.exists():
                story.append(scaled_image(image_path))
                story.append(Paragraph(escape(image_match.group("alt")), caption_style))
            else:
                story.append(
                    Paragraph(
                        escape(f"Imagem não encontrada: {image_match.group('path')}"),
                        body_style,
                    )
                )
            continue

        if URL_PATTERN.fullmatch(stripped):
            safe_url = escape(stripped)
            story.append(Paragraph(f'<link href="{safe_url}">{safe_url}</link>', body_style))
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(escape(stripped[2:]), styles["Title"]))
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(escape(stripped[3:]), styles["Heading1"]))
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(escape(stripped[4:]), styles["Heading2"]))
            continue
        if stripped.startswith("- "):
            story.append(Paragraph(f"&bull; {escape(stripped[2:])}", body_style))
            continue
        if re.match(r"^\d+\.\s+", stripped):
            story.append(Paragraph(escape(stripped), body_style))
            continue

        story.append(Paragraph(escape(stripped), body_style))

    append_table_block(story, table_lines, table_style)
    append_code_block(story, code_lines, code_style)

    document.build(story)
    print(f"PDF gerado em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
