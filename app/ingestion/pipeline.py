from app.ingestion.chunkers.financial_chunker import FinancialChunker
from app.ingestion.embeddings.gemini import GeminiEmbeddingService
from app.ingestion.loaders.pdf_loader import PDFLoader
from app.ingestion.vectorstores.qdrant import QdrantVectorStore


class FinancialIngestionPipeline:

    def __init__(self):

        self.loader = PDFLoader()
        self.chunker = FinancialChunker()
        self.embedding_service = GeminiEmbeddingService()
        self.vector_store = QdrantVectorStore()

    async def run(
        self,
        file_path: str,
        document_id: str,
        filename: str,
    ) -> dict:

        # 1. Extract
        pages = self.loader.load(file_path)

        if not pages:
            raise ValueError("No text extracted from document.")

        # 2. Structure-aware chunking
        chunks = self.chunker.chunk(
            pages=pages,
            document_id=document_id,
            filename=filename,
        )

        if not chunks:
            raise ValueError("No chunks generated.")

        # 3. Embeddings
        texts = [chunk.text for chunk in chunks]

        embeddings = self.embedding_service.embed_documents(
            texts
        )

        if not embeddings:
            raise ValueError("Embedding generation failed.")

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                f"Chunk/embedding mismatch: "
                f"{len(chunks)} chunks, "
                f"{len(embeddings)} embeddings"
            )

        # 4. Create collection
        self.vector_store.ensure_collection(
            vector_size=len(embeddings[0])
        )

        # 5. Store
        self.vector_store.upsert(
            chunks=chunks,
            embeddings=embeddings,
        )

        return {
            "document_id": document_id,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "completed",
        }