import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.api.routes.ingestion import router as ingestion_router
from app.core.logging import configure_logging
from app.retrieval.retriever import FinancialRetriever
from app.retrieval.query import RetrievalQuery
from app.schemas.retrieval import RetrievalResponse
from app.api.routes.metrics import router as metrics_router
from app.api.routes.query import router as query_router

configure_logging()

logger = logging.getLogger(__name__)


app = FastAPI(
    title="Financial RAG API",
    version="1.0.0",
)

app.include_router(ingestion_router)
app.include_router(metrics_router)
app.include_router(query_router)

class RetrieveRequest(BaseModel):
    query: str
    company: str | None = None
    fiscal_year: int | None = None
    document_id: str | None = None
    top_k: int = 5

@app.post("/retrieve", response_model=RetrievalResponse)
def retrieve_chunks(request: RetrieveRequest):
    try:
        retriever = FinancialRetriever()
        query = RetrievalQuery(
            text=request.query,
            company=request.company,
            fiscal_year=request.fiscal_year,
            document_id=request.document_id,
            top_k=request.top_k
        )
        results = retriever.retrieve(query)
        return RetrievalResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
    except Exception as e:
        logger.exception("Retrieval endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))