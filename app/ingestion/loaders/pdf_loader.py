import fitz
from dataclasses import dataclass


@dataclass
class DocumentPage:
    page_number: int
    text: str


class PDFLoader:

    def load(self, file_path: str) -> list[DocumentPage]:
        pages: list[DocumentPage] = []

        with fitz.open(file_path) as document:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text("text").strip()

                if not text:
                    continue

                pages.append(
                    DocumentPage(
                        page_number=page_number,
                        text=text,
                    )
                )

        return pages