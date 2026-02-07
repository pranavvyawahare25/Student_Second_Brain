from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)

    def embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True)
