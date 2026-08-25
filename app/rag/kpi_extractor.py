from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.ingestion.chunkers.financial_chunker import DocumentChunk


class FinancialMetricsResult(BaseModel):

    revenue: str | None = Field(
        default=None,
        description="Reported revenue exactly as stated in the annual report.",
    )

    net_income: str | None = Field(
        default=None,
        description="Reported net income exactly as stated in the annual report.",
    )

    operating_income: str | None = Field(
        default=None,
        description="Reported operating income exactly as stated in the annual report.",
    )

    operating_cash_flow: str | None = Field(
        default=None,
        description="Cash flow from operating activities exactly as reported.",
    )

    total_assets: str | None = Field(
        default=None,
        description="Reported total assets.",
    )

    total_liabilities: str | None = Field(
        default=None,
        description="Reported total liabilities.",
    )

    risk_factors: list[str] = Field(
        default_factory=list,
        description="Important company-specific risks explicitly supported by the report.",
    )

    growth_drivers: list[str] = Field(
        default_factory=list,
        description="Important company-specific growth drivers explicitly supported by the report.",
    )


class FinancialKPIExtractor:

    def __init__(self):

        settings = get_settings()

        self.client = genai.Client(
            api_key=settings.google_api_key
        )

        self.model = settings.extraction_model

    def extract(
        self,
        chunks: list[DocumentChunk],
        company: str,
        fiscal_year: int,
    ) -> FinancialMetricsResult:
        context = self._build_context(chunks)

        prompt = f"""
You are an expert financial analyst.

Company: {company}
Fiscal Year: {fiscal_year}

Extract financial information from the provided annual report context.

Rules:

1. Use ONLY the provided context.
2. Never invent or infer financial values.
3. Preserve reported financial values exactly.
4. Return null when a metric is not available.
5. Identify risks only when explicitly supported by the report.
6. Identify growth drivers only when explicitly supported by the report.
7. Prefer primary financial statements and notes over narrative summaries.
8. If multiple values exist, prefer the value belonging to the specified
   fiscal year.
9. Do not calculate values.
10. Do not mix values from different fiscal years.

Annual Report Context:

{context}
"""
        try:
            print(
                f"[KPI] Starting extraction | "
                f"company={company} | "
                f"fiscal_year={fiscal_year} | "
                f"chunks={len(chunks)}"
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    response_mime_type="application/json",
                    response_schema=FinancialMetricsResult,
                    automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                    )
                ),
            )

            print("[KPI] Gemini response received")

            if response.parsed is None:
                print(
                    "[KPI] ERROR: response.parsed is None"
                )

                print(
                    f"[KPI] Raw response: {response.text}"
                )

                raise RuntimeError(
                    "Gemini returned no structured KPI result."
                )

            print("[KPI] Extraction successful")

            return response.parsed

        except Exception as exc:

            print(
                f"[KPI] EXTRACTION FAILED | "
                f"{type(exc).__name__}: {exc}"
            )

            raise

    @staticmethod
    def _build_context(
        chunks: list[DocumentChunk],
    ) -> str:

        return "\n\n".join(
            (
                f"[Page: {chunk.metadata.get('page')}]\n"
                f"[Section: {chunk.metadata.get('section')}]\n"
                f"{chunk.text}"
            )
            for chunk in chunks
        )