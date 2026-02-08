# Student Second Brain 🧠

A comprehensive AI-powered knowledge management system that ingests handwritten notes, documents, and multimedia to create a unified knowledge graph. It features advanced RAG (Retrieval-Augmented Generation), web research capabilities, and LLM-powered summarization.

## 🌟 **MAIN FEATURE: Native Indian Language Support** 🇮🇳

This system has **built-in support for Indian languages**, making it uniquely suited for Indian students:

- 🎤 **Audio/Video Transcription in 10+ Indian Languages** using Sarvam AI Saaras v2.5
  - Hindi, Tamil, Telugu, Marathi, Bengali, Kannada, Malayalam, Gujarati, Punjabi, and more
  - Automatic language detection and translation to English
  - Preserves original language with metadata
  
- ✍️ **Handwritten Notes in Indian Scripts** via PaddleOCR
  - Supports Devanagari, Tamil, Telugu, Bengali, and other Indian scripts
  - OCR for 80+ languages including all major Indian languages

- 🤖 **Language-Aware Summarization**
  - Processes Indian language content and generates English summaries
  - Maintains cultural and linguistic context

**See [PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md) for complete architecture details and Indian language features.**

**Quick Start? See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for a condensed guide with all models and API endpoints.**

## 🌟 Key Features

### 1. **Handwritten Notes Processor** ✍️
- **OCR & Text Extraction:** Converts handwritten text to digital text using Azure Form Recognizer (production) or PaddleOCR (supports 80+ languages including Indian scripts).
- **Diagram Detection:** Identifies and extracts diagrams/sketches from notes using OpenCV.
- **Layout Analysis:** Preserves the structure of the original notes.

### 2. **Multimodal Ingestion** 📚
- **Documents:** PDF processing with `pdf2image` and metadata extraction.
- **Multimedia:** 
  - **Audio/Video Transcription:** Uses Sarvam AI Saaras v2.5 for Indian language audio (Hindi, Tamil, Telugu, etc.)
  - **Automatic Translation:** Converts Indian language content to English while preserving original
- **Images:** Text extraction from images with multi-language support.

### 3. **Indian Language Processing** 🇮🇳
- **Speech-to-Text:** Sarvam AI Saaras v2.5 model supports 10+ Indian languages
- **Auto-Detection:** Automatically detects which Indian language is being spoken
- **Translation:** Translates to English for universal accessibility
- **Metadata Preservation:** Keeps language_code and original content
- **OCR Support:** PaddleOCR ready for handwritten Indian scripts (Hindi, Tamil, Telugu, Bengali, Kannada, Malayalam, Gujarati, Punjabi)

### 3. **Knowledge Graph & RAG** 🕸️
- **Unified Schema:** Consolidates all data into a structured JSON graph with language metadata.
- **Vector Search:** Uses `sentence-transformers` (all-MiniLM-L6-v2, 384-dim embeddings) and `FAISS` for semantic search.
- **Contextual Retrieval:** Retrieves relevant knowledge chunks based on query similarity.
- **Multilingual Support:** Searches across content in any language (embedded as English).

### 4. **Web Extractor & Research Agent** 🌍
- **Smart Web Search:** Fetches categorized content (Wikipedia, Papers, Tutorials) via **Brave Search API**.
- **YouTube Integration:** Discovers high-quality educational videos with metadata via **YouTube Data API v3**.
- **Image Search:** Finds relevant diagrams and visual aids with source context.

### 5. **AI Summarization & Insights** 🤖
- **LLM Powered:** Uses **Groq API (Llama 3.3 70B Versatile)** to synthesize information.
- **Language-Aware:** Processes Indian language content and generates structured English summaries
- **Structured Knowledge:** Generates:
    - Key Concepts & Definitions (5-8 items)
    - Step-by-Step Explanations (5-7 steps)
    - Practical To-Dos (5-7 actions)
    - Common Mistakes (4-6 pitfalls)
    - Learning Roadmaps (4-6 stages)
    - Curated Resource Links

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- **Tesseract OCR** (optional): `brew install tesseract`
- **Poppler:** `brew install poppler` (for PDF processing)
- **Git**
- **API Keys Required:**
  - Sarvam AI API key (for Indian language audio processing)
  - Groq API key (for summarization)
  - Brave Search API key (optional, for web discovery)
  - YouTube Data API key (optional, for video search)
  - Azure Form Recognizer credentials (optional, for production OCR)

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
    # Indian Language Support (REQUIRED for audio processing)
    SARVAM_API_KEY=your_sarvam_api_key_here
    
    # LLM API (REQUIRED for summarization)
    GROQ_API_KEY=your_groq_api_key_here
    
    # Search APIs (Optional)
    BRAVE_API_KEY=your_brave_api_key_here
    YOUTUBE_API_KEY=your_youtube_api_key_here
    
    # Azure OCR (Optional - for production handwritten notes)
    AZURE_FORM_RECOGNIZER_ENDPOINT=your_azure_endpoint
    AZURE_FORM_RECOGNIZER_KEY=your_azure_key
    
    # Alternative: For Gemini (if switching models)
    # GEMINI_API_KEY=your_gemini_api_key_here
    ```
    
    **Get API Keys:**
    - **Sarvam AI:** https://www.sarvam.ai/ (for Indian language support)
    - **Groq:** https://console.groq.com/
    - **Brave Search:** https://brave.com/search/api/
    - **YouTube Data API:** https://console.cloud.google.com/
    - **Azure:** https://portal.azure.com/

---

## 🛠️ Usage

### Start the API Server
Run the FastAPI server to access all features:
```bash
python -m api.server
```
*The server will start at `http://localhost:8000` (and provide a public `ngrok` URL if configured).*

### Run the Frontend 💻
The project includes a React frontend for easy interaction.

1.  **Navigate to frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Start development server:**
    ```bash
    npm run dev
    ```
    *Access the UI at `http://localhost:5173`*

    > **Note:** Ensure the backend server is running first!

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

#### 🇮🇳 Indian Language Processing
-   **Upload Audio (Hindi/Tamil/Telugu/etc.):** `POST /upload/audio`
    - Automatically detects Indian language
    - Transcribes and translates to English
    - Stores both original and translated versions
-   **Example:**
    ```bash
    curl -X POST http://localhost:8000/upload/audio \
      -F "file=@lecture_hindi.mp3"
    ```
-   **Response includes:**
    - `language_code`: Detected language (e.g., "hi-IN")
    - `transcript_original`: Text in original language
    - `transcript_english`: English translation
    - `summary`: AI-generated insights

---

## 🇮🇳 Using Indian Languages

### Supported Languages
This system natively supports **10+ Indian languages**:
- Hindi (हिन्दी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Marathi (मराठी)
- Bengali (বাংলা)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Gujarati (ગુજરાતી)
- Punjabi (ਪੰਜਾਬੀ)
- And more...

### How to Use

1. **Upload Indian Language Audio:**
   ```bash
   # Upload a Hindi lecture
   python -m speech_to_text.speech_to_text lecture_hindi.mp3
   
   # Or via API
   curl -X POST http://localhost:8000/upload/audio \
     -F "file=@lecture_tamil.mp3"
   ```

2. **The System Automatically:**
   - Detects the language (Hindi, Tamil, etc.)
   - Transcribes the audio in the original language
   - Translates to English for searchability
   - Stores both versions with language metadata

3. **Search Across Languages:**
   ```bash
   # Search in English, find Hindi content
   curl "http://localhost:8000/search?q=machine+learning"
   
   # Results include content from all languages
   ```

4. **Get Summarized Insights:**
   ```bash
   # Summarize mixed-language content
   curl "http://localhost:8000/research?topic=neural+networks"
   ```

### For Handwritten Notes in Indian Scripts

**Currently:** Azure Form Recognizer (English-focused)

**To Enable PaddleOCR for Indian Languages:**
1. Edit `handwritten_notes_processor/test_ocr_minimal.py`
2. Change: `lang='en'` to `lang='hi'` (Hindi) or `lang=['hi','ta','te']` (multiple)
3. Supports: Devanagari, Tamil, Telugu, Bengali, Kannada, Malayalam, Gujarati, Gurmukhi

**Example:**
```python
# Single language (Hindi)
ocr = PaddleOCR(use_angle_cls=True, lang='hi', use_gpu=False)

# Multiple languages
ocr = PaddleOCR(use_angle_cls=True, lang=['hi','ta','te'], use_gpu=False)
```

---

## 📂 Project Structure

```
Student_Second_Brain/
├── api/                    # FastAPI server & endpoints
├── handwritten_notes_processor/ # OCR & Diagram processing
│   ├── text_pipeline/      # Text extraction (Azure/PaddleOCR)
│   ├── diagram_pipeline/   # Diagram detection (OpenCV)
│   ├── fusion/             # Text-diagram spatial matching
│   ├── graph_pipeline/     # Graph refinement & deduplication
│   └── knowledge_pipeline/ # Schema generation
├── multimodal_preprocessor/ # PDF, Video, Audio adapters
│   ├── adapters/           # Format-specific processors
│   └── rag/                # Vector store & Embedding (FAISS + sentence-transformers)
├── speech_to_text/         # 🇮🇳 Sarvam AI Indian language transcription
├── web_extractor/          # Web search & AI summarization
│   ├── brave_search.py     # Brave API client
│   ├── youtube_search.py   # YouTube API client
│   └── summarizer.py       # Groq Llama 3.3 70B summarization
├── frontend/               # React UI (Vite + Clerk auth)
├── PIPELINE_DOCUMENTATION.md # 📚 Complete architecture & model details
├── ARCHITECTURE_GUIDE.md   # Detailed design rationale
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

## 📚 Documentation

- **[PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)** - Complete pipeline architecture, all models used, and detailed Indian language support explanation
- **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - Design philosophy and technical walkthrough
- **[README.md](README.md)** - This file (quick start guide)

## 🔧 Technologies & Models Used

### Core Models
- **OCR:** Azure Form Recognizer (handwritten text) + PaddleOCR (80+ languages)
- **Indian Language STT:** Sarvam AI Saaras v2.5
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2, 384-dim)
- **Vector DB:** FAISS (Facebook AI Similarity Search)
- **LLM:** Groq API - Llama 3.3 70B Versatile
- **Computer Vision:** OpenCV (Canny, Contours)
- **Graph Processing:** NetworkX

### APIs & Services
- Brave Search API (web discovery)
- YouTube Data API v3 (video search)
- Sarvam AI (Indian language processing)
- Groq (LLM inference)
- Azure Cognitive Services (optional)

## 📖 Documentation Index

1. **[README.md](README.md)** (This file) - Installation, setup, and basic usage
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick start guide with all models and API endpoints
3. **[PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)** - Complete technical architecture and Indian language features
4. **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - Design philosophy and detailed walkthrough

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## 📄 License
MIT License