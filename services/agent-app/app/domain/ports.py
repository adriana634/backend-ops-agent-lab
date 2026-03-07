from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence

@dataclass(frozen=True)
class RetrievedDoc:
    source: str
    content: str
    score: float


@dataclass(frozen=True)
class Incident:
    incident_id: str
    service: str
    severity: str
    summary: str
    status: str


class LlmPort(Protocol):
    async def answer(self, system_prompt: str, user_prompt: str) -> str: ...


class DocsRetrieverPort(Protocol):
    async def search(self, query: str, limit: int = 3) -> Sequence[RetrievedDoc]: ...


class IncidentReaderPort(Protocol):
    async def get_by_id(self, incident_id: str) -> Incident | None: ...
