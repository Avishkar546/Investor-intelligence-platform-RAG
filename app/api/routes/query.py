from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.query import QueryRequest
from app.services.query_service import QueryService


router = APIRouter(
    prefix="/query",
    tags=["query"],
)


@router.post("")
def query(
    request: QueryRequest,
    db: Session = Depends(get_db),
):

    service = QueryService(db)

    return service.process(
        question=request.question,
        company=request.company,
        fiscal_year=request.fiscal_year,
        document_id=request.document_id,
        top_k=request.top_k,
    )