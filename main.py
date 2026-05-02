import re
from enum import Enum, auto


class TokenType(Enum):
    FLOAT = auto()
    INT = auto()
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    LPAREN = auto()
    RPAREN = auto()
    FUNC = auto()
    ID = auto()


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type.name}, {self.value})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = []

        self.rules = [
            (TokenType.FLOAT, r'\d+\.\d+'),
            (TokenType.INT, r'\d+'),
            (TokenType.PLUS, r'\+'),
            (TokenType.MINUS, r'-'),
            (TokenType.MUL, r'\*'),
            (TokenType.DIV, r'/'),
            (TokenType.LPAREN, r'\('),
            (TokenType.RPAREN, r'\)'),
            (TokenType.FUNC, r'sin|cos|tan'),
            (TokenType.ID, r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ]

        parts = [f'(?P<{tt.name}>{pattern})' for tt, pattern in self.rules]
        parts.append(r'(?P<SKIP>[ \t\n]+)')
        parts.append(r'(?P<MISMATCH>.)')
        self.regex = '|'.join(parts)

    def tokenize(self):
        for match in re.finditer(self.regex, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Unexpected character: {value}')
            else:
                self.tokens.append(Token(TokenType[kind], value))
        return self.tokens


class ASTNode:
    pass


class Num(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"


class Var(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var({self.name})"


class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left}, {self.op}, {self.right})"


class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


class FuncCall(ASTNode):
    def __init__(self, name, arg):
        self.name = name
        self.arg = arg

    def __repr__(self):
        return f"FuncCall({self.name}, {self.arg})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self, expected_type=None):
        tok = self._peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type is not None and tok.type != expected_type:
            raise SyntaxError(f"Expected {expected_type.name}, got {tok.type.name}")
        self.pos += 1
        return tok

    def parse(self):
        result = self._parse_expression()
        if self._peek() is not None:
            raise SyntaxError(f"Unexpected token at end: {self._peek()}")
        return result

    def _parse_expression(self):
        # expression -> term (('+' | '-') term)*
        node = self._parse_term()
        while self._peek() is not None and self._peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self._consume().value
            right = self._parse_term()
            node = BinOp(node, op, right)
        return node

    def _parse_term(self):
        # term -> factor (('*' | '/') factor)*
        node = self._parse_factor()
        while self._peek() is not None and self._peek().type in (TokenType.MUL, TokenType.DIV):
            op = self._consume().value
            right = self._parse_factor()
            node = BinOp(node, op, right)
        return node

    def _parse_factor(self):
        # factor -> NUMBER | ID | FUNC '(' expression ')' | '(' expression ')' | '-' factor
        tok = self._peek()
        if tok is None:
            raise SyntaxError("Unexpected end of input")

        if tok.type == TokenType.MINUS:
            self._consume()
            return UnaryOp('-', self._parse_factor())

        if tok.type == TokenType.INT:
            self._consume()
            return Num(int(tok.value))

        if tok.type == TokenType.FLOAT:
            self._consume()
            return Num(float(tok.value))

        if tok.type == TokenType.FUNC:
            self._consume()
            self._consume(TokenType.LPAREN)
            arg = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return FuncCall(tok.value, arg)

        if tok.type == TokenType.ID:
            self._consume()
            return Var(tok.value)

        if tok.type == TokenType.LPAREN:
            self._consume()
            node = self._parse_expression()
            self._consume(TokenType.RPAREN)
            return node

        raise SyntaxError(f"Unexpected token: {tok}")


def print_ast(node, indent=0):
    prefix = '  ' * indent
    if isinstance(node, Num):
        print(f"{prefix}Num({node.value})")
    elif isinstance(node, Var):
        print(f"{prefix}Var({node.name})")
    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp({node.op})")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnaryOp({node.op})")
        print_ast(node.operand, indent + 1)
    elif isinstance(node, FuncCall):
        print(f"{prefix}FuncCall({node.name})")
        print_ast(node.arg, indent + 1)


def run_demo():
    expressions = [
        "3.14 + cos(45) * var_name - 10",
        "1 + 2 * 3",
        "(1 + 2) * 3",
        "sin(x + 1) * 2",
        "-5 + 3 * (a - b)"
    ]

    for expr in expressions:
        print(f"\n=== Input: {expr} ===")

        lexer = Lexer(expr)
        tokens = lexer.tokenize()
        print("\nTokens:")
        for t in tokens:
            print(f"  {t}")

        parser = Parser(tokens)
        ast = parser.parse()
        print("\nAST:")
        print_ast(ast)


if __name__ == "__main__":
    run_demo()