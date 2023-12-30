import typing as T


class AST:
    """
        Abstract syntax tree node.

        @attrs:
            value [str]: symbol associated with that node, either a terminal (in leaf nodes) or a non-terminal
            children [list[AST]]: list of subtrees
    """

    def __init__(self, value: str, children: T.List["AST"]):
        self.value: str = value
        self.children: T.List["AST"] = children

    def _stringify(self, current_depth):
        final_str = ""
        final_str += current_depth * " " + str(self.value) + "\n"
        link = "└──"
        for subtree in self.children:
            spacing = current_depth * " " + link + "─" * max(len(str(self.value)) - 3, 0)
            final_str += spacing + subtree._stringify(len(spacing))[len(spacing):]
        return final_str

    def __str__(self):
        return self._stringify(0)

    # TODO decide on implementation of internal representation (repr)
    #  def __repr__(self):
    #      return str(self)

    def __repr__(self):
        if len(self.children) == 0:
            return f"[{self.value}]"
        else:
            repr_str = "["
            repr_str += str(self.value)
            for c in self.children:
                repr_str += ", " + repr(c)
            repr_str += "]"
            return repr_str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AST):
            if (self.value != other.value) or (len(self.children) != len(other.children)):
                return False
            for c1, c2 in zip(self.children, other.children):
                if not (c1 == c2):
                    return False
            return True
        else:
            return NotImplemented

    def __neq__(self, other: object) -> bool:
        return not (self == other)

    def find_diff(self, other: "AST", lineno: int = 0) -> T.Tuple[int, int, T.Union[str, "AST"]]:
        """
            Performs a detailed comparison between ASTs

            @return
                [int] : line number of first diff
                [int] : type of diff
                    -1 for missing children in "other"
                    0 for equal
                    1 for different values
                    2 for extra children in "other", not in the first AST
                [Union[str, AST]] if mode 1, string value of different symbol. Else return the whole subtree
        """
        if not isinstance(other, AST):
            raise ValueError(f"Can't perform rich comparison on object of type {type(other)} != AST")
        else:
            if self.value != other.value:
                return lineno, 1, other.value
            else:
                lineno += 1
                for c1, c2 in zip(self.children, other.children):
                    if c1 != c2:
                        return c1.find_diff(c2, lineno)
                    else:
                        lineno += len(str(c1).split('\n'))
                if len(self.children) > len(other.children):  # missing children
                    return lineno + 1, -1, self.children[len(other.children)]
                elif len(other.children) > len(self.children):
                    return lineno + 1, 2, other.children[len(self.children)]
                else:
                    return -1, 0, ""  # equal
