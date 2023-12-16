from parsers.SLR import SLR_Parser
from utils.preprocessing import parse_file
from sys import argv

grammar = parse_file(argv[1])

slr_parser = SLR_Parser(grammar)
action_table_str, parser_table_str = slr_parser.repr_table()

print("Transition table is", slr_parser.automaton.transition_table, sep="\n")
print(action_table_str)
print(parser_table_str)
