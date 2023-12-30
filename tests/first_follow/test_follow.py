from sys import argv
import string

from grammar import Grammar
from utils.preprocessing import parse_file

G = parse_file(argv[1])

print(f"For grammar G = \n{G}")
print(f"with variables={G.vars} and terminals={G.terminals}")
print(f"raw grammar: {G.grammar}")
print("We have the following follow sets\n")

first_set = G.first()
follow_set = G.follow(first_set)
for A in follow_set:
    print(f"Follow({A}) = {follow_set[A]}")