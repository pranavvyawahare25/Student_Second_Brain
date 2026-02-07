📚 PDF → Vector Search (Local RAG Backend)

A backend system that converts uploaded PDFs into vector embeddings using open-source models and stores them locally for semantic search.

Built with FastAPI + FAISS + HuggingFace embeddings.

🚀 Features

Upload PDFs via API

Extract text from PDF

Split text into chunks

Convert chunks → vector embeddings

Store vectors locally (no cloud DB)

Query using semantic similarity

🧠 Tech Stack
Purpose	Tool
Backend API	FastAPI
PDF Text Extraction	PyMuPDF
Embeddings	BAAI/bge-small-en-v1.5 (HuggingFace)
Vector Database	FAISS
Language	Python
📁 Project Structure
pdf-rag/
│
├── app.py
├── config.py
│
├── ingestion/
│   ├── pdf_loader.py
│   ├── text_splitter.py
│   └── embedder.py
│
├── database/
│   └── faiss_store.py
│
├── uploads/
├── vector.index
├── meta.pkl
└── requirements.txt

⚙️ Installation
git clone <repo>
cd pdf-rag
pip install -r requirements.txt

▶ Run Server
uvicorn app:app --reload


Open API docs:

http://127.0.0.1:8000/docs

📤 Upload a PDF

Endpoint:

POST /upload-pdf


Process:

File saved temporarily

Text extracted

Chunked

Embeddings generated

Stored in FAISS index

Files created:

vector.index   # Embeddings
meta.pkl       # Text chunks

🔍 Query the System

Endpoint:

GET /query?question=your_question


Returns top-matching text chunks from uploaded PDFs.

🧩 How It Works
PDF → Text → Chunks → Embeddings → FAISS Index


Vectors are normalized and stored locally.
Each vector maps to a text chunk for retrieval.

📌 Notes

Works fully offline

No MongoDB or cloud required

Best for development and prototyping RAG systems

🔮 Future Improvements

Add LLM response generation

Support multiple PDFs

Add user sessions

Deploy to cloud
