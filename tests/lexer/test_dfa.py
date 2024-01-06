import typing as T
import pytest
from lexer.dfa import DFA

def test_dfa():
    """
        DFA for {0,1}*1{0,1}*0{0,1}*
        Fixed tests
    """
    transitions = {
        0: {
            '0': 0,
            '1': 1
        },
        1: {
            '0': 2,
            '1': 1
        },
        2: {
            '0': 2,
            '1': 2
        }
    }
    dfa = DFA(3, ['0', '1'], transitions, [2])
    assert dfa.accepts('10')
    assert dfa.accepts('11111110')
    assert dfa.accepts('0000011111110')
    assert dfa.accepts('111111101010101')
    assert dfa.accepts('0000011111110001010')
    assert dfa.accepts('1010')
    assert not dfa.accepts('')
    assert not dfa.accepts('00000')
    assert not dfa.accepts('00001')
    assert not dfa.accepts('01111')
    assert not dfa.accepts('1111')


@pytest.mark.parametrize(["x", "y", "m1", "m2", "maxlen", "samples"], [(5, 7, 11, 13, 1000, 100), (0, 0, 3, 5, 10000, 100)])
def test_dfa_stress(x: int, y: int, m1: int, m2: int, maxlen: int, samples: int):
    """
        DFA for L := {w in {a,b,c}* | the amount of a's is x mod m1 and the amount of b's is y mod m2}
    """

    # m2 repeating blocks of size m1
    # inner block mod (i % m1) expresses count of a's mod m1
    # block number (i // m1) expresses count of b's mod m2
    transition_table: T.Dict[int, T.Dict[str, T.Optional[int]]] = dict()
    accepting = []
    for i in range(m1 * m2):
        mod_m1 = i % m1  # take mod inside block of side m1
        mod_m2 = (i // m1) % m2
        transition_table[i] = dict()
        transition_table[i] = {
            'a': m1 * (i // m1) + (i + 1) % m1,  # take mod inside block of side m1
            'b': (i + m1) % (m1 * m2),  # next block
            'c': i
        }
        if mod_m1 == x and mod_m2 == y:
            accepting.append(i)
    dfa = DFA(m1 * m2, ['a', 'b', 'c'], transition_table, accepting)

    # Generate positive tests
    from random import shuffle, choice
    for i in range(samples // 2):
        num_a = choice(list(range(x, maxlen - 1 - y, m1)))
        num_b = choice(list(range(y, maxlen - 1 - num_a, m2)))
        num_c = choice(list(range(1, maxlen - num_a - num_b, 1)))
        seq = ['a'] * num_a + ['b'] * num_b + ['c'] * num_c
        # assert permuting does not matter
        for j in range(3):
            cp = seq.copy()
            shuffle(seq)
            assert dfa.accepts(seq)
            seq = cp.copy()

    # Generate random tests (mostly negative depending on m1, m2)
    for i in range((samples + 1) // 2):
        num_a = choice(list(range(1, maxlen - 2, 1)))
        num_b = choice(list(range(1, maxlen - 1 - num_a, 1)))
        num_c = choice(list(range(1, maxlen - num_a - num_b, 1)))
        seq = ['a'] * num_a + ['b'] * num_b + ['c'] * num_c
        shuffle(seq)
        assert dfa.accepts(seq) == ((num_a % m1 == x) and (num_b % m2 == y))
