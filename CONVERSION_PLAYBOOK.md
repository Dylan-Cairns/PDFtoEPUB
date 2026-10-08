# PDF-to-EPUB conversion playbook

Make the mechanical stages repeatable, and calibrate the interpretation of
each new PDF from representative pages. A successful conversion of one layout
does not establish that the same rules are safe for another.

Store publication-specific files under `local/books/<job>/`. This includes
source hashes and metadata, sample pages, geometric thresholds, note groups,
font interpretations, repairs, overrides, reports and generated artifacts.
Keep shared tools and general lessons in source control.

## 1. Inspect the source

Preserve the source unchanged. Record its filename, size, page count and hash
in the local job record. Use `pdfinfo` and `pdftotext` on a small range first.

Determine whether text is selectable and correctly ordered, whether italics
and superscripts survive extraction, whether bookmarks are useful, and whether
layouts vary across body text, notes and indexes. Test difficult material such
as accented names, foreign-language terms, mathematical notation and URLs.

Use native extraction when the text layer is reliable. OCR is appropriate for
scans, missing text, widespread character-map corruption or unrecoverable
reading order. A poor direct PDF-to-EPUB conversion is not evidence that the
source text layer requires OCR.

## 2. Build a representative prototype

Sample front matter, chapter openings, ordinary prose across a page boundary,
italics, superscripts, quotations, lists, figures, long notes and multi-column
indexes. Include pages with known encoding defects.

Review the prototype at narrow and wide widths. Copy text across print-page
boundaries, follow links, compare diacritics against rendered source pages, and
check paragraph breaks. Prototype approval establishes a promising method;
the completed publication still needs a separate QA pass.

## 3. Cache coordinate-aware extraction

Use Poppler's XML extraction to retain positions, font information and images:

```powershell
& 'C:\Program Files\Calibre2\app\bin\pdftohtml.exe' `
  -q -xml -noroundcoord -fontfullname `
  local/books/example/source.pdf local/books/example/build/raw/source.xml
```

Create the destination directory first. The executable can also be invoked
from `PATH` on installations that expose Poppler directly.

Retain the raw XML as evidence. Compare suspicious output with coordinates
and rasterized source pages. Font declarations may be inherited across pages;
do not assume every page has a complete, independent `fontspec` mapping.

## 4. Reconstruct lines and glyphs

Group runs by vertical position and sort each line horizontally. Calibrate the
vertical tolerance against actual line spacing. Separately positioned accents
can differ from their host letters by several coordinate units, while too
large a tolerance can merge unrelated lines.

For detached diacritics, choose the host character using horizontal position
and nearby bounding boxes. Attaching every mark to the preceding text run can
produce plausible-looking but incorrect Unicode. Distinguish dots above and
below by geometry, and treat spacing accents separately from combining marks.

Normalize to Unicode NFC after related runs have been joined. Normalizing each
run independently cannot compose a base letter and mark in different runs.

## 5. Remove layout noise conservatively

Calibrate body rectangles and recognize running headers, folios, repeated
download footers, letterspaced display text and blank-page notices. Record the
rules in the local profile rather than hiding them in generic extraction code.

Do not discard text merely because it is centered or letterspaced. It may be
a meaningful heading. Search the complete output for remaining print artifacts
and verify removals against the source.

## 6. Reconstruct paragraphs across pages

A physical page boundary usually does not begin a new paragraph. Join across
pages unless indentation, spacing or structure indicates a genuine break.
Preserve source-page positions as visually empty inline markers:

```html
<span id="page-237" class="pagebreak" epub:type="pagebreak"
      role="doc-pagebreak" aria-label="237" title="237"></span>
```

Declare the EPUB namespace on the XHTML root. Keep markers inline, including
when a print page divides a word. A block element or added newline can produce
an erroneous return in the reflowed text.

Flag suspicious boundaries where a paragraph lacks terminal punctuation and
the following paragraph starts lowercase. Review candidates against the source
rather than automatically merging them. `tools/audit_structure.py` implements
this heuristic for the XHTML structures used in the local conversions.

## 7. Resolve line-wrap hyphens

Construct joined and hyphenated candidates for words split at a line ending.
Use dictionary recognition, intact forms elsewhere in the same publication,
and reviewed overrides as evidence. Dictionaries omit proper names, specialist
terms, transliterations and historical spellings; both candidates may be valid.

Keep publication-specific `force_join` and `force_keep` decisions in local
configuration. Begin each new job with fresh overrides. Log the exact fragments
and decision: a complete word in an override may not match the fragments seen
when a PDF divides that word into several font runs.

Distinguish a semantic hyphen inside a compound from a discretionary line-wrap
hyphen. Some PDFs encode these using combinations of a visible and soft hyphen.
Record unresolved decisions for review rather than silently choosing a form.

## 8. Preserve styles and identify note references

Use font family, size and position to recover italics and superscripts. Merge
adjacent runs with the same style before rendering where practical.

Parse all note groups before linking superscripts. A number becomes a note
reference only when the corresponding section-and-number target exists.
Other superscripts, including mathematical exponents, remain `<sup>` content.
Check spacing when a reference is followed immediately by a word.

## 9. Build semantic structure and navigation

Use separate logical documents for chapters and major front or back matter.
Use real headings, definition lists for glossaries, lists for indexes and
blockquotes for actual quotations. Treat PDF bookmarks as evidence to verify,
not an unquestioned source of structure.

The table of contents should link to logical content. Preserve source
pagination in a separate `page-list` and inline page markers. Printed page
labels and physical PDF page indices differ, especially around front matter;
record their mapping explicitly. Identify the pagination source in metadata.

## 10. Link endnotes in both directions

Note numbering often restarts by section. Match starts using the observed
indentation, numbering punctuation, fonts and geometry. A permissive expression
can misread continuation lines beginning with dates or numbered titles.

Give each note and each reference a unique ID. Preserve multiple references
with distinct IDs and backlinks. Reconcile references and targets exactly;
explain genuinely unreferenced notes instead of suppressing the finding.

Large notes documents may exceed conservative reader file-size limits. Split
them by logical note group, retain a Notes landing page, and preserve the spine
order. Validate both existing and newly generated links.

## 11. Reconstruct and link indexes and glossaries

Read each index column from top to bottom before moving to the next column.
Use base margins and indentation to distinguish entries, subentries and
continuations. Preserve hierarchy when the evidence permits it.

Keep printed index locators as labels and link them to corresponding content
destinations. A page range is a single link to its first page. Preserve Roman
labels, range spacing and italic figure locators. Match across font runs so
formatting cannot divide a locator into incomplete pieces.

Recognize locator syntax from each publication. Exclude embedded numerals in
term names and figure labels. Note-style locators require special care because
several chapter note groups may share a printed page. Link to the notes page
when a unique note target cannot be established without guessing.

Link glossary chapter references to chapter openings and cross-references to
term definitions. Selectively linking a term's first occurrence in a section
can help readers; linking every occurrence can overwhelm navigation.

Count linked locators and report missing or ambiguous destinations. A report
of zero broken links says nothing about references that were never linked.
Compare text, entry order, page markers and inline styling before and after
link insertion. Hyperlinks can make a formerly small index exceed reader limits;
split between complete entries and update the manifest, spine and page list.

## 12. Rejoin URLs

Do not insert prose spaces at URL line breaks before `/` or `.`. Remove unwanted
whitespace from initial note lines as well as continuations. Search explicitly
for whitespace in URL-like strings; ordinary punctuation rules miss defects.
Keep URL repair narrow enough to avoid changing valid prose.

## 13. Package authored EPUB directly

Packaging finished XHTML directly avoids a conversion program reinterpreting
its navigation, splitting at page markers or dropping front and back matter.
Use Calibre for checking, viewing, metadata inspection and test rendering.

For an EPUB ZIP archive:

- The first member is `mimetype`, stored uncompressed.
- Its exact content is `application/epub+zip`, with no trailing newline.
- `META-INF/container.xml` identifies the package document.
- The EPUB 3 manifest includes all resources and identifies navigation.
- The spine preserves the intended reading order.

Content and structural determinism differ from byte-for-byte reproducibility.
For identical archive hashes, also stabilize resource ordering, ZIP timestamps,
metadata modification dates, compression settings and generated images. Record
tool versions and the inputs to each build. The local converters have not yet
established byte-for-byte reproducibility.

## 14. Validate, render and record evidence

Run internal checks, independent Calibre checking and EPUBCheck when available.
They cover different problems. Render the packaged EPUB and inspect source
comparisons and reflow; validating XHTML alone is insufficient.

See [Quality checks](docs/QUALITY_CHECKS.md) for the review checklist and tool
limitations. Store each publication's expected counts, hashes, visual samples,
known compromises and exact commands in its ignored job record.

## Working toward a deterministic process

Promote a rule into shared code only after it proves reusable across layouts.
Packaging, link validation, Unicode checks, dictionary batching and reporting
are good candidates. Geometry, font interpretation, section ranges and ambiguous
repairs should remain explicit local profiles until evidence supports a common
abstraction. Store synthetic examples in tests instead of publication excerpts.

A useful handoff records source identity, extraction method, representative
pages reviewed, assumptions, overrides, unresolved items, expected counts,
build commands and visual verification. Explain why extraction is believed to
be faithful; a build completing successfully is not enough.
