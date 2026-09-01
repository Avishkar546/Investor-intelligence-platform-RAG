from enum import StrEnum


class QueryType(StrEnum):
    STRUCTURED = "structured"
    SEMANTIC = "semantic"
    COMPARISON = "comparison"
    HYBRID = "hybrid"