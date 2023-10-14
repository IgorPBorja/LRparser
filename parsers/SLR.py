import typing as T
import copy
from grammar import Grammar

## P[v] = set of all productions v -> a
PRODUCTION_TABLE = T.Dict[str, T.Set[T.Tuple[str, ...]]]
## P[s, v] = set of all productions v -> a.sb (s is the lookahead)
LOOKAHEAD_TABLE = T.Dict[T.Tuple[str, str], T.Set[T.Tuple[str, ...]]]

class LR0_State:
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
        grammar: Grammar,
        var: str,
        current_productions: LOOKAHEAD_TABLE,
        indicator: str = '.') -> LOOKAHEAD_TABLE:
        """
            Given a variable v, add all productions v -> x WORD
            as v -> .x WORD
        """
        for word in grammar.grammar[var]:
            prepended_dot_word = tuple((indicator, *(word)))
            ref_symbol = word[0]
            if ((ref_symbol, var) not in current_productions):
                current_productions[(ref_symbol, var)] = set()   
            current_productions[(ref_symbol, var)].add(prepended_dot_word)
        return current_productions

    @staticmethod
    def __closure_LR0(grammar: Grammar,
                    productions: LOOKAHEAD_TABLE,
                    indicator: str) -> LOOKAHEAD_TABLE:
        converged = False
        while (not converged):
            converged = True
            ## so it does not change along with the production lookahead table
            old_productions_dict = copy.deepcopy(productions) ## FIXME?
            for (_, possible_targets) in old_productions_dict.items():
                for word in possible_targets:
                    idx = word.index(indicator)
                    if (idx == len(word) - 1 or 
                        (not word[idx + 1] in grammar.vars)):
                        continue
                    new_var = word[idx + 1]
                    productions = LR0_State.__closure_step(
                        grammar,
                        new_var,
                        productions,
                        indicator
                    )
            if (productions != old_productions_dict):
                converged = False
        return productions

    def __init__(self,
                 grammar: Grammar,
                 start_productions: LOOKAHEAD_TABLE,
                 id: int,
                 indicator: str = '.'):
        self.id = id
        self.productions = LR0_State.__closure_LR0(
            grammar, 
            start_productions, 
            indicator
        )
    
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

    def __eq__(self, other):
        return self.productions == other.productions


## TODO add support for epsilon transitions

class LR0_Automaton:
    def build(self,
              state: LR0_State):
        for s in self.grammar.symbols: ## FIXME does not consider case s = epsilon
            new_productions : LOOKAHEAD_TABLE = dict()
            for v in self.grammar.vars:
                if ((s, v) not in state.productions):
                    continue
                ## look at all productions v -> a.sb
                ## and create a state with the corresponding v -> as.b
                for word in state.productions[(s, v)]:
                    idx = word.index(self.indicator)
                    new_word : list[str] = list(word) ## turn mutable
                    new_word[idx] = word[idx + 1]
                    new_word[idx + 1] = self.indicator
                    ref_symbol = '' if idx + 2 == len(new_word) else new_word[idx + 2]
                    if ((ref_symbol, v) not in new_productions):
                        new_productions[(ref_symbol, v)] = set()
                    new_productions[(ref_symbol, v)].add(tuple(new_word))

            ## now all next productions were generated using s as lookahead
            new_state = LR0_State(
                grammar=self.grammar,
                start_productions=new_productions,
                id=len(self.states)
            )

            ## if there was no rules with a specific lookahead symbol, the generated new state will be empty, so we need to consider this new case

            if (len(new_state.productions) == 0):
                return
            
            if (not (new_state in self.states)):
                ## no state with the same exact productions
                self.states.append(new_state)
                self.transition_table.append(dict({t: None for t in self.grammar.symbols})) ## empty dictionary list
                self.transition_table[state.id][s] = new_state.id
            else:
                self.transition_table[state.id][s] = self.states.index(new_state).id

    def __init__(self,
                 grammar: Grammar,
                 indicator: str = '.'):
        self.states : T.List[LR0_State] = []
        self.transition_table : T.List[T.Dict[str, T.Optional[int]]] = []
        self.indicator : str = indicator
        self.grammar = grammar

        start_productions : LOOKAHEAD_TABLE = dict()
        for s in grammar.symbols:
            start_productions[(s, grammar.start)] = set()
        for symbol_list in grammar.grammar[grammar.start]:
            start_productions[(symbol_list[0], grammar.start)].add(
                tuple((indicator, *symbol_list))
            )

        self.states.append(LR0_State(grammar, start_productions, 0, indicator))
        self.transition_table.append(dict({s: None for s in self.grammar.symbols}))

        ## the while loop accounts for the fact that
        ## the states list is changing mid-loop
        i = 0
        while (i < len(self.states)):
            self.build(self.states[i])
            i += 1