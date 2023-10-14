from parsers.SLR import LR0_Automaton, LR0_State
from utils.preprocessing import parse_file
from sys import argv

grammar = parse_file(argv[1])

LR0_aut = LR0_Automaton(grammar)

for i, state in enumerate(LR0_aut.states):
    print(f"State {i}:", end=2*'\n')
    print(state)
    
