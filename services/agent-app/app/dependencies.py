from functools import lru_cache
from fastapi import Depends

from app.config import get_settings
from app.adapters.ollama_client import OllamaClient
from app.adapters.mock_api_client import MockApiIncidentReader
from app.adapters.qdrant_client import NoopDocsRetriever
from app.domain.agent_service import AgentService
from app.domain.ports import DocsRetrieverPort


@lru_cache
def get_docs_retriever() -> DocsRetrieverPort:
    return NoopDocsRetriever()


def get_agent_service(docs: DocsRetrieverPort = Depends(get_docs_retriever)) -> AgentService:
    settings = get_settings()
    llm = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
    incidents = MockApiIncidentReader(base_url=settings.mock_api_base_url)
    return AgentService(llm=llm, docs=docs, incidents=incidents)
