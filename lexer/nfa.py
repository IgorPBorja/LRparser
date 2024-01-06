import typing as T
from lexer.dfa import DFA
import tabulate


class NFA:
    """
        epsilon-NFA (NFA with empty transitions) class.

        States are always numbered starting from 0 to (total of states - 1).

        Implements conversion method to DFA.
    """

    def __init__(self,
                 num_states: int,
                 symbols: T.Sequence[str],
                 transition_table: T.Dict[T.Tuple[int, str], T.Iterable[int]],
                 accepting_states: T.Iterable[int],
                 start: int = 0):
        # fill table
        for state in range(num_states):
            for symb in ['', *symbols]:
                if (state, symb) not in transition_table:
                    transition_table[state, symb] = set()

        self.num_states = num_states
        self.states = list(range(num_states))
        self.symbols = symbols
        self.transition_table = transition_table
        self.accepting_states = accepting_states
        self.is_accepting = [False for i in range(num_states)]
        for acc in accepting_states:
            self.is_accepting[acc] = True
        self.start = start

    def epsilon_closure(self, states: T.Iterable[int]) -> T.Set[int]:
        """
            Given a set S of states, calculate the epsilon closure E(S)

            E(S) := U E_k(S) over k >= 0
            where E_0 = S and E_{k + 1} := E_{k} U {transition_table[t, epsilon], t in E_{k}}. Implements this using an iterative DFS

            Complexity: O(n + m) (assuming iteration over states is linear), where n is the number of states and m is the number of epsilon-edges
                m = sum(s is a state) |transition_table[s, epsilon]|
        """
        epsilon = ''
        visited: T.List[bool] = [False for i in range(self.num_states)]
        search_stack = [s for s in states]
        while len(search_stack) > 0:
            s = search_stack.pop()
            if visited[s]:
                continue
            visited[s] = True
            for t in self.transition_table[s, epsilon]:
                if not visited[t]:  # optimization: do no t push visited states
                    search_stack.append(t)
        return set([s for s in range(self.num_states) if visited[s]])

    def step(self, states: T.Iterable[int], symbol: str) -> T.Set[int]:
        """
            Given a set of states S, and a input symbol a, not equal to the empty string, returns the epsilon closure of the set
                S_a = {transition_table[s, a] for s in S}

            Complexity: O(n + m)
            More precisely: O(sum |transition_table[s, a]| for s in S) (which is O(m)) + O(n + m), where n is the number of states and m is the number of total edges
        """
        if symbol == '':
            raise ValueError("Target symbol in step function cannot be the empty string")
        states_after_symbol: T.Set[int] = set()
        for s in states:
            states_after_symbol = states_after_symbol.union(self.transition_table[s, symbol])
        return self.epsilon_closure(states_after_symbol)

    def process(self, sequence: T.Iterable[str]) -> T.Set[int]:
        """
            Processes a sequence entirely, returning the set of possible final states

            @param:

                sequence: Iterable[str]: input sequence of tokens/chars
            @return:
                possible final states: Set[int]

            Complexity: O(k * (n + m)), where k is the size of the input sequence, n is the number of states and m is the total number of edges.
        """
        curr_possible_states = self.epsilon_closure({self.start})
        for char in sequence:
            curr_possible_states = self.step(curr_possible_states, char)
        return curr_possible_states

    def lazy_process(self, sequence) -> T.Generator[T.Set[int], None, None]:
        """
            Processes a sequence lazily, returning a generator that yield each set of possible current states (at each symbol processed)

            @param:

                sequence: Iterable[str]: input sequence of tokens/chars
            @return:
                a generator that yield Set[int] elements

            Complexity: O(k * (n + m)), where k is the size of the input sequence, n is the number of states and m is the total number of edges.
        """
        curr_possible_states = self.epsilon_closure({self.start})
        yield curr_possible_states
        for char in sequence:
            curr_possible_states = self.step(curr_possible_states, char)
            yield curr_possible_states

    def accepts(self, sequence: T.Iterable[str]) -> bool:
        """
            Returns whether the sequence is accepted by the DFA
            @param:
                sequence: Iterable[str]
            @return:
                bool
        """
        return any(self.is_accepting[x] for x in self.process(sequence))

    def toDFA(self) -> DFA:
        """
            Returns an equivalent DFA using the standard conversion procedure based on representing subsets of states in the NFA as single states in the new DFA.

            Performs a DFS starting from the unit set containing the starting state, and stepping using each possible symbol.

            @param: None
            @return:
                DFA instance that recognizes the same language
        """
        # this DFS works in two stages
        # 1. looking at stage (which implies numbering it)
        # 2. visiting stage / stepping into it (which implies marking as visited)
        # this is so we can write transition rules to states we haven't visited yet, just looked via their neighbors
        reachable_subsets_stack: T.List[T.FrozenSet[int]] = [frozenset({self.start})]
        idx_table: T.Dict[T.FrozenSet[int], int] = dict()
        visited_table: T.Dict[T.FrozenSet[int], bool] = dict()
        dfa_transition_table: T.Dict[T.Tuple[int, str], int] = dict()

        idx_table[reachable_subsets_stack[-1]] = 0  # we start looking at the start state
        curr_idx = 1
        reverse_symbol_list = reversed(self.symbols)  # just so the DFS tree is consistent with the order of symbols provided
        while len(reachable_subsets_stack) > 0:
            curr_subset = reachable_subsets_stack.pop()
            if visited_table[curr_subset]:
                continue
            visited_table[curr_subset] = True
            for symb in reverse_symbol_list:
                next_subset = frozenset(self.step(curr_subset, symb))  # freeze set to make it hashable
                if next_subset not in idx_table:
                    # looking at for the first time -> number it
                    idx_table[next_subset] = curr_idx
                    curr_idx += 1
                # mark the transition on the new table
                dfa_transition_table[idx_table[curr_subset], symb] = idx_table[next_subset]
                reachable_subsets_stack.append(next_subset)

    def __str__(self) -> str:
        """
            Returns transition table (as string)
            Rows are state numbers, colums are symbols.
        """
        table_data = [["States", *self.symbols]]
        for s in self.states:
            row_data = [s] + [self.transition_table[s, a] for a in self.symbols]
            table_data.append(row_data)
        return tabulate.tabulate(table_data, headers='firstrow')
