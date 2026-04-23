from __future__ import annotations

import json
import os
import pickle
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np


class FaissStore:
    def __init__(self, index: faiss.Index, metadata: List[Dict[str, Any]]):
        self.index = index
        self.metadata = metadata

    @classmethod
    def build(cls, embeddings: np.ndarray, metadata: List[Dict[str, Any]]) -> "FaissStore":
        if len(embeddings) != len(metadata):
            raise ValueError("embeddings and metadata must have same length")

        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)

        faiss.normalize_L2(embeddings)
        index.add(embeddings)

        return cls(index=index, metadata=metadata)

    def save(self, index_dir: str) -> None:
        os.makedirs(index_dir, exist_ok=True)

        faiss.write_index(self.index, os.path.join(index_dir, "index.faiss"))

        with open(os.path.join(index_dir, "metadata.pkl"), "wb") as f:
            pickle.dump(self.metadata, f)

        with open(os.path.join(index_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "count": len(self.metadata),
                },
                f,
                indent=2,
            )

    @classmethod
    def load(cls, index_dir: str) -> "FaissStore":
        index_path = os.path.join(index_dir, "index.faiss")
        metadata_path = os.path.join(index_dir, "metadata.pkl")

        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found: {index_path}")

        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"FAISS metadata not found: {metadata_path}")

        index = faiss.read_index(index_path)

        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        return cls(index=index, metadata=metadata)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 4,
    ) -> List[Tuple[Dict[str, Any], float]]:
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results: List[Tuple[Dict[str, Any], float]] = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            results.append((self.metadata[idx], float(score)))

        return results