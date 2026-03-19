# Lexer Implementation

### Course: Formal Languages & Finite Automata
### Author: Augustin Carazanu

---

## Theory

A lexer (also called a tokenizer or scanner) is the first phase of a compiler or interpreter. Its role is to read raw source text and break it down into a flat sequence of meaningful units called tokens. Each token has a type (such as INT, PLUS, or ID) and a value (the actual matched text). The lexer operates using a set of pattern rules, typically expressed as regular expressions, where each pattern corresponds to a token type. Whitespace and unrecognized characters are handled explicitly — whitespace is usually skipped, while unexpected characters raise an error. Lexers do not understand grammar or meaning; they only classify pieces of text.

## Objectives

* Implement a lexer capable of tokenizing arithmetic expressions containing integers, floats, operators, parentheses, built-in functions, and identifiers.
* Use Python's `re` module with named groups to define and apply token rules efficiently.
* Handle whitespace skipping and invalid character detection gracefully.

## Implementation Description

* The `Token` class is a simple data container that holds a token's type and value, with a `__repr__` method for clean printing during testing and debugging.

* The `Lexer` class accepts an input string and defines a prioritized list of regex rules. Each rule is a `(name, pattern)` pair. The rules are combined into a single regex using named groups (`(?P<name>pattern)`), and `re.finditer` is used to scan the input from left to right, matching the highest-priority rule at each position.

* The `tokenize` method iterates over all regex matches: `SKIP` matches are discarded (whitespace), `MISMATCH` matches raise a `RuntimeError` for unexpected characters, and all other matches are wrapped into `Token` objects and appended to the result list.

```python
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
            ('FLOAT',    r'\d+\.\d+'),
            ('INT',      r'\d+'),
            ('PLUS',     r'\+'),
            ('MINUS',    r'-'),
            ('MUL',      r'\*'),
            ('DIV',      r'/'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('FUNC',     r'sin|cos|tan'),
            ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('SKIP',     r'[ \t\n]+'),
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
```

**Sample output for input `"3.14 + cos(45) * var_name - 10"`:**

```
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
```

## Conclusion

This laboratory work demonstrated the practical construction of a lexer using regular expressions in Python. By combining multiple token patterns into a single compiled regex with named groups, the implementation achieves both efficiency and clarity. The rule ordering is intentional: FLOAT is placed before INT to ensure decimal numbers are not split into two integer tokens, and FUNC is placed before ID so that reserved function names like `sin`, `cos`, and `tan` are correctly classified rather than treated as generic identifiers. The use of `re.finditer` allows linear scanning of the input without backtracking. Overall, the exercise reinforced the foundational role a lexer plays in language processing pipelines and highlighted the importance of rule priority when designing token grammars.