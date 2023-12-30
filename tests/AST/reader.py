import io
import typing as T
from utils.AST import AST


def read_ast(stream: io.TextIOWrapper,
             indent: int = 4) -> T.Optional[AST]:
    if (not stream.read(1)):
        return None
    stream.seek(stream.tell() - 1)  # put back

    state_stack: T.List[AST] = []
    line = stream.readline()
    root_value = line.strip()
    root = AST(root_value, [])
    state_stack.append(root)
    curr_depth = (len(line) - len(line.lstrip())) // indent
    lineno = 1
    while (len(state_stack) > 0 and stream.read(1)):
        lineno += 1
        stream.seek(stream.tell() - 1)  # put back
        line = stream.readline()
        line = line.replace('\t', indent * ' ')
        val = line.strip()
        node = AST(val, [])
        depth = (len(line) - len(line.lstrip())) // indent
        if depth == curr_depth + 1:  # descend
            state_stack[-1].children.append(node)
            state_stack.append(node)
            curr_depth += 1
        elif depth <= curr_depth and (curr_depth - depth) + 1 < len(state_stack):
            # pop from stack
            for i in range((curr_depth - depth) + 1):
                state_stack.pop()
            state_stack[-1].children.append(node)
            state_stack.append(node)
            curr_depth = depth
        else:
            raise RuntimeError(f"Invalid tree representation: invalid depth progression (from {curr_depth} to {depth}) on line {lineno}: '{line.strip()}'.")
    return root
