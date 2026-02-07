import faiss
import numpy as np
import pickle

class FAISSStore:
    def __init__(self, dim=384, index_path="vector.index", meta_path="meta.pkl"):
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path

        self.index = faiss.IndexFlatIP(dim)  # cosine similarity
        self.texts = []

    def store(self, chunks, embeddings):
        vectors = np.array(embeddings).astype("float32")
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.texts.extend(chunks)

        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.texts, f)

    def load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            self.texts = pickle.load(f)

    def search(self, query_vector, k=5):
        q = np.array([query_vector]).astype("float32")
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        return [self.texts[i] for i in I[0]]
