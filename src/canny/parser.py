#!/usr/env python3

"""
This module contains the parser for canny.
"""

import re
import bs4
from bs4 import BeautifulSoup

MAPPING = {}


class Position:
    """
    Position object for storing the position of a token in the text
    """

    def __init__(self, line, column, length):
        self.line = line
        self.column = column
        self.length = length
        self.raw_position = None
        self.tag = None

    def __repr__(self):
        return f"Position({self.line}, {self.column}, {self.length})"

    def __eq__(self, other):
        return (
            self.line == other.line
            and self.column == other.column
            and self.length == other.length
        )


def get_postions_for_tag(tags: iter) -> Position:
    """
    Generator for Position objects for from the tags contained in the text.
    """
    carry, last_line = 0, 0

    for tag in tags:
        if not isinstance(tag, bs4.element.Tag):
            continue

        line_nr = tag.sourceline - 1

        # reset carry if we are on a new line
        if line_nr != last_line:
            last_line = line_nr
            carry = 0

        # calculate prefix and carry
        tag_prefix = tag.string.index(tag.string)
        carry_new = len(str(tag)) - len(tag.string)

        # create position object
        result = Position(line_nr, tag.sourcepos - tag_prefix - carry, len(tag.string))
        result.tag = tag
        result.raw_position = Position(line_nr, tag.sourcepos - 1, len(str(tag)))

        carry += carry_new

        yield result


def lexer(text):
    """
    Tokenizer - Tokens for newlines and non-whitespace elements
    """
    # regex for tokenizing
    token_specification = [
        ("ELEMENT", r"\S+"),
        ("NEWLINE", r"\n"),
    ]

    # join regexes with OR-operator
    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
    line_num = 0
    line_start = 0

    # iterate over all matches
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start

        # newline handling
        if kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1
            continue
        yield Position(line_num, column, len(value))


def get_all_tags(soup: iter) -> list:
    """
    Get all tags from a beautifulsoup object
    """
    return [tag.name for tag in soup.find_all() if tag.name not in ("html", "body")]


def modify_tree(text: str, tags: iter) -> str:
    """
    Replace tags in text only with their body
    """
    global MAPPING
    assert tags and hasattr(tags, "__iter__")

    lines = text.splitlines(keepends=True)

    for tag in get_postions_for_tag(tags):
        line_nr = tag.raw_position.line
        o_tag = tag.tag

        assert o_tag is not None
        assert str(o_tag) in lines[line_nr]

        # replace tag with its body
        lines[line_nr] = lines[line_nr].replace(str(o_tag), o_tag.string, 1)

        del tag.raw_position, tag.tag

        # create a mapping of line_numbers to tags
        MAPPING.setdefault(line_nr, []).append(tag)

    return "".join(lines)


def tree_transform(text: str, html=False) -> str:
    """
    Transform the text by replacing tags with their body and generate a mapping
    """
    global MAPPING
    assert text and isinstance(text, str)

    # replace tabs with spaces
    text = text.replace("\t", "     ")

    MAPPING = {}

    tags = []
    if html:
        soup = BeautifulSoup(text, "html.parser")
        # try html parsing, on failure tokenize
        tags = soup.contents

    if not tags or all(isinstance(tag, str) for tag in tags):
        for token in lexer(text):
            MAPPING.setdefault(token.line, []).append(token)
        return text

    # modify the text
    return modify_tree(text, tags)


if __name__ == "__main__":
    try:
        import sys

        text = sys.stdin.read()
    except KeyboardInterrupt:
        sys.exit(1)

    if not text:
        print("No input")
        sys.exit(1)

    print("Input text: ")
    print(text)

    print("Raw text: ")
    print(repr(text), end="\n\n")

    new_text = tree_transform(text, html=True)

    print("new text: ")
    print(repr(new_text), end="\n\n")

    from pprint import pprint

    pprint(MAPPING)
    print()
