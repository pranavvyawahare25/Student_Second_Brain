import os
from fastapi import FastAPI, UploadFile, File
from ingestion.pdf_loder import extract_text_from_pdf
from ingestion.text_spliter import split_text
from ingestion.embedder import Embedder
# from database.mongo_store import MongoVectorStore
from database.faiss_store import FAISSStore


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()
embedder = Embedder()
store = FAISSStore()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # 🔥 Process PDF
    text = extract_text_from_pdf(file_path)
    chunks = split_text(text)
    embeddings = embedder.embed(chunks)
    store.store(chunks, embeddings, source_file=file.filename)

    # Optional: delete after processing
    os.remove(file_path)

    return {"message": "PDF converted to vectors and stored in MongoDB"}
