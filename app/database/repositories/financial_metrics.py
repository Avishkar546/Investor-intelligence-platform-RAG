from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import FinancialMetrics
from app.rag.kpi_extractor import FinancialMetricsResult


class FinancialMetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_company_and_year(
        self,
        company: str,
        fiscal_year: int,
    ) -> FinancialMetrics | None:

        statement = (
            select(FinancialMetrics)
            .where(
                FinancialMetrics.company == company,
                FinancialMetrics.fiscal_year
                == fiscal_year,
            )
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def get_by_company(
        self,
        company: str,
    ) -> list[FinancialMetrics]:

        statement = (
            select(FinancialMetrics)
            .where(
                FinancialMetrics.company == company
            )
            .order_by(
                FinancialMetrics.fiscal_year
            )
        )

        return list(
            self.db.execute(statement).scalars()
        )

    def get_by_document(
        self,
        document_id: str,
    ) -> FinancialMetrics | None:

        statement = (
            select(FinancialMetrics)
            .where(
                FinancialMetrics.document_id
                == document_id
            )
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def upsert(
        self,
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

        record = self.db.scalar(statement)

        if record is None:

            record = FinancialMetrics(
                document_id=document_id,
                company=company,
                fiscal_year=fiscal_year,
            )

            self.db.add(record)

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

        self.db.commit()
        self.db.refresh(record)

        return record