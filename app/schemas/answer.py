from pydantic import BaseModel


class Source(BaseModel):

    source_id: int

    document_id: str

    company: str

    fiscal_year: int

    page: int | None = None

    section: str | None = None

    score: float | None = None


class AnswerResponse(BaseModel):

    question: str

    query_type: str

    answer: str

    sources: list[Source]