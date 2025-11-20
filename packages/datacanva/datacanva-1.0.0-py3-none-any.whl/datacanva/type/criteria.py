from .expression_tree import ExpressionTreeNode
from ..type.warehouse import *


class ConditionalOperator(str, Enum):
    EQUAL_TO = "EQUAL_TO"
    NOT_EQUAL_TO = "NOT_EQUAL_TO"
    GREATER_THAN_OR_EQUAL_TO = "GREATER_THAN_OR_EQUAL_TO"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN_OR_EQUAL_TO = "LESS_THAN_OR_EQUAL_TO"
    LESS_THAN = "LESS_THAN"
    IN = "IN"
    NOT_IN = "NOT_IN"
    MATCH_PATTERN = "MATCH_PATTERN"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    CONTAINS = "CONTAINS"
    IS_NULL = "IS_NULL"
    IS_NOT_NULL = "IS_NOT_NULL"
    WITHIN_RECENT_DAYS = "WITHIN_RECENT_DAYS"
    WITHIN_RECENT_HOURS = "WITHIN_RECENT_HOURS"
    WITHIN_RECENT_MINUTES = "WITHIN_RECENT_MINUTES"
    WITHIN_TODAY = "WITHIN_TODAY"
    WITHIN_THIS_WEEK = "WITHIN_THIS_WEEK"
    WITHIN_THIS_MONTH = "WITHIN_THIS_MONTH"
    WITHIN_THIS_QUARTER = "WITHIN_THIS_QUARTER"
    WITHIN_THIS_YEAR = "WITHIN_THIS_YEAR"
    WITHIN_YESTERDAY = "WITHIN_YESTERDAY"
    WITHIN_LAST_WEEK = "WITHIN_LAST_WEEK"
    WITHIN_LAST_MONTH = "WITHIN_LAST_MONTH"
    WITHIN_LAST_QUARTER = "WITHIN_LAST_QUARTER"
    WITHIN_LAST_YEAR = "WITHIN_LAST_YEAR"
    HAS_ALL_TAGS = "HAS_ALL_TAGS"
    HAS_ANY_TAGS = "HAS_ANY_TAGS"
    TAGS_COUNT_GREATER_THAN = "TAGS_COUNT_GREATER_THAN"
    TAGS_COUNT_LESS_THAN = "TAGS_COUNT_LESS_THAN"


class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class Criterion(TypedDict):
    field: str
    value: str
    valueType: DataType
    listValue: list[str]
    operator: ConditionalOperator


Criteria = ExpressionTreeNode[Criterion, LogicalOperator]
