# LAB_LFAF
# Chomsky Normal Form

### Course: Formal Languages & Finite Automata
### Author: Augustin Carazanu

----

## Theory

A context-free grammar G = (V_n, V_t, P, S) is in Chomsky Normal Form (CNF) if every production has one of two forms: A → BC where A, B, C are non-terminals, or A → a where a is a terminal. Any context-free language without ε can be expressed by an equivalent grammar in CNF, which makes CNF a useful canonical form for parsing algorithms such as CYK.

Converting an arbitrary context-free grammar into CNF is done in five sequential steps. First, ε-productions are removed by computing the set of nullable non-terminals and rewriting each production into all variants with nullable symbols optionally dropped. Second, unit productions of the form X → Y (renaming) are removed by collapsing chains of unit productions into direct non-unit productions. Third, inaccessible symbols (those not reachable from S) are eliminated. Fourth, non-productive symbols (those that cannot derive any string of terminals) are eliminated. Finally, the cleaned grammar is rewritten so all right-hand sides have either a single terminal or exactly two non-terminals, by introducing fresh non-terminals for terminals appearing in long productions and for the chained binary breakdown of productions longer than two symbols.

## Objectives

* Implement a `Grammar` class that stores a context-free grammar and provides methods for each of the five normalization steps.
* Implement a method that runs the full pipeline and produces a grammar in CNF.
* Apply the implementation to the Variant 3 grammar and display the grammar after each step.
* Verify the final grammar satisfies the CNF restrictions through an `is_cnf()` check.
* Bonus: ensure the methods work on any input grammar, not only the variant.

## Implementation Description

### Grammar Class

The `Grammar` class stores the four components V_n, V_t, P, and S. Productions are kept as a dictionary mapping each non-terminal to a list of right-hand sides, where each right-hand side is itself a list of symbols. An ε production is represented as an empty list. The `display()` method prints the grammar with productions numbered globally, starting from the start symbol.

```python
def __init__(self, V_n, V_t, P, S):
    self.V_n = set(V_n)
    self.V_t = set(V_t)
    self.P = {nt: [list(prod) for prod in prods] for nt, prods in P.items()}
    self.S = S
```

### Step 1: Eliminate ε Productions

The method first computes the set of nullable non-terminals. A non-terminal is nullable if it has a direct ε production, or if all symbols of one of its right-hand sides are themselves nullable. The fixed point is reached by iterating until no new nullable symbols are added. Then for each production, every non-empty subset of nullable positions is generated, producing all combinations with those nullable symbols removed. Empty productions are dropped at the end.

```python
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
```

### Step 2: Eliminate Renaming

A unit production (also called renaming) has the form X → Y where Y is a single non-terminal. The method computes, for each non-terminal X, the set of non-terminals reachable from X through chains of unit productions. Each X then receives all non-unit productions of every non-terminal in its reachable set, and unit productions are dropped.

```python
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
```

### Step 3: Eliminate Inaccessible Symbols

A non-terminal is accessible if it appears in some derivation starting from S. The method does a forward search from S through all productions, marking every non-terminal it encounters. Any non-terminal not marked is inaccessible and removed along with all its productions.

```python
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
```

### Step 4: Eliminate Non-productive Symbols

A non-terminal is productive if it can derive a string consisting only of terminals. The method computes the set of productive non-terminals iteratively: a non-terminal becomes productive once one of its productions has all symbols either terminal or already productive. Non-productive non-terminals are removed, and any production containing a non-productive symbol is also dropped.

```python
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
```

### Step 5: Convert to CNF

The final step has two passes. The first pass replaces every terminal that appears in a production of length 2 or more with a fresh non-terminal X_i, and adds the production X_i → terminal. The second pass breaks productions of length 3 or more into chained binary productions by introducing fresh non-terminals Y_i. Identical right-hand-side suffixes share the same Y to keep the result compact.

```python
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
```

### Variant 3 Grammar Definition

The grammar assigned to Variant 3 is:

```
V_n = {S, A, B, C, E}
V_t = {a, d}
P:
  1. S -> dB
  2. S -> A
  3. A -> d
  4. A -> dS
  5. A -> aAdAB
  6. B -> aC
  7. B -> aS
  8. B -> AC
  9. C -> ε
  10. E -> AS
```

The order of normalization steps follows the variant statement: ε-elimination, renaming elimination, inaccessible-symbol elimination, non-productive-symbol elimination, and finally CNF transformation.

## Conclusions / Screenshots / Results

Running `run_variant_3()` produces the following output, with the grammar shown after each transformation step.

```
--- Initial Grammar ---
P:
  1. S -> dB
  2. S -> A
  3. A -> d
  4. A -> dS
  5. A -> aAdAB
  6. B -> aC
  7. B -> aS
  8. B -> AC
  9. C -> ε
  10. E -> AS

--- After Step 1: Eliminate epsilon productions ---
P:
  1. S -> dB
  2. S -> A
  3. A -> d
  4. A -> dS
  5. A -> aAdAB
  6. B -> aC
  7. B -> a
  8. B -> aS
  9. B -> AC
  10. B -> A
  11. E -> AS

--- After Step 2: Eliminate renaming ---
P:
  1. S -> d
  2. S -> dS
  3. S -> aAdAB
  4. S -> dB
  5. A -> d
  6. A -> dS
  7. A -> aAdAB
  8. B -> aC
  9. B -> a
  10. B -> aS
  11. B -> AC
  12. B -> d
  13. B -> dS
  14. B -> aAdAB
  15. E -> AS

--- After Step 3: Eliminate inaccessible symbols ---
V_n = {A, B, C, S}
(E and its production E -> AS are removed)

--- After Step 4: Eliminate non-productive symbols ---
V_n = {A, B, S}
(C has no productions and is non-productive; B -> aC and B -> AC are also removed)

--- After Step 5: Chomsky Normal Form ---
V_n = {A, B, S, X1, X2, Y1, Y2, Y3}
P:
  1. S -> d
  2. S -> X2S
  3. S -> X1Y1
  4. S -> X2B
  5. A -> d
  6. A -> X2S
  7. A -> X1Y1
  8. B -> a
  9. B -> X1S
  10. B -> d
  11. B -> X2S
  12. B -> X1Y1
  13. X1 -> a
  14. X2 -> d
  15. Y1 -> AY2
  16. Y2 -> X2Y3
  17. Y3 -> AB

Is in CNF: True
```

The final grammar contains 17 productions and 8 non-terminals. Every production matches one of the two CNF forms: a single terminal on the right side, or two non-terminals. The `is_cnf()` check confirms this programmatically.

## Conclusions

The lab demonstrated that a context-free grammar can be normalized into Chomsky Normal Form through a sequence of independent transformations, each preserving the language defined by the grammar. Encapsulating each step in its own method made the pipeline easy to inspect and debug, since the grammar can be printed after every step and compared against a manual trace.

The implementation is general. The same `Grammar` class accepts any input grammar through its constructor, and `to_cnf()` runs the full pipeline regardless of which non-terminals or terminals the input uses. This satisfies the bonus requirement.

The main difficulty was the order of removal steps. The variant lists inaccessible-symbol removal before non-productive-symbol removal, which differs from the example in the lab handout. For Variant 3, both orders produce the same final grammar, but in general a stricter implementation would re-run the accessibility check after non-productive removal to catch symbols that became unreachable when their only path was through a removed non-productive non-terminal. Adding a second cleanup pass would handle this edge case.

## References

1. Hopcroft, J., Motwani, R., Ullman, J. - *Introduction to Automata Theory, Languages, and Computation*, 3rd edition, Pearson, 2006.
2. Sipser, M. - *Introduction to the Theory of Computation*, 3rd edition, Cengage Learning, 2012.
3. Chomsky Normal Form - Wikipedia. https://en.wikipedia.org/wiki/Chomsky_normal_form
4. Course materials for Formal Languages & Finite Automata, Technical University of Moldova.