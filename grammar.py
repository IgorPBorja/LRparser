import typing as T

class Grammar:
    def __init__(self,
                 grammar: T.Dict[str, T.Set[str]],
                 start: str,
                 eof_symbol: str = "$"):
        """

        Args:
            grammar (dict[str, set[str]]): 
                the dictionary of grammar productions
            start (str):
                start variable
            eof_symbol (str):
                symbol for end of input
                
        NOTE: any symbol not in the left hand of any rule is considered a terminal 
        """
        
        ## TODO decide if epsilon should be symbol
        
        self.symbols : T.Set[str] = set()
        self.terminals : T.Set[str] = set()
        self.vars : T.Set[str] = set()
        self.raw_grammar : T.Dict[str, T.Set[str]] = grammar
        self.grammar : T.Dict[str, T.Set[T.Tuple[str, ...]]] = dict()
        for A in self.raw_grammar:
            if A not in self.grammar:
                self.grammar[A] = set()
            for raw_word in self.raw_grammar[A]:
                self.grammar[A].add(tuple(raw_word.split()))
            
        self.start = start
        self.eof_symbol = eof_symbol
        
        for A, right_side in self.grammar.items():
            self.symbols.add(A)
            self.vars.add(A)
            for word in right_side:
                for symbol in word:
                    self.symbols.add(symbol)
        self.terminals = self.symbols.difference(self.vars)
        if '' in self.terminals:
            self.terminals.remove('')
            self.symbols.remove('')
        
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
                right_side : T.Set[str] = self.raw_grammar[A]
                if (use_epsilon_unicode and '' in right_side):
                    right_side.remove('')
                    right_side.add("\u03B5")
                s += f"{A} {rule_separator} " \
                    f"{(' ' + or_clause + ' ').join(right_side)}\n"
        return s.strip()

    def first(self) -> T.Dict[str, T.Set[str]]:
        """
        Args:
            self: grammar object
        
        Algorithm:
            First(t) = [t] for all terminals
            For each grammar production A -> X1 ... XN
                if (epsilon in First(X1) and ... and epsilon in First(X(i-1)))
                    First(A) <- First(A) U First(Xi)
        """
        first : T.Dict[str, T.Set[str]] = dict()
        first[''] = set({''})
        for t in self.terminals:
            first[t] = set({t})
        ## pre-create all first sets for variables (as empty)
        for A in self.vars:
            first[A] = set()

        converged = False
        while (not converged):
            converged = True
            for A, possible_targets in self.grammar.items():
                for word in possible_targets:
                    old_first = first[A]
                    for i in range(len(word)):
                        if (all(['' in first[word[j]] for j in range(i)])):
                            first[A] = first[A].union(first[word[i]])
                    if (all(['' in first[x] for x in word])):
                        first[A].add('')
                    if (first[A] != old_first):
                        converged = False
        return first

    @staticmethod
    def first_fromword(word: T.Union[T.List[str], T.Tuple[str, ...]],
                    first: T.Dict[str, T.Set[str]]) -> T.Set[str]:
        """Generate First(W1W2 ... WN) where W1W2 ... WN is a list of symbols
        (either terminals/tokens or variables) 

        Args:
            word (list[str]): list of symbols
            first (dict[str, set[str]]): first set of all grammar symbols

        Returns:
            set[str]: first set of W1W2...WN
        Complexity (estimated):
            O(|word|^2 + sum first[Wi]) algorithm (naive approach)
        """
        F : T.Set[str] = set()
        for i in range(len(word)):
            if (all(['' in first[word[j]] for j in range(i)])):
                F = F.union(first[word[i]])
        if (all(['' in first[w] for w in word])):
            F.add('')
        return F

    def follow(self,
            first: T.Dict[str, T.Set[str]]) -> T.Dict[str, T.Set[str]]:
        """
        Args:
            self: grammar object
            first (dict[str, set[str]]): first set of all symbols in grammar
        
        Algorithm:  
            follow(S) <- ['$']
            do
                for A -> aBb productions
                    if '' not in first(b)
                        follow(B) <- follow(B) U first(b)
                    else
                        follow(B) <- follow(B) U (first(b) \ {''}) U follow(A)
            while changes occur
            
        Returns:
            dict[str, set[str]]: follow set of each nonterminal
        """
        follow : T.Dict[str, T.Set[str]] = dict()
        converged : bool = False
        
        ## pre-create all follow sets
        for A in self.vars:
            follow[A] = set()
            
        ## follow set of start variable starts with EOF symbol (end of input)
        follow[self.start] = set({self.eof_symbol})
        
        while (not converged):
            converged = True
            for A, possible_targets in self.grammar.items():
                for word in possible_targets:
                    for i, symb in enumerate(word):
                        if (not (symb in self.vars)):
                            continue
                        suffix = word[i+1:]
                        first_suffix = Grammar.first_fromword(suffix, first)

                        old_follow = follow[symb]
                        
                        if ('' in first_suffix):
                            first_suffix.remove('')
                            follow[symb] = follow[symb].union(first_suffix, follow[A])
                        else:
                            follow[symb] = follow[symb].union(first_suffix)
                        
                        if (follow[symb] != old_follow):
                            converged = False
        return follow
