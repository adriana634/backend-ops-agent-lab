from fastapi import APIRouter, HTTPException

router = APIRouter()

INCIDENTS = {
    "INC-001": {
        "incident_id": "INC-001",
        "service": "billing-api",
        "severity": "high",
        "summary": "Spike of HTTP 429 errors when calling an external provider",
        "status": "open",
    },
    "INC-002": {
        "incident_id": "INC-002",
        "service": "orders-api",
        "severity": "medium",
        "summary": "Timeouts observed during background synchronization",
        "status": "investigating",
    },
}


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: str) -> dict:
    incident = INCIDENTS.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
