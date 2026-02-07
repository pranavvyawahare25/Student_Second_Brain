"""
Multi-Modal Preprocessor: Main Orchestrator

Discovers and loads all data sources, merges them into a unified
knowledge base, and outputs a single JSON file ready for RAG.

Usage:
    python -m multimodal_preprocessor.preprocessor \
        --handwritten output_artifacts/ \
        --pdf pdf_to_text/text_chunks.json \
        --transcript output_audio/test_transcript.json \
        --output unified_knowledge.json
"""

import argparse
import os
from .unified_schema import UnifiedKnowledgeBase
from .adapters.handwritten_adapter import load_handwritten_knowledge
from .adapters.pdf_adapter import load_pdf_chunks
from .adapters.transcript_adapter import load_transcript


def run_preprocessor(
    handwritten_dir: str = None,
    pdf_json: str = None,
    transcript_json: str = None,
    output_path: str = "unified_knowledge.json"
) -> UnifiedKnowledgeBase:
    """
    Run the multi-modal preprocessor.
    
    Args:
        handwritten_dir: Directory containing text_knowledge.json and graph_knowledge.json
        pdf_json: Path to pdf_to_text/text_chunks.json
        transcript_json: Path to *_transcript.json
        output_path: Output path for unified JSON
    
    Returns:
        UnifiedKnowledgeBase instance
    """
    kb = UnifiedKnowledgeBase()
    
    # Load handwritten notes
    if handwritten_dir:
        text_path = os.path.join(handwritten_dir, "text_knowledge.json")
        graph_path = os.path.join(handwritten_dir, "graph_knowledge.json")
        
        if os.path.exists(text_path):
            graph_path_arg = graph_path if os.path.exists(graph_path) else None
            chunks, graphs = load_handwritten_knowledge(text_path, graph_path_arg)
            for c in chunks:
                kb.add_chunk(c)
            for g in graphs:
                kb.add_graph(g)
        else:
            print(f"Warning: {text_path} not found, skipping handwritten notes.")
    
    # Load PDF chunks
    if pdf_json and os.path.exists(pdf_json):
        chunks = load_pdf_chunks(pdf_json)
        for c in chunks:
            kb.add_chunk(c)
    elif pdf_json:
        print(f"Warning: {pdf_json} not found, skipping PDF.")
    
    # Load transcript
    if transcript_json and os.path.exists(transcript_json):
        # Determine if video or audio based on path
        source_type = "video" if "video" in transcript_json.lower() else "audio"
        chunks = load_transcript(transcript_json, source_type)
        for c in chunks:
            kb.add_chunk(c)
    elif transcript_json:
        print(f"Warning: {transcript_json} not found, skipping transcript.")
    
    # Summary
    print(f"\n{'='*50}")
    print("UNIFIED KNOWLEDGE BASE SUMMARY")
    print(f"{'='*50}")
    print(f"Total Chunks: {len(kb.chunks)}")
    print(f"Total Graphs: {len(kb.graphs)}")
    
    # Breakdown by source
    source_counts = {}
    for c in kb.chunks:
        source_counts[c.source_type] = source_counts.get(c.source_type, 0) + 1
    print("\nChunks by Source:")
    for src, count in source_counts.items():
        print(f"  - {src}: {count}")
    
    # Save
    kb.save(output_path)
    
    return kb


def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Preprocessor for RAG")
    parser.add_argument("--handwritten", help="Directory with handwritten notes outputs")
    parser.add_argument("--pdf", help="Path to PDF text_chunks.json")
    parser.add_argument("--transcript", help="Path to transcript JSON")
    parser.add_argument("--output", default="unified_knowledge.json", help="Output path")
    
    args = parser.parse_args()
    
    run_preprocessor(
        handwritten_dir=args.handwritten,
        pdf_json=args.pdf,
        transcript_json=args.transcript,
        output_path=args.output
    )


if __name__ == "__main__":
    main()
