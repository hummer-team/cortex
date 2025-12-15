# main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from cortex.core.models import IngestRequest, QueryRequest, ContextResponse
from cortex.services.ingestion import IngestionService
from cortex.services.retrieval import RetrievalService
from cortex.logger.logger import get_logger

log = get_logger(__name__)

app = FastAPI(
    title="个人记忆层助手 (Personal Memory Assistant)",
    description="一个本地优先的、为用户提供智能上下文的AI助手核心引擎。",
    version="0.1.0"
)

ingestion_service = IngestionService()
retrieval_service = RetrievalService()


@app.get("/", tags=["Health Check"])
def read_root():
    """健康检查端点"""
    return {"status": "ok", "message": "Memory Assistant is running."}


@app.post("/ingest", tags=["Memory Ingestion"], status_code=202)
def ingest_memory(request: IngestRequest):
    """
    摄入一份新的记忆。
    这是一个异步的过程，客户端可以立即得到响应。
    """
    try:
        ingestion_service.process(request.content, request.source)
        return {"message": "Ingestion task accepted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=ContextResponse, tags=["Memory Retrieval"])
def query_memory(request: QueryRequest) -> ContextResponse:
    """
    根据查询主题，检索并生成上下文摘要。
    """
    try:
        response = retrieval_service.query_and_synthesize(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    log.info("Starting Memory Assistant server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
