from app.domain.agent_service import AgentService
from app.domain.models import Incident


class FakeLlm:
    async def answer(self, system_prompt: str, user_prompt: str) -> str:
        assert "Do not invent facts" in system_prompt
        assert "billing-api" in user_prompt
        return (
            "Summary: External provider returned 429 errors.\n"
            "Likely cause: Provider-side rate limiting.\n"
            "Evidence: Incident summary mentions repeated 429 responses.\n"
            "Next step: Review retry and backoff strategy."
        )


class FakeIncidents:
    async def get_by_id(self, incident_id: str) -> Incident | None:
        if incident_id == "INC-404":
            return None

        return Incident(
            incident_id=incident_id,
            service="billing-api",
            severity="high",
            summary="Spike of HTTP 429 errors when calling an external provider",
            status="open",
        )


async def test_investigate_incident_returns_diagnosis() -> None:
    service = AgentService(llm=FakeLlm(), incidents=FakeIncidents())

    result = await service.investigate_incident("INC-001")

    assert result.incident_id == "INC-001"
    assert "Likely cause" in result.diagnosis


async def test_investigate_incident_handles_missing_incident() -> None:
    service = AgentService(llm=FakeLlm(), incidents=FakeIncidents())

    result = await service.investigate_incident("INC-404")

    assert result.incident_id == "INC-404"
    assert "not found" in result.diagnosis
