from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalQuery:
    text: str
    company: str | None = None
    fiscal_year: int | None = None
    document_id: str | None = None
    top_k: int = 5

    def validate(self) -> None:

        if not self.text.strip():
            raise ValueError(
                "Retrieval query cannot be empty."
            )

        if self.top_k < 1:
            raise ValueError(
                "top_k must be greater than 0."
            )

        if self.top_k > 20:
            raise ValueError(
                "top_k cannot exceed 20."
            )

        if self.fiscal_year is not None:
            if self.fiscal_year < 1900:
                raise ValueError(
                    "Invalid fiscal year."
                )