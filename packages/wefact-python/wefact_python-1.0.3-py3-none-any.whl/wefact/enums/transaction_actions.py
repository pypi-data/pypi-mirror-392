from enum import Enum


class TransactionAction(str, Enum):
    MATCH = "match"
    IGNORE = "ignore"
