import collections


class Grammar:
    def __init__(self, V_n, V_t, P, S):
        self.V_n = V_n
        self.V_t = V_t
        self.P = P
        self.S = S

    def classify(self):
        is_type_1 = True
        is_type_2 = True
        is_type_3 = True

        for lhs, rhs_list in self.P.items():
            for rhs in rhs_list:
                if len(lhs) > len(rhs) and rhs != 'ε':
                    is_type_1 = False

                if len(lhs) != 1 or lhs not in self.V_n:
                    is_type_2 = False

                if is_type_2:
                    is_regular_rhs = False
                    if all(char in self.V_t for char in rhs):
                        is_regular_rhs = True
                    elif len(rhs) == 2:
                        if rhs[0] in self.V_t and rhs[1] in self.V_n:
                            is_regular_rhs = True

                    if not is_regular_rhs:
                        is_type_3 = False

        if is_type_3: return "Type 3 (Regular)"
        if is_type_2: return "Type 2 (Context-Free)"
        if is_type_1: return "Type 1 (Context-Sensitive)"
        return "Type 0 (Unrestricted)"


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def is_deterministic(self):
        seen_transitions = set()
        for (state, symbol), target in self.transitions.items():
            if isinstance(target, list) and len(target) > 1:
                return False
            if (state, symbol) in seen_transitions:
                return False
            seen_transitions.add((state, symbol))
        return True

    def to_regular_grammar(self):
        vn = self.states
        vt = self.alphabet
        p = collections.defaultdict(list)

        for (state, symbol), targets in self.transitions.items():
            if not isinstance(targets, list):
                targets = [targets]
            for t in targets:
                p[state].append(f"{symbol}{t}")
                if t in self.final_states:
                    p[state].append(symbol)

        return Grammar(vn, vt, dict(p), self.start_state)

    def to_dfa(self):
        new_states = []
        new_transitions = {}
        start_set = frozenset([self.start_state])
        queue = collections.deque([start_set])
        new_states.append(start_set)

        dfa_final_states = []

        while queue:
            current_set = queue.popleft()

            if any(s in self.final_states for s in current_set):
                if current_set not in dfa_final_states:
                    dfa_final_states.append(current_set)

            for symbol in self.alphabet:
                next_set = set()
                for state in current_set:
                    res = self.transitions.get((state, symbol), [])
                    if isinstance(res, list):
                        next_set.update(res)
                    else:
                        next_set.add(res)

                if not next_set:
                    continue

                target_frozenset = frozenset(next_set)
                new_transitions[(current_set, symbol)] = target_frozenset

                if target_frozenset not in new_states:
                    new_states.append(target_frozenset)
                    queue.append(target_frozenset)

        return FiniteAutomaton(
            [list(s) for s in new_states],
            self.alphabet,
            new_transitions,
            list(start_set),
            [list(s) for s in dfa_final_states]
        )


def run_variant_3():
    q = {'q0', 'q1', 'q2', 'q3', 'q4'}
    sigma = {'a', 'b'}
    f = {'q4'}
    delta = {
        ('q0', 'a'): ['q1'],
        ('q1', 'b'): ['q1'],
        ('q1', 'a'): ['q2'],
        ('q2', 'b'): ['q2', 'q3'],
        ('q3', 'b'): ['q4'],
        ('q3', 'a'): ['q1']
    }

    fa = FiniteAutomaton(q, sigma, delta, 'q0', f)

    print(f"Is Deterministic: {fa.is_deterministic()}")

    rg = fa.to_regular_grammar()
    print("\nRegular Grammar Productions:")
    for lhs, rhs in rg.P.items():
        print(f"{lhs} -> {' | '.join(rhs)}")

    dfa = fa.to_dfa()
    print("\nConverted DFA Transitions:")
    for (state, char), target in dfa.transitions.items():
        print(f"δ({set(state)}, {char}) = {set(target)}")


if __name__ == "__main__":
    run_variant_3()