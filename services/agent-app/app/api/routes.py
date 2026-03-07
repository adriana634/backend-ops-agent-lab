from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging

from app.dependencies import get_agent_service
from app.domain.agent_service import AgentService
from app.adapters.ollama_client import OllamaTimeout

logger = logging.getLogger(__name__)

router = APIRouter()

class InvestigateRequest(BaseModel):
    incident_id: str

class InvestigateResponse(BaseModel):
    incident_id: str
    diagnosis: str

@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/investigate", response_model=InvestigateResponse)
async def investigate(
    payload: InvestigateRequest,
    service: AgentService = Depends(get_agent_service),
) -> InvestigateResponse:
    logger.info("Request received: /investigate incident=%s", payload.incident_id)
    logger.info("Injected service: %s", type(service).__name__)
    try:
        result = await service.investigate_incident(payload.incident_id)
        logger.info("Investigation completed for incident=%s", payload.incident_id)
        return InvestigateResponse(incident_id=payload.incident_id, diagnosis=result)
    except OllamaTimeout:
        logger.exception("LLM timeout while investigating %s", payload.incident_id)
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except Exception:
        logger.exception("Unexpected error while investigating %s", payload.incident_id)
        raise HTTPException(status_code=500, detail="Investigation failed due to an internal error")
