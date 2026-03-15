from __future__ import annotations

import hashlib
import os
from pathlib import Path

import httpx
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

RUNBOOKS_DIR = Path("docs/runbooks")
QDRANT_URL = os.getenv("LAB_QDRANT_URL", "http://localhost:6333")
OLLAMA_BASE_URL = os.getenv("LAB_OLLAMA_BASE_URL", "http://localhost:11434/api")
EMBED_MODEL = os.getenv("LAB_OLLAMA_EMBED_MODEL", "all-minilm")
COLLECTION_NAME = "runbooks"

def read_runbooks() -> list[dict]:
    documents: list[dict] = []

    for path in sorted(RUNBOOKS_DIR.glob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        documents.append(
            {
                "id": stable_int_id(str(path)),
                "title": path.stem,
                "path": str(path),
                "content": content,
            }
        )

    return documents

def stable_int_id(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)

def embed_text(text: str) -> list[float]:
    payload = {
        "model": EMBED_MODEL,
        "input": text,
    }

    with httpx.Client(timeout=60.0) as client:
        response = client.post(f"{OLLAMA_BASE_URL}/embed", json=payload)
        response.raise_for_status()
        data = response.json()

    return data["embeddings"][0]

def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    collections = client.get_collections().collections
    names = {collection.name for collection in collections}

    if COLLECTION_NAME in names:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

def upsert_documents(client: QdrantClient, documents: list[dict]) -> None:
    if not documents:
        print("No runbooks found.")
        return

    first_vector = embed_text(documents[0]["content"])
    ensure_collection(client, vector_size=len(first_vector))

    points: list[PointStruct] = [
        PointStruct(
            id=documents[0]["id"],
            vector=first_vector,
            payload={
                "title": documents[0]["title"],
                "path": documents[0]["path"],
                "content": documents[0]["content"],
            },
        )
    ]

    for doc in documents[1:]:
        vector = embed_text(doc["content"])
        points.append(
            PointStruct(
                id=doc["id"],
                vector=vector,
                payload={
                    "title": doc["title"],
                    "path": doc["path"],
                    "content": doc["content"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Indexed {len(points)} runbooks into '{COLLECTION_NAME}'.")

def main() -> None:
    client = QdrantClient(url=QDRANT_URL)
    documents = read_runbooks()
    upsert_documents(client, documents)

if __name__ == "__main__":
    main()
