import random


class Grammar:
    def __init__(self, vn, vt, p, s):
        self.VN = vn
        self.VT = vt
        self.P = p
        self.S = s

    def generate_string(self):
        word = ""
        current_symbol = self.S

        while current_symbol:
            options = self.P.get(current_symbol)
            if not options:
                break

            chosen_production = random.choice(options)

            for char in chosen_production:
                if char in self.VT:
                    word += char
                if char in self.VN:
                    current_symbol = char
                    break
            else:
                current_symbol = None

        return word

    def to_finite_automaton(self):
        states = self.VN.copy()
        states.add('X')

        alphabet = self.VT
        initial_state = self.S
        final_states = {'X'}
        transitions = {}

        for non_terminal, rules in self.P.items():
            for rule in rules:
                if len(rule) == 1 and rule in self.VT:
                    state_from = non_terminal
                    symbol = rule
                    state_to = 'X'
                else:
                    state_from = non_terminal
                    symbol = rule[0]
                    state_to = rule[1]

                if (state_from, symbol) not in transitions:
                    transitions[(state_from, symbol)] = []
                transitions[(state_from, symbol)].append(state_to)

        return FiniteAutomaton(states, alphabet, transitions, initial_state, final_states)


class FiniteAutomaton:
    def __init__(self, q, sigma, delta, q0, f):
        self.Q = q
        self.Sigma = sigma
        self.delta = delta
        self.q0 = q0
        self.F = f

    def string_belong_to_language(self, input_string):
        current_states = {self.q0}

        for char in input_string:
            next_states = set()
            for state in current_states:
                if (state, char) in self.delta:
                    for transition_target in self.delta[(state, char)]:
                        next_states.add(transition_target)

            if not next_states:
                return False
            current_states = next_states

        return any(state in self.F for state in current_states)


if __name__ == "__main__":
    vn = {'S', 'D', 'R'}
    vt = {'a', 'b', 'c', 'd', 'f'}
    p = {
        'S': ['aS', 'bD', 'fR'],
        'D': ['cD', 'dR', 'd'],
        'R': ['bR', 'f']
    }
    s = 'S'

    my_grammar = Grammar(vn, vt, p, s)

    print("--- Generated Strings ---")
    generated_words = [my_grammar.generate_string() for _ in range(5)]
    for i, word in enumerate(generated_words, 1):
        print(f"{i}: {word}")

    fa = my_grammar.to_finite_automaton()

    print("\n--- FA Validation ---")
    for word in generated_words:
        is_valid = fa.string_belong_to_language(word)
        print(f"String '{word}' is valid: {is_valid}")

    invalid_test = "abc"
    print(f"String '{invalid_test}' is valid: {fa.string_belong_to_language(invalid_test)}")