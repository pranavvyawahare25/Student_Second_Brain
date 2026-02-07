"""
Unified Schema for Multi-Modal RAG Pipeline.

All data sources are converted to this common format before being merged
into a single knowledge base for RAG.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import uuid
import json


@dataclass
class UnifiedChunk:
    """A single chunk of content from any source."""
    chunk_id: str
    source_type: str  # "handwritten", "pdf", "video", "audio"
    source_file: str
    content: str
    modality: str  # "text", "diagram", "transcript"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, source_type: str, source_file: str, content: str, 
               modality: str = "text", metadata: Optional[Dict] = None):
        """Factory method with auto-generated chunk_id."""
        return cls(
            chunk_id=f"{source_type}_{uuid.uuid4().hex[:8]}",
            source_type=source_type,
            source_file=source_file,
            content=content,
            modality=modality,
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphNode:
    """A node in a knowledge graph."""
    node_id: str
    label: str
    node_type: str
    aliases: List[str] = field(default_factory=list)
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GraphEdge:
    """An edge in a knowledge graph."""
    from_node: str
    to_node: str
    relation: str
    confidence: float = 0.9
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UnifiedGraph:
    """A knowledge graph from diagram sources."""
    graph_id: str
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "metadata": self.metadata
        }


@dataclass
class UnifiedKnowledgeBase:
    """The complete unified knowledge base for RAG."""
    version: str = "1.0"
    chunks: List[UnifiedChunk] = field(default_factory=list)
    graphs: List[UnifiedGraph] = field(default_factory=list)

    def add_chunk(self, chunk: UnifiedChunk):
        self.chunks.append(chunk)

    def add_graph(self, graph: UnifiedGraph):
        self.graphs.append(graph)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "chunks": [c.to_dict() for c in self.chunks],
            "graphs": [g.to_dict() for g in self.graphs]
        }

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Saved unified knowledge base to {path}")

    @classmethod
    def load(cls, path: str) -> "UnifiedKnowledgeBase":
        with open(path, "r") as f:
            data = json.load(f)
        kb = cls(version=data.get("version", "1.0"))
        for c in data.get("chunks", []):
            kb.chunks.append(UnifiedChunk(**c))
        # Graphs would need more complex loading
        return kb
