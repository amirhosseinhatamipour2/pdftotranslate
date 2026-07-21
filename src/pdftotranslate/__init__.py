"""Tools for preparing styled PDF text for human-guided translation."""

__all__ = ["apply_translations_to_html", "extract_pdf_project", "translate_selection_file"]


def __getattr__(name: str):
    if name == "extract_pdf_project":
        from .extractor import extract_pdf_project

        return extract_pdf_project
    if name in {"apply_translations_to_html", "translate_selection_file"}:
        from .translator import apply_translations_to_html, translate_selection_file

        return {"apply_translations_to_html": apply_translations_to_html, "translate_selection_file": translate_selection_file}[name]
    raise AttributeError(name)
