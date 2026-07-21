# pdftotranslate

`pdftotranslate` is an early-stage tool for translating selected PDF text while keeping each page's original visual layout.

## Workflow

1. Extract the PDF into a small HTML project:

   ```bash
   pdftotranslate extract input.pdf build/input
   ```

   The command renders every full PDF page as a PNG background and extracts each text run with its bounding box, font, size, and color into `project.json`.

2. Open `build/input/index.html` in a browser. Click consecutive text runs that should be translated together, then copy the generated selection JSON.

3. Save the selection, set a Gemini key, and translate it:

   ```bash
   export GEMINI_API_KEY=...
   pdftotranslate translate build/input/project.json selection.json translated.json
   ```

4. Insert the translated text into a styled HTML copy:

   ```bash
   pdftotranslate apply build/input translated.json
   ```

   Each translated item keeps the original span id, so the tool inserts the translation back into the same region with the same style. Separately styled runs, such as a blue word inside a black paragraph, remain separate spans.

## English-to-Persian sample

A small English PDF fixture is available at `examples/english_sample/english-sample.pdf` for checking the workflow without using a private document. It includes a separately styled blue word so you can verify that inline styling survives translation.

```bash
# Apply the included Persian translation preview to the sample HTML.
pdftotranslate apply examples/english_sample examples/english_sample/translated.fa.json
```

Open `examples/english_sample/translated.html` and confirm that the Persian word `آبی` is still in the blue span.

## Current scope

- Page backgrounds are rasterized from the original PDF.
- Text runs are extracted from PyMuPDF with position and basic style metadata.
- The browser helper lets a human choose contiguous text runs before sending them to Gemini.
- Gemini is instructed to preserve span boundaries so inline colors and fonts can be reapplied.
- `pdftotranslate apply` creates `translated.html` with translations inserted into the original styled text spans.

Future work should add automatic PDF re-export after translated spans are reviewed.
