import re


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []

        self.rules = [
            ('FLOAT', r'\d+\.\d+'),
            ('INT', r'\d+'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MUL', r'\*'),
            ('DIV', r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('FUNC', r'sin|cos|tan'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('SKIP', r'[ \t\n]+'),
            ('MISMATCH', r'.'),
        ]
        self.regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.rules)

    def tokenize(self):
        for match in re.finditer(self.regex, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character: {value}')
            else:
                self.tokens.append(Token(kind, value))
        return self.tokens


if __name__ == "__main__":
    code = "3.14 + cos(45) * var_name - 10"
    lexer = Lexer(code)
    try:
        tokens = lexer.tokenize()
        for token in tokens:
            print(token)
    except RuntimeError as e:
        print(e)