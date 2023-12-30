from sys import argv
import string

from grammar import Grammar
from utils.preprocessing import parse_file

G = parse_file(argv[1])

print(f"For grammar G = \n{G}")
print(f"with variables={G.vars} and terminals={G.terminals}")
print(f"raw grammar: {G.grammar}")
print("We have the following first sets\n")

first_set = G.first()
for A in first_set:
    print(f"First({A}) = {first_set[A]}")