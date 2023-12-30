import typing as T
import copy
from grammar import Grammar

# P[v] = set of all productions v -> a
PRODUCTION_TABLE = T.Dict[str, T.Set[T.Tuple[str, ...]]]
# P[s, v] = set of all productions v -> a.sb (s is the lookahead)
LOOKAHEAD_TABLE = T.Dict[T.Tuple[str, str], T.Set[T.Tuple[str, ...]]]


class Abstract_LR0_State:
    """
        Abstract LR0 state, not vinculated to any grammar.
    """

    def __init__(self,
                 id: int,
                 productions: LOOKAHEAD_TABLE):
        self.id = id
        self.productions = productions

    def __str__(self,
                rule_separator: str = '->',
                or_clause: str = '|'):
        s = ""
        for (symb, var), word_list in self.productions.items():
            if (word_list == set()):
                continue
            for word in word_list:
                s += f"{var} {rule_separator} "
                s += f"{' '.join(word)}\n"
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # compare only non-empty entries
        # so if a pair (symb, var) maps to an empty set, it is desconsidered
        def clean_dict(d):
            return {a: b for a, b in d.items() if len(b) != 0}
        return clean_dict(self.productions) == clean_dict(other.productions)


class LR0_State(Abstract_LR0_State):
    """
        This class represents an state of an LR0 automaton.

        The respective productions 'P' are represented as a
        dict[tuple[str, str], set[tuple[str]]],
        where for each symbol 's' (variable or terminal or empty)
        and each variable X

        P[s, X] = set of productions of the form X -> a.sb
    """

    @staticmethod
    def __closure_step(
            transition: T.Tuple[str, T.Tuple[str, ...]],
            grammar: Grammar,
            current_productions: LOOKAHEAD_TABLE,
            first_set: T.Dict[str, T.Set[str]],
            indicator: str = '.') -> LOOKAHEAD_TABLE:
        """
            This simply calculates the closure of a production of the form v -> x0x1...x[i].x[i+1]...x[n-1]

            for (j=i+1...n-1)
                if epsilon in first(x[i+1]...x[j]) / derives epsilon
                    add all productions x[i + 1] -> alpha with a prepended dot (x[i+1] -> .alpha)

            This makes it possible to accept grammar with epsilon transitions.
        """
        var, word = transition
        lookahead_pos = word.index(indicator) + 1
        nullable = [('' in first_set[x]) for x in word[lookahead_pos:]]
        for i in range(lookahead_pos, len(word)):
            prepended_dot_word = tuple((indicator, *(word[i + 1:])))
            if all(nullable[: i - lookahead_pos]) and word[i] in grammar.vars:
                for new_target_word in grammar.grammar[word[i]]:
                    lookahead = '' if len(new_target_word) == 0 else new_target_word[0]
                    prepended_dot_word = (indicator, *new_target_word)
                    if (lookahead, word[i]) not in current_productions:  # safe add
                        current_productions[lookahead, word[i]] = {prepended_dot_word}
                    else:
                        current_productions[lookahead, word[i]].add(prepended_dot_word)
        if all(nullable):
            current_productions['', var].add((indicator,))
        return current_productions

    @staticmethod
    def __closure_LR0(grammar: Grammar,
                      productions: LOOKAHEAD_TABLE,
                      first_set: T.Dict[str, T.Set[str]],
                      indicator: str) -> LOOKAHEAD_TABLE:
        converged = False
        while (not converged):
            converged = True
            # so it does not change along with the production lookahead table
            old_productions_dict = copy.deepcopy(productions)  # FIXME?
            for ((lookahead, var), possible_targets) in old_productions_dict.items():
                if (lookahead not in grammar.vars):
                    continue
                for word in possible_targets:
                    productions = LR0_State.__closure_step(
                        (var, word),
                        grammar,
                        productions,
                        first_set,
                        indicator
                    )
            if (productions != old_productions_dict):
                converged = False
        return productions

    def __init__(self,
                 grammar: Grammar,
                 start_productions: LOOKAHEAD_TABLE,
                 id: int,
                 first_set: T.Dict[str, T.Set[str]],
                 follow_set: T.Dict[str, T.Set[str]],
                 indicator: str = '.'):
        self.id = id
        self.first_set = first_set
        self.follow_set = follow_set

        self.productions = LR0_State.__closure_LR0(
            grammar,
            start_productions,
            first_set,
            indicator
        )


class Abstract_LR0_Automaton:
    """
        Abstract LR0 Automaton, not vinculated to any grammar.
    """

    def __init__(self,
                 indicator: str = '.',
                 eof_symbol: str = '$'):
        self.states: T.List[Abstract_LR0_State] = []
        self.accepting: T.Set[int] = set()
        self.transition_table: T.List[T.Dict[str, T.Optional[int]]] = []
        self.indicator: str = indicator
        self.eof_symbol = eof_symbol

    def display_table(self,
                      horizontal_separator: str = "|",
                      vertical_separator: str = "-") -> str:
        """
            Displays graphical representation of transition table
        """
        grammar_symbols = set()  # only the usable grammar symbols
        for row in self.transition_table:
            for symb in row:
                grammar_symbols.add(symb)

        width: int = max(len(str(s.id)) for s in self.states)
        width = max(width, max(len(symb) for symb in grammar_symbols))
        lines: T.List[str] = []

        # top line
        top: str = (width + 1) * " "
        for symb in grammar_symbols:
            top += horizontal_separator
            top += symb.center(width + 1, " ")
        lines.append(top)
        # normal lines
        for state in self.states:
            lines.append((len(lines[-1]) // len(vertical_separator)) * vertical_separator)
            curr_line: str = str(state.id).center(width + 1, " ")
            for symb in grammar_symbols:
                new_state_id: T.Optional[int] = self.transition_table[state.id][symb]
                curr_line += horizontal_separator
                if new_state_id is not None:
                    curr_line += str(new_state_id).center(width + 1, " ")
                else:
                    curr_line += (width + 1) * " "
            lines.append(curr_line)
        return '\n'.join(lines)

# TODO add support for epsilon transitions


class LR0_Automaton(Abstract_LR0_Automaton):
    """
        LR0 Automaton built from an specific (provided) grammar.
    """

    def build(self,
              state: LR0_State):
        """
            Given a state t of the LR0,
            for each symbol s,
                for each rule that has s as lookahead in state t (v -> a.sb)
                    create a new state t' with all corresponding rules v -> as.b and their closure, and make t point to t'
                    if this state t' already exists, delete this copy and make t point to the already existing state instead
        """
        for s in self.grammar.symbols:
            new_productions: LOOKAHEAD_TABLE = dict()
            for v in self.grammar.vars:
                if ((s, v) not in state.productions):
                    continue
                # look at all productions v -> a.sb
                # and create a state with the corresponding v -> as.b
                for word in state.productions[(s, v)]:
                    idx = word.index(self.indicator)
                    new_word: list[str] = list(word)  # turn mutable
                    new_word[idx] = word[idx + 1]
                    new_word[idx + 1] = self.indicator
                    ref_symbol = '' if idx + 2 == len(new_word) else new_word[idx + 2]
                    if ((ref_symbol, v) not in new_productions):
                        new_productions[(ref_symbol, v)] = set()
                    new_productions[(ref_symbol, v)].add(tuple(new_word))

            # now all next productions were generated using s as lookahead
            new_state = LR0_State(
                grammar=self.grammar,
                start_productions=new_productions,
                id=len(self.states),
                first_set=self.first,
                follow_set=self.follow
            )

            # if there was no rules with a specific lookahead symbol, the generated new state will be empty, so we need to consider this new case

            if (len(new_state.productions) == 0):
                continue

            if (not (new_state in self.states)):
                # no state with the same exact productions
                self.states.append(new_state)
                # empty dictionary line
                self.transition_table.append(dict({t: None for t in self.grammar.symbols}))
                self.transition_table[state.id][s] = new_state.id
            else:
                idx = self.states.index(new_state)
                self.transition_table[state.id][s] = self.states[idx].id

    def __init__(self,
                 grammar: Grammar,
                 indicator: str = '.',
                 eof_symbol: str = '$'):
        super().__init__(indicator, eof_symbol)
        self.states: T.List[LR0_State] = []
        self.grammar = grammar
        self.first = grammar.first()
        self.follow = grammar.follow(self.first)

        # BUILD START LOOKAHED TABLE for start state
        start_productions: LOOKAHEAD_TABLE = dict()
        for s in grammar.symbols:
            start_productions[(s, grammar.start)] = set()
        start_productions[('', grammar.start)] = set()

        for symbol_list in grammar.grammar[grammar.start]:
            if len(symbol_list) > 0:
                start_productions[(symbol_list[0], grammar.start)].add(
                    tuple((indicator, *symbol_list))
                )
            else:
                start_productions['', grammar.start].add(tuple(indicator,))

        self.states.append(LR0_State(grammar,
                                     start_productions,
                                     0,
                                     self.first,
                                     self.follow,
                                     indicator))
        self.transition_table.append(dict({s: None for s in self.grammar.symbols}))
        self.start_state = self.states[0]

        # the while loop accounts for the fact that
        # the states list is changing mid-loop
        i = 0
        while (i < len(self.states)):
            self.build(self.states[i])
            i += 1

        # build transitions to accept state
        for state in self.states:
            for (_, var), possible_targets in state.productions.items():
                for word in possible_targets:
                    if (var == self.grammar.start and word[-1] == self.indicator):
                        self.accepting.add(state.id)
