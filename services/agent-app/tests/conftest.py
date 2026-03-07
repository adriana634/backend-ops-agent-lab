import pytest

from app.domain.agent_service import AgentService
from app.domain.ports import Incident, RetrievedDoc

class FakeLlm:
	async def answer(self, system_prompt: str, user_prompt: str) -> str:
		assert "Do not invent information" in system_prompt
		assert "billing-api" in user_prompt
		return "Initial diagnosis correct"

class FakeDocs:
	async def search(self, query: str, limit: int = 3):
		return [
			RetrievedDoc(
				source="runbook_429.md",
				content="When there are 429s, check rate limits and backoff.",
				score=0.92,
			)
		]

class FakeIncidents:
	async def get_by_id(self, incident_id: str):
		return Incident(
			incident_id=incident_id,
			service="billing-api",
			severity="high",
			summary="Spike of 429 errors",
			status="open",
		)

@pytest.mark.asyncio
async def test_investigate_incident_returns_diagnosis():
	service = AgentService(
		llm=FakeLlm(),
		docs=FakeDocs(),
		incidents=FakeIncidents(),
	)

	result = await service.investigate_incident("INC-001")

	assert "Initial diagnosis" in result
