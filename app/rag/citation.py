from app.schemas.answer import Source


class CitationBuilder:

    @staticmethod
    def build(chunks) -> list[Source]:

        sources = []

        for index, chunk in enumerate(chunks):

            sources.append(
                Source(
                    source_id=index + 1,
                    document_id=chunk.document_id,
                    company=chunk.company,
                    fiscal_year=chunk.fiscal_year,
                    page=chunk.page,
                    section=chunk.section,
                    score=chunk.score,
                )
            )

        return sources