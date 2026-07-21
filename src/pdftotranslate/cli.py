"""Command line interface for pdftotranslate."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a PDF for styled, human-guided translation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract = subparsers.add_parser("extract", help="Extract page backgrounds and styled text into an HTML project.")
    extract.add_argument("pdf")
    extract.add_argument("output_dir")
    extract.add_argument("--zoom", type=float, default=2.0)

    translate = subparsers.add_parser("translate", help="Translate selected text spans with Gemini.")
    translate.add_argument("project_json")
    translate.add_argument("selection_json")
    translate.add_argument("output_json")
    translate.add_argument("--model", default="gemini-2.5-flash")

    apply_cmd = subparsers.add_parser("apply", help="Insert translated text into a translated HTML copy.")
    apply_cmd.add_argument("project_dir")
    apply_cmd.add_argument("translations_json")
    apply_cmd.add_argument("--output-html")

    args = parser.parse_args()
    if args.command == "extract":
        from .extractor import extract_pdf_project

        extract_pdf_project(args.pdf, args.output_dir, args.zoom)
    elif args.command == "translate":
        from .translator import translate_selection_file

        translate_selection_file(args.project_json, args.selection_json, args.output_json, args.model)
    elif args.command == "apply":
        from .translator import apply_translations_to_html

        apply_translations_to_html(args.project_dir, args.translations_json, args.output_html)


if __name__ == "__main__":
    main()
