"""
Adapter for speech_to_text / video_processor outputs.

Reads: *_transcript.json files
"""

import json
import re
from typing import List
from ..unified_schema import UnifiedChunk


def split_transcript(text: str, max_chunk_size: int = 500) -> List[str]:
    """Split transcript into sentence-based chunks."""
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def load_transcript(json_path: str, source_type: str = "video") -> List[UnifiedChunk]:
    """
    Load transcript JSON and convert to unified chunks.
    
    Transcripts are split into sentence-based chunks for better RAG retrieval.
    
    Args:
        json_path: Path to *_transcript.json
        source_type: "video" or "audio"
    
    Returns:
        List of UnifiedChunk
    """
    chunks = []

    with open(json_path, "r") as f:
        data = json.load(f)

    transcript = data.get("transcript", "")
    language = data.get("language_code", "en")
    request_id = data.get("request_id", "unknown")
    
    # Extract source filename from path
    import os
    source_file = os.path.basename(json_path).replace("_transcript.json", "")
    if not source_file:
        source_file = "unknown"

    # Split transcript into chunks
    text_chunks = split_transcript(transcript)
    
    for i, content in enumerate(text_chunks):
        chunk = UnifiedChunk(
            chunk_id=f"{source_type}_{request_id[:8]}_{i}",
            source_type=source_type,
            source_file=source_file,
            content=content,
            modality="transcript",
            metadata={
                "language": language,
                "request_id": request_id,
                "chunk_index": i,
                "total_chunks": len(text_chunks)
            }
        )
        chunks.append(chunk)

    print(f"Loaded {len(chunks)} chunks from transcript ({source_type}).")
    return chunks
