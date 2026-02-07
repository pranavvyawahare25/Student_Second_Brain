"""
Adapter for pdf_to_text outputs.

Reads: pdf_to_text/text_chunks.json
"""

import json
from typing import List
from ..unified_schema import UnifiedChunk


def load_pdf_chunks(json_path: str) -> List[UnifiedChunk]:
    """
    Load PDF text chunks and convert to unified format.
    
    The pdf_to_text module already outputs in our unified format,
    so this is mostly a passthrough with validation.
    
    Args:
        json_path: Path to text_chunks.json
    
    Returns:
        List of UnifiedChunk
    """
    chunks = []

    with open(json_path, "r") as f:
        data = json.load(f)

    for item in data:
        chunk = UnifiedChunk(
            chunk_id=item.get("chunk_id", "pdf_unknown"),
            source_type=item.get("source_type", "pdf"),
            source_file=item.get("source_file", "unknown.pdf"),
            content=item.get("content", ""),
            modality=item.get("modality", "text"),
            metadata=item.get("metadata", {})
        )
        chunks.append(chunk)

    print(f"Loaded {len(chunks)} chunks from PDF.")
    return chunks
