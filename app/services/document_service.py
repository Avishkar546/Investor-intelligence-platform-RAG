from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ingestion.pipeline import FinancialIngestionPipeline


class DocumentService:

    def __init__(self):

        settings = get_settings()

        self.upload_dir = Path(
            settings.upload_dir
        )

        self.pipeline = (
            FinancialIngestionPipeline()
        )

    def process_upload(
        self,
        file: UploadFile,
        company: str,
        fiscal_year: int,
        db: Session,
    ) -> dict:

        document_id = uuid4().hex

        extension = Path(
            file.filename or ""
        ).suffix.lower()

        file_path = (
            self.upload_dir
            / f"{document_id}{extension}"
        )

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            with file_path.open("wb") as buffer:

                while chunk := file.file.read(
                    1024 * 1024
                ):
                    buffer.write(chunk)

            return self.pipeline.run(
                file_path=str(file_path),
                document_id=document_id,
                filename=file.filename or "unknown",
                company=company,
                fiscal_year=fiscal_year,
                db=db,
            )

        finally:
            file.file.close()