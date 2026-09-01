from app.schemas.retrieval import RetrievedChunk


class RetrievalPostProcessor:

    def process(
        self,
        chunks: list[RetrievedChunk],
        *,
        min_score: float = 0.25,
        max_chunks: int = 8,
    ) -> list[RetrievedChunk]:

        if not chunks:
            return []

        # Remove weak results
        filtered = [
            chunk
            for chunk in chunks
            if chunk.score >= min_score
        ]

        # Deduplicate exact chunk content
        seen: set[str] = set()
        unique: list[RetrievedChunk] = []

        for chunk in filtered:

            normalized_text = (
                chunk.text.strip().lower()
            )

            if normalized_text in seen:
                continue

            seen.add(normalized_text)
            unique.append(chunk)

        # Highest relevance first
        unique.sort(
            key=lambda chunk: chunk.score,
            reverse=True,
        )

        return unique[:max_chunks]