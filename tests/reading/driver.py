from sys import argv

from utils.preprocessing import parse_file
from grammar import Grammar

filepath = argv[1]

G = parse_file(filepath)
print(f"Raw grammar: {G.grammar}")

print("Grammar is", G.grammar, f"with start variable \'{G.start}\'", sep='\n')

print("Representation (one rule per line):")
print(G.__str__(separate_rules=True))
print("Compact representation:")
print(G)
print(f"Terminals are: {G.terminals}")
print(f"Variables are: {G.vars}")