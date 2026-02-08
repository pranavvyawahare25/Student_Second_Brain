from sentence_transformers import SentenceTransformer

# Try to import from config, fallback to default
try:
    from pdf_to_text.config import EMBEDDING_MODEL
except ImportError:
    try:
        from config import EMBEDDING_MODEL
    except ImportError:
        EMBEDDING_MODEL = "all-MiniLM-L6-v2"

class Embedder:
    def __init__(self, model_name: str = None):
        self.model = SentenceTransformer(model_name or EMBEDDING_MODEL)

    def embed(self, texts):
        return self.model.encode(texts, normalize_embeddings=True).tolist()

