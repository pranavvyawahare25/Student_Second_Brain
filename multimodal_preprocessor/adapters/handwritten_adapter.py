"""
Adapter for handwritten_notes_processor outputs.

Reads:
- output_artifacts/text_knowledge.json
- output_artifacts/graph_knowledge.json
"""

import json
from typing import List, Tuple
from ..unified_schema import UnifiedChunk, UnifiedGraph, GraphNode, GraphEdge


def load_handwritten_knowledge(text_json_path: str, graph_json_path: str = None) -> Tuple[List[UnifiedChunk], List[UnifiedGraph]]:
    """
    Load handwritten notes outputs and convert to unified format.
    
    Args:
        text_json_path: Path to text_knowledge.json
        graph_json_path: Path to graph_knowledge.json (optional)
    
    Returns:
        Tuple of (chunks, graphs)
    """
    chunks = []
    graphs = []

    # Load text chunks
    with open(text_json_path, "r") as f:
        text_data = json.load(f)

    for item in text_data:
        chunk = UnifiedChunk(
            chunk_id=item.get("chunk_id", f"hw_{item.get('doc_id', 'unknown')}"),
            source_type="handwritten",
            source_file=item.get("metadata", {}).get("source_image", "unknown.png"),
            content=item.get("content", ""),
            modality="text",
            metadata={
                "original_doc_id": item.get("doc_id"),
                "original_type": item.get("type"),
                "topic": item.get("metadata", {}).get("topic"),
                "page": item.get("metadata", {}).get("page")
            }
        )
        chunks.append(chunk)

    # Load graph if provided
    if graph_json_path:
        with open(graph_json_path, "r") as f:
            graph_data = json.load(f)

        nodes = []
        for n in graph_data.get("nodes", []):
            nodes.append(GraphNode(
                node_id=n.get("node_id"),
                label=n.get("label"),
                node_type=n.get("type", "concept"),
                aliases=n.get("aliases", []),
                source=n.get("source", "")
            ))

        edges = []
        for e in graph_data.get("edges", []):
            edges.append(GraphEdge(
                from_node=e.get("from"),
                to_node=e.get("to"),
                relation=e.get("relation", "related_to"),
                confidence=e.get("confidence", 0.9),
                source=e.get("source", "")
            ))

        graph = UnifiedGraph(
            graph_id=graph_data.get("graph_id", "unknown_graph"),
            nodes=nodes,
            edges=edges,
            metadata=graph_data.get("metadata", {})
        )
        graphs.append(graph)

    print(f"Loaded {len(chunks)} chunks and {len(graphs)} graphs from handwritten notes.")
    return chunks, graphs
