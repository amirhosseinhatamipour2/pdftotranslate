"""Translate selected PDF text spans and preserve inline styling."""

from __future__ import annotations

import json
import os
from pathlib import Path


SYSTEM_PROMPT = """Translate the provided ordered PDF text runs into Persian.
Return JSON only with a `translations` array. The array length and order must exactly match the input spans.
Preserve markup boundaries: if a word is blue, bold, or otherwise separately styled, translate that span separately so the caller can place it back with the same style.
Do not merge, split, remove, or reorder spans."""


def _load_selected_spans(project: dict, selection: dict) -> list[dict]:
    wanted = set(selection["span_ids"])
    spans = []
    for page in project["pages"]:
        for span in page["spans"]:
            if span["id"] in wanted:
                spans.append(span)
    return spans


def translate_selection_file(
    project_json: str | Path,
    selection_json: str | Path,
    output_json: str | Path,
    model: str = "gemini-2.5-flash",
) -> dict:
    """Send selected spans to Gemini and write translated span replacements."""

    project = json.loads(Path(project_json).read_text(encoding="utf-8"))
    selection = json.loads(Path(selection_json).read_text(encoding="utf-8"))
    spans = _load_selected_spans(project, selection)
    if not spans:
        raise ValueError("Selection did not match any extracted spans.")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY before translating.")

    from google import genai

    client = genai.Client(api_key=api_key)
    payload = {"spans": [{"id": span["id"], "text": span["text"], "style": {"color": span["color"], "font": span["font"]}} for span in spans]}
    response = client.models.generate_content(model=model, contents=f"{SYSTEM_PROMPT}\n\n{json.dumps(payload, ensure_ascii=False)}")
    data = json.loads(response.text.strip().removeprefix("```json").removesuffix("```").strip())
    translations = data.get("translations", [])
    if len(translations) != len(spans):
        raise ValueError("Gemini response length did not match selected spans.")

    result = {"translations": [{"id": span["id"], "source": span["text"], "text": translated} for span, translated in zip(spans, translations)]}
    Path(output_json).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def apply_translations_to_html(project_dir: str | Path, translations_json: str | Path, output_html: str | Path | None = None) -> Path:
    """Create an HTML copy with translated text inserted into the original styled spans."""

    project_dir = Path(project_dir)
    output_path = Path(output_html) if output_html else project_dir / "translated.html"
    translations = json.loads(Path(translations_json).read_text(encoding="utf-8"))["translations"]
    replacement_script = "<script id=\"translated-spans\" type=\"application/json\">"
    replacement_script += json.dumps({item["id"]: item["text"] for item in translations}, ensure_ascii=False)
    replacement_script += "</script><script>const translatedSpans = JSON.parse(document.getElementById('translated-spans').textContent); for (const [id, text] of Object.entries(translatedSpans)) { const el = document.querySelector(`[data-span-id=\"${CSS.escape(id)}\"]`); if (el) el.textContent = text; }</script>"
    html_text = (project_dir / "index.html").read_text(encoding="utf-8")
    output_path.write_text(html_text.replace("</body>", f"{replacement_script}</body>"), encoding="utf-8")
    return output_path
