import typing as T
from parsers.SLR import SLR_Parser
from utils.preprocessing import parse_file
from tests.AST.reader import read_ast
import os
import pytest

TARGET_PATH = "tests/data/answers/ast_no_lexer"
GRAMMAR_PATH = "tests/data/grammars/ast_no_lexer"
PROGRAM_PATH = "tests/data/programs/ast_no_lexer"


def tokenize(program_filepath: str) -> T.List[str]:
    tok_list = []
    with open(program_filepath, "r") as f:
        for line in f.readlines():
            line = line.replace("\t", " ").replace("\n", " ").replace("\r", " ")
            tok_per_line = line.split()
            if '' in tok_per_line:
                tok_per_line.remove('')
            tok_list.extend(tok_per_line)
    return tok_list


@pytest.mark.parametrize(["grammar_filename", "program_filename", "target_filename"], zip(os.listdir(GRAMMAR_PATH), os.listdir(PROGRAM_PATH), os.listdir(TARGET_PATH)))
def test_AST(grammar_filename: str, program_filename: str, target_filename: str):
    grammar = parse_file(os.path.join(GRAMMAR_PATH, grammar_filename))
    parser = SLR_Parser(grammar)
    parse_sequence = tokenize(os.path.join(PROGRAM_PATH, program_filename))
    error_code, result_ast = parser.parse(parse_sequence)
    print(f"Result: {'parse successful' if error_code == 0 else 'syntax error'}")
    print(result_ast, end=2 * '\n')

    stream = open(os.path.join(TARGET_PATH, target_filename))
    target_ast = read_ast(stream, indent=2)
    stream.close()
    print(target_ast, end=2 * '\n')
    if result_ast != target_ast:
        lineno, mode, diff = target_ast.find_diff(result_ast)
        print(f"Parsed AST diverged from target on line number {lineno + 1}")
        if mode == -1:
            print("Missing children in resulting ast")
            print(diff)
        elif mode == 1:
            print(f"Wrong symbol on resulting ast: {diff}")
        else:
            print(f"Unexpected children on resulting ast: {diff}")

    if target_ast is not None:
        assert error_code == 0 and result_ast == target_ast
    else:
        assert error_code == -1
