# LAB_LFAF
# Parser & Abstract Syntax Tree

### Course: Formal Languages & Finite Automata
### Author: Augustin Carazanu

----

## Theory

Parsing is the process of analyzing a sequence of tokens against a formal grammar to determine its syntactic structure. The output is a hierarchical representation of the input, most often a parse tree or an abstract syntax tree (AST). A parse tree captures every grammar rule applied during recognition, while an AST keeps only the structural information that matters for further processing - it discards punctuation and intermediate non-terminals that exist for grammar reasons but carry no semantic value.

A common parsing technique is recursive descent, where each non-terminal in the grammar becomes a function in the parser. The functions call each other based on the lookahead token, and the call stack mirrors the derivation tree. Recursive descent works well for grammars expressed in operator-precedence form, where each precedence level is its own non-terminal calling into the next-tighter level. For arithmetic expressions, this yields a clean three-level grammar: expression for sums, term for products, and factor for atoms.

The AST node types reflect the language. For arithmetic expressions over numbers, identifiers, and unary functions, five node kinds suffice: numeric literals, variable references, binary operations, unary operations, and function calls. Each node holds references to its children, and traversal of the tree corresponds to evaluation, transformation, or code generation in later compiler phases.

## Objectives

* Extend the Lab 3 lexer with a `TokenType` enum so token categories are first-class values rather than strings, while keeping the regex-driven scanning approach intact.
* Define a small set of AST node classes (`Num`, `Var`, `BinOp`, `UnaryOp`, `FuncCall`) that together can represent any arithmetic expression supported by the lexer.
* Implement a recursive descent `Parser` that consumes the token stream from the lexer and produces an AST honoring standard operator precedence and associativity.
* Implement a tree printer that renders the AST in indented form for inspection.
* Verify the pipeline end-to-end on multiple expressions including numbers, variables, function calls, parenthesized sub-expressions, and unary minus.

## Implementation Description

### TokenType Enum and Lexer

The token type is now an `Enum`, which makes type comparisons in the parser direct (`tok.type == TokenType.PLUS`) rather than string-based. The `Lexer` builds a single combined regex by joining each rule's pattern under a named group, where the group name matches the enum member name. Two extra non-rule groups, `SKIP` and `MISMATCH`, handle whitespace and unknown characters at the bottom of the alternation.

```python
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
```

When `tokenize()` runs, each match is converted into a `Token` whose type is the corresponding enum member, looked up by name with `TokenType[kind]`.

### AST Node Classes

The AST is built from five node types. `Num` holds a numeric literal converted to `int` or `float`. `Var` holds an identifier name. `BinOp` represents a binary operation with left and right sub-trees and an operator string. `UnaryOp` represents a single-operand operation (used for unary minus). `FuncCall` represents a call to a built-in function and stores the function name plus its argument expression.

```python
class Num(ASTNode):
    def __init__(self, value):
        self.value = value


class Var(ASTNode):
    def __init__(self, name):
        self.name = name


class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand


class FuncCall(ASTNode):
    def __init__(self, name, arg):
        self.name = name
        self.arg = arg
```

### Parser Class

The parser is a recursive descent parser implementing the following grammar:

```
expression -> term (('+' | '-') term)*
term       -> factor (('*' | '/') factor)*
factor     -> INT | FLOAT | ID | FUNC '(' expression ')' | '(' expression ')' | '-' factor
```

Each non-terminal has its own method. `_parse_expression` handles the lowest-precedence operators (`+`, `-`) with left associativity, building a left-leaning tree. `_parse_term` does the same for `*` and `/` at the next precedence level. `_parse_factor` handles atoms and the highest-precedence constructs: literals, identifiers, function calls, parenthesized sub-expressions, and unary minus. Parentheses are consumed but produce no AST node, since they exist only to override default precedence.

```python
def _parse_expression(self):
    node = self._parse_term()
    while self._peek() is not None and self._peek().type in (TokenType.PLUS, TokenType.MINUS):
        op = self._consume().value
        right = self._parse_term()
        node = BinOp(node, op, right)
    return node

def _parse_factor(self):
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
```

### AST Pretty Printer

The `print_ast` function walks the tree recursively and prints each node with indentation reflecting its depth. It is dispatched on the node class and handles all five node types.

```python
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
```

## Conclusions / Screenshots / Results

The pipeline was tested on five expressions covering numbers, variables, function calls, parentheses, and unary minus.

**Input:** `3.14 + cos(45) * var_name - 10`

```
Tokens:
  Token(FLOAT, 3.14)
  Token(PLUS, +)
  Token(FUNC, cos)
  Token(LPAREN, ()
  Token(INT, 45)
  Token(RPAREN, ))
  Token(MUL, *)
  Token(ID, var_name)
  Token(MINUS, -)
  Token(INT, 10)

AST:
BinOp(-)
  BinOp(+)
    Num(3.14)
    BinOp(*)
      FuncCall(cos)
        Num(45)
      Var(var_name)
  Num(10)
```

**Input:** `1 + 2 * 3`

```
AST:
BinOp(+)
  Num(1)
  BinOp(*)
    Num(2)
    Num(3)
```

The multiplication is grouped under the right side of the addition, confirming `*` binds tighter than `+`.

**Input:** `(1 + 2) * 3`

```
AST:
BinOp(*)
  BinOp(+)
    Num(1)
    Num(2)
  Num(3)
```

Parentheses correctly override default precedence, putting the addition under the multiplication.

**Input:** `-5 + 3 * (a - b)`

```
AST:
BinOp(+)
  UnaryOp(-)
    Num(5)
  BinOp(*)
    Num(3)
    BinOp(-)
      Var(a)
      Var(b)
```

Unary minus wraps the literal `5` and binds tighter than the binary `+`, while the parenthesized subtraction sits under the multiplication on the right side.

All five test expressions produced correct ASTs that match standard arithmetic operator precedence (unary minus and parentheses tightest, then `*`/`/`, then `+`/`-`) and left-associativity for binary operators.

## Conclusions

The lab connected the lexer from Lab 3 to a parser stage and made the token-to-tree pipeline explicit. Switching token categories from strings to a `TokenType` enum was a small change that paid off immediately - it removed a class of typo bugs in the parser and made the code more readable, since enum comparisons read like grammar rules.

The recursive descent parser turned out to be a natural fit for the operator-precedence grammar. Each precedence level got its own method, and the call hierarchy of the methods directly mirrors the precedence hierarchy. The trickiest design decision was where to place unary minus - putting it in `_parse_factor` and recursing back into the same level cleanly handles cases like `--x` or `5 - -3` without a separate grammar rule.

The AST is intentionally small. Five node kinds cover all valid inputs of the lexer's grammar. If the language were extended (more operators, multi-argument functions, assignments, control flow), the AST would grow correspondingly, but the recursive descent structure would scale with it - each new construct becomes another node type and another method.

## References

1. Aho, A., Lam, M., Sethi, R., Ullman, J. - *Compilers: Principles, Techniques, and Tools*, 2nd edition, Pearson, 2006.
2. Parsing - Wikipedia. https://en.wikipedia.org/wiki/Parsing
3. Abstract Syntax Tree - Wikipedia. https://en.wikipedia.org/wiki/Abstract_syntax_tree
4. Course materials for Formal Languages & Finite Automata, Technical University of Moldova.