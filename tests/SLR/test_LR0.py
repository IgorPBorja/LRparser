from utils.preprocessing import parse_file
from parsers.LR0 import LR0_Automaton
from tests.SLR.reader import read_LR0
from tests.SLR.verifier import compare_LR0
import os
import pytest


@pytest.mark.parametrize(["filepath"], [(filepath,) for filepath in os.listdir("tests/data/grammars/automaton")])
def test_LR0(filepath):
    assert filepath in os.listdir("tests/data/answers/automaton"), f"File {filepath} does not have answer registered"
    grammar_file = os.path.join("tests/data/grammars/automaton", filepath)
    oracle_file = os.path.join("tests/data/answers/automaton", filepath)
    grammar = parse_file(grammar_file)
    with open(oracle_file, 'r') as oracle_file:
        answer_aut = LR0_Automaton(grammar)
        oracle_aut = read_LR0(oracle_file)
        assert compare_LR0(answer_aut, oracle_aut)
