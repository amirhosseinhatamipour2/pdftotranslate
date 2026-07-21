"""PDF extraction and HTML project generation."""

from __future__ import annotations

import html
import json
from pathlib import Path

import fitz

from .models import PageData, TextSpan


def _color_to_hex(color: int) -> str:
    return f"#{(color >> 16) & 255:02x}{(color >> 8) & 255:02x}{color & 255:02x}"


def _span_id(page_index: int, block_index: int, line_index: int, span_index: int) -> str:
    return f"p{page_index + 1}-b{block_index}-l{line_index}-s{span_index}"


def _extract_page(page: fitz.Page, page_index: int, output_dir: Path, zoom: float) -> PageData:
    rect = page.rect
    background_name = f"page-{page_index + 1}.png"
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False, annots=True)
    pixmap.save(output_dir / background_name)

    page_data = PageData(
        number=page_index + 1,
        width=rect.width,
        height=rect.height,
        background=background_name,
    )
    text_dict = page.get_text("dict")
    for block_index, block in enumerate(text_dict.get("blocks", [])):
        if block.get("type") != 0:
            continue
        for line_index, line in enumerate(block.get("lines", [])):
            for span_index, span in enumerate(line.get("spans", [])):
                text = span.get("text", "")
                if not text.strip():
                    continue
                page_data.spans.append(
                    TextSpan(
                        id=_span_id(page_index, block_index, line_index, span_index),
                        text=text,
                        bbox=[round(float(value), 3) for value in span.get("bbox", [])],
                        font=span.get("font", "sans-serif"),
                        size=round(float(span.get("size", 12)), 3),
                        color=_color_to_hex(int(span.get("color", 0))),
                        flags=int(span.get("flags", 0)),
                    )
                )
    return page_data


def extract_pdf_project(pdf_path: str | Path, output_dir: str | Path, zoom: float = 2.0) -> list[PageData]:
    """Extract each page background and absolutely positioned styled text spans."""

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with fitz.open(pdf_path) as document:
        pages = [_extract_page(page, index, output_dir, zoom) for index, page in enumerate(document)]

    (output_dir / "project.json").write_text(
        json.dumps({"source_pdf": str(pdf_path), "pages": [page.to_dict() for page in pages]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output_dir / "index.html").write_text(_render_html(pages, zoom), encoding="utf-8")
    return pages


def _render_html(pages: list[PageData], zoom: float) -> str:
    page_markup = []
    for page in pages:
        spans = []
        for span in page.spans:
            x0, y0, x1, y1 = span.bbox
            spans.append(
                f'<span class="pdf-span" data-span-id="{span.id}" '
                f'style="left:{x0}px; top:{y0}px; width:{max(x1 - x0, 1):.3f}px; '
                f'font-family:{html.escape(span.font)}; font-size:{span.size}px; color:{span.color};">'
                f'{html.escape(span.text)}</span>'
            )
        page_markup.append(
            f'<section class="page" data-page="{page.number}" style="width:{page.width}px;height:{page.height}px;">'
            f'<img class="background" src="{page.background}" width="{page.width}" height="{page.height}" />'
            f'{"".join(spans)}</section>'
        )
    return HTML_TEMPLATE.replace("__PAGES__", "\n".join(page_markup)).replace("__ZOOM__", str(zoom))


HTML_TEMPLATE = """<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8" />
<title>PDF to Translate</title>
<style>
body { margin: 0; background: #1f2937; font-family: system-ui, sans-serif; }
.toolbar { position: sticky; top: 0; z-index: 3; background: #111827; color: white; padding: 0.75rem; direction: ltr; }
.page { position: relative; margin: 1rem auto; background: white; overflow: hidden; box-shadow: 0 10px 30px #0008; direction: ltr; }
.background { position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0.35; user-select: none; pointer-events: none; }
.pdf-span { position: absolute; white-space: pre; cursor: pointer; line-height: 1; direction: ltr; }
.pdf-span.selected { outline: 2px solid #f59e0b; background: #fef3c755; }
textarea { width: min(900px, 90vw); height: 7rem; display: block; margin-top: 0.5rem; }
</style>
</head>
<body>
<div class="toolbar">
  <strong>PDF to Translate</strong>
  <button id="clear">Clear selection</button>
  <button id="copy">Copy selection JSON</button>
  <small>Click consecutive text runs, copy JSON, translate it with the CLI, then reload this page.</small>
  <textarea id="selection" placeholder="Selected span ids appear here"></textarea>
</div>
__PAGES__
<script>
const selected = [];
const box = document.getElementById('selection');
document.querySelectorAll('.pdf-span').forEach(span => {
  span.addEventListener('click', () => {
    span.classList.toggle('selected');
    const id = span.dataset.spanId;
    const index = selected.indexOf(id);
    if (index >= 0) selected.splice(index, 1); else selected.push(id);
    box.value = JSON.stringify({ span_ids: selected }, null, 2);
  });
});
document.getElementById('clear').onclick = () => {
  selected.splice(0);
  document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
  box.value = '';
};
document.getElementById('copy').onclick = async () => navigator.clipboard.writeText(box.value);
</script>
</body>
</html>
"""
