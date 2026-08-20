from fastapi import FastAPI

from app.api.routes.ingestion import router as ingestion_router


app = FastAPI(
    title="Financial RAG API",
    version="1.0.0",
)

app.include_router(ingestion_router)