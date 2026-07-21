import json
from pathlib import Path

from pdftotranslate.translator import apply_translations_to_html


def test_apply_translations_to_html_preserves_span_style(tmp_path: Path):
    (tmp_path / "index.html").write_text(
        '<html><body><span data-span-id="s1" style="color:#0066cc">blue</span></body></html>',
        encoding="utf-8",
    )
    translations = tmp_path / "translated.json"
    translations.write_text(json.dumps({"translations": [{"id": "s1", "text": "آبی"}]}), encoding="utf-8")

    output = apply_translations_to_html(tmp_path, translations)

    rendered = output.read_text(encoding="utf-8")
    assert 'style="color:#0066cc"' in rendered
    assert '"s1": "آبی"' in rendered
