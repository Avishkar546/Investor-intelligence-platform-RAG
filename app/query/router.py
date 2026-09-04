from app.query.classifier import (
    FinancialQueryClassifier,
)
from app.query.models import QueryType


class FinancialQueryRouter:

    def __init__(
        self,
        classifier: FinancialQueryClassifier | None = None,
    ):
        self.classifier = (
            classifier
            or FinancialQueryClassifier()
        )

    def route(
        self,
        question: str,
    ) -> QueryType:

        return self.classifier.classify(
            question
        )