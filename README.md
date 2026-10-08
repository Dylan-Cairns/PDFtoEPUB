# PDF-to-EPUB workshop

Reusable tools and accumulated guidance for making readable, reflowable EPUBs
from PDFs. The aim is to make the mechanical stages deterministic while keeping
each publication's interpretation explicit and reviewable.

The converters developed so far are calibrated for particular publications.
This repository contains shared QA tools and guidance; it does not yet provide
a universal PDF-to-EPUB conversion command.

## Layout

| Path | Purpose |
| --- | --- |
| `CONVERSION_PLAYBOOK.md` | Extraction, reconstruction, navigation and packaging workflow |
| `docs/QUALITY_CHECKS.md` | Automated checks, visual review and known limits |
| `tools/` | Book-independent command-line QA tools |
| `templates/styles.css` | Starting typography for authored EPUB XHTML |
| `local/` | Ignored source PDFs, individual converters, repairs and generated files |

Keep all work for a particular publication under `local/books/<job>/`, including
its source, metadata, coordinates, page ranges, override dictionaries, excerpts,
covers, outputs and review notes. Generic lessons and reusable code belong in
the tracked directories above. Existing local conversions have been preserved
with their original extraction caches and outputs.

## Requirements

- Python 3.10 or newer for the audit scripts; they use the standard library.
- Calibre for independent EPUB checking and its bundled Hunspell dictionaries.
- Poppler for PDF inspection, coordinate extraction and page rendering.
  Calibre's Windows installation also includes these programs.

There is no Python package installation step. The two `calibre_*` scripts must
run through `calibre-debug`, which supplies Calibre's Python modules.

## Run shared checks

Examples use a private job directory. Replace it with your own paths.

```powershell
python tools/audit_structure.py local/books/example/output/xhtml

python tools/audit_spelling.py local/books/example/output/xhtml `
  --work-dir local/books/example/build/spelling-audit

& 'C:\Program Files\Calibre2\calibre-debug.exe' -e tools/calibre_check.py -- `
  local/books/example/output/publication.epub

& 'C:\Program Files\Calibre2\calibre-debug.exe' -e tools/calibre_hunspell.py -- `
  local/books/example/build/words.json local/books/example/build/recognized.json
```

`calibre-debug` can also be invoked by name when it is on `PATH`.
`audit_spelling.py` accepts `--calibre-debug` to select another installation.
Hunspell input is a JSON list of words; output maps each word to a recognition
boolean. Audit output can contain publication text and therefore belongs in
the ignored job directory.

Structure and spelling audits produce candidates for human review. They do
not automatically repair text. Calibre checking exits unsuccessfully when it
finds an error; warnings are printed for review.

## Source control

`.gitignore` excludes the entire local workspace, generated directories,
publication files, extracted images and fonts, Python caches and local settings.
`.gitattributes` gives shared source and documentation consistent line endings.

Before committing, review `git diff --cached --stat` and `git diff --cached`.
Book titles, hashes, bibliographic metadata, quotations and book-specific
configuration should stay in the private workspace, even when stored in a
normally trackable format such as Markdown, JSON or Python.
