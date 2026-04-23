from __future__ import annotations

import os
from typing import Any, Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.rag.chunking.text_chunker import split_text_into_chunks
from app.rag.vectorstore.faiss_store import FaissStore


def infer_category_from_filename(filename: str) -> str:
    lower = filename.lower()

    if "safety" in lower or "hazard" in lower or "risk" in lower:
        return "safety"
    if "troubleshooting" in lower or "error" in lower:
        return "troubleshooting"
    if "material" in lower:
        return "materials"
    if "manual" in lower or "spec" in lower:
        return "machine_manual"
    if "maker-space" in lower or "room description" in lower or "workshop" in lower:
        return "room_info"
    if "dmaic" in lower or "lean" in lower or "six-sigma" in lower:
        return "process_improvement"

    return "general"


def load_text_files_recursively(root_dir: str) -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []

    for current_root, _, files in os.walk(root_dir):
        for file_name in files:
            if not file_name.lower().endswith(".txt"):
                continue

            full_path = os.path.join(current_root, file_name)
            rel_path = os.path.relpath(full_path, root_dir)

            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            documents.append(
                {
                    "file_name": file_name,
                    "file_path": full_path,
                    "relative_path": rel_path,
                    "category": infer_category_from_filename(file_name),
                    "text": text,
                }
            )

    return documents


def build_chunk_records(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    chunk_records: List[Dict[str, Any]] = []

    for doc in documents:
        chunks = split_text_into_chunks(
            text=doc["text"],
            chunk_size=settings.rag_chunk_size,
            chunk_overlap=settings.rag_chunk_overlap,
        )

        for chunk_index, chunk_text in enumerate(chunks):
            chunk_records.append(
                {
                    "file_name": doc["file_name"],
                    "file_path": doc["file_path"],
                    "relative_path": doc["relative_path"],
                    "category": doc["category"],
                    "chunk_index": chunk_index,
                    "chunk_text": chunk_text,
                }
            )

    return chunk_records


def main() -> None:
    print(f"Loading static knowledge from: {settings.static_knowledge_dir}")
    documents = load_text_files_recursively(settings.static_knowledge_dir)
    print(f"Loaded {len(documents)} text files.")

    chunk_records = build_chunk_records(documents)
    print(f"Created {len(chunk_records)} chunks.")

    if not chunk_records:
        raise RuntimeError("No chunks were created. Check your static knowledge directory.")

    model = SentenceTransformer(settings.rag_embedding_model)

    texts = [record["chunk_text"] for record in chunk_records]
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    store = FaissStore.build(
        embeddings=embeddings,
        metadata=chunk_records,
    )
    store.save(settings.rag_index_dir)

    print(f"Saved FAISS index to: {settings.rag_index_dir}")


if __name__ == "__main__":
    main()