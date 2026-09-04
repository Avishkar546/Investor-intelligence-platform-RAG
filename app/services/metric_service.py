from sqlalchemy.orm import Session

from app.database.repositories.financial_metrics import (
    FinancialMetricsRepository,
)
from app.schemas.metrics import (
    FinancialMetricResponse,
    MetricComparison,
)


class MetricsService:

    def __init__(self, db: Session):

        self.repository = (
            FinancialMetricsRepository(db)
        )

    def get_all_metrics(self) -> list[FinancialMetricResponse]:
        metrics = self.repository.get_all()
        return [
            FinancialMetricResponse.model_validate(metric)
            for metric in metrics
        ]

    def get_company_year_metrics(
        self,
        company: str,
        fiscal_year: int,
    ) -> FinancialMetricResponse | None:

        metric = (
            self.repository.get_by_company_and_year(
                company=company,
                fiscal_year=fiscal_year,
            )
        )

        if metric is None:
            return None

        return FinancialMetricResponse.model_validate(
            metric
        )

    def get_company_metrics(
        self,
        company: str,
    ) -> list[FinancialMetricResponse]:

        metrics = (
            self.repository.get_by_company(
                company
            )
        )

        return [
            FinancialMetricResponse.model_validate(
                metric
            )
            for metric in metrics
        ]

    def compare_metric(
        self,
        company: str,
        metric: str,
    ) -> MetricComparison:

        allowed_metrics = {
            "revenue",
            "net_income",
            "operating_income",
            "operating_cash_flow",
            "total_assets",
            "total_liabilities",
        }

        if metric not in allowed_metrics:
            raise ValueError(
                f"Unsupported financial metric: {metric}"
            )

        records = (
            self.repository.get_by_company(
                company
            )
        )

        values = {
            record.fiscal_year: getattr(
                record,
                metric,
            )
            for record in records
        }

        return MetricComparison(
            company=company,
            metric=metric,
            values=values,
        )