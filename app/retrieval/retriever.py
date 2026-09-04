import logging

from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint

from app.core.config import get_settings
from app.ingestion.embeddings.gemini import (
    GeminiEmbeddingService,
)
from app.retrieval.filters import (
    build_retrieval_filter,
)
from app.retrieval.query import RetrievalQuery
from app.schemas.retrieval import (
    RetrievedChunk,
)


logger = logging.getLogger(__name__)


class FinancialRetriever:

    def __init__(
        self,
        embedding_service: GeminiEmbeddingService | None = None,
    ):

        settings = get_settings()

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        self.collection_name = (
            settings.qdrant_collection
        )

        self.embedding_service = (
            embedding_service
            or GeminiEmbeddingService()
        )

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> list[RetrievedChunk]:

        query.validate()

        logger.info(
            "[RETRIEVAL] Starting | "
            "query=%s | company=%s | "
            "fiscal_year=%s | top_k=%s",
            query.text,
            query.company,
            query.fiscal_year,
            query.top_k,
        )

        # ------------------------------------------
        # 1. Generate query embedding
        # ------------------------------------------

        query_vector = (
            self.embedding_service.embed_query(
                query.text
            )
        )

        if not query_vector:
            raise RuntimeError(
                "Query embedding is empty."
            )

        # ------------------------------------------
        # 2. Build metadata filter
        # ------------------------------------------

        query_filter = build_retrieval_filter(
            company=query.company,
            fiscal_year=query.fiscal_year,
            document_id=query.document_id,
        )

        # ------------------------------------------
        # 3. Search Qdrant
        # ------------------------------------------

        try:

            response = self.client.query_points(
                collection_name=(
                    self.collection_name
                ),
                query=query_vector,
                query_filter=query_filter,
                limit=query.top_k,
                with_payload=True,
            )

        except Exception as exc:

            logger.exception(
                "[RETRIEVAL] Qdrant search failed"
            )

            raise RuntimeError(
                "Qdrant retrieval failed."
            ) from exc

        points = response.points

        logger.info(
            "[RETRIEVAL] Qdrant search completed | "
            "results=%d",
            len(points),
        )

        # ------------------------------------------
        # 4. Convert Qdrant → application objects
        # ------------------------------------------

        results = [
            self._to_retrieved_chunk(point)
            for point in points
        ]

        return results

    @staticmethod
    def _to_retrieved_chunk(
        point: ScoredPoint,
    ) -> RetrievedChunk:

        payload = point.payload or {}

        return RetrievedChunk(
            chunk_id=str(
                payload.get(
                    "chunk_id",
                    point.id,
                )
            ),
            score=float(point.score),
            text=str(
                payload.get("text", "")
            ),
            document_id=str(
                payload.get(
                    "document_id",
                    "",
                )
            ),
            company=str(
                payload.get(
                    "company",
                    "",
                )
            ),
            fiscal_year=int(
                payload.get(
                    "fiscal_year",
                    0,
                )
            ),
            page=(
                int(payload["page"])
                if payload.get("page") is not None
                else None
            ),
            section=payload.get(
                "section"
            ),
        )