from __future__ import annotations
from dataclasses import dataclass
import logging

from app.domain.ports import DocsRetrieverPort, IncidentReaderPort, LlmPort

logger = logging.getLogger(__name__)

@dataclass
class AgentService:
	llm: LlmPort
	docs: DocsRetrieverPort
	incidents: IncidentReaderPort

	async def investigate_incident(self, incident_id: str) -> str:
		logger.info("Investigation started for incident=%s", incident_id)
		logger.info("Fetching incident %s", incident_id)
		incident = await self.incidents.get_by_id(incident_id)
		if incident is None:
			logger.info("Incident not found: %s", incident_id)
			return f"Incident {incident_id} not found."

		logger.info(
			"Incident fetched: id=%s service=%s summary=%s",
			incident.incident_id,
			incident.service,
			incident.summary,
		)

		logger.info("Searching docs for incident=%s", incident_id)
		docs = await self.docs.search(
			query=f"{incident.service} {incident.summary}",
			limit=3,
		)

		docs_block = "\n\n".join(
			f"[{doc.source}] score={doc.score:.3f}\n{doc.content}"
			for doc in docs
		) or "No relevant documentation found."

		logger.info("Docs retrieved: count=%d for incident=%s", len(docs), incident_id)

		logger.info("Constructing prompts for incident=%s", incident_id)
		system_prompt = (
			"You are a backend operations assistant. "
			"Do not invent information. "
			"If the evidence is insufficient, state that explicitly. "
			"Respond with: summary, hypothesis, evidence, and next steps."
		)

		user_prompt = f"""\
Incident:
- id: {incident.incident_id}
- service: {incident.service}
- severity: {incident.severity}
- status: {incident.status}
- summary: {incident.summary}

Retrieved documentation:
{docs_block}
""".strip()

		logger.info("Calling LLM for incident=%s", incident_id)
		try:
			response = await self.llm.answer(system_prompt=system_prompt, user_prompt=user_prompt)
			logger.info("LLM response received for incident=%s length=%d", incident_id, len(response) if response else 0)
			logger.info("Investigation finished for incident=%s", incident_id)
			return response
		except Exception:
			logger.exception("Investigation failed for incident=%s", incident_id)
			raise
