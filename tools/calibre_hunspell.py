#!/usr/bin/env python3
"""Batch spell queries, executed inside Calibre's bundled Python runtime."""

from __future__ import annotations

import json
import sys

from calibre.spell import parse_lang_code
from calibre.spell.dictionary import get_dictionary, load_dictionary


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: calibre-debug -e calibre_hunspell.py -- WORDS.json RESULTS.json")
    source, destination = sys.argv[-2:]
    dictionary = load_dictionary(get_dictionary(parse_lang_code("en-US"))).obj
    with open(source, encoding="utf-8") as stream:
        words = json.load(stream)
    result = {word: bool(dictionary.recognized(word)) for word in words}
    with open(destination, "w", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
