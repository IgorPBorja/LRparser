import typing as T

class AST:
    def __init__(self, value: str, children: T.List["AST"]):
        self.value = value
        self.children = children

    def _stringify(self, current_depth):
        final_str = ""
        final_str += current_depth * " " + str(self.value) + "\n"
        link = "└──"
        for subtree in self.children:
            spacing = current_depth * " " + link + " " * max(len(self.value) - 3, 0)
            final_str += spacing + subtree._stringify(len(spacing))[len(spacing):]
        return final_str

    def __repr__(self):
        return self._stringify(0)

