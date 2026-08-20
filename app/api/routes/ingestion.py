from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/api",
    tags=["upload"],
)

service = DocumentService()

ALLOWED_EXTENSIONS = {".pdf"}


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF annual reports are supported.",
        )

    try:

        result = await service.process_upload(file)

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        ) from exc