from itertools import combinations


class Grammar:
    def __init__(self, V_n, V_t, P, S):
        self.V_n = set(V_n)
        self.V_t = set(V_t)
        self.P = {nt: [list(prod) for prod in prods] for nt, prods in P.items()}
        self.S = S

    def display(self, label=""):
        if label:
            print(f"\n--- {label} ---")
        print(f"V_n = {{{', '.join(sorted(self.V_n))}}}")
        print(f"V_t = {{{', '.join(sorted(self.V_t))}}}")
        print(f"S = {self.S}")
        print("P:")
        idx = 1
        order = [self.S] + sorted(nt for nt in self.P if nt != self.S)
        for nt in order:
            if nt not in self.P:
                continue
            for prod in self.P[nt]:
                rhs = ''.join(prod) if prod else 'ε'
                print(f"  {idx}. {nt} -> {rhs}")
                idx += 1

    def eliminate_epsilon(self):
        nullable = set()
        for nt, prods in self.P.items():
            for prod in prods:
                if len(prod) == 0:
                    nullable.add(nt)

        changed = True
        while changed:
            changed = False
            for nt, prods in self.P.items():
                if nt in nullable:
                    continue
                for prod in prods:
                    if len(prod) > 0 and all(sym in nullable for sym in prod):
                        nullable.add(nt)
                        changed = True
                        break

        new_P = {}
        for nt, prods in self.P.items():
            new_P[nt] = []
            for prod in prods:
                if len(prod) == 0:
                    continue
                nullable_positions = [i for i, sym in enumerate(prod) if sym in nullable]
                if list(prod) not in new_P[nt]:
                    new_P[nt].append(list(prod))
                for r in range(1, len(nullable_positions) + 1):
                    for combo in combinations(nullable_positions, r):
                        new_prod = [sym for i, sym in enumerate(prod) if i not in combo]
                        if len(new_prod) > 0 and new_prod not in new_P[nt]:
                            new_P[nt].append(new_prod)

        self.P = new_P
        return nullable

    def eliminate_renaming(self):
        unit_reachable = {nt: {nt} for nt in self.V_n}
        changed = True
        while changed:
            changed = False
            for nt in self.V_n:
                for reachable in list(unit_reachable[nt]):
                    if reachable in self.P:
                        for prod in self.P[reachable]:
                            if len(prod) == 1 and prod[0] in self.V_n:
                                if prod[0] not in unit_reachable[nt]:
                                    unit_reachable[nt].add(prod[0])
                                    changed = True

        new_P = {nt: [] for nt in self.V_n}
        for nt in self.V_n:
            for reachable in unit_reachable[nt]:
                if reachable in self.P:
                    for prod in self.P[reachable]:
                        if not (len(prod) == 1 and prod[0] in self.V_n):
                            if prod not in new_P[nt]:
                                new_P[nt].append(list(prod))
        self.P = new_P

    def eliminate_inaccessible(self):
        accessible = {self.S}
        changed = True
        while changed:
            changed = False
            for nt in list(accessible):
                if nt in self.P:
                    for prod in self.P[nt]:
                        for sym in prod:
                            if sym in self.V_n and sym not in accessible:
                                accessible.add(sym)
                                changed = True

        self.V_n &= accessible
        self.P = {nt: prods for nt, prods in self.P.items() if nt in accessible}

    def eliminate_non_productive(self):
        productive = set()
        changed = True
        while changed:
            changed = False
            for nt, prods in self.P.items():
                if nt in productive:
                    continue
                for prod in prods:
                    if len(prod) > 0 and all(sym in self.V_t or sym in productive for sym in prod):
                        productive.add(nt)
                        changed = True
                        break

        self.V_n &= productive
        new_P = {}
        for nt, prods in self.P.items():
            if nt in productive:
                new_P[nt] = []
                for prod in prods:
                    if all(sym in self.V_t or sym in productive for sym in prod):
                        if prod not in new_P[nt]:
                            new_P[nt].append(prod)
        self.P = new_P

    def _cnf_replace_terminals(self):
        terminal_to_nt = {}
        counter = 1
        new_P = {nt: [] for nt in self.V_n}

        for nt, prods in self.P.items():
            for prod in prods:
                if len(prod) >= 2:
                    new_prod = []
                    for sym in prod:
                        if sym in self.V_t:
                            if sym not in terminal_to_nt:
                                while f'X{counter}' in self.V_n:
                                    counter += 1
                                new_nt = f'X{counter}'
                                counter += 1
                                terminal_to_nt[sym] = new_nt
                            new_prod.append(terminal_to_nt[sym])
                        else:
                            new_prod.append(sym)
                    new_P[nt].append(new_prod)
                else:
                    new_P[nt].append(list(prod))

        for term, nt in terminal_to_nt.items():
            self.V_n.add(nt)
            new_P[nt] = [[term]]

        self.P = new_P

    def _cnf_break_long(self):
        new_P = {nt: [] for nt in self.V_n}
        long_to_nt = {}
        counter = 1

        def break_prod(prod):
            nonlocal counter
            if len(prod) <= 2:
                return list(prod)
            rest_tuple = tuple(prod[1:])
            if rest_tuple not in long_to_nt:
                while f'Y{counter}' in self.V_n:
                    counter += 1
                new_nt = f'Y{counter}'
                counter += 1
                long_to_nt[rest_tuple] = new_nt
                self.V_n.add(new_nt)
                new_P[new_nt] = []
                new_P[new_nt].append(break_prod(list(prod[1:])))
            return [prod[0], long_to_nt[rest_tuple]]

        for nt, prods in list(self.P.items()):
            if nt not in new_P:
                new_P[nt] = []
            for prod in prods:
                new_P[nt].append(break_prod(list(prod)))

        self.P = new_P

    def to_cnf(self):
        self.eliminate_epsilon()
        self.eliminate_renaming()
        self.eliminate_inaccessible()
        self.eliminate_non_productive()
        self._cnf_replace_terminals()
        self._cnf_break_long()

    def is_cnf(self):
        for nt, prods in self.P.items():
            for prod in prods:
                if len(prod) == 1:
                    if prod[0] not in self.V_t:
                        return False
                elif len(prod) == 2:
                    if not (prod[0] in self.V_n and prod[1] in self.V_n):
                        return False
                else:
                    return False
        return True


def run_variant_3():
    V_n = {'S', 'A', 'B', 'C', 'E'}
    V_t = {'a', 'd'}
    P = {
        'S': [['d', 'B'], ['A']],
        'A': [['d'], ['d', 'S'], ['a', 'A', 'd', 'A', 'B']],
        'B': [['a', 'C'], ['a', 'S'], ['A', 'C']],
        'C': [[]],
        'E': [['A', 'S']]
    }
    S = 'S'

    g = Grammar(V_n, V_t, P, S)
    g.display("Initial Grammar")

    g.eliminate_epsilon()
    g.display("After Step 1: Eliminate epsilon productions")

    g.eliminate_renaming()
    g.display("After Step 2: Eliminate renaming")

    g.eliminate_inaccessible()
    g.display("After Step 3: Eliminate inaccessible symbols")

    g.eliminate_non_productive()
    g.display("After Step 4: Eliminate non-productive symbols")

    g._cnf_replace_terminals()
    g._cnf_break_long()
    g.display("After Step 5: Chomsky Normal Form")

    print(f"\nIs in CNF: {g.is_cnf()}")


if __name__ == "__main__":
    run_variant_3()