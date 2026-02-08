"""
Syllabus Management Module

Provides:
- SyllabusParser: Parse syllabus text into units/topics
- SyllabusVectorStore: Store syllabus embeddings
- SyllabusComparator: Compare lecture content against syllabus
"""

from syllabus.parser import SyllabusParser, ParsedSyllabus, Unit, Topic
from syllabus.vector_store import SyllabusVectorStore
from syllabus.comparator import SyllabusComparator, ComparisonResult

__all__ = [
    "SyllabusParser",
    "ParsedSyllabus", 
    "Unit",
    "Topic",
    "SyllabusVectorStore",
    "SyllabusComparator",
    "ComparisonResult"
]
