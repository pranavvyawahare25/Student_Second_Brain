import os
import json
from handwritten_notes_processor.knowledge_pipeline.vector_store import VectorStore

OUTPUT_DIR = "output_artifacts"

def verify_vector_store():
    print("Verifying Vector Store...")
    
    # 1. Load Store
    store = VectorStore()
    store.load(OUTPUT_DIR)
    
    if not store.index or not store.metadata:
        print("❌ Error: Vector Store not found or empty.")
        return

    print(f"✅ Loaded {len(store.metadata)} documents from index.")
    
    # 2. Test Queries
    queries = [
        "What is machine learning?",
        "What does Tom Mitchell say?",
        "What are the types of models?"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        results = store.search(q, k=1)
        if results:
            top = results[0]
            print(f"  Top Match (Score: {top['score']:.4f}):")
            print(f"  Content: {top['chunk']['content'][:100]}...")
        else:
            print("  No results found.")

if __name__ == "__main__":
    verify_vector_store()
