"""
Embedder for Unified Knowledge Base

Generates embeddings for all chunks in unified_knowledge.json
using sentence-transformers.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Please install sentence-transformers: pip install sentence-transformers")


class UnifiedEmbedder:
    """Generate embeddings for unified knowledge chunks."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder.
        
        Args:
            model_name: Sentence transformer model name.
                       Default: all-MiniLM-L6-v2 (fast, good quality)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Embed multiple texts.
        
        Args:
            texts: List of text strings to embed.
            batch_size: Batch size for encoding.
            
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        return self.model.encode(texts, batch_size=batch_size, convert_to_numpy=True, show_progress_bar=True)
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> tuple:
        """
        Embed chunks from unified knowledge format.
        
        Args:
            chunks: List of chunk dicts with 'content' field.
            
        Returns:
            Tuple of (embeddings, chunk_ids, metadata)
        """
        texts = []
        chunk_ids = []
        metadata = []
        
        for chunk in chunks:
            content = chunk.get("content", "")
            if content.strip():  # Skip empty chunks
                texts.append(content)
                chunk_ids.append(chunk.get("chunk_id", "unknown"))
                metadata.append({
                    "source_type": chunk.get("source_type", "unknown"),
                    "source_file": chunk.get("source_file", "unknown"),
                    "modality": chunk.get("modality", "text"),
                    "chunk_id": chunk.get("chunk_id", "unknown")
                })
        
        print(f"Embedding {len(texts)} chunks...")
        embeddings = self.embed_texts(texts)
        
        return embeddings, chunk_ids, metadata
    
    def load_and_embed(self, unified_json_path: str) -> tuple:
        """
        Load unified_knowledge.json and generate embeddings.
        
        Args:
            unified_json_path: Path to unified_knowledge.json
            
        Returns:
            Tuple of (embeddings, chunk_ids, metadata)
        """
        with open(unified_json_path, "r") as f:
            data = json.load(f)
        
        chunks = data.get("chunks", [])
        print(f"Loaded {len(chunks)} chunks from {unified_json_path}")
        
        return self.embed_chunks(chunks)


# Convenience function
def embed_unified_knowledge(json_path: str, model_name: str = "all-MiniLM-L6-v2") -> tuple:
    """
    Load and embed unified knowledge.
    
    Args:
        json_path: Path to unified_knowledge.json
        model_name: Sentence transformer model name
        
    Returns:
        Tuple of (embeddings, chunk_ids, metadata)
    """
    embedder = UnifiedEmbedder(model_name)
    return embedder.load_and_embed(json_path)
