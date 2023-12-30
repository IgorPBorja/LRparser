import typing as T
from grammar import Grammar


def parse_file(filepath: str,
               rule_separator: str = "->",
               or_clause: str = '|') -> Grammar:
    grammar: T.Dict[str, T.Set[str]] = dict()
    start: str = ""

    with open(filepath, 'r') as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue
            if (len(line.strip()) != 0 and len(line.lstrip().split(rule_separator)) != 2):
                raise ValueError(f"In line '{line.lstrip()}' \n\
                        Wrong format: each line must be either empty or \
                        of the format 'word -> word1 | word2 | ... | wordn', where no word has either -> or '|'")
            var, raw_production = line.strip().split(rule_separator)  # split on white space
            var = var.strip()  # remove internal whitespace
            if start == "":
                start = var
            words = raw_production.split(or_clause)
            words = [w.strip() for w in words]  # remove internal whitespace
            # now we are sure the format is right
            # unite on or_clause
            if (var not in grammar):
                grammar[var] = set()
            grammar[var] = grammar[var].union(set(words))

    return Grammar(grammar, start)
