# Quality checks

Review the packaged EPUB and compare difficult passages with rendered source
pages. Structural validation, dictionary recognition and visual review answer
different questions; none alone establishes faithful conversion.

## Automated checks

Track XHTML parse errors, duplicate IDs, missing resources and broken internal
links. Reconcile notes and references, including backlinks and references that
repeat. Count sections, headings, figures, glossary terms, index entries,
page destinations and linked locators. Counts are per-job regression signals,
not universal targets.

Search for replacement characters, unrepaired glyph placeholders, Unicode
normalization defects, unresolved soft hyphens, running headers, repeated
footers, letterspaced artifacts, whitespace in URLs and missing spaces beside
note references. Record all unresolved hyphen choices.

Reference coverage is separate from link validity. An index containing no
hyperlinks can pass a broken-link check. Check that expected locators actually
became links, and compare text and styling after inserting them.

Run Calibre's independent checker against the EPUB archive. EPUBCheck is also
recommended when available. Oversized XHTML can cause reading-system problems;
splitting content requires updating the manifest, spine and all moved targets.

## Shared tools and their limits

`tools/calibre_check.py` prints Calibre findings and returns a failing exit code
for errors. It runs inside Calibre's Python runtime and relies on its internal
checking APIs. Warnings are printed even when the exit status is successful.

`tools/calibre_hunspell.py` answers batch dictionary-recognition queries using
Calibre's bundled English dictionary. Recognition is evidence, not a guarantee
that a word is correct in its sentence.

`tools/audit_structure.py` reports suspicious paragraph boundaries and selected
empty list items in the existing authored XHTML layout. It skips named back
matter documents. It is a heuristic, not a general XHTML validator, and does
not automatically change content.

`tools/audit_spelling.py` flags adjacent token combinations that form dictionary
words while at least one component is unrecognized. It checks selected prose,
list, definition and caption elements. Tokenization can cross punctuation and
inline markup; scholarly terms and hyphenation can produce false positives.
Review every candidate. The query cache and report contain publication text and
should be written inside the local job directory.

## Visual review

Check cover scaling, title and copyright pages, contents navigation, short and
long chapter titles, paragraphs following headings, quotations and lists.
Inspect prose across source-page boundaries and quotations across rendered
pages. Test narrow and wide views and several font sizes.

Review mixed italics, accented text, non-note superscripts, note-marker spacing,
figures, captions and alternative text. Test forward note links and backlinks.
Check early, middle and late notes, long entries and split note groups.

Test representative index numbers, Roman labels, ranges, figure locators and
note locators. Test glossary chapter links and cross-references when provided.
Inspect reading continuity after a large section is split into multiple files.

A temporary PDF produced from the EPUB is useful for layout sampling, but an
EPUB reader is needed to assess actual reflow and navigation. Automated passes
do not replace these checks.

## Recalibrate when evidence is insufficient

Pause broad automatic rules when layouts conflict, the text layer omits or
duplicates content, reading order is uncertain, footnotes overlap body text,
illustrations contain essential text, tables or equations lose semantics,
hyphen repair remains ambiguous, or note numbering cannot be reconciled.

Use narrower profiles, selected-page OCR, custom parsing or reviewed manual
reconstruction. Record unresolved compromises in the private job record rather
than treating a successful build as proof of accuracy.
