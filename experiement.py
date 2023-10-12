import re


class Token:
    def __init__(self, kind, value, line, column):
        self.kind = kind
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.kind}, {repr(self.value)}, {self.line}, {self.column})"


def lexer(text):
    # Define the regular expressions for each token
    token_specification = [
        ("NUMBER", r"\d+(\.\d+)?"),  # Integer or decimal number
        ("PLUS", r"\+"),  # Plus sign
        ("MINUS", r"-"),  # Minus sign
        ("TIMES", r"\*"),  # Multiplication sign
        ("DIVIDE", r"/"),  # Division sign
        ("LPAREN", r"\("),  # Left parenthesis
        ("RPAREN", r"\)"),  # Right parenthesis
        ("NEWLINE", r"\n"),  # Line endings
    ]
    tok_regex = "|".join("(?P<%s>%s)" % pair for pair in token_specification)
    # print(tok_regex)
    line_num = 1
    line_start = 0
    for mo in re.finditer(tok_regex, text):
        # print(mo)
        kind = mo.lastgroup
        value = mo.group()
        if kind == "SPACE":
            continue
        column = mo.start() - line_start
        yield Token(kind, value, line_num, column)
        if kind == "NEWLINE":
            line_start = mo.end()
            line_num += 1


# test the lexer
# for token in lexer("1+2*(3-4)/5\n11111"):
#    print(token)
