import re
from dataclasses import dataclass
from uuid import uuid4

from app.core.config import get_settings
from app.ingestion.loaders.pdf_loader import DocumentPage


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: dict


class FinancialChunker:

    def __init__(self):
        settings = get_settings()

        self.chunk_size = settings.chunk_size
        self.overlap = settings.chunk_overlap

    def chunk(
        self,
        pages: list[DocumentPage],
        document_id: str,
        filename: str,
    ) -> list[DocumentChunk]:

        chunks: list[DocumentChunk] = []

        current_section = "Unknown"

        for page in pages:

            sections = self._split_sections(page.text)

            for section, content in sections:

                if section:
                    current_section = section

                paragraphs = self._split_paragraphs(content)

                current_text = ""

                for paragraph in paragraphs:

                    if len(current_text) + len(paragraph) > self.chunk_size:

                        if current_text.strip():
                            chunks.append(
                                self._create_chunk(
                                    current_text,
                                    document_id,
                                    filename,
                                    page.page_number,
                                    current_section,
                                )
                            )

                        overlap_text = current_text[
                            -self.overlap:
                        ]

                        current_text = (
                            overlap_text + "\n" + paragraph
                        )

                    else:
                        current_text += "\n" + paragraph

                if current_text.strip():
                    chunks.append(
                        self._create_chunk(
                            current_text,
                            document_id,
                            filename,
                            page.page_number,
                            current_section,
                        )
                    )

        return chunks

    def _split_sections(
        self,
        text: str,
    ) -> list[tuple[str, str]]:

        lines = text.splitlines()

        sections = []
        current_section = ""
        current_content = []

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if self._is_heading(line):

                if current_content:
                    sections.append(
                        (
                            current_section,
                            "\n".join(current_content),
                        )
                    )

                current_section = line
                current_content = []

            else:
                current_content.append(line)

        if current_content:
            sections.append(
                (
                    current_section,
                    "\n".join(current_content),
                )
            )

        return sections

    def _is_heading(self, line: str) -> bool:

        if len(line) > 120:
            return False

        heading_patterns = [
            r"^item\s+\d+",
            r"^management['’]s discussion",
            r"^financial statements",
            r"^balance sheet",
            r"^income statement",
            r"^cash flow",
            r"^notes to",
            r"^risk factors",
            r"^corporate governance",
            r"^auditor",
        ]

        return any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in heading_patterns
        )

    def _split_paragraphs(self, text: str) -> list[str]:

        return [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

    def _create_chunk(
        self,
        text: str,
        document_id: str,
        filename: str,
        page_number: int,
        section: str,
    ) -> DocumentChunk:

        return DocumentChunk(
            chunk_id=str(uuid4()),
            text=text.strip(),
            metadata={
                "document_id": document_id,
                "filename": filename,
                "page": page_number,
                "section": section,
                "document_type": "financial_annual_report",
            },
        )