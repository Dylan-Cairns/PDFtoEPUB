#!/usr/bin/env python3
"""Flag likely residual word splits by comparing adjacent tokens with Hunspell."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


HUNSPELL = Path(__file__).resolve().with_name("calibre_hunspell.py")
NS = "{http://www.w3.org/1999/xhtml}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xhtml", type=Path, help="directory containing authored XHTML")
    parser.add_argument("--work-dir", type=Path, help="dictionary queries and report directory")
    parser.add_argument("--calibre-debug", help="path to Calibre's Python launcher")
    args = parser.parse_args()
    if not args.xhtml.is_dir():
        parser.error(f"XHTML directory does not exist: {args.xhtml}")
    calibre = args.calibre_debug or shutil.which("calibre-debug")
    if not calibre:
        windows_default = Path(r"C:\Program Files\Calibre2\calibre-debug.exe")
        if windows_default.is_file():
            calibre = str(windows_default)
    if not calibre:
        parser.error("Calibre launcher not found; provide --calibre-debug")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    build = args.work_dir or args.xhtml.parent / "spelling-audit"
    build.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, str, tuple[str, ...], str]] = []
    words: set[str] = set()
    element_names = {f"{NS}p", f"{NS}li", f"{NS}dd", f"{NS}dt", f"{NS}figcaption"}
    for path in sorted(args.xhtml.glob("*.xhtml")):
        root = ET.parse(path).getroot()
        for node in root.iter():
            if node.tag not in element_names:
                continue
            text = " ".join("".join(node.itertext()).split())
            tokens = re.findall(r"[^\W\d_]+", text, re.UNICODE)
            words.update(tokens)
            for size in (2, 3, 4):
                for index in range(len(tokens) - size + 1):
                    parts = tuple(tokens[index:index + size])
                    if any(len(part) < 2 for part in parts):
                        continue
                    joined = "".join(parts)
                    if len(joined) > 35:
                        continue
                    words.add(joined)
                    rows.append((path.name, joined, parts, text))
    source = build / "input.json"
    result_path = build / "results.json"
    source.write_text(json.dumps(sorted(words), ensure_ascii=False), encoding="utf-8")
    subprocess.run([str(calibre), "-e", str(HUNSPELL), "--", str(source), str(result_path)], check=True)
    known = json.loads(result_path.read_text(encoding="utf-8"))
    findings: dict[tuple[str, str, tuple[str, ...]], str] = {}
    for filename, joined, parts, context in rows:
        if known.get(joined, False) and any(not known.get(part, False) for part in parts):
            key = (filename, joined, parts)
            if key not in findings:
                phrase = " ".join(parts)
                location = context.find(phrase)
                findings[key] = context[max(0, location - 45):location + len(phrase) + 45]
    output = build / "candidates.tsv"
    lines = ["file\tparts\tjoined\tcontext"]
    for (filename, joined, parts), context in sorted(findings.items()):
        lines.append(f"{filename}\t{' '.join(parts)}\t{joined}\t{context}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Candidates: {len(findings)}; {output}")


if __name__ == "__main__":
    main()
