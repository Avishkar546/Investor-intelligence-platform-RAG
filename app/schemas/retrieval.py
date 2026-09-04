from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):

    chunk_id: str

    score: float

    text: str

    document_id: str

    company: str

    fiscal_year: int

    page: int | None = None

    section: str | None = None


class RetrievalResponse(BaseModel):

    query: str

    results: list[RetrievedChunk]

    total_results: int