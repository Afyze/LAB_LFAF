# Finite Automata & Grammar Classification

### Course: Formal Languages & Finite Automata
### Author: Augustin Carazanu

----

## Theory

A Finite Automaton (FA) is a mathematical model of computation consisting of a finite set of states, an input alphabet, a transition function, a start state, and a set of accepting (final) states. Automata can be either deterministic (DFA) — where each state has exactly one transition per symbol — or nondeterministic (NFA), where multiple transitions per symbol are allowed.

Grammars are classified according to the Chomsky hierarchy into four types: Type 0 (Unrestricted), Type 1 (Context-Sensitive), Type 2 (Context-Free), and Type 3 (Regular). Regular grammars correspond exactly to finite automata in their expressive power. Every NFA can be converted to an equivalent DFA via the subset construction algorithm, and every finite automaton defines a regular grammar.


## Objectives

* Implement a `Grammar` class capable of classifying any given grammar according to the Chomsky hierarchy (Type 0 through Type 3).
* Implement a `FiniteAutomaton` class that can determine whether a given automaton is deterministic (DFA) or nondeterministic (NFA).
* Convert a given NFA to a regular grammar by deriving production rules from its transition function.
* Convert an NFA to an equivalent DFA using the subset construction (powerset) algorithm.
* Apply the implementation to Variant 3, a specific NFA with states q0–q4, and verify the correctness of all conversions.


## Implementation Description

### Grammar Class

The `Grammar` class stores the four components of a formal grammar: non-terminals (`V_n`), terminals (`V_t`), production rules (`P`), and start symbol (`S`). Its `classify()` method iterates over all productions and checks the conditions for each Chomsky type — verifying rule lengths for Type 1, single non-terminal left-hand sides for Type 2, and right-linear form for Type 3. The most restrictive type that still satisfies all conditions is returned.

```python
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
                elif len(rhs) == 2 and rhs[0] in self.V_t and rhs[1] in self.V_n:
                    is_regular_rhs = True
                if not is_regular_rhs:
                    is_type_3 = False

    if is_type_3: return "Type 3 (Regular)"
    if is_type_2: return "Type 2 (Context-Free)"
    if is_type_1: return "Type 1 (Context-Sensitive)"
    return "Type 0 (Unrestricted)"
```

### FiniteAutomaton Class

The `FiniteAutomaton` class encapsulates the 5-tuple definition of an automaton. The `is_deterministic()` method checks whether any `(state, symbol)` pair leads to more than one target state. The `to_regular_grammar()` method creates `Grammar` productions by converting each transition `(state, symbol) -> target` into a production `state -> symbol target`, and adds a unit production `state -> symbol` when the target is a final state.

```python
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
    p = collections.defaultdict(list)
    for (state, symbol), targets in self.transitions.items():
        if not isinstance(targets, list):
            targets = [targets]
        for t in targets:
            p[state].append(f"{symbol}{t}")
            if t in self.final_states:
                p[state].append(symbol)
    return Grammar(self.states, self.alphabet, dict(p), self.start_state)
```

### NFA to DFA Conversion

The `to_dfa()` method implements the subset construction algorithm. Starting from a frozenset containing only the NFA start state, it processes each unvisited set of states by computing, for each alphabet symbol, the union of all NFA transitions from states in the current set. Each unique resulting set becomes a new DFA state. A DFA state is final if it contains at least one NFA final state.

```python
def to_dfa(self):
    start_set = frozenset([self.start_state])
    queue = collections.deque([start_set])
    new_states = [start_set]
    new_transitions = {}
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
                next_set.update(res if isinstance(res, list) else [res])
            if not next_set:
                continue
            target = frozenset(next_set)
            new_transitions[(current_set, symbol)] = target
            if target not in new_states:
                new_states.append(target)
                queue.append(target)
    ...
```

### Variant 3 — NFA Definition

The `run_variant_3()` function defines the following NFA and runs all three operations on it:

* **States:** Q = {q0, q1, q2, q3, q4}
* **Alphabet:** Σ = {a, b}
* **Start state:** q0
* **Final states:** F = {q4}
* **Transitions:** δ(q0,a)={q1}, δ(q1,b)={q1}, δ(q1,a)={q2}, δ(q2,b)={q2,q3}, δ(q3,b)={q4}, δ(q3,a)={q1}


## Conclusions / Screenshots / Results

Running the program on Variant 3 produces the following output:

```
Is Deterministic: False

Regular Grammar Productions:
q0 -> aq1
q1 -> bq1 | aq2
q2 -> bq2 | bq3
q3 -> bq4 | b | aq1

Converted DFA Transitions:
δ({'q0'}, a) = {'q1'}
δ({'q1'}, b) = {'q1'}
δ({'q1'}, a) = {'q2'}
δ({'q2'}, b) = {'q2', 'q3'}
δ({'q2', 'q3'}, b) = {'q2', 'q3', 'q4'}
δ({'q2', 'q3'}, a) = {'q1'}
δ({'q2', 'q3', 'q4'}, b) = {'q2', 'q3', 'q4'}
δ({'q2', 'q3', 'q4'}, a) = {'q1'}
δ({'q3'}, b) = {'q4'}
δ({'q3'}, a) = {'q1'}
```

This laboratory work successfully demonstrated the close theoretical relationship between finite automata and formal grammars. The Grammar class correctly classifies grammars according to the Chomsky hierarchy by checking each production against increasingly strict structural requirements, from unrestricted to right-linear form.

The FiniteAutomaton class proved that the Variant 3 automaton is nondeterministic, as the transition from q2 on symbol 'b' leads to two distinct states. The regular grammar derived from the NFA accurately captures the language by translating each transition into a right-linear production rule, with additional unit productions added for transitions leading into final states.

The subset construction algorithm correctly converted the NFA to a DFA by grouping states into sets and computing composite transitions. The resulting DFA contains merged states such as {q2, q3} and {q2, q3, q4}, demonstrating how nondeterminism is resolved by tracking all possible current states simultaneously. The implementation is general and can be applied to any NFA, not just Variant 3.