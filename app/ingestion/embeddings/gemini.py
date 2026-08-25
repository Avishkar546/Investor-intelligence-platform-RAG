from google import genai
from google.genai import types

from app.core.config import get_settings


class GeminiEmbeddingService:

    def __init__(self):
        settings = get_settings()

        self.client = genai.Client(
            api_key=settings.google_api_key
        )

        self.model = settings.embedding_model

    def embed_documents(
        self,
        texts: list[str],
        batch_size: int = 20,
    ) -> list[list[float]]:

        if not texts:
            return []

        embeddings: list[list[float]] = []

        for start in range(0, len(texts), batch_size):

            batch = texts[start:start + batch_size]

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text)
                    ],
                )
                for text in batch
            ]

            response = self.client.models.embed_content(
                model=self.model,
                contents=contents,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                ),
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini returned no embeddings."
                )

            batch_embeddings = [
                embedding.values
                for embedding in response.embeddings
            ]

            if len(batch_embeddings) != len(batch):
                raise RuntimeError(
                    "Embedding count mismatch: "
                    f"expected={len(batch)}, "
                    f"received={len(batch_embeddings)}"
                )

            embeddings.extend(batch_embeddings)

        return embeddings

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=query)
                    ],
                ),
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                ),
            )

            if not response.embeddings:
                raise RuntimeError(
                    "Gemini returned no query embedding."
                )

            return response.embeddings[0].values
        except Exception as exc:

            raise RuntimeError(
                f"Failed to generate query embedding: {exc}"
            ) from exc