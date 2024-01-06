import typing as T
from lexer.nfa import NFA
from lexer.dfa import DFA
import pytest


def test_conversion_1():
    """
        NFA for L = (a*b + b*a)b*
    """
    transition_table = {
        0: {
            'a': {1, 3},
            'b': {1, 2, 3},
        },
        1: {
            'a': {1},
            'b': {3},
        },
        2: {
            'a': {3},
            'b': {2},
        },
        3: {
            'a': {},
            'b': {3},
        }
    }
    nfa = NFA(4, ['a', 'b'], transition_table, [3])
    dfa = nfa.toDFA()
    print(nfa)
    print(dfa)

    # random tests
    assert nfa.accepts('ab') and dfa.accepts('ab')
    assert (not nfa.accepts('')) and (not dfa.accepts(''))
    assert (not nfa.accepts('baa') and (not dfa.accepts('baa')))
    assert (not nfa.accepts('baba') and (not dfa.accepts('baba')))
    assert (nfa.accepts('aaaaaaab')) and (dfa.accepts('aaaaaaab'))  # path 1 w/o last star
    assert (nfa.accepts('aaaaaaabbb')) and (dfa.accepts('aaaaaaabbb'))  # path 1 w/ last star
    assert (nfa.accepts('bbbbba')) and (dfa.accepts('bbbbba'))  # path 2 w/o last star
    assert (nfa.accepts('bbbbbabbbbbb')) and (dfa.accepts('bbbbbabbbbbb'))  # path 2 w/o last star
