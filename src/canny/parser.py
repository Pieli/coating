#!/usr/env python3

"""
This module contains the parser for canny.
"""

import re
import bs4
from bs4 import BeautifulSoup


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


class Parser:
    """
    Generates a mapping of line numbers to Position objects for a given text.
    """

    def __init__(self, text: str, html=False):
        assert text and isinstance(text, str)
        assert isinstance(html, bool)

        # replace tabs with spaces
        self.text = text.replace("\t", "     ")

        self.html = html
        self.__mapping = {}

    def get_mapping(self):
        """Getter for the mapping"""
        return self.__mapping

    def get_postions_for_tag(self, tags: iter) -> Position:
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
            result = Position(
                line_nr, tag.sourcepos - tag_prefix - carry, len(tag.string)
            )
            result.tag = tag
            result.raw_position = Position(line_nr, tag.sourcepos - 1, len(str(tag)))

            carry += carry_new

            yield result

    def lexer(self):
        """
        Tokenizer - Tokens for newlines and non-whitespace elements
        """
        # regex for tokenizing
        token_specification = [
            ("ELEMENT", r"\S+"),
            ("NEWLINE", r"\n"),
        ]

        # join regexes with OR-operator
        tok_regex = "|".join(
            f"(?P<{tok_name}>{tok_str})" for tok_name, tok_str in token_specification
        )
        line_num = 0
        line_start = 0

        # iterate over all matches
        for mo in re.finditer(tok_regex, self.text):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            # newline handling
            if kind == "NEWLINE":
                line_start = mo.end()
                line_num += 1
                continue
            yield Position(line_num, column, len(value))

    def modify_tree(self, tags: iter) -> str:
        """
        Replace tags in text only with their body
        """
        assert tags and hasattr(tags, "__iter__")

        lines = self.text.splitlines(keepends=True)

        for tag in self.get_postions_for_tag(tags):
            line_nr = tag.raw_position.line
            o_tag = tag.tag

            assert o_tag is not None
            assert str(o_tag) in lines[line_nr]

            # replace tag with its body
            lines[line_nr] = lines[line_nr].replace(str(o_tag), o_tag.string, 1)

            del tag.raw_position, tag.tag

            # create a mapping of line_numbers to tags
            self.__mapping.setdefault(line_nr, []).append(tag)

        return "".join(lines)

    def tree_transform(self) -> str:
        """
        Transform the text by replacing tags with their body and generate a mapping
        """

        tags = []
        if self.html:
            soup = BeautifulSoup(self.text, "html.parser")
            # try html parsing, on failure tokenize
            tags = soup.contents

        if not tags or all(isinstance(tag, str) for tag in tags):
            for token in self.lexer():
                self.__mapping.setdefault(token.line, []).append(token)
            return self.text

        # modify the text
        return self.modify_tree(tags)


if __name__ == "__main__":
    try:
        import sys

        text_input = sys.stdin.read()
    except KeyboardInterrupt:
        sys.exit(1)

    if not text_input:
        print("No input")
        sys.exit(1)

    print("Input text: ")
    print(text_input)

    print("Raw text: ")
    print(repr(text_input), end="\n\n")

    parser = Parser(text_input, html=True)
    new_text = parser.tree_transform()

    print("new text: ")
    print(repr(new_text), end="\n\n")

    from pprint import pprint

    pprint(parser.get_mapping())
    print()
