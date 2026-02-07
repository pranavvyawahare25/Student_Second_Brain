import pickle

with open("meta.pkl", "rb") as f:
    texts = pickle.load(f)

print("Total chunks stored:", len(texts))

print("\n===== FIRST 5 CHUNKS =====\n")
for i, chunk in enumerate(texts[:5]):
    print(f"\n--- Chunk {i+1} ---\n")
    print(chunk)
