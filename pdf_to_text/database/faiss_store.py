import faiss
import numpy as np
import pickle
import json
import uuid

class FAISSStore:
    def __init__(self, dim=384, index_path="vector.index", meta_path="meta.pkl", json_path="text_chunks.json"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.json_path = json_path

        self.index = faiss.IndexFlatIP(dim)  # cosine similarity
        self.texts = []

    def store(self, chunks, embeddings, source_file="unknown.pdf"):
        vectors = np.array(embeddings).astype("float32")
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.texts.extend(chunks)

        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.texts, f)

        # Also save as JSON for Multi-Modal Preprocessor
        json_chunks = []
        for i, chunk in enumerate(chunks):
            json_chunks.append({
                "chunk_id": f"pdf_{uuid.uuid4().hex[:8]}",
                "source_type": "pdf",
                "source_file": source_file,
                "content": chunk,
                "modality": "text",
                "metadata": {
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
        with open(self.json_path, "w") as f:
            json.dump(json_chunks, f, indent=2)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.texts = pickle.load(f)

    def search(self, query_vector, k=5):
        q = np.array([query_vector]).astype("float32")
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        return [self.texts[i] for i in I[0]]

