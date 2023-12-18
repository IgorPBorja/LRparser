import typing as T
import io
import string
from grammar import Grammar
from parsers.LR0 import LOOKAHEAD_TABLE, Abstract_LR0_Automaton, LR0_Automaton, Abstract_LR0_State, LR0_State

def _readline_ignore_blank(stream: io.TextIOBase) -> str:
    line = ""
    ## read(k) consumes the next k chars
    ## stream.read(1) returns false if it is an empty byte (end of stream)
    while (line == "" and stream.read(1)):
        stream.seek(stream.tell() - 1) ## put back
        new_line = stream.readline()
        line = new_line.strip()
    return line

def read_state(stream: io.TextIOBase, state_id : int, indicator : str = '.') -> Abstract_LR0_State:
    """
        Formatting rules: 
        - there has to be at least one blank line between states
        - there must be at least one transition per state
        - there can't be blank lines between transitions
    """
    lookahead_table : LOOKAHEAD_TABLE = dict()

    line = _readline_ignore_blank(stream).strip()

    while (line != ''): 
        var, word = line.split()[0], tuple(line.split()[2:])
        lookahead = '' if word.index(indicator) == len(word) - 1 else word[word.index(indicator) + 1]
        if not ((lookahead, var) in lookahead_table):
            lookahead_table[lookahead, var] = {word}
        else:
            lookahead_table[lookahead, var].add(word)
        line = stream.readline().strip()

    state = Abstract_LR0_State(state_id, lookahead_table)
    return state

def read_LR0(stream: io.TextIOBase, indicator : str = '.', eof_symbol : str = '$') -> Abstract_LR0_Automaton:
    aut = Abstract_LR0_Automaton(indicator, eof_symbol)
    while (stream.read(1)):
        stream.seek(stream.tell() - 1) ## put back
        ## peek at the next line 
        state_line = _readline_ignore_blank(stream)
        if state_line == '':
            break

        state_id_str = ""
        for char in state_line:
            if char in string.digits:
                state_id_str += char
        state_id = int(state_id_str)
        state = read_state(stream, state_id, indicator)
        aut.states.append(state)

    return aut

def read_grammar(stream: io.TextIOBase, eof_symbol : str = '$') -> Grammar:
    raw_g : T.Dict[str, T.Set] = {}
    start_var : str = ''
    rule_separator : str = ''
    while (True):
        ## read next line
        line = _readline_ignore_blank(stream).strip()
        if (line.startswith('-')):
            break
        var, word = line.split()[0], " ".join(line.split()[2:])
        if start_var == '':
            start_var = var
        if rule_separator == '':
            rule_separator = line.split()[1]
        if not (var in raw_g):
            raw_g[var] = {word}
        else:
            raw_g[var].add(word)
    return Grammar(raw_g, start_var)
