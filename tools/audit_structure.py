#!/usr/bin/env python3
"""Report suspicious generated block boundaries for manual review."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


NS = "{http://www.w3.org/1999/xhtml}"


def clean(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xhtml", type=Path, help="directory containing authored XHTML")
    parser.add_argument("--output", type=Path, help="review report (default: beside the XHTML directory)")
    args = parser.parse_args()
    if not args.xhtml.is_dir():
        parser.error(f"XHTML directory does not exist: {args.xhtml}")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    findings: list[str] = []
    for path in sorted(args.xhtml.glob("*.xhtml")):
        if path.name.startswith(("notes-", "index-")) or path.name in {"notes.xhtml", "references.xhtml", "index.xhtml", "glossary.xhtml"}:
            continue
        root = ET.parse(path).getroot()
        section = root.find(f".//{NS}section")
        if section is None:
            continue
        blocks = list(section)
        for index, node in enumerate(blocks):
            text = clean(node)
            if node.tag == f"{NS}ul":
                for item in node.findall(f"{NS}li"):
                    if not clean(item):
                        findings.append(f"{path.name}: empty list item")
            if node.tag not in {f"{NS}p", f"{NS}blockquote"} or not text:
                continue
            if text.endswith("-"):
                findings.append(f"{path.name}: paragraph ends hyphen: …{text[-55:]}")
            following = None
            for candidate in blocks[index + 1:]:
                if candidate.tag == f"{NS}figure":
                    break
                if candidate.tag == f"{NS}blockquote" and clean(candidate):
                    break
                if candidate.tag == f"{NS}p" and clean(candidate):
                    following = clean(candidate)
                    break
                if candidate.tag in {f"{NS}h1", f"{NS}h2", f"{NS}h3"}:
                    break
            if following and text[-1] not in ".!?…”’)]}:;" and re.match(r"^[a-z]", following):
                findings.append(f"{path.name}: …{text[-55:]} | {following[:55]}…")
    output = args.output or args.xhtml.parent / "structure-review.txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(findings) + ("\n" if findings else ""), encoding="utf-8")
    print(f"Suspicious boundaries: {len(findings)}; {output}")
    for finding in findings[:100]:
        print(finding)


if __name__ == "__main__":
    main()
