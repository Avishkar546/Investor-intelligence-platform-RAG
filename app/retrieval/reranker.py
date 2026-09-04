from app.schemas.retrieval import RetrievedChunk


class RetrievalReranker:

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:

        if not chunks:
            return []

        query_terms = {
            term.lower()
            for term in query.split()
            if len(term) > 2
        }

        scored = []

        for chunk in chunks:

            text = chunk.text.lower()

            keyword_hits = sum(
                1
                for term in query_terms
                if term in text
            )

            keyword_score = min(
                keyword_hits / max(
                    len(query_terms),
                    1,
                ),
                1.0,
            )

            final_score = (
                0.7 * chunk.score
                + 0.3 * keyword_score
            )

            scored.append(
                (
                    final_score,
                    chunk,
                )
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            chunk
            for _, chunk in scored
        ]