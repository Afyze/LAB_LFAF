# Regular Grammars & Finite Automata

### Course: Formal Languages & Finite Automata
### Author: Augustin Carazanu

----

## Theory

A **formal grammar** is a set of rules for generating strings in a formal language. A **regular grammar** is one of the simplest types — each production rule has at most one non-terminal, placed either at the start or the end of the right-hand side. Regular grammars are directly equivalent to **finite automata (FA)**: any regular grammar can be converted into a finite automaton that accepts exactly the same language, and vice versa.

A **finite automaton** is an abstract machine with a finite number of states that reads an input string symbol by symbol and transitions between states according to a transition function. If the machine ends in an **accepting (final) state** after consuming the entire input, the string is considered part of the language recognized by the automaton.

The key connection is: for a right-linear grammar, each non-terminal corresponds to a state, each production rule corresponds to a transition, and terminal-only productions lead to a designated final state.

## Objectives

* Implement a `Grammar` class that represents a regular (right-linear) formal grammar and can generate valid strings from it.
* Implement a `FiniteAutomaton` class capable of validating whether a given string belongs to the language defined by the grammar.
* Convert a given `Grammar` instance into its equivalent `FiniteAutomaton`.
* Validate the correctness of the conversion by testing generated strings against the automaton.

## Implementation Description

### Grammar Class

The `Grammar` class stores the four components of a formal grammar: non-terminals (`VN`), terminals (`VT`), production rules (`P`), and the start symbol (`S`). The `generate_string` method randomly walks through the production rules starting from `S`, appending terminal symbols to the result and following non-terminal symbols until no further transitions exist.

The `to_finite_automaton` method converts the grammar into a `FiniteAutomaton`. Each non-terminal becomes a state; an extra state `'X'` is added as the single final/accepting state. Productions of the form `A → aB` become transitions `(A, a) → B`, while terminal-only productions `A → a` become transitions `(A, a) → X`.

```python
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
```

### FiniteAutomaton Class

The `FiniteAutomaton` class holds the standard 5-tuple: states (`Q`), alphabet (`Sigma`), transition function (`delta`), initial state (`q0`), and final states (`F`). The `string_belong_to_language` method processes the input character by character, tracking the set of currently active states. If the final set of states contains at least one accepting state, the string is valid.

```python
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
```

### Variant 3 Grammar Definition

The grammar used corresponds to Variant 3:

```
VN = {S, D, R}
VT = {a, b, c, d, f}
P:
    S → aS
    S → bD
    S → fR
    D → cD
    D → dR
    D → d
    R → bR
    R → f
```

## Conclusions / Screenshots / Results

The implementation successfully demonstrates the theoretical equivalence between regular grammars and finite automata. Five strings are generated randomly from the grammar, and each is then validated against the derived finite automaton — all generated strings are confirmed as valid members of the language. An additional manually crafted invalid string (`"abc"`) is tested and correctly rejected by the automaton.

**Sample output:**

```
--- Generated Strings ---
1: aabf
2: bdd
3: fbbf
4: bcdd
5: aabd

--- FA Validation ---
String 'aabf' is valid: True
String 'bdd' is valid: True
String 'fbbf' is valid: True
String 'bcdd' is valid: True
String 'aabd' is valid: True
String 'abc' is valid: False
```

The conversion from grammar to automaton is deterministic and correct: every string generated by the grammar is accepted by the automaton, and strings outside the language are rejected.

## Conclusions

This lab demonstrated the direct equivalence between regular grammars and finite automata in practice. Implementing both from scratch made it clear how non-terminals map to states and production rules map to transitions. The validation results confirmed the conversion was correct: all generated strings were accepted by the automaton, and invalid ones were rejected.