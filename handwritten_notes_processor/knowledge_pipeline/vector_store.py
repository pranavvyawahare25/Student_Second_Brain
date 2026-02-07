import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = [] # List of dicts, parallel to index
        self.dimension = 0

    def add_documents(self, documents):
        """
        Args:
            documents (list): List of dicts, each must have 'content'.
                              Other fields (chunk_id, metadata) are stored as payload.
        """
        if not documents:
            return

        texts = [doc['content'] for doc in documents]
        embeddings = self.model.encode(texts)
        
        if self.index is None:
            self.dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)
            
        self.index.add(np.array(embeddings).astype('float32'))
        self.metadata.extend(documents)
        print(f"Added {len(documents)} documents to VectorStore.")

    def search(self, query, k=3):
        if not self.index:
            return []
            
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                item = self.metadata[idx]
                results.append({
                    "score": float(distances[0][i]),
                    "chunk": item
                })
        return results

    def save(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Save Index
        index_path = os.path.join(output_dir, "knowledge.index")
        if self.index:
            faiss.write_index(self.index, index_path)
        
        # Save Metadata
        meta_path = os.path.join(output_dir, "knowledge_meta.json")
        with open(meta_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
            
        print(f"Vector Store saved to {output_dir}")

    def load(self, input_dir):
        index_path = os.path.join(input_dir, "knowledge.index")
        meta_path = os.path.join(input_dir, "knowledge_meta.json")
        
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                self.metadata = json.load(f)
