from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.metric_service import MetricsService


router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get("")
def get_all_metrics(
    db: Session = Depends(get_db),
):
    service = MetricsService(db)
    return service.get_all_metrics()


@router.get("/{company}/{fiscal_year}")
def get_metrics(
    company: str,
    fiscal_year: int,
    db: Session = Depends(get_db),
):

    service = MetricsService(db)

    result = service.get_company_year_metrics(
        company=company,
        fiscal_year=fiscal_year,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Financial metrics not found.",
        )

    return result

@router.get("/{company}")
def get_company_metrics(
    company: str,
    db: Session = Depends(get_db),
):
    service = MetricsService(db)

    return service.get_company_metrics(
        company
    )