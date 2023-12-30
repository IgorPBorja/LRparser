import warnings
import typing as T
from parsers.LR0 import LR0_Automaton
from grammar import Grammar
from utils.AST import AST

TRANSITION = T.Tuple[str, T.Tuple[str, ...]]
ACTION_TABLE = T.Dict[T.Tuple[int, str], T.Union[T.Optional[int], TRANSITION]]
GOTO_TABLE = T.Dict[T.Tuple[int, str], T.Optional[int]]


class SLR_Parser:
    def _identify_action_conflicts(self,
                                   entry: T.Tuple[int, str],
                                   new_value: T.Union[int, TRANSITION],
                                   action_table: ACTION_TABLE) -> bool:
        """
            Identify possible conflicts when processing new rule in state. Raise error in case of reduce-reduce conflict. Give a warning in case of shift-reduce error. Returns true only if there was a shift-reduce conflict.
        """
        if action_table[entry] is None:
            return False
        elif isinstance(action_table[entry], int):
            if isinstance(new_value, int) and action_table[entry] == new_value:
                return False
            elif isinstance(new_value, int) and action_table[entry] != new_value:
                raise RuntimeError(f"Shift-shift conflict on state {entry[0]} for lookahead token '{entry[1]}': can't decide between states {action_table[entry]} (current) and {new_value} (new). This should not happen when using this function with a correctly built automaton, you might want to post a github issue on https://github.com/IgorPBorja/LRparser.")
            elif isinstance(new_value, tuple):
                var, word = new_value
                warning_text = f"Shift-reduce conflict on lookahead {entry[1]}: defaulting to reduce action {var} -> {' '.join(word)} (new)."
                warnings.warn(warning_text, UserWarning)
                return True
            else:
                raise RuntimeError(f"Unexpected type for new value: {type(new_value)}")  # FIXME remove
        elif isinstance(action_table[entry], tuple):
            if isinstance(new_value, int):
                var, word = action_table[entry]
                warning_text = f"Shift-reduce conflict on lookahead {entry[1]}: defaulting to reduce action {var} -> {' '.join(word)} (current)."
                warnings.warn(warning_text, UserWarning)
                return True
            elif isinstance(new_value, tuple):
                var1, word1 = action_table[entry]
                var2, word2 = new_value
                if (var1 != var2 or word1 != word2):
                    error_text = f"Reduce-reduce conflict: options of actions {var1} -> {' '.join(word1)} (current) or {var2} -> {' '.join(word2)} (new)"
                    raise ValueError(error_text)
            else:
                raise RuntimeError(f"Unexpected type for new value: {type(new_value)}")  # FIXME remove
        else:
            raise RuntimeError(f"Unexpected type for current entry: {type(action_table[entry])}")  # FIXME remove

    def _identify_goto_conflicts(self,
                                 entry: T.Tuple[int, str],
                                 new_value: int,
                                 goto_table: GOTO_TABLE):
        if (goto_table[entry] is not None) and (goto_table[entry] != new_value):
            raise RuntimeError(f"Shift-shift conflict on state {entry[0]} for lookahead token '{entry[1]}': can't decide between states {goto_table[entry]} (current) and {new_value} (new). This should not happen when using this function with a correctly built automaton, you might want to post a github issue on https://github.com/IgorPBorja/LRparser.")

    def build_table(self) -> T.Tuple[ACTION_TABLE, GOTO_TABLE]:
        """
            Builds the SLR ACTION and GOTO parsing table in the following way

            given state s and its rules
                for all state rules A -> a.xb for terminal x:
                    add the corresponding shift to ACTION[s, a]
                for all state rules A -> a.
                    for all terminals b in FOLLOW(a)
                        add the corresponding rule A -> a to ACTION[s, b]
                for all state rules A -> a.Xb for variable X:
                    add the corresponding goto rule to GOTO[s, X]

            @returns:
                ACTION: Dict[Tuple[int, str], Union[int, TRANSITION]]: maps a pair (state_id, token) to a action (if integer, goto state with this new id, else reduce by rule given)
                GOTO: Dict[Tuple[int, str], int]: maps a pair (state_id, variable) to the id of the next state
        """
        action_table: ACTION_TABLE = {}
        goto_table: GOTO_TABLE = {}
        # prefill tables
        for state in self.automaton.states:
            for var in self.grammar.vars:
                goto_table[state.id, var] = None
            for terminal in self.grammar.terminals:
                action_table[state.id, terminal] = None
            action_table[state.id, self.eof_symbol] = None

        for state in self.automaton.states:
            id = state.id
            for lookahead in self.grammar.symbols:
                for var in self.grammar.vars:
                    if ((lookahead, var) not in state.productions or len(state.productions[lookahead, var]) == 0):  # FIXME impose consistent behavior
                        continue
                    if lookahead in self.grammar.terminals:  # shift
                        next_state_id = self.automaton.transition_table[id][lookahead]
                        if next_state_id is None:
                            raise RuntimeError(f"Unexpected error, in state {id} with lookahead {lookahead} transition table shows nothing, even though a rule exists.")
                        conflict = self._identify_action_conflicts((id, lookahead), next_state_id, action_table)
                        if (not conflict):
                            action_table[id, lookahead] = next_state_id

                    if lookahead in self.grammar.vars:  # goto
                        next_state_id = self.automaton.transition_table[id][lookahead]
                        if next_state_id is None:
                            raise RuntimeError(f"Unexpected error, in state {id} with lookahead {lookahead} transition table shows nothing, even though a rule exists.")
                        self._identify_goto_conflicts((id, lookahead), next_state_id, goto_table)
                        goto_table[id, lookahead] = next_state_id

            # lookahead == '' (which is not a grammar symbol)
            for var in self.grammar.vars:
                if ('', var) not in state.productions:
                    continue
                for word in state.productions['', var]:
                    for lookahead in self.follow[var]:

                        # iterate over reductions in the same state
                        self._identify_action_conflicts((id, lookahead), (var, word), action_table)  # FIXME what about the indicator (dot)
                        action_table[(id, lookahead)] = (var, word)

        return action_table, goto_table

    def __init__(self,
                 grammar: Grammar,
                 indicator='.',
                 eof_symbol='$'):
        # the indicator is internal to the LR0 automaton and does not need to be an attr
        self.grammar = grammar
        self.eof_symbol = eof_symbol
        self.automaton: LR0_Automaton = LR0_Automaton(grammar, indicator, eof_symbol)
        self.first = self.grammar.first()
        self.follow = self.grammar.follow(self.first)

        # build parse table
        self.action_table, self.goto_table = self.build_table()

    def _calculate_width_table_column(self) -> T.Tuple[int, int]:
        """
            Calculates the minimum width to fit all entries (as str representations) of the action and goto tables, respectively
        """
        action_table_maxW, goto_table_maxW = 4, 4  # so that at least "None" can fit
        for state in self.automaton.states:
            action_table_maxW = max(action_table_maxW, len(str(state.id)))
            goto_table_maxW = max(action_table_maxW, len(str(state.id)))
        for tok in self.grammar.symbols:
            action_table_maxW = max(action_table_maxW, len(tok))
            goto_table_maxW = max(action_table_maxW, len(tok))

        for (_, _), action in self.action_table.items():
            if (action is not None) and (not isinstance(action, int)):  # is reduce
                var, word = action
                reduce_repr = var + " -> " + " ".join(word)
                action_table_maxW = max(action_table_maxW, len(reduce_repr))
        return action_table_maxW, goto_table_maxW

    def repr_table(self) -> T.Tuple[str, str]:
        """
            Creates a visual representation of the tables ACTION and GOTO. We are careful to traverse the states in the same order (the order of index) so that merging these two tables into one is easier.
        """
        action_table_str, goto_table_str = "", ""
        action_table_maxW, goto_table_maxW = self._calculate_width_table_column()  # first, calculate max width needed
        ids = [state.id for state in self.automaton.states]
        # top row
        action_table_str += "".center(action_table_maxW) + "|"
        goto_table_str += "".center(goto_table_maxW) + "|"
        for var in self.grammar.vars:
            goto_table_str += var.center(goto_table_maxW) + "|"
        for tok in self.grammar.terminals:
            action_table_str += tok.center(action_table_maxW) + "|"
        action_table_str += self.eof_symbol.center(action_table_maxW) + "|"
        action_table_str += "\n"
        goto_table_str += "\n"

        for i in ids:
            action_table_str += str(i).center(action_table_maxW) + "|"
            goto_table_str += str(i).center(goto_table_maxW) + "|"
            for var in self.grammar.vars:
                goto_table_str += str(self.goto_table[i, var]).center(goto_table_maxW) + "|"
            for tok in self.grammar.terminals:
                if (self.action_table[i, tok] is None):
                    action_table_str += action_table_maxW * " " + "|"
                elif not isinstance(self.action_table[i, tok], tuple):
                    action_table_str += str(self.action_table[i, tok]).center(action_table_maxW) + "|"
                else:
                    var, word = self.action_table[i, tok]
                    action_table_str += f"{var} -> {' '.join(word)}".center(action_table_maxW) + "|"
            if self.action_table[i, self.eof_symbol] is None:
                action_table_str += action_table_maxW * " " + "|"
            elif isinstance(self.action_table[i, self.eof_symbol], tuple):
                var, word = self.action_table[i, self.eof_symbol]
                action_table_str += f"{var} -> {' '.join(word)}".center(action_table_maxW) + "|"
            else:
                raise RuntimeError("Unexpected error: parse table (with lookahead = EOF) has non-empty entry that is not a reduce action")
            action_table_str += "\n"
            goto_table_str += "\n"
        return action_table_str, goto_table_str

    def parse(self, stream: T.List[str]) -> T.Tuple[int, AST]:
        """
            Run SLR parsing algorithm over list of tokens.
            Return a tuple (status code, AST).
            Status code: 0 for sucessful parsing, -1 for Error
        """
        tok_list = stream.copy()
        tok_list.append(self.eof_symbol)
        ast_bottom_nodes = []
        state_stack = [0]
        ptr = 0
        tok = stream[0]
        while (True):
            s = state_stack[-1]
            if isinstance(self.action_table[s, tok], int):  # shift
                ast_bottom_nodes.append(AST(tok, []))
                state_stack.append(self.action_table[s, tok])
                tok = tok_list[ptr + 1]
                ptr += 1
            elif isinstance(self.action_table[s, tok], tuple):  # reduce
                var, word = self.action_table[s, tok]
                if (var == self.grammar.start and tok == self.eof_symbol):
                    return 0, AST(self.grammar.start, ast_bottom_nodes)  # accepting state, parse sucessful
                # pop states corresponding to rule A -> alpha
                reduce_size = len(word) - 1  # HACK: exclude indicator (dot)
                reduce_components = ast_bottom_nodes[-reduce_size:]
                for i in range(reduce_size):
                    state_stack.pop()
                    ast_bottom_nodes.pop()
                t = state_stack[-1]
                if self.goto_table[t, var] is None:
                    return -1, AST(-1, ast_bottom_nodes)  # parse unsucessful
                else:
                    state_stack.append(self.goto_table[t, var])
                    ast_bottom_nodes.append(AST(var, reduce_components))
            else:
                return -1, AST(-1, ast_bottom_nodes)  # parse unsucessful
