# Student Second Brain - Quick Reference Guide

## 🚀 What is this?
An **AI-powered knowledge management system** for students that processes handwritten notes, PDFs, videos, and audio (especially **Indian languages**) into a searchable knowledge base.

---

## 🌟 Main Feature: Indian Language Support 🇮🇳

### Supported Languages (10+)
Hindi • Tamil • Telugu • Marathi • Bengali • Kannada • Malayalam • Gujarati • Punjabi • and more

### How It Works
1. Upload audio/video in any Indian language
2. System auto-detects language (e.g., Hindi, Tamil)
3. Transcribes in original language
4. Translates to English
5. Both versions stored and searchable

---

## 🔧 Core Models & Technologies

| Component | Technology | What It Does |
|-----------|-----------|--------------|
| **Indian Language STT** | Sarvam AI Saaras v2.5 | Transcribes Hindi, Tamil, Telugu, etc. + translates to English |
| **Handwritten OCR** | Azure Form Recognizer | Extracts text from handwritten notes |
| **Multi-language OCR** | PaddleOCR (80+ langs) | Supports Indian scripts (Devanagari, Tamil, Telugu, etc.) |
| **Diagram Detection** | OpenCV (Canny, Contours) | Finds shapes, arrows in notes |
| **Text Embeddings** | sentence-transformers all-MiniLM-L6-v2 | Converts text to 384-dim vectors |
| **Vector Search** | FAISS | Fast similarity search |
| **AI Summarization** | Groq Llama 3.3 70B Versatile | Generates structured insights |
| **Web Search** | Brave Search API | Categorized web results |
| **Video Search** | YouTube Data API v3 | Educational video discovery |
| **Graph Processing** | NetworkX | Knowledge graph operations |

---

## 📊 Pipeline Stages

```
1. INPUT
   ↓ Upload files (images, PDFs, audio, video)
   
2. PARALLEL PROCESSING
   ↓ Text Pipeline: OCR (Azure/PaddleOCR)
   ↓ Diagram Pipeline: Shape detection (OpenCV)
   ↓ Audio Pipeline: Transcription (Sarvam AI for Indian languages)
   
3. FUSION
   ↓ Match text to shapes using spatial proximity
   
4. CONSOLIDATION
   ↓ Group fragments into paragraphs & diagrams
   
5. REFINEMENT
   ↓ Deduplicate, canonicalize, infer semantics
   
6. UNIFIED SCHEMA
   ↓ Convert to standard JSON format with metadata
   
7. VECTOR STORE
   ↓ Embed text (all-MiniLM-L6-v2) → FAISS index
   
8. API ENDPOINTS
   ↓ Serve search, discovery, summarization
   
9. FRONTEND UI
   ↓ React interface for interaction
```

---

## 🎯 Key Capabilities

### 1. **Multimodal Processing**
- ✍️ Handwritten notes → Digital text
- 📄 PDFs → Searchable content
- 🎤 Audio → Transcripts (Indian languages!)
- 🎥 Videos → Transcripts
- 📊 Diagrams → Knowledge graphs

### 2. **Semantic Search**
- Search across all content types
- Language-aware (search in English, find Hindi content)
- Vector similarity matching (not just keywords)

### 3. **Web Discovery**
- Categorized results: Wikipedia, Papers, Tutorials, Blogs
- YouTube educational videos
- Image search for visual aids

### 4. **AI Insights**
- Key concepts extraction
- Step-by-step explanations
- Practical to-dos
- Common mistakes
- Learning roadmaps
- Curated resources

---

## 🔌 API Quick Reference

### Upload & Process
```bash
POST /upload/image    # Handwritten notes
POST /upload/pdf      # Documents
POST /upload/audio    # 🇮🇳 Indian language audio
POST /upload/video    # Lectures
```

### Search & Retrieve
```bash
GET /search?q=machine+learning      # Search knowledge base
GET /rag/stats                       # Vector store stats
POST /embed                          # Generate embeddings
GET /knowledge                       # View all content
```

### Web Discovery
```bash
GET /discover?topic=neural+networks  # All sources
GET /discover/papers?topic=...       # Research papers
GET /discover/guides?topic=...       # Tutorials
GET /discover/images?topic=...       # Visual aids
```

### YouTube
```bash
GET /youtube?topic=python            # All videos
GET /youtube/tutorials               # Medium length
GET /youtube/courses                 # Long form
GET /youtube/shorts                  # Quick videos
```

### AI Summarization
```bash
GET /research?topic=transformers     # Full research + insights
GET /summarize?topic=...             # Quick insights only
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
git clone https://github.com/pranavvyawahare25/Student_Second_Brain.git
cd Student_Second_Brain
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r handwritten_notes_processor/requirements.txt
pip install -r pdf_to_text/requirements.txt
```

### 2. Set Up API Keys (.env file)
```env
# REQUIRED for Indian language support
SARVAM_API_KEY=your_key_here

# REQUIRED for summarization
GROQ_API_KEY=your_key_here

# Optional
BRAVE_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
AZURE_FORM_RECOGNIZER_ENDPOINT=your_endpoint
AZURE_FORM_RECOGNIZER_KEY=your_key
```

### 3. Start Backend
```bash
python -m api.server
# Server runs at http://localhost:8000
```

### 4. Start Frontend (Optional)
```bash
cd frontend
npm install
npm run dev
# UI at http://localhost:5173
```

---

## 🇮🇳 Using Indian Languages

### Upload Hindi Audio
```bash
# CLI
python -m speech_to_text.speech_to_text lecture_hindi.mp3

# API
curl -X POST http://localhost:8000/upload/audio \
  -F "file=@lecture_tamil.mp3"
```

### Response Format
```json
{
  "language_code": "hi-IN",
  "transcript_original": "मशीन लर्निंग...",
  "transcript_english": "Machine learning...",
  "summary": {
    "key_concepts": [...],
    "topics": [...]
  }
}
```

### Enable PaddleOCR for Indian Scripts
Edit `handwritten_notes_processor/test_ocr_minimal.py`:
```python
# Hindi
ocr = PaddleOCR(use_angle_cls=True, lang='hi', use_gpu=False)

# Multiple languages
ocr = PaddleOCR(use_angle_cls=True, lang=['hi','ta','te'], use_gpu=False)
```

---

## 📚 Full Documentation

- **[PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)** - Complete architecture & models
- **[ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md)** - Design philosophy
- **[README.md](README.md)** - Installation & usage guide

---

## 💡 Common Use Cases

1. **Digitize Class Notes**
   - Take photo of handwritten notes
   - Upload → OCR → Searchable knowledge base

2. **Process Lecture Recordings (Indian Languages)**
   - Record Hindi/Tamil/Telugu lecture
   - Upload → Transcribe → Translate → Summarize

3. **Research a New Topic**
   - Query `/research?topic=quantum+computing`
   - Get: Web articles + YouTube videos + AI insights

4. **Search Your Knowledge**
   - Query `/search?q=backpropagation`
   - Find: Notes, transcripts, diagrams containing that concept

5. **Build Study Materials**
   - Upload semester content
   - Generate learning roadmaps and flashcards

---

## 🔒 Security Notes

- Never commit API keys (use `.env`)
- API keys in `.env.example` are placeholders only
- Each user's knowledge base is isolated
- File uploads are validated and sanitized

---

## ⚡ Performance Tips

- **OCR:** ~2-3 sec/page (Azure), ~5-10 sec/page (PaddleOCR)
- **Audio Transcription:** ~1 hour audio = 5-10 min processing
- **Search:** <100ms for 10K chunks
- **Summarization:** ~5-10 seconds per topic

---

## 🎓 Target Users

- **Indian Students** learning in regional languages
- **Researchers** managing multimodal content
- **Educators** creating searchable course materials
- **Lifelong Learners** building personal knowledge bases

---

*For detailed technical information, see [PIPELINE_DOCUMENTATION.md](PIPELINE_DOCUMENTATION.md)*
