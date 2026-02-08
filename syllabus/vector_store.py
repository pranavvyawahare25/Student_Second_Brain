"""
Syllabus Vector Store

FAISS-based vector store for syllabus embeddings.
Stores unit/topic embeddings for comparison with lecture content.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# Try to import FAISS
try:
    import faiss
except ImportError:
    faiss = None
    print("Warning: FAISS not installed. Using numpy similarity search.")


@dataclass
class SyllabusEmbedding:
    """Single syllabus topic with embedding."""
    unit_number: int
    unit_title: str
    topic: str
    embedding: List[float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_number": self.unit_number,
            "unit_title": self.unit_title,
            "topic": self.topic
        }


class SyllabusVectorStore:
    """Vector store for syllabus content."""
    
    def __init__(self, store_path: str = "syllabus_index", dimension: int = 384):
        """
        Initialize syllabus vector store.
        
        Args:
            store_path: Directory to store index and metadata
            dimension: Embedding dimension (default 384 for all-MiniLM-L6-v2)
        """
        self.store_path = Path(store_path)
        self.store_path.mkdir(exist_ok=True)
        self.dimension = dimension
        
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        
        self._init_index()
        self._load_metadata()
    
    def _init_index(self):
        """Initialize or load FAISS index."""
        index_path = self.store_path / "syllabus.index"
        
        if faiss and index_path.exists():
            self.index = faiss.read_index(str(index_path))
        elif faiss:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine sim
        else:
            self.index = []  # Fallback to list
    
    def _load_metadata(self):
        """Load metadata from disk."""
        meta_path = self.store_path / "syllabus_meta.json"
        if meta_path.exists():
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)
    
    def _save(self):
        """Save index and metadata to disk."""
        if faiss and self.index:
            faiss.write_index(self.index, str(self.store_path / "syllabus.index"))
        
        with open(self.store_path / "syllabus_meta.json", "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def add_embeddings(
        self,
        embeddings: List[List[float]],
        metadata_list: List[Dict[str, Any]]
    ):
        """
        Add syllabus topic embeddings to the store.
        
        Args:
            embeddings: List of embedding vectors
            metadata_list: List of metadata dicts (unit_number, unit_title, topic)
        """
        if not embeddings:
            return
        
        vectors = np.array(embeddings, dtype=np.float32)
        
        # Normalize for cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / (norms + 1e-9)
        
        if faiss:
            self.index.add(vectors)
        else:
            self.index.extend(vectors.tolist())
        
        self.metadata.extend(metadata_list)
        self._save()
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar syllabus topics.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            
        Returns:
            List of matched topics with scores
        """
        query = np.array([query_embedding], dtype=np.float32)
        query = query / (np.linalg.norm(query) + 1e-9)
        
        if faiss and self.index.ntotal > 0:
            scores, indices = self.index.search(query, min(top_k, self.index.ntotal))
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.metadata):
                    result = self.metadata[idx].copy()
                    result["score"] = float(score)
                    results.append(result)
            return results
        elif not faiss and self.index:
            # Numpy fallback
            index_array = np.array(self.index, dtype=np.float32)
            scores = np.dot(index_array, query.T).flatten()
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [
                {**self.metadata[i], "score": float(scores[i])}
                for i in top_indices if i < len(self.metadata)
            ]
        
        return []
    
    def get_all_units(self) -> List[Dict[str, Any]]:
        """Get all unique units in the syllabus."""
        units = {}
        for meta in self.metadata:
            unit_num = meta.get("unit_number")
            if unit_num not in units:
                units[unit_num] = {
                    "number": unit_num,
                    "title": meta.get("unit_title", ""),
                    "topics": []
                }
            units[unit_num]["topics"].append(meta.get("topic", ""))
        return list(units.values())
    
    def clear(self):
        """Clear the vector store."""
        self._init_index()
        self.metadata = []
        self._save()
    
    @property
    def count(self) -> int:
        """Number of embeddings in store."""
        if faiss:
            return self.index.ntotal if self.index else 0
        return len(self.index)


# CLI for testing
if __name__ == "__main__":
    store = SyllabusVectorStore("test_syllabus_index")
    print(f"Store initialized with {store.count} embeddings")
    print(f"Units: {store.get_all_units()}")
