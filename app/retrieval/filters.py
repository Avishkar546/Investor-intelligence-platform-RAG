from qdrant_client.models import (
    FieldCondition,
    Filter,
    MatchValue,
)


def build_retrieval_filter(
    *,
    company: str | None = None,
    fiscal_year: int | None = None,
    document_id: str | None = None,
) -> Filter | None:

    conditions: list[FieldCondition] = []

    if company:

        conditions.append(
            FieldCondition(
                key="company",
                match=MatchValue(
                    value=company
                ),
            )
        )

    if fiscal_year:

        conditions.append(
            FieldCondition(
                key="fiscal_year",
                match=MatchValue(
                    value=fiscal_year
                ),
            )
        )

    if document_id:

        conditions.append(
            FieldCondition(
                key="document_id",
                match=MatchValue(
                    value=document_id
                ),
            )
        )

    if not conditions:
        return None

    return Filter(
        must=conditions
    )