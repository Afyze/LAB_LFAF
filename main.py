import random

REPEAT_LIMIT = 5


class RegexParser:
    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0

    def _peek(self):
        return self.pattern[self.pos] if self.pos < len(self.pattern) else None

    def _consume(self):
        ch = self.pattern[self.pos]
        self.pos += 1
        return ch

    def parse(self):
        return self._parse_alternation()

    def _parse_alternation(self):
        left = self._parse_concat()
        if self._peek() == '|':
            options = [left]
            while self._peek() == '|':
                self._consume()
                options.append(self._parse_concat())
            return ('alt', options)
        return left

    def _parse_concat(self):
        items = []
        while self._peek() is not None and self._peek() not in ('|', ')'):
            items.append(self._parse_repeat())
        if len(items) == 1:
            return items[0]
        return ('concat', items)

    def _parse_repeat(self):
        atom = self._parse_atom()
        nxt = self._peek()
        if nxt == '*':
            self._consume()
            return ('star', atom)
        if nxt == '+':
            self._consume()
            return ('plus', atom)
        if nxt == '?':
            self._consume()
            return ('question', atom)
        if nxt == '{':
            self._consume()
            num = ''
            while self._peek() != '}':
                num += self._consume()
            self._consume()
            return ('exact', atom, int(num))
        return atom

    def _parse_atom(self):
        if self._peek() == '(':
            self._consume()
            inner = self._parse_alternation()
            self._consume()
            return inner
        return ('literal', self._consume())


class RegexGenerator:
    def __init__(self, ast):
        self.ast = ast

    def generate(self):
        return self._gen(self.ast)

    def _gen(self, node):
        kind = node[0]
        if kind == 'literal':
            return node[1]
        if kind == 'concat':
            return ''.join(self._gen(c) for c in node[1])
        if kind == 'alt':
            return self._gen(random.choice(node[1]))
        if kind == 'star':
            n = random.randint(0, REPEAT_LIMIT)
            return ''.join(self._gen(node[1]) for _ in range(n))
        if kind == 'plus':
            n = random.randint(1, REPEAT_LIMIT)
            return ''.join(self._gen(node[1]) for _ in range(n))
        if kind == 'question':
            return self._gen(node[1]) if random.choice([True, False]) else ''
        if kind == 'exact':
            return ''.join(self._gen(node[1]) for _ in range(node[2]))
        return ''


class RegexExplainer:
    def __init__(self, ast):
        self.ast = ast
        self.steps = []

    def explain(self):
        self.steps = []
        self._walk(self.ast, 0)
        return self.steps

    def _walk(self, node, depth):
        indent = '  ' * depth
        kind = node[0]
        if kind == 'literal':
            self.steps.append(f"{indent}Output literal '{node[1]}'")
        elif kind == 'concat':
            self.steps.append(f"{indent}Concatenate {len(node[1])} parts:")
            for c in node[1]:
                self._walk(c, depth + 1)
        elif kind == 'alt':
            self.steps.append(f"{indent}Choose one of {len(node[1])} alternatives:")
            for c in node[1]:
                self._walk(c, depth + 1)
        elif kind == 'star':
            self.steps.append(f"{indent}Repeat 0 to {REPEAT_LIMIT} times:")
            self._walk(node[1], depth + 1)
        elif kind == 'plus':
            self.steps.append(f"{indent}Repeat 1 to {REPEAT_LIMIT} times:")
            self._walk(node[1], depth + 1)
        elif kind == 'question':
            self.steps.append(f"{indent}Optional (0 or 1 occurrence):")
            self._walk(node[1], depth + 1)
        elif kind == 'exact':
            self.steps.append(f"{indent}Repeat exactly {node[2]} times:")
            self._walk(node[1], depth + 1)


def run_variant_3():
    regexes = [
        "O(P|Q|R)+2(3|4)",
        "A*B(C|D|E)F(G|H|i){2}",
        "J+K(L|M|N)*O?(P|Q){3}"
    ]

    for regex in regexes:
        print(f"\n=== Regex: {regex} ===")
        ast = RegexParser(regex).parse()

        print("\nGenerated strings:")
        gen = RegexGenerator(ast)
        for i in range(5):
            print(f"  {i + 1}: {gen.generate()}")

        print("\nProcessing sequence:")
        for step in RegexExplainer(ast).explain():
            print(step)


if __name__ == "__main__":
    run_variant_3()