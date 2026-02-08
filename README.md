# Student Second Brain 🧠

A comprehensive AI-powered knowledge management system that ingests handwritten notes, documents, and multimedia to create a unified knowledge graph. It features advanced RAG (Retrieval-Augmented Generation), web research capabilities, and LLM-powered summarization.

## 🌟 Key Features

### 1. **Handwritten Notes Processor** ✍️
- **OCR & Text Extraction:** Converts handwritten text to digital text using Tesseract.
- **Diagram Detection:** Identifies and extracts diagrams/sketches from notes.
- **Layout Analysis:** Preserves the structure of the original notes.

### 2. **Multimodal Ingestion** 📚
- **Documents:** PDF processing with `pdf2image` and metadata extraction.
- **Multimedia:** Video and Audio transcription (integrating with optional Whisper models).
- **Images:** Text extraction from images.

### 3. **Knowledge Graph & RAG** 🕸️
- **Unified Schema:** Consolidates all data into a structured JSON graph.
- **Vector Search:** Uses `sentence-transformers` (all-MiniLM-L6-v2) and `FAISS` for semantic search.
- **Contextual Retrieval:** Retrieves relevant knowledge chunks based on query similarity.

### 4. **Web Extractor & Research Agent** 🌍
- **Smart Web Search:** Fetches categorized content (Wikipedia, Papers, Tutorials) via **Brave Search API**.
- **YouTube Integration:** Discovers high-quality educational videos with metadata via **YouTube Data API**.
- **Image Search:** Finds relevant diagrams and visual aids with source context.

### 5. **AI Summarization & Insights** 🤖
- **LLM Powered:** Uses **Groq API (Llama 3.3 70B)** to synthesize information.
- **Structured Knowledge:** Generates:
    - Key Concepts & Definitions
    - Step-by-Step Explanations
    - Practical To-Dos
    - Common Mistakes
    - Learning Roadmaps
    - Curated Resource Links

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- **Tesseract OCR:** `brew install tesseract`
- **Poppler:** `brew install poppler` (for PDF processing)
- **Git**

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pranavvyawahare25/Student_Second_Brain.git
    cd Student_Second_Brain
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    # Search APIs
    BRAVE_API_KEY=your_brave_api_key_here
    YOUTUBE_API_KEY=your_youtube_api_key_here

    # LLM API (Groq)
    GROQ_API_KEY=your_groq_api_key_here

    # Optional: For Gemini (if switching models)
    # GEMINI_API_KEY=your_gemini_api_key_here
    ```

---

## 🛠️ Usage

### Start the API Server
Run the FastAPI server to access all features:
```bash
python -m api.server
```
*The server will start at `http://localhost:8000` (and provide a public `ngrok` URL if configured).*

### API Endpoints

#### 🔍 Research & Summarization
-   **Get Complete Research (Data + Insights):**
    `GET /research?topic=vector+databases`
-   **Get Quick Summary (Insights Only):**
    `GET /summarize?topic=vector+databases`

#### 🌍 Web Discovery
-   **Search Web Topics:** `GET /discover?topic=machine+learning`
-   **Search Specifically:**
    -   `/discover/papers?topic=...`
    -   `/discover/guides?topic=...`
    -   `/discover/images?topic=...`

#### 📺 YouTube Search
-   **Find Videos:** `GET /youtube?topic=python+tutorial`
-   **Filter by Type:**
    -   `/youtube/tutorials` (Medium length)
    -   `/youtube/courses` (Long length)
    -   `/youtube/shorts` (Short length)

#### 🧠 RAG / Knowledge Base
-   **Search Local Knowledge:** `GET /search?q=my+notes+on+physics`
-   **Get Embeddings:** `POST /embed`
-   **System Stats:** `GET /rag/stats`

---

## 📂 Project Structure

```
Student_Second_Brain/
├── api/                    # FastAPI server & endpoints
├── handwritten_notes_processor/ # OCR & Diagram processing
│   ├── text_pipeline/      # Text extraction logic
│   ├── diagram_pipeline/   # Diagram detection logic
│   └── knowledge_pipeline/ # Graph construction
├── multimodal_preprocessor/ # PDF, Video, Audio adapters
│   └── rag/                # Vector store & Embedding logic
├── web_extractor/          # Web search & AI summarization
│   ├── brave_search.py     # Brave API client
│   ├── youtube_search.py   # YouTube API client
│   └── summarizer.py       # Groq/Llama summarization logic
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License
MIT License