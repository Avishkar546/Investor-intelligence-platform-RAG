import logging
from sqlalchemy.orm import Session

from app.database.repositories.financial_metrics import (
    FinancialMetricsRepository,
)
from app.ingestion.chunkers.financial_chunker import (
    FinancialChunker,
)
from app.ingestion.embeddings.gemini import (
    GeminiEmbeddingService,
)
from app.ingestion.loaders.pdf_loader import PDFLoader
from app.ingestion.vectorstores.qdrant import (
    QdrantVectorStore,
)
from app.rag.kpi_extractor import FinancialKPIExtractor

logger = logging.getLogger(__name__)

class FinancialIngestionPipeline:

    def __init__(self):

        self.loader = PDFLoader()
        self.chunker = FinancialChunker()
        self.embedding_service = (
            GeminiEmbeddingService()
        )
        self.vector_store = QdrantVectorStore()

        self.kpi_extractor = (
            FinancialKPIExtractor()
        )
        self.metrics_repository = None

    def run(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        company: str,
        fiscal_year: int,
        db: Session,
    ) -> dict:

        self.metrics_repository = (
            FinancialMetricsRepository(db)
        )

        # 1. Extract
        pages = self.loader.load(file_path)

        if not pages:
            raise ValueError(
                "No text extracted from document."
            )

        # 2. Financial-aware chunking
        chunks = self.chunker.chunk(
            pages=pages,
            document_id=document_id,
            filename=filename,
            company=company,
            fiscal_year=fiscal_year
        )

        if not chunks:
            raise ValueError(
                "No chunks generated."
            )

        # 3. Generate embeddings
        texts = [
            chunk.text
            for chunk in chunks
        ]

        embeddings = (
            self.embedding_service.embed_documents(
                texts
            )
        )

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                "Chunk/embedding count mismatch: "
                f"{len(chunks)} chunks, "
                f"{len(embeddings)} embeddings."
            )

        # 4. Store vectors
        self.vector_store.ensure_collection(
            vector_size=len(embeddings[0])
        )

        self.vector_store.upsert(
            chunks=chunks,
            embeddings=embeddings,
        )

        # --------------------------------------------------
        # 5. Extract financial KPIs
        # --------------------------------------------------

        metrics = self.kpi_extractor.extract(
            chunks=chunks,
            company=company,
            fiscal_year=fiscal_year,
        )

        # --------------------------------------------------
        # 6. Persist KPIs
        # --------------------------------------------------

        logger.info(
                "[INGESTION] PostgreSQL metrics insertion started"
            )

        self.metrics_repository.upsert(
            document_id=document_id,
            company=company,
            fiscal_year=fiscal_year,
            metrics=metrics,
        )

        logger.info(
            "[INGESTION] PostgreSQL metrics insertion completed"
        )

        return {
            "document_id": document_id,
            "pages": len(pages),
            "chunks": len(chunks),
            "kpis_extracted": True,
            "status": "completed",
        }