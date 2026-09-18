import hashlib
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from app.config import settings

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams
except ImportError:  # local unit tests can exercise the deterministic memory store
    AsyncQdrantClient = None


import asyncio
import json

COLLECTION = "retailflow_knowledge"
VECTOR_SIZE = 1024


@dataclass
class RetrievedSource:
    source_id: str
    source_type: str
    title: str
    chunk_id: str
    score: float
    version: str
    text: str
    policy_id: str | None = None
    case_id: str | None = None
    metadata: dict[str, Any] | None = None

    def public_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["text_excerpt"] = value.pop("text")[:700]
        return value


class LocalHashEmbedder:
    """Offline deterministic development fallback."""

    model_name = "local-hash-embedding-v1"

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * VECTOR_SIZE
        for token in text.lower().replace("/", " ").replace("_", " ").split():
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % VECTOR_SIZE
            vector[index] += -1.0 if digest[4] & 1 else 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class BedrockTitanEmbedder:
    """Real Amazon Titan Text Embeddings via AWS Bedrock."""

    model_name = "amazon.titan-embed-text-v2:0"

    def __init__(self, model_id: str = "amazon.titan-embed-text-v2:0", fallback: Any | None = None):
        self.model_id = model_id
        self.model_name = model_id
        self.fallback = fallback or LocalHashEmbedder()
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from app.agents.llm_provider import llm_provider
                self._client = llm_provider._get_bedrock_client()
            except Exception:
                self._client = None
        return self._client

    async def embed(self, text: str) -> list[float]:
        client = self._get_client()
        if client:
            try:
                payload = {"inputText": text[:8192]}
                res = await asyncio.to_thread(
                    client.invoke_model,
                    modelId=self.model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload)
                )
                body = json.loads(res["body"].read().decode("utf-8"))
                embedding = body.get("embedding")
                if embedding and len(embedding) == VECTOR_SIZE:
                    return embedding
            except Exception:
                pass
        return await self.fallback.embed(text)


class RetrievalService:
    def __init__(self, url: str | None = None, embedder: Any | None = None, client: Any | None = None):
        self.embedder = embedder or BedrockTitanEmbedder()
        self._url = url or settings.QDRANT_URL
        self._client = client
        self._memory: list[tuple[list[float], dict[str, Any]]] = []

    @property
    def client(self) -> Any | None:
        if self._client is None and self._url and AsyncQdrantClient:
            try:
                self._client = AsyncQdrantClient(url=self._url, timeout=5.0)
            except Exception:
                self._client = None
        return self._client

    @client.setter
    def client(self, value: Any | None) -> None:
        self._client = value
        if value is None:
            self._url = None

    async def ensure_collection(self) -> None:
        client = self.client
        if not client:
            return
        try:
            if not await client.collection_exists(COLLECTION):
                await client.create_collection(COLLECTION, vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE))
        except Exception:
            pass

    async def upsert_documents(self, documents: list[dict[str, Any]]) -> int:
        await self.ensure_collection()
        points = []
        for document in documents:
            payload = {**document, "embedding_model": self.embedder.model_name, "created_at": document.get("created_at") or datetime.now(timezone.utc).isoformat()}
            vector = await self.embedder.embed(payload["text"])
            point_id = int(hashlib.sha256(payload["chunk_id"].encode()).hexdigest()[:15], 16)
            points.append(PointStruct(id=point_id, vector=vector, payload=payload) if self.client else None)
            self._memory = [(v, p) for v, p in self._memory if p["chunk_id"] != payload["chunk_id"]]
            self._memory.append((vector, payload))
        if self.client and points:
            try:
                await self.client.upsert(COLLECTION, points=points, wait=True)
            except Exception:
                pass
        return len(documents)

    async def search(self, query: str, top_k: int = 5, source_type: str | None = None) -> list[RetrievedSource]:
        vector = await self.embedder.embed(query)
        matches: list[tuple[float, dict[str, Any]]] = []
        client = self.client
        if client:
            try:
                query_filter = Filter(must=[FieldCondition(key="source_type", match=MatchValue(value=source_type))]) if source_type else None
                response = await client.query_points(collection_name=COLLECTION, query=vector, query_filter=query_filter, limit=max(4, min(top_k, 6)), with_payload=True)
                matches = [(float(point.score), point.payload or {}) for point in response.points]
            except Exception:
                matches = []

        if not matches:
            for candidate, payload in self._memory:
                if source_type and payload.get("source_type") != source_type:
                    continue
                matches.append((sum(a * b for a, b in zip(vector, candidate)), payload))
            matches.sort(key=lambda row: row[0], reverse=True)
            matches = matches[:top_k]
        return [RetrievedSource(score=score, **{key: payload.get(key) for key in ("source_id", "source_type", "title", "chunk_id", "version", "text", "policy_id", "case_id", "metadata")}) for score, payload in matches if payload]


def chunk_document(document: dict[str, Any], size: int = 400, overlap: int = 50) -> list[dict[str, Any]]:
    words = document["text"].split()
    chunks = []
    for index, start in enumerate(range(0, len(words), size - overlap)):
        text = " ".join(words[start:start + size])
        if not text:
            break
        stable = hashlib.sha256(f'{document["source_id"]}:{document.get("version", "1")}:{index}:{text}'.encode()).hexdigest()[:24]
        chunks.append({**document, "text": text, "chunk_id": stable, "metadata": document.get("metadata", {})})
        if start + size >= len(words):
            break
    return chunks


retrieval_service = RetrievalService()
