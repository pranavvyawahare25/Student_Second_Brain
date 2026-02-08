"""
Multi-Modal Ingestion API Server

FastAPI server with endpoints for uploading and processing:
- PDFs
- Handwritten note images
- Audio files
- Video files

Run with: python -m api.server
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# ============ Configuration ============
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("output_api")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============ FastAPI App ============
app = FastAPI(
    title="Student Second Brain API",
    description="Multi-modal ingestion API for RAG pipeline",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Helper Functions ============
def save_upload(file: UploadFile, subdir: str) -> Path:
    """Save uploaded file and return path."""
    dest_dir = UPLOAD_DIR / subdir
    dest_dir.mkdir(exist_ok=True)
    dest = dest_dir / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return dest


def summarize_transcript(transcript: str) -> dict:
    """
    Summarize a transcript using Groq AI.
    
    Args:
        transcript: The full transcript text (English)
        
    Returns:
        Dict with summary, key_points, and topics
    """
    try:
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {"error": "GROQ_API_KEY not configured", "summary": None}
        
        client = Groq(api_key=api_key)
        
        # Truncate if too long (Groq has token limits)
        max_chars = 15000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "..."
        
        prompt = f"""Analyze this lecture/audio transcript and provide:

1. **Summary** (2-3 paragraphs): A clear, comprehensive summary of the main content
2. **Key Points** (5-7 bullet points): The most important takeaways
3. **Topics Covered**: List the main topics/subjects discussed

Transcript:
{transcript}

Respond in JSON format:
{{
    "summary": "...",
    "key_points": ["point 1", "point 2", ...],
    "topics": ["topic 1", "topic 2", ...]
}}"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert at summarizing educational content. Always respond with valid JSON only, no markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        import json
        import re
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        # Clean control characters that break JSON parsing
        result_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', result_text)
        result_text = result_text.strip()
        
        # Try to parse JSON
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text as summary
            return {
                "summary": result_text[:2000] if len(result_text) > 100 else "Summary could not be parsed.",
                "key_points": [],
                "topics": []
            }
        
    except Exception as e:
        print(f"Summarization error: {e}")
        return {"error": str(e), "summary": None}


# ============ Endpoints ============

@app.get("/")
def root():
    return {"status": "ok", "message": "Student Second Brain API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")
    
    # Save file
    file_path = save_upload(file, "pdf")
    
    try:
        # Import pdf processing modules
        sys.path.insert(0, "pdf_to_text")
        from pdf_to_text.ingestion.pdf_loder import extract_text_from_pdf
        from pdf_to_text.ingestion.text_spliter import split_text
        from pdf_to_text.ingestion.embedder import Embedder
        from pdf_to_text.database.faiss_store import FAISSStore
        
        # Process
        text = extract_text_from_pdf(str(file_path))
        chunks = split_text(text)
        
        embedder = Embedder()
        embeddings = embedder.embed(chunks)
        
        # Store with unique paths
        json_path = OUTPUT_DIR / f"{file.filename}_chunks.json"
        store = FAISSStore(
            index_path=str(OUTPUT_DIR / f"{file.filename}.index"),
            meta_path=str(OUTPUT_DIR / f"{file.filename}.pkl"),
            json_path=str(json_path)
        )
        store.store(chunks, embeddings, source_file=file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks),
            "output": str(json_path)
        }
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")
    finally:
        # Cleanup uploaded file
        if file_path.exists():
            file_path.unlink()


@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload and process a handwritten note image."""
    allowed = [".png", ".jpg", ".jpeg"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Only {allowed} files are allowed")
    
    file_path = save_upload(file, "image")
    
    try:
        from handwritten_notes_processor.text_pipeline.ocr_engine import OCREngine
        from handwritten_notes_processor.diagram_pipeline.diagram_detector import DiagramDetector
        from handwritten_notes_processor.fusion.region_consolidator import RegionConsolidator
        
        # Run OCR
        ocr_engine = OCREngine()
        text_regions = ocr_engine.process_image(str(file_path))
        
        # Run diagram detection
        detector = DiagramDetector()
        diagram_regions = detector.process_image(str(file_path), save_visualization=False)
        
        # Consolidate regions
        consolidator = RegionConsolidator()
        consolidated = consolidator.consolidate(diagram_regions, text_regions)
        
        return {
            "status": "success",
            "filename": file.filename,
            "text_regions": len(text_regions),
            "diagram_regions": len(diagram_regions),
            "consolidated_regions": len(consolidated.get("regions", [])),
            "regions": consolidated.get("regions", [])[:5]  # First 5 for preview
        }
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")
    finally:
        if file_path.exists():
            file_path.unlink()


@app.post("/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload and transcribe an audio file."""
    allowed = [".mp3", ".wav", ".m4a"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Only {allowed} files are allowed")
    
    file_path = save_upload(file, "audio")
    
    try:
        import requests
        import time
        import json
        
        api_key = os.getenv("SARVAM_API_KEY")
        if not api_key:
            raise HTTPException(500, "SARVAM_API_KEY not configured")
        
        # Try importing Sarvam SDK
        try:
            from sarvamai import SarvamAI
            client = SarvamAI(api_subscription_key=api_key)
        except ImportError:
            raise HTTPException(500, "sarvamai SDK not installed. Run: pip install sarvamai")
        
        # Initialize job
        init_response = client.speech_to_text_translate_job.initialise(
            job_parameters={"model": "saaras:v2.5"}
        )
        job_id = init_response.job_id
        
        # Get upload link
        upload_response = client.speech_to_text_translate_job.get_upload_links(
            job_id=job_id,
            files=[file.filename]
        )
        # upload_urls is a dict: {filename: FileSignedUrlDetails}
        file_url_details = upload_response.upload_urls.get(file.filename)
        if not file_url_details:
            raise HTTPException(500, f"No upload URL returned for {file.filename}")
        upload_url = file_url_details.file_url
        
        # Upload file
        with open(file_path, "rb") as f:
            requests.put(
                upload_url,
                data=f,
                headers={"Content-Type": "audio/mpeg", "x-ms-blob-type": "BlockBlob"}
            )
        
        # Start job
        client.speech_to_text_translate_job.start(job_id)
        
        # Poll for completion (max 2 minutes)
        for _ in range(24):
            job = client.speech_to_text_translate_job.get_job(job_id)
            status = job.get_status()
            job_state = status.job_state
            print(f"Job {job_id} state: {job_state}")
            
            if job_state == "Completed":
                # Download result (saves files to output_dir, returns bool)
                job.download_outputs(output_dir=str(OUTPUT_DIR))
                
                # Find the transcript JSON in output dir
                import glob
                json_files = glob.glob(str(OUTPUT_DIR / f"*{job_id}*.json"))
                if not json_files:
                    json_files = glob.glob(str(OUTPUT_DIR / "*.json"))
                
                for json_file in json_files:
                    with open(json_file, "r") as jf:
                        transcript_data = json.load(jf)
                        
                        # Get full transcript text
                        full_transcript = transcript_data.get("transcript", "")
                        
                        # Generate summary using Groq AI
                        summary_data = summarize_transcript(full_transcript)
                        
                        # Save to our output path (with summary)
                        output_path = OUTPUT_DIR / f"{file.filename}_transcript.json"
                        output_data = {
                            **transcript_data,
                            "ai_summary": summary_data
                        }
                        with open(output_path, "w") as f:
                            json.dump(output_data, f, indent=2)
                        
                        return {
                            "status": "success",
                            "filename": file.filename,
                            "transcript": full_transcript[:500] + ("..." if len(full_transcript) > 500 else ""),
                            "full_transcript": full_transcript,
                            "language": transcript_data.get("language_code"),
                            "summary": summary_data.get("summary"),
                            "key_points": summary_data.get("key_points", []),
                            "topics": summary_data.get("topics", []),
                            "output": str(output_path)
                        }
                raise HTTPException(500, "No transcript file found in output")
            elif job_state == "Failed":
                raise HTTPException(500, f"Transcription failed: {status.error_message}")
            time.sleep(5)
        
        raise HTTPException(500, "Transcription timed out")
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Audio upload error: {error_detail}")
        raise HTTPException(500, f"Processing failed: {str(e)}")
    finally:
        if file_path.exists():
            file_path.unlink()


@app.post("/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video, extract audio, and transcribe."""
    allowed = [".mp4", ".mov", ".avi", ".mkv"]
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"Only {allowed} files are allowed")
    
    file_path = save_upload(file, "video")
    
    try:
        from video_processor.audio_extraction.extractor import AudioExtractor
        
        # Extract audio (uses internal output_dir)
        extractor = AudioExtractor(output_dir=str(OUTPUT_DIR))
        audio_path, manifest_path = extractor.extract_audio(str(file_path))
        
        # Return paths for next step
        return {
            "status": "success",
            "filename": file.filename,
            "audio_extracted": audio_path,
            "manifest": manifest_path,
            "message": "Audio extracted. Upload the audio file to /upload/audio to transcribe."
        }
    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")
    finally:
        if file_path.exists():
            file_path.unlink()


@app.post("/preprocess")
async def run_preprocessor():
    """Run the multi-modal preprocessor to unify all outputs."""
    try:
        from multimodal_preprocessor.preprocessor import run_preprocessor
        
        kb = run_preprocessor(
            handwritten_dir="output_artifacts",
            pdf_json="pdf_to_text/text_chunks.json",
            transcript_json="output_audio/test_transcript.json",
            output_path="unified_knowledge.json"
        )
        
        return {
            "status": "success",
            "total_chunks": len(kb.chunks),
            "total_graphs": len(kb.graphs),
            "output": "unified_knowledge.json"
        }
    except Exception as e:
        raise HTTPException(500, f"Preprocessing failed: {str(e)}")


@app.get("/knowledge")
async def get_knowledge():
    """Get the unified knowledge base."""
    kb_path = Path("unified_knowledge.json")
    if not kb_path.exists():
        raise HTTPException(404, "Knowledge base not found. Run /preprocess first.")
    
    import json
    with open(kb_path) as f:
        data = json.load(f)
    
    return data


# ============ RAG Endpoints ============
# Global RAG instance (lazy loaded)
_rag_instance = None

def get_rag():
    """Get or initialize RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        from multimodal_preprocessor.rag.pipeline import UnifiedRAG
        _rag_instance = UnifiedRAG(index_dir="rag_index")
    return _rag_instance


@app.post("/embed")
async def build_embeddings():
    """Build embeddings and vector index from unified knowledge."""
    kb_path = Path("unified_knowledge.json")
    if not kb_path.exists():
        raise HTTPException(404, "unified_knowledge.json not found. Run /preprocess first.")
    
    try:
        rag = get_rag()
        stats = rag.build_from_json(str(kb_path))
        return {
            "status": "success",
            "message": "Vector index built successfully",
            "stats": stats
        }
    except Exception as e:
        import traceback
        print(f"Embed error: {traceback.format_exc()}")
        raise HTTPException(500, f"Embedding failed: {str(e)}")


@app.get("/search")
async def search_knowledge(q: str, top_k: int = 5):
    """
    Semantic search across unified knowledge.
    
    Args:
        q: Search query
        top_k: Number of results (default 5)
    """
    if not q:
        raise HTTPException(400, "Query parameter 'q' is required")
    
    try:
        rag = get_rag()
        
        # Try to load existing index
        if rag.store is None:
            if not rag.load():
                raise HTTPException(404, "Vector index not found. Call /embed first.")
        
        results = rag.search(q, top_k=top_k)
        
        return {
            "status": "success",
            "query": q,
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Search error: {traceback.format_exc()}")
        raise HTTPException(500, f"Search failed: {str(e)}")


@app.get("/rag/stats")
async def rag_stats():
    """Get RAG pipeline statistics."""
    try:
        rag = get_rag()
        if rag.store is None:
            rag.load()
        return rag.get_stats()
    except Exception as e:
        return {"status": "not_initialized", "error": str(e)}


# ============ Web Discovery Endpoints ============
@app.get("/discover")
async def discover_topic(
    topic: str,
    web_count: int = 20,
    news_count: int = 5,
    image_count: int = 5,
    video_count: int = 5
):
    """
    Discover content for a topic using Brave Search API.
    
    Returns categorized results:
    - Wikipedia articles
    - Research papers
    - Study guides
    - Documentation
    - Tutorials
    - News
    - Videos
    - Images
    - Blogs
    """
    if not topic:
        raise HTTPException(400, "Topic parameter is required")
    
    try:
        from web_extractor.brave_search import BraveSearchClient
        
        client = BraveSearchClient()
        result = client.discover_topic(
            topic,
            web_count=web_count,
            news_count=news_count,
            image_count=image_count,
            video_count=video_count
        )
        
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(500, str(e))
    except Exception as e:
        import traceback
        print(f"Discovery error: {traceback.format_exc()}")
        raise HTTPException(500, f"Discovery failed: {str(e)}")


@app.get("/discover/wikipedia")
async def discover_wikipedia(topic: str, count: int = 5):
    """Search specifically for Wikipedia articles on a topic."""
    try:
        from web_extractor.brave_search import BraveSearchClient
        client = BraveSearchClient()
        results = client.search_wikipedia(topic, count)
        return {"query": topic, "results": [r.to_dict() for r in results]}
    except Exception as e:
        raise HTTPException(500, f"Wikipedia search failed: {str(e)}")


@app.get("/discover/papers")
async def discover_papers(topic: str, count: int = 10):
    """Search for research papers on a topic."""
    try:
        from web_extractor.brave_search import BraveSearchClient
        client = BraveSearchClient()
        results = client.search_research_papers(topic, count)
        return {"query": topic, "results": [r.to_dict() for r in results]}
    except Exception as e:
        raise HTTPException(500, f"Research paper search failed: {str(e)}")


@app.get("/discover/guides")
async def discover_guides(topic: str, count: int = 10):
    """Search for study guides and tutorials on a topic."""
    try:
        from web_extractor.brave_search import BraveSearchClient
        client = BraveSearchClient()
        results = client.search_study_guides(topic, count)
        return {"query": topic, "results": [r.to_dict() for r in results]}
    except Exception as e:
        raise HTTPException(500, f"Study guide search failed: {str(e)}")


@app.get("/discover/images")
async def discover_images(topic: str, count: int = 10):
    """
    Search for topic-related images using Brave Search API.
    
    Returns images with thumbnails, source URLs, and dimensions.
    """
    try:
        from web_extractor.brave_search import BraveSearchClient
        client = BraveSearchClient()
        results = client.search_images(topic, count)
        
        # Format image results
        images = []
        for r in results:
            img = {
                "title": r.title,
                "url": r.url,
                "source": r.source,
                "thumbnail": r.metadata.get("thumbnail", ""),
                "properties": r.metadata.get("properties", {})
            }
            images.append(img)
        
        return {
            "query": topic,
            "total": len(images),
            "images": images
        }
    except Exception as e:
        import traceback
        print(f"Image search error: {traceback.format_exc()}")
        raise HTTPException(500, f"Image search failed: {str(e)}")


# ============ LLM Research & Summarization Endpoints ============
@app.get("/research")
async def research_topic(
    topic: str,
    web_count: int = 15,
    youtube_count: int = 5,
    image_count: int = 5
):
    """
    Complete topic research with LLM-powered summarization.
    
    Fetches content from web, YouTube, and images, then uses Gemini
    to generate structured insights:
    - Key concepts
    - Step-by-step explanation
    - Practical to-dos
    - Common mistakes
    - Learning roadmap
    """
    try:
        from web_extractor.summarizer import TopicResearcher
        
        researcher = TopicResearcher()
        result = researcher.research_topic(
            topic,
            web_count=web_count,
            youtube_count=youtube_count,
            image_count=image_count
        )
        
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback
        print(f"Research error: {traceback.format_exc()}")
        raise HTTPException(500, f"Research failed: {str(e)}")


@app.get("/summarize")
async def summarize_content(topic: str):
    """
    Quick summarization of a topic (insights only, no raw data).
    
    Returns structured insights for rapid learning.
    """
    try:
        from web_extractor.summarizer import TopicResearcher
        
        researcher = TopicResearcher()
        result = researcher.research_topic(topic, web_count=10, youtube_count=3, image_count=3)
        
        # Return only insights for quick consumption
        return {
            "topic": topic,
            "insights": result["insights"]
        }
    except Exception as e:
        import traceback
        print(f"Summarize error: {traceback.format_exc()}")
        raise HTTPException(500, f"Summarization failed: {str(e)}")


# ============ YouTube Video Endpoints ============
@app.get("/youtube")
async def youtube_search(
    topic: str,
    max_results: int = 10,
    order: str = "viewCount",
    duration: str = "any"
):
    """
    Search YouTube videos for a topic.
    
    Args:
        topic: Topic to search
        max_results: Number of results (max 50)
        order: viewCount, relevance, date, rating
        duration: any, short (<4min), medium (4-20min), long (>20min)
    """
    try:
        from web_extractor.youtube_search import (
            YouTubeSearchClient, VideoOrder, VideoDuration
        )
        
        client = YouTubeSearchClient()
        result = client.discover_videos(
            topic,
            max_results=max_results,
            order=VideoOrder(order),
            duration=VideoDuration(duration)
        )
        
        return result.to_dict()
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback
        print(f"YouTube search error: {traceback.format_exc()}")
        raise HTTPException(500, f"YouTube search failed: {str(e)}")


@app.get("/youtube/tutorials")
async def youtube_tutorials(topic: str, max_results: int = 10):
    """Search for tutorial videos on a topic (medium duration, by views)."""
    try:
        from web_extractor.youtube_search import YouTubeSearchClient
        client = YouTubeSearchClient()
        result = client.search_tutorials(topic, max_results)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(500, f"Tutorial search failed: {str(e)}")


@app.get("/youtube/courses")
async def youtube_courses(topic: str, max_results: int = 10):
    """Search for full course videos on a topic (long duration)."""
    try:
        from web_extractor.youtube_search import YouTubeSearchClient
        client = YouTubeSearchClient()
        result = client.search_courses(topic, max_results)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(500, f"Course search failed: {str(e)}")


@app.get("/youtube/shorts")
async def youtube_shorts(topic: str, max_results: int = 10):
    """Search for short explainer videos on a topic (<4 min)."""
    try:
        from web_extractor.youtube_search import YouTubeSearchClient
        client = YouTubeSearchClient()
        result = client.search_shorts(topic, max_results)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(500, f"Shorts search failed: {str(e)}")


# ============ Syllabus Management Endpoints ============

# Global syllabus stores (in production, use per-user stores)
_syllabus_parser = None
_syllabus_store = None

def _get_syllabus_parser():
    global _syllabus_parser
    if _syllabus_parser is None:
        from syllabus.parser import SyllabusParser
        _syllabus_parser = SyllabusParser()
    return _syllabus_parser

def _get_syllabus_store():
    global _syllabus_store
    if _syllabus_store is None:
        from syllabus.vector_store import SyllabusVectorStore
        _syllabus_store = SyllabusVectorStore(store_path="syllabus_index")
    return _syllabus_store


@app.post("/syllabus/upload")
async def upload_syllabus(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = None,
    course_name: str = "My Course"
):
    """
    Upload and parse syllabus.
    
    Accepts either a PDF/text file or raw text.
    Parses into units/topics and stores embeddings.
    """
    try:
        parser = _get_syllabus_parser()
        store = _get_syllabus_store()
        
        syllabus_text = ""
        
        if file:
            # Save and extract text from file
            file_path = save_upload(file, "syllabus")
            
            if file.filename.endswith(".pdf"):
                # Extract text from PDF
                from pdf_to_text.ingestion.pdf_loder import extract_text_from_pdf
                syllabus_text = extract_text_from_pdf(str(file_path))
            else:
                # Read as text file
                with open(file_path, "r", encoding="utf-8") as f:
                    syllabus_text = f.read()
        elif text:
            syllabus_text = text
        else:
            raise HTTPException(400, "Provide either a file or text")
        
        # Parse syllabus
        parsed = parser.parse(syllabus_text, course_name)
        
        if not parsed.units:
            raise HTTPException(400, "Could not detect any units in the syllabus")
        
        # Generate embeddings for each topic
        from pdf_to_text.ingestion.embedder import Embedder
        embedder = Embedder()
        
        topic_texts = parser.get_all_topics_text(parsed)
        embeddings = embedder.embed(topic_texts)
        
        # Prepare metadata
        metadata_list = []
        topic_idx = 0
        for unit in parsed.units:
            for topic in unit.topics:
                metadata_list.append({
                    "unit_number": unit.number,
                    "unit_title": unit.title,
                    "topic": topic.name
                })
                topic_idx += 1
        
        # Clear old and add new
        store.clear()
        store.add_embeddings(embeddings, metadata_list)
        
        return {
            "status": "success",
            "course_name": parsed.course_name,
            "units_detected": len(parsed.units),
            "topics_indexed": len(topic_texts),
            "syllabus": parsed.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Syllabus upload failed: {str(e)}")


@app.get("/syllabus")
async def get_syllabus():
    """Get current stored syllabus structure."""
    try:
        store = _get_syllabus_store()
        units = store.get_all_units()
        
        return {
            "status": "success",
            "topics_count": store.count,
            "units": units
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get syllabus: {str(e)}")


@app.post("/syllabus/compare")
async def compare_syllabus(lecture_texts: List[str] = []):
    """
    Compare lecture content against syllabus.
    
    Args:
        lecture_texts: List of lecture content chunks to compare
        
    Returns:
        Coverage percentage per unit
    """
    try:
        if not lecture_texts:
            raise HTTPException(400, "Provide lecture_texts to compare")
        
        store = _get_syllabus_store()
        
        if store.count == 0:
            raise HTTPException(400, "No syllabus uploaded yet")
        
        # Generate embeddings for lecture content
        from pdf_to_text.ingestion.embedder import Embedder
        embedder = Embedder()
        lecture_embeddings = embedder.embed(lecture_texts)
        
        # Compare using comparator
        from syllabus.comparator import SyllabusComparator
        comparator = SyllabusComparator(store)
        result = comparator.compare(lecture_embeddings, lecture_texts)
        
        return {
            "status": "success",
            **result.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Comparison failed: {str(e)}")


# ============ Main ============
def main():
    """Run server with ngrok tunnel."""
    try:
        from pyngrok import ngrok
        
        # Start ngrok tunnel
        public_url = ngrok.connect(8000)
        print(f"\n{'='*60}")
        print(f"🚀 PUBLIC URL: {public_url}")
        print(f"{'='*60}\n")
    except ImportError:
        print("⚠️  pyngrok not installed. Run: pip install pyngrok")
        print("Running on localhost only.\n")
    except Exception as e:
        print(f"⚠️  Ngrok failed: {e}")
        print("Running on localhost only.\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
