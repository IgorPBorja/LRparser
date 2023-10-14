import re
import typing as T
from grammar import Grammar

word_pattern : str = r"^[a-zA-Z_][a-zA-Z_0-9]*$"

def check_pattern(rule_words: T.List[str],
                  rule_separator: str = '->',
                  or_clause: str = '|') -> bool:
    if (len(rule_words) < 3):
        return False
    
    match : bool = ( (re.match(word_pattern, rule_words[0])) is not None )
    match = match and (rule_words[1] == rule_separator)
    for i in range(2, len(rule_words)):
        match = match and ( (re.match(word_pattern, rule_words[i]) 
                           or rule_words[i] == or_clause) is not None )
    return match

def parse_file(filepath: str, 
               rule_separator : str = "->",
               or_clause: str = '|') -> Grammar:
    grammar : T.Dict[str, T.List[str]] = dict()
    start : str = ""

    with open(filepath, 'r') as f:
        for line in f.readlines():
            words = line.split() ## split on white space
            words = [w for w in words if w != '']
            
            if (words != [] and (not check_pattern(words, rule_separator, or_clause))):
                raise ValueError(
                    f"In line '{line.strip()}' \n\
                        Wrong format: each line must be either empty or \
                        of the format 'word -> word1 | word2 | ... | wordn")
            
            ## now we are sure the format is right
            ## unite on or_clause
            right_side : T.List[str] = ' '.join(words[2:]).split(or_clause)
            right_side = [r.strip() for r in right_side] ## remove whitespace
        
            if (words != [] and start == ""):
                start = words[0]
            if (words != [] and not (words[0] in grammar)):
                grammar[words[0]] = [] ## create new key
            for i in range(len(right_side)):
                grammar[words[0]].append(right_side[i])
    
    ## remove duplicates
    grammar_unique_keys: T.Dict[str, T.Set[str]] = {}
    for var in grammar:
        grammar_unique_keys[var] = set(grammar[var])
    
    return Grammar(grammar_unique_keys, start)