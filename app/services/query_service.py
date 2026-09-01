from sqlalchemy.orm import Session

from app.query.models import QueryType
from app.query.router import FinancialQueryRouter
from app.retrieval.query import RetrievalQuery
from app.retrieval.retriever import (
    FinancialRetriever,
)
from app.services.metric_service import (
    MetricsService,
)


class QueryService:

    def __init__(
        self,
        db: Session,
    ):

        self.router = FinancialQueryRouter()

        self.retriever = FinancialRetriever()

        self.metrics_service = MetricsService(
            db
        )

    def process(
        self,
        *,
        question: str,
        company: str | None = None,
        fiscal_year: int | None = None,
        document_id: str | None = None,
        top_k: int = 5,
    ):

        query_type = self.router.route(
            question
        )

        result = {
            "query": question,
            "query_type": query_type,
        }

        if query_type == QueryType.STRUCTURED:

            result["metrics"] = (
                self._get_metrics(
                    company=company,
                    fiscal_year=fiscal_year,
                )
            )

        elif query_type == QueryType.SEMANTIC:

            result["chunks"] = (
                self._retrieve_chunks(
                    question=question,
                    company=company,
                    fiscal_year=fiscal_year,
                    document_id=document_id,
                    top_k=top_k,
                )
            )

        elif query_type == QueryType.COMPARISON:

            result["metrics"] = (
                self._get_metrics(
                    company=company,
                    fiscal_year=fiscal_year,
                )
            )

            result["note"] = (
                "Comparison calculation will be "
                "implemented in the next iteration."
            )

        elif query_type == QueryType.HYBRID:

            result["metrics"] = (
                self._get_metrics(
                    company=company,
                    fiscal_year=fiscal_year,
                )
            )

            result["chunks"] = (
                self._retrieve_chunks(
                    question=question,
                    company=company,
                    fiscal_year=fiscal_year,
                    document_id=document_id,
                    top_k=top_k,
                )
            )

        return result

    def _get_metrics(
        self,
        *,
        company: str | None,
        fiscal_year: int | None,
    ):

        if not company:
            return []

        if fiscal_year:

            return (
                self.metrics_service
                .get_company_year_metrics(
                    company=company,
                    fiscal_year=fiscal_year,
                )
            )

        return (
            self.metrics_service
            .get_company_metrics(
                company=company
            )
        )

    def _retrieve_chunks(
        self,
        *,
        question: str,
        company: str | None,
        fiscal_year: int | None,
        document_id: str | None,
        top_k: int,
    ):

        retrieval_query = RetrievalQuery(
            text=question,
            company=company,
            fiscal_year=fiscal_year,
            document_id=document_id,
            top_k=top_k,
        )

        return self.retriever.retrieve(
            retrieval_query
        )