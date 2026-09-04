from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FinancialMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: str
    company: str
    fiscal_year: int

    revenue: str | None = None
    net_income: str | None = None
    operating_income: str | None = None
    operating_cash_flow: str | None = None

    total_assets: str | None = None
    total_liabilities: str | None = None

    risk_factors: str | None = None
    growth_drivers: str | None = None


class MetricComparison(BaseModel):
    company: str
    metric: str
    values: dict[int, str | None]