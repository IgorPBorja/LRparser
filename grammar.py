class Grammar:
    def __init__(self,
                 grammar: dict[str, set[str]],
                 start: str):
        """

        Args:
            grammar (dict[str, set[str]]): 
                the dictionary of grammar productions
                
        NOTE: any symbol not in the left hand of any rule is considered a terminal 
        """
        
        self.symbols : set[str] = set()
        self.terminals : set[str] = set()
        self.vars : set[str] = set()
        self.raw_grammar : dict[str, set[str]] = grammar
        self.grammar : dict[str, set[tuple[str]]] = dict()
        for A in self.raw_grammar:
            if A not in self.grammar:
                self.grammar[A] = set()
            for raw_word in self.raw_grammar[A]:
                self.grammar[A].add(tuple(raw_word.split()))
            
        self.start = start
        
        for A, right_side in self.grammar.items():
            self.symbols.add(A)
            self.vars.add(A)
            for word in right_side:
                for symbol in word:
                    self.symbols.add(symbol)
        self.terminals = self.symbols.difference(self.vars)
        if '' in self.terminals:
            self.terminals.remove('')
        
    def __str__(self,
            rule_separator: str = "->",
            or_clause:  str = "|",
            *,
            separate_rules: bool = False,
            use_epsilon_unicode: bool = True):
        s = ""
        if (separate_rules):
            for A in self.raw_grammar:
                for w in self.raw_grammar[A]:
                    if (w != '' or not use_epsilon_unicode):
                        s += f"{A} {rule_separator} {w}\n"
                    else:
                        s += f"{A} {rule_separator} \u03B5\n"
        else:
            for A in self.raw_grammar:
                right_side : set[str] = self.raw_grammar[A]
                if (use_epsilon_unicode and '' in right_side):
                    right_side.remove('')
                    right_side.add("\u03B5")
                s += f"{A} {rule_separator} " \
                    f"{(' ' + or_clause + ' ').join(right_side)}\n"
        return s.strip()
