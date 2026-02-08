"""
Syllabus vs Lecture Comparator

Compares lecture content embeddings against syllabus embeddings
to determine coverage percentage per unit.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TopicCoverage:
    """Coverage result for a single topic."""
    topic: str
    covered: bool
    confidence: float  # 0-1 score
    matched_content: Optional[str] = None


@dataclass
class UnitCoverage:
    """Coverage result for a unit."""
    unit_number: int
    unit_title: str
    topics: List[TopicCoverage] = field(default_factory=list)
    
    @property
    def coverage_percent(self) -> float:
        """Calculate coverage percentage for this unit."""
        if not self.topics:
            return 0.0
        covered = sum(1 for t in self.topics if t.covered)
        return (covered / len(self.topics)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_number": self.unit_number,
            "unit_title": self.unit_title,
            "coverage_percent": round(self.coverage_percent, 1),
            "topics_covered": sum(1 for t in self.topics if t.covered),
            "topics_total": len(self.topics),
            "topics": [
                {
                    "name": t.topic,
                    "covered": t.covered,
                    "confidence": round(t.confidence, 2),
                    "matched_content": t.matched_content
                }
                for t in self.topics
            ]
        }


@dataclass
class ComparisonResult:
    """Full comparison result."""
    total_coverage: float
    units: List[UnitCoverage] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_coverage": round(self.total_coverage, 1),
            "units": [u.to_dict() for u in self.units]
        }


class SyllabusComparator:
    """Compare lecture content against syllabus."""
    
    # Threshold for considering a topic "covered"
    COVERAGE_THRESHOLD = 0.6
    
    def __init__(self, syllabus_store, lecture_store=None, embedder=None):
        """
        Initialize comparator.
        
        Args:
            syllabus_store: SyllabusVectorStore instance
            lecture_store: Lecture content vector store (optional)
            embedder: Embedding function (optional)
        """
        self.syllabus_store = syllabus_store
        self.lecture_store = lecture_store
        self.embedder = embedder
    
    def compare(
        self,
        lecture_embeddings: List[List[float]],
        lecture_texts: Optional[List[str]] = None
    ) -> ComparisonResult:
        """
        Compare lecture embeddings against syllabus.
        
        Args:
            lecture_embeddings: List of lecture content embedding vectors
            lecture_texts: Optional list of lecture text chunks for display
            
        Returns:
            ComparisonResult with coverage per unit
        """
        if not lecture_embeddings:
            return ComparisonResult(total_coverage=0.0)
        
        # Get all syllabus units
        units_data = self.syllabus_store.get_all_units()
        
        if not units_data:
            return ComparisonResult(total_coverage=0.0)
        
        # For each syllabus topic, find best matching lecture content
        unit_coverages = []
        
        for unit_data in units_data:
            unit_coverage = UnitCoverage(
                unit_number=unit_data["number"],
                unit_title=unit_data["title"]
            )
            
            for topic in unit_data.get("topics", []):
                # Search syllabus store for this topic's embedding index
                # Then compare against lecture embeddings
                
                # Find best match from lecture content for this topic
                best_score = 0.0
                best_match_text = None
                
                # Get topic embedding from syllabus store
                topic_results = self.syllabus_store.search(
                    lecture_embeddings[0],  # Use first lecture embedding as query
                    top_k=1
                )
                
                # Actually, we need to do it the other way:
                # For each syllabus topic, check if any lecture content matches
                
                # Simplified: For each lecture embedding, search syllabus
                # and accumulate which topics are covered
                
                for i, lecture_emb in enumerate(lecture_embeddings):
                    matches = self.syllabus_store.search(lecture_emb, top_k=3)
                    for match in matches:
                        if match.get("topic") == topic:
                            if match.get("score", 0) > best_score:
                                best_score = match["score"]
                                if lecture_texts and i < len(lecture_texts):
                                    best_match_text = lecture_texts[i][:100]
                
                unit_coverage.topics.append(TopicCoverage(
                    topic=topic,
                    covered=best_score >= self.COVERAGE_THRESHOLD,
                    confidence=best_score,
                    matched_content=best_match_text
                ))
            
            unit_coverages.append(unit_coverage)
        
        # Calculate total coverage
        total_topics = sum(len(u.topics) for u in unit_coverages)
        covered_topics = sum(
            sum(1 for t in u.topics if t.covered)
            for u in unit_coverages
        )
        
        total_coverage = (covered_topics / total_topics * 100) if total_topics > 0 else 0.0
        
        return ComparisonResult(
            total_coverage=total_coverage,
            units=unit_coverages
        )
    
    def quick_coverage_check(
        self,
        query_embedding: List[float]
    ) -> Dict[str, Any]:
        """
        Quick check: which syllabus topics match a single query.
        
        Args:
            query_embedding: Single embedding vector
            
        Returns:
            Dict with matched topics
        """
        matches = self.syllabus_store.search(query_embedding, top_k=5)
        return {
            "matches": matches,
            "covered_units": list(set(m.get("unit_number") for m in matches))
        }


# CLI for testing
if __name__ == "__main__":
    from syllabus.vector_store import SyllabusVectorStore
    
    store = SyllabusVectorStore("test_syllabus_index")
    comparator = SyllabusComparator(store)
    
    # Test with dummy embeddings
    dummy_embeddings = [[0.1] * 384, [0.2] * 384]
    result = comparator.compare(dummy_embeddings)
    
    import json
    print(json.dumps(result.to_dict(), indent=2))
