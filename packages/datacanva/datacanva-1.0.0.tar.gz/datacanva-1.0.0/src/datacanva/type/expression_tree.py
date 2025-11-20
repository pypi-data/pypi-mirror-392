from typing import Generic, TypeVar, List, Optional

# Define type variables for ExpressionType and OperatorType
ExpressionType = TypeVar("ExpressionType")
OperatorType = TypeVar("OperatorType")


class ExpressionTreeNode(Generic[ExpressionType, OperatorType]):

    def __init__(
        self,
        # OperatorType is None if the node is a leaf
        operator: Optional[OperatorType] = None,
        # ExpressionType is None if the node is not a leaf
        expression: Optional[ExpressionType] = None,
        # Recursive definition
        children: Optional[
            List["ExpressionTreeNode[ExpressionType, OperatorType]"]
        ] = None,
    ):
        self.operator = operator
        self.expression = expression
        self.children = children

    def __dict__(self):
        return {
            "operator": self.operator,
            "expression": self.expression,
            "children": self.children,
        }
