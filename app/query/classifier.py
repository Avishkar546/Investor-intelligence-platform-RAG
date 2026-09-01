import re

from app.query.models import QueryType


class FinancialQueryClassifier:

    STRUCTURED_TERMS = {
        "revenue",
        "sales",
        "net income",
        "profit",
        "operating income",
        "operating cash flow",
        "cash flow",
        "total assets",
        "total liabilities",
        "earnings",
        "eps",
    }

    COMPARISON_TERMS = {
        "compare",
        "comparison",
        "compared",
        "increase",
        "decrease",
        "growth",
        "grew",
        "declined",
        "change",
        "year over year",
        "yoy",
    }

    SEMANTIC_TERMS = {
        "risk",
        "risks",
        "strategy",
        "strategies",
        "growth drivers",
        "management",
        "outlook",
        "challenges",
        "opportunities",
        "explain",
        "why",
        "how",
    }

    def classify(
        self,
        question: str,
    ) -> QueryType:

        normalized = question.lower().strip()

        has_structured = any(
            term in normalized
            for term in self.STRUCTURED_TERMS
        )

        has_comparison = any(
            term in normalized
            for term in self.COMPARISON_TERMS
        )

        has_semantic = any(
            term in normalized
            for term in self.SEMANTIC_TERMS
        )
        
        # Questions requiring both factual metrics
        # and narrative explanation
        if has_structured and has_semantic:
            return QueryType.HYBRID

        # Comparison involving financial metrics
        if has_comparison and has_structured:
            return QueryType.COMPARISON

        if has_structured:
            return QueryType.STRUCTURED

        return QueryType.SEMANTIC