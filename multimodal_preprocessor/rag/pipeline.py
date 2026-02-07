"""
RAG Pipeline for Unified Knowledge Base

End-to-end pipeline for:
1. Loading unified_knowledge.json
2. Generating embeddings
3. Building FAISS vector store
4. Semantic search
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from .embedder import UnifiedEmbedder
from .vector_store import UnifiedVectorStore


class UnifiedRAG:
    """
    Complete RAG pipeline for unified knowledge.
    
    Usage:
        rag = UnifiedRAG()
        rag.build_from_json("unified_knowledge.json")
        results = rag.search("What is machine learning?")
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_dir: str = "rag_index"
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            model_name: Sentence transformer model name.
            index_dir: Directory to store FAISS index.
        """
        self.model_name = model_name
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        
        self.embedder = None
        self.store = None
        self.chunks = []  # Store original chunks for retrieval
    
    def _init_embedder(self):
        """Lazy initialization of embedder."""
        if self.embedder is None:
            self.embedder = UnifiedEmbedder(self.model_name)
    
    def build_from_json(self, json_path: str) -> Dict[str, Any]:
        """
        Build vector store from unified_knowledge.json.
        
        Args:
            json_path: Path to unified_knowledge.json
            
        Returns:
            Build stats dict
        """
        self._init_embedder()
        
        # Load chunks
        with open(json_path, "r") as f:
            data = json.load(f)
        
        self.chunks = data.get("chunks", [])
        print(f"Loaded {len(self.chunks)} chunks")
        
        # Generate embeddings
        embeddings, chunk_ids, metadata = self.embedder.embed_chunks(self.chunks)
        
        # Build vector store
        self.store = UnifiedVectorStore(
            index_path=str(self.index_dir / "unified_index.faiss"),
            meta_path=str(self.index_dir / "unified_meta.pkl")
        )
        self.store.build_index(embeddings, chunk_ids, metadata)
        self.store.save()
        
        # Save chunks for lookup
        with open(self.index_dir / "chunks.json", "w") as f:
            json.dump({"chunks": self.chunks}, f, indent=2)
        
        return self.store.get_stats()
    
    def load(self) -> bool:
        """
        Load existing vector store.
        
        Returns:
            True if loaded successfully
        """
        self._init_embedder()
        
        self.store = UnifiedVectorStore(
            index_path=str(self.index_dir / "unified_index.faiss"),
            meta_path=str(self.index_dir / "unified_meta.pkl")
        )
        
        if not self.store.load():
            return False
        
        # Load chunks
        chunks_path = self.index_dir / "chunks.json"
        if chunks_path.exists():
            with open(chunks_path, "r") as f:
                data = json.load(f)
                self.chunks = data.get("chunks", [])
        
        return True
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        include_content: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant chunks.
        
        Args:
            query: Search query string
            top_k: Number of results
            include_content: Whether to include chunk content in results
            
        Returns:
            List of result dicts
        """
        if self.store is None:
            raise ValueError("No vector store loaded. Call build_from_json() or load() first.")
        
        self._init_embedder()
        
        # Embed query
        query_embedding = self.embedder.embed_text(query)
        
        # Search
        results = self.store.search(query_embedding, top_k)
        
        # Add content if requested
        if include_content:
            chunk_map = {c.get("chunk_id"): c for c in self.chunks}
            for result in results:
                chunk_id = result["chunk_id"]
                if chunk_id in chunk_map:
                    result["content"] = chunk_map[chunk_id].get("content", "")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG pipeline statistics."""
        if self.store is None:
            return {"status": "not_initialized"}
        
        stats = self.store.get_stats()
        stats["total_chunks"] = len(self.chunks)
        stats["model_name"] = self.model_name
        return stats


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified RAG Pipeline")
    parser.add_argument("--build", type=str, help="Path to unified_knowledge.json to build index")
    parser.add_argument("--search", type=str, help="Query to search")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("--index-dir", type=str, default="rag_index", help="Index directory")
    
    args = parser.parse_args()
    
    rag = UnifiedRAG(index_dir=args.index_dir)
    
    if args.build:
        print(f"Building index from {args.build}...")
        stats = rag.build_from_json(args.build)
        print(f"Build complete: {stats}")
    
    if args.search:
        if not args.build:
            rag.load()
        
        print(f"\nSearching for: {args.search}")
        results = rag.search(args.search, top_k=args.top_k)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {result['score']:.3f}) ---")
            print(f"Source: {result['metadata']['source_type']} - {result['metadata']['source_file']}")
            print(f"Content: {result.get('content', 'N/A')[:200]}...")
