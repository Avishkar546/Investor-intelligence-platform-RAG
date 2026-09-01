import logging

from sqlalchemy.orm import Session

from app.query.models import QueryType
from app.query.router import FinancialQueryRouter
from app.rag.answer_generator import AnswerGenerator
from app.rag.citation import CitationBuilder
from app.rag.context_builder import ContextBuilder
from app.retrieval.query import RetrievalQuery
from app.retrieval.retriever import FinancialRetriever
from app.schemas.answer import AnswerResponse
from app.services.financial_calculator import FinancialCalculator
from app.services.metric_service import MetricsService
from app.retrieval.post_processor import RetrievalPostProcessor
from app.retrieval.reranker import RetrievalReranker
from app.rag.grounding import GroundingValidator


logger = logging.getLogger(__name__)


class QueryService:

    def __init__(self, db: Session):

        self.router = FinancialQueryRouter()

        self.retriever = FinancialRetriever()

        self.metrics_service = MetricsService(db)

        self.calculator = FinancialCalculator()

        self.context_builder = ContextBuilder()

        self.answer_generator = AnswerGenerator()

        self.post_processor = RetrievalPostProcessor()

        self.reranker = RetrievalReranker()

        self.grounding_validator = GroundingValidator()

    def process(
        self,
        *,
        question: str,
        company: str | None = None,
        fiscal_year: int | None = None,
        document_id: str | None = None,
        top_k: int = 5,
    ) -> AnswerResponse:

        logger.info(
            "[QUERY] Processing query | "
            "company=%s | fiscal_year=%s | "
            "document_id=%s",
            company,
            fiscal_year,
            document_id,
        )

        # 1. Classify query
        query_type = self.router.route(question)

        logger.info(
            "[QUERY] Classified as: %s",
            query_type,
        )

        metrics = None
        chunks = []
        calculations = {}

        # 2. Retrieve required data
        if query_type in (
            QueryType.STRUCTURED,
            QueryType.COMPARISON,
            QueryType.HYBRID,
        ):

            metrics = self._get_metrics(
                company=company,
                fiscal_year=fiscal_year,
            )

        if query_type in (
            QueryType.SEMANTIC,
            QueryType.HYBRID,
        ):

            chunks = self._retrieve_chunks(
                question=question,
                company=company,
                fiscal_year=fiscal_year,
                document_id=document_id,
                top_k=top_k,
            )

            chunks = self.post_processor.process(
                chunks,
            )

            chunks = self.reranker.rerank(
                question,
                chunks,
            )

        # 3. Deterministic calculations
        if query_type == QueryType.COMPARISON:

            calculations = self._calculate_metrics(
                metrics
            )

        # 4. Build LLM context
        context = self.context_builder.build(
            metrics=metrics,
            chunks=chunks,
            calculations=calculations,
        )

        if not context.strip():

            logger.warning(
                "[QUERY] No context found"
            )

            answer = (
                "I don't have sufficient financial "
                "data to answer this question."
            )

        else:

            # 5. Generate grounded answer
            answer = self.answer_generator.generate(
                question=question,
                context=context,
            )

            is_grounded = (
                self.grounding_validator.validate(
                    answer=answer,
                    context=context,
                )
            )

            if not is_grounded:

                logger.warning(
                    "[QUERY] Answer failed grounding check"
                )

                answer = (
                    "I could not generate a sufficiently "
                    "grounded answer from the available "
                    "financial data."
                )

        # 6. Build citations
        sources = CitationBuilder.build(chunks)

        logger.info(
            "[QUERY] Completed | type=%s | "
            "chunks=%d | sources=%d",
            query_type,
            len(chunks),
            len(sources),
        )

        return AnswerResponse(
            question=question,
            query_type=query_type,
            answer=answer,
            sources=sources,
        )

    # PostgreSQL
    def _get_metrics(
        self,
        *,
        company: str | None,
        fiscal_year: int | None,
    ):

        if not company:

            logger.warning(
                "[QUERY] Company not provided "
                "for structured query"
            )

            return None

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

    # Qdrant
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

    # Financial calculations
    def _calculate_metrics(
        self,
        metrics,
    ) -> dict:

        if not metrics:

            return {}

        # Phase 4 keeps this intentionally simple.
        # Multi-year comparison logic will be expanded
        # once the metric schema is normalized.

        return {
            "available_metrics": metrics
        }