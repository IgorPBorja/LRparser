import typing as T
import tabulate


class DFA:
    """
        DFA implementation with minimization method.

        States are always numbered starting from 0 to (total of states - 1).
    """

    def __init__(self,
                 num_states: int,
                 symbols: T.Sequence[str],
                 transition_table: T.Dict[int, T.Dict[str, T.Optional[int]]],
                 accepting_states: T.Iterable[int],
                 start: int = 0):
        """
            @param
                states [int]: determine the number of states
                symbols [sequence[str]]: list of symbols for the underlying alphabet
                transition_table [dict[int, dict[str, int]]: description of the transition function as a table/hashmap
                    transition_table[s][a] is the next state when processing 'a' from state 's'
                accepting_states [iterable[int]]: container detailing all the accepting states
                start [int]: initial state
                    Default: 0

            If there is not edge leaving s reading symbol a, it is accepted to either leave the key (s, a) missing or set transition_table[s][a] to None. Either way, the constructor will fill the missing spots on the table with None.
        """
        # fill table
        for state in range(num_states):
            for symb in symbols:
                if symb not in transition_table[state]:
                    transition_table[state][symb] = None

        self.num_states = num_states
        self.states = list(range(num_states))
        self.symbols = symbols
        self.transition_table = transition_table
        self.accepting_states = accepting_states
        self.is_accepting = [False for i in range(num_states)]
        for acc in accepting_states:
            self.is_accepting[acc] = True
        self.start = start

    def lazy_process(self, sequence: T.Iterable[str]) -> T.Generator[T.Optional[int], None, None]:
        """
            Processes a sequence lazily, returning a generator

            @param:
                sequence: Iterable[str]
            @return
                generator yielding the states obtained when processing the string, in order. Skips the initial state
                Will yield None when trying to walk non-existent transition. If there are any iterations after that, there will be a error raised.
        """
        state: int = self.start
        for char in sequence:
            if self.transition_table[state][char] is None:
                yield None
                return
            else:
                state = self.transition_table[state][char]
                yield state

    def process(self, sequence: T.Iterable[str]):
        """
            Processes a sequence entirely, returning the final state
            @param:
                sequence: Iterable[str]
            @return:
                final state: int
        """
        state = self.start
        for char in sequence:
            if self.transition_table[state][char] is None:
                raise RuntimeError(f"No transition registered from state {state} reading symbol '{char}'")
            state = self.transition_table[state][char]
        return state

    def accepts(self, sequence: T.Iterable[str]) -> bool:
        """
            Returns whether the sequence is accepted by the DFA
            @param:
                sequence: Iterable[str]
            @return:
                bool
        """
        return self.is_accepting[self.process(sequence)]

    def remove_unreachable(self) -> "DFA":
        """
            Creates a new DFA removing all unreachable (relative to the initial state) states from the original DFA

            Implements an iterative DFS for searching the DFA graph.
            Complexity: O(nk) where n is the number of states and k is the size of the alphabet

            @returns:
                New DFA, containing only the reachable states, renumbered to form a contiguous sequence starting at 0.
        """
        reachable_status: T.List[bool] = [False for i in range(self.num_states)]
        reverse_symbol_list = reversed([s for s in self.symbols])
        search_stack = [self.start]
        while len(search_stack) > 0:
            curr = search_stack.pop()
            if reachable_status[curr]:
                continue
            reachable_status[curr] = True
            for char in reverse_symbol_list:
                if self.transition_table[curr][char] is not None:
                    search_stack.append(self.transition_table[curr][char])

        reachable = [s for s in range(self.num_states) if reachable_status[s]]
        new_accepting = [s for s in reachable if self.is_accepting[s]]
        new_transition_table: T.Dict[int, T.Dict[str, T.Optional[int]]] = {s: dict() for s in range(len(reachable))}
        renumbering_mapping: T.Dict[int, int] = {}
        for i, s in enumerate(reachable):
            renumbering_mapping[s] = i
        for state in reachable:
            for symb in self.symbols:
                new_transition_table[renumbering_mapping[state]][symb] = self.transition_table[state][symb]
        return DFA(len(reachable), self.symbols, new_transition_table, new_accepting, self.start)

    def _hopcroft_minimize(self) -> "DFA":
        """
            Implements Hopcroft (1971) minimization algorithm.

            Uses DSU to merge states.
        """
        # TODO implement
        # TODO analyze complexity
        pass

    def minimize(self, strategy: str = "hopcroft") -> "DFA":
        """
            Returns the minimized DFA using the minimization algorithm given the the 'strategy' param.
            @param:
                strategy [str]: algorithm to use
                    Accepted strategies: hopcroft
                    All others raise NotImplementedError
        """
        if strategy == "hopcroft":
            return self._hopcroft_minimize()
        else:
            raise NotImplementedError(f"Invalid minimization algorithm '{strategy}'")

    def __str__(self) -> str:
        """
            Returns transition table (as string)
            Rows are state numbers, colums are symbols
        """
        table_data = [["States", *self.symbols]]
        for s in self.states:
            row_data = [s] + [self.transition_table[s][a] for a in self.symbols]
            table_data.append(row_data)
        return tabulate.tabulate(table_data, headers='firstrow')
