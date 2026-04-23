from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.rag.vectorstore.faiss_store import FaissStore


class StaticKnowledgeRetriever:
    def __init__(self, model: SentenceTransformer, store: FaissStore):
        self.model = model
        self.store = store

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        category: str | None = None,
    ) -> List[Dict[str, Any]]:
        top_k = top_k or settings.rag_top_k

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=False,
        )
        query_embedding = np.asarray(query_embedding, dtype=np.float32)

        results = self.store.search(query_embedding=query_embedding, top_k=max(top_k * 3, top_k))

        normalized: List[Dict[str, Any]] = []
        for item, score in results:
            if category and item.get("category") != category:
                continue

            normalized.append(
                {
                    "score": score,
                    "file_name": item.get("file_name"),
                    "relative_path": item.get("relative_path"),
                    "category": item.get("category"),
                    "chunk_index": item.get("chunk_index"),
                    "chunk_text": item.get("chunk_text"),
                }
            )

            if len(normalized) >= top_k:
                break

        return normalized


@lru_cache(maxsize=1)
def get_static_knowledge_retriever() -> StaticKnowledgeRetriever:
    model = SentenceTransformer(settings.rag_embedding_model)
    store = FaissStore.load(settings.rag_index_dir)
    return StaticKnowledgeRetriever(model=model, store=store)