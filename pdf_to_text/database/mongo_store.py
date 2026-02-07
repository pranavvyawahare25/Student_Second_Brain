from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME

class MongoVectorStore:
    def __init__(self):
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        self.collection = db[COLLECTION_NAME]

    def store(self, chunks, embeddings):
        docs = []
        for i, chunk in enumerate(chunks):
            docs.append({
                "text": chunk,
                "embedding": embeddings[i].tolist()
            })
        self.collection.insert_many(docs)

    def search(self, query_vector, limit=5):
        results = self.collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": limit,
                    "index": "default"
                }
            }
        ])
        return [r["text"] for r in results]
