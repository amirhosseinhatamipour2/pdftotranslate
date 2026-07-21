from pathlib import Path

from pdftotranslate.translator import apply_translations_to_html


def test_english_sample_applies_farsi_translation_and_keeps_blue_style(tmp_path: Path):
    sample_dir = Path("examples/english_sample")
    work_dir = tmp_path / "english_sample"
    work_dir.mkdir()
    (work_dir / "index.html").write_text((sample_dir / "index.html").read_text(encoding="utf-8"), encoding="utf-8")

    output = apply_translations_to_html(work_dir, sample_dir / "translated.fa.json")

    html = output.read_text(encoding="utf-8")
    assert "سلام، این یک پاراگراف انگلیسی" in html
    assert 'data-span-id="p1-b0-l0-s1" style="color:#0000ff"' in html
    assert '"p1-b0-l0-s1": "آبی"' in html
