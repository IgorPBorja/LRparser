import io
from tests.reader import read_LR0
from parsers.LR0 import Abstract_LR0_Automaton, LR0_Automaton, LR0_State
from parsers.SLR import SLR_Parser

def infer_state_order(answer: Abstract_LR0_Automaton, oracle: Abstract_LR0_Automaton):
    """
        Ordering of states may differ when generating the LR0 automatically (answer) or by hand (oracle).
        We don't want this to matter, so we use a O(n^2) straightforward approach to figure out how to transform one order to another. Target order is the oracle.
        Order of productions inside a state shouldn't matter since it is a dict.
    """
    answer_to_oracle = [-1 for i in range(len(answer.states))]

    for i, state in enumerate(answer.states):
        for j, oracle_state in enumerate(oracle.states):
            if (state == oracle_state):
                answer_to_oracle[i] = j
                break
    return answer_to_oracle

def compare_LR0(answer : Abstract_LR0_Automaton, oracle : Abstract_LR0_Automaton) -> bool:
    if (len(answer.states) != len(oracle.states)):
        return False
    answer_to_oracle = infer_state_order(answer, oracle)
    for i in answer_to_oracle:
        if i == -1:
            return False
    return True

class VerifierSLR:
    pass
