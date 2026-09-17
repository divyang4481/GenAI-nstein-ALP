#!/usr/bin/env python3
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "backend" if (ROOT / "backend").exists() else Path("/app")
sys.path.insert(0, str(APP_ROOT))

from app.retrieval import RetrievalService, chunk_document  # noqa: E402


async def main() -> None:
    documents = []
    knowledge_dir = ROOT / "knowledge" if (ROOT / "knowledge").exists() else Path("/knowledge")
    for path in sorted(knowledge_dir.glob("*.json")):
        documents.extend(json.loads(path.read_text()))
    chunks = [chunk for document in documents for chunk in chunk_document(document)]
    count = await RetrievalService().upsert_documents(chunks)
    print(f"Upserted {count} stable chunks into retailflow_knowledge")


if __name__ == "__main__":
    asyncio.run(main())
