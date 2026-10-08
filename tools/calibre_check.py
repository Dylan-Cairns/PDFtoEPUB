#!/usr/bin/env python
"""Run Calibre's Edit Book validation engine from the command line."""

from __future__ import annotations

import sys
from calibre.ebooks.oeb.polish.check.base import WARN
from calibre.ebooks.oeb.polish.check.main import run_checks
from calibre.ebooks.oeb.polish.container import get_container


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: calibre-debug -e calibre_check.py -- PUBLICATION.epub")
    container = get_container(sys.argv[-1])
    findings = run_checks(container)
    errors = [finding for finding in findings if finding.level < WARN]
    for finding in findings:
        print(f"{finding.level}: {finding.msg} ({finding.name}:{finding.line})")
    print(f"Findings: {len(findings)}; errors: {len(errors)}")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
