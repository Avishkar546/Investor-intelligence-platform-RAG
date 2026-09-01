from pydantic import BaseModel, Field


class QueryRequest(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=1000,
    )

    company: str | None = Field(
        default=None,
        max_length=255,
    )

    fiscal_year: int | None = None

    document_id: str | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class QueryClassification(BaseModel):

    query_type: str

    reason: str