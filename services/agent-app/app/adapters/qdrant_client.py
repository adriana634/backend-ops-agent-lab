from __future__ import annotations
from typing import Sequence

from app.domain.ports import DocsRetrieverPort, RetrievedDoc

class NoopDocsRetriever(DocsRetrieverPort):
	async def search(self, query: str, limit: int = 3) -> Sequence[RetrievedDoc]:
		# TODO: Implement real qdrant client
		# This placeholder returns no documents to keep the app runnable during development.
		return []
