from utils.preprocessing import parse_file
from parsers.LR0 import LR0_Automaton
from tests.reader import read_LR0
from tests.SLR.verifier import compare_LR0
from sys import argv

grammar = parse_file(argv[1])

with open(argv[2], 'r') as oracle_file:
    answer_aut = LR0_Automaton(grammar)
    oracle_aut = read_LR0(oracle_file)
    if (compare_LR0(answer_aut, oracle_aut)):
        print("test passed!")
    else:
        print("test failed!")
        print(" answer ".center(80, '-'))
        for state in answer_aut.states:
            print(">>>", state.id)
            print(state)
        print(" oracle ".center(80, '-'))
        for state in oracle_aut.states:
            print(">>>", state.id)
            print(state)
