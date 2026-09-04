from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FinancialMetrics(Base):

    __tablename__ = "financial_metrics"

    __table_args__ = (
        UniqueConstraint(
            "company",
            "fiscal_year",
            name="uq_company_fiscal_year",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    fiscal_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    revenue: Mapped[str | None] = mapped_column(
        String(255)
    )

    net_income: Mapped[str | None] = mapped_column(
        String(255)
    )

    operating_income: Mapped[str | None] = mapped_column(
        String(255)
    )

    operating_cash_flow: Mapped[str | None] = mapped_column(
        String(255)
    )

    total_assets: Mapped[str | None] = mapped_column(
        String(255)
    )

    total_liabilities: Mapped[str | None] = mapped_column(
        String(255)
    )

    risk_factors: Mapped[str | None] = mapped_column(
        Text
    )

    growth_drivers: Mapped[str | None] = mapped_column(
        Text
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )