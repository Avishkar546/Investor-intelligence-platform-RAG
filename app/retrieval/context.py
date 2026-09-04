from app.schemas.retrieval import RetrievedChunk


def build_retrieval_context(
    chunks: list[RetrievedChunk],
) -> str:

    sections = []

    for index, chunk in enumerate(chunks, start=1):

        sections.append(
            f"""
[Source {index}]
Company: {chunk.company}
Fiscal Year: {chunk.fiscal_year}
Page: {chunk.page}
Section: {chunk.section}
Relevance Score: {chunk.score:.4f}

{chunk.text}
""".strip()
        )

    return "\n\n".join(sections)