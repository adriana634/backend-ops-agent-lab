import logging
import httpx

from app.domain.ports import Incident

logger = logging.getLogger(__name__)

class MockApiIncidentReader:
	def __init__(self, base_url: str) -> None:
		self._base_url = base_url.rstrip("/")

	async def get_by_id(self, incident_id: str) -> Incident | None:
		logger.info("Calling mock-api to fetch incident=%s", incident_id)
		async with httpx.AsyncClient(timeout=10.0) as client:
			response = await client.get(f"{self._base_url}/incidents/{incident_id}")
			if response.status_code == 404:
				logger.info("Mock-api returned 404 for incident=%s", incident_id)
				return None

			try:
				response.raise_for_status()
			except Exception:
				logger.exception("Error fetching incident=%s from mock-api", incident_id)
				raise

			data = response.json()
			logger.info("Mock-api returned incident=%s service=%s", data.get("incident_id"), data.get("service"))
			return Incident(**data)
