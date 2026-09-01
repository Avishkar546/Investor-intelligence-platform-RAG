from typing import Any


class ContextBuilder:

    @staticmethod
    def build(
        *,
        metrics: Any = None,
        chunks: list[Any] | None = None,
        calculations: dict | None = None,
    ) -> str:

        sections: list[str] = []

        if metrics:

            sections.append(
                "STRUCTURED FINANCIAL DATA:\n"
                f"{metrics}"
            )

        if calculations:

            sections.append(
                "DETERMINISTIC CALCULATIONS:\n"
                f"{calculations}"
            )

        if chunks:

            chunk_text = "\n\n".join(
                (
                    f"[Source {index + 1}]\n"
                    f"Company: {chunk.company}\n"
                    f"Fiscal Year: {chunk.fiscal_year}\n"
                    f"Page: {chunk.page}\n"
                    f"Section: {chunk.section}\n"
                    f"Content:\n{chunk.text}"
                )
                for index, chunk in enumerate(chunks)
            )

            sections.append(
                "ANNUAL REPORT CONTEXT:\n"
                f"{chunk_text}"
            )

        return "\n\n".join(sections)