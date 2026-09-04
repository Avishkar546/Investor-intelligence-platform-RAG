import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.document_service import DocumentService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

service = DocumentService()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    company: str = Form(...),
    fiscal_year: int = Form(...),
    db: Session = Depends(get_db),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    try:

        return service.process_upload(
            file=file,
            company=company,
            fiscal_year=fiscal_year,
            db=db,
        )

    except ValueError as exc:

        logger.warning(
            "[API] Validation error: %s",
            exc,
        )

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception:

        logger.exception(
            "[API] Document ingestion failed | "
            "filename=%s | company=%s | fiscal_year=%s",
            file.filename,
            company,
            fiscal_year,
        )

        # Don't expose internal traceback to the client.
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        )