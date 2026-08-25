from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    PayloadSchemaType
)

from app.core.config import get_settings
from app.ingestion.chunkers.financial_chunker import DocumentChunk


class QdrantVectorStore:

    def __init__(self):

        settings = get_settings()

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        self.collection = settings.qdrant_collection

    def ensure_collection(
        self,
        vector_size: int,
    ) -> None:

        collections = self.client.get_collections()

        exists = any(
            collection.name == self.collection
            for collection in collections.collections
        )

        if not exists:

            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:

        points = []

        for chunk, embedding in zip(chunks, embeddings):

            points.append(
                PointStruct(
                    id=chunk.chunk_id,
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        **chunk.metadata,
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection,
            points=points,
        )

    def create_payload_indexes(
        self,
    ) -> None:

        self.client.create_payload_index(
            collection_name=self.collection,
            field_name="company",
            field_schema=PayloadSchemaType.KEYWORD,
        )

        self.client.create_payload_index(
            collection_name=self.collection,
            field_name="fiscal_year",
            field_schema=PayloadSchemaType.INTEGER,
        )

        self.client.create_payload_index(
            collection_name=self.collection,
            field_name="document_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )