from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import FinancialMetrics
from app.rag.kpi_extractor import FinancialMetricsResult


class FinancialMetricsRepository:

    def upsert(
        self,
        db: Session,
        *,
        document_id: str,
        company: str,
        fiscal_year: int,
        metrics: FinancialMetricsResult,
    ) -> FinancialMetrics:

        statement = select(FinancialMetrics).where(
            FinancialMetrics.company == company,
            FinancialMetrics.fiscal_year == fiscal_year,
        )

        record = db.scalar(statement)

        if record is None:

            record = FinancialMetrics(
                document_id=document_id,
                company=company,
                fiscal_year=fiscal_year,
            )

            db.add(record)

        record.document_id = document_id
        record.revenue = metrics.revenue
        record.net_income = metrics.net_income
        record.operating_income = metrics.operating_income
        record.operating_cash_flow = metrics.operating_cash_flow
        record.total_assets = metrics.total_assets
        record.total_liabilities = metrics.total_liabilities

        record.risk_factors = (
            "\n".join(metrics.risk_factors)
            if metrics.risk_factors
            else None
        )

        record.growth_drivers = (
            "\n".join(metrics.growth_drivers)
            if metrics.growth_drivers
            else None
        )

        db.commit()
        db.refresh(record)

        return record