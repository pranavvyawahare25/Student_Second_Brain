"""
FAISS Vector Store for Unified Knowledge Base

Stores embeddings and metadata for semantic search across
all knowledge sources (handwritten notes, PDFs, audio, video).
"""

import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

try:
    import faiss
except ImportError:
    raise ImportError("Please install faiss: pip install faiss-cpu")


class UnifiedVectorStore:
    """FAISS-based vector store for unified knowledge."""
    
    def __init__(
        self,
        index_path: str = "unified_index.faiss",
        meta_path: str = "unified_meta.pkl",
        embedding_dim: int = 384  # Default for all-MiniLM-L6-v2
    ):
        """
        Initialize vector store.
        
        Args:
            index_path: Path to save/load FAISS index.
            meta_path: Path to save/load metadata.
            embedding_dim: Dimension of embeddings.
        """
        self.index_path = Path(index_path)
        self.meta_path = Path(meta_path)
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata = []
        self.chunk_ids = []
    
    def build_index(
        self,
        embeddings: np.ndarray,
        chunk_ids: List[str],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Build FAISS index from embeddings.
        
        Args:
            embeddings: numpy array of shape (n, embedding_dim)
            chunk_ids: List of chunk IDs
            metadata: List of metadata dicts
        """
        n_embeddings, dim = embeddings.shape
        print(f"Building FAISS index with {n_embeddings} embeddings of dim {dim}...")
        
        # Use L2 distance index
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype(np.float32))
        
        self.chunk_ids = chunk_ids
        self.metadata = metadata
        self.embedding_dim = dim
        
        print(f"Index built. Total vectors: {self.index.ntotal}")
    
    def save(self) -> None:
        """Save index and metadata to disk."""
        if self.index is None:
            raise ValueError("No index to save. Build index first.")
        
        faiss.write_index(self.index, str(self.index_path))
        
        with open(self.meta_path, "wb") as f:
            pickle.dump({
                "chunk_ids": self.chunk_ids,
                "metadata": self.metadata,
                "embedding_dim": self.embedding_dim
            }, f)
        
        print(f"Saved index to {self.index_path}")
        print(f"Saved metadata to {self.meta_path}")
    
    def load(self) -> bool:
        """
        Load index and metadata from disk.
        
        Returns:
            True if loaded successfully, False otherwise.
        """
        if not self.index_path.exists() or not self.meta_path.exists():
            return False
        
        self.index = faiss.read_index(str(self.index_path))
        
        with open(self.meta_path, "rb") as f:
            data = pickle.load(f)
            self.chunk_ids = data["chunk_ids"]
            self.metadata = data["metadata"]
            self.embedding_dim = data.get("embedding_dim", 384)
        
        print(f"Loaded index with {self.index.ntotal} vectors")
        return True
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks.
        
        Args:
            query_embedding: Query embedding of shape (embedding_dim,) or (1, embedding_dim)
            top_k: Number of results to return.
            
        Returns:
            List of result dicts with 'chunk_id', 'score', 'metadata'
        """
        if self.index is None:
            raise ValueError("No index loaded. Build or load index first.")
        
        # Ensure correct shape
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0:  # FAISS returns -1 for not found
                continue
            results.append({
                "chunk_id": self.chunk_ids[idx],
                "score": float(1 / (1 + dist)),  # Convert L2 distance to similarity score
                "distance": float(dist),
                "metadata": self.metadata[idx]
            })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        if self.index is None:
            return {"status": "not_loaded"}
        
        # Count by source type
        source_counts = {}
        for meta in self.metadata:
            source = meta.get("source_type", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        
        return {
            "total_vectors": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "source_counts": source_counts,
            "index_path": str(self.index_path),
            "meta_path": str(self.meta_path)
        }


def build_unified_vector_store(
    embeddings: np.ndarray,
    chunk_ids: List[str],
    metadata: List[Dict[str, Any]],
    output_dir: str = "."
) -> UnifiedVectorStore:
    """
    Build and save unified vector store.
    
    Args:
        embeddings: Embeddings array
        chunk_ids: List of chunk IDs
        metadata: List of metadata dicts
        output_dir: Directory to save index and metadata
        
    Returns:
        UnifiedVectorStore instance
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    store = UnifiedVectorStore(
        index_path=str(output_dir / "unified_index.faiss"),
        meta_path=str(output_dir / "unified_meta.pkl")
    )
    
    store.build_index(embeddings, chunk_ids, metadata)
    store.save()
    
    return store
