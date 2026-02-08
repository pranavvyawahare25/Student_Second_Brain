"""
Syllabus Parser

Parses syllabus text/PDF into structured units and topics.
Detects unit boundaries using pattern matching.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Topic:
    """Single topic within a unit."""
    name: str
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Unit:
    """Unit/Chapter in syllabus."""
    number: int
    title: str
    topics: List[Topic] = field(default_factory=list)
    hours: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "topics": [t.to_dict() for t in self.topics],
            "hours": self.hours
        }


@dataclass
class ParsedSyllabus:
    """Complete parsed syllabus structure."""
    course_name: str
    units: List[Unit] = field(default_factory=list)
    total_hours: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "course_name": self.course_name,
            "units": [u.to_dict() for u in self.units],
            "total_hours": self.total_hours
        }


class SyllabusParser:
    """Parser for extracting structured units from syllabus text."""
    
    # Common unit/chapter patterns
    UNIT_PATTERNS = [
        r"(?:Unit|UNIT)\s*[-:]?\s*(\d+)\s*[-:]?\s*(.+)",
        r"(?:Chapter|CHAPTER)\s*[-:]?\s*(\d+)\s*[-:]?\s*(.+)",
        r"(?:Module|MODULE)\s*[-:]?\s*(\d+)\s*[-:]?\s*(.+)",
        r"(\d+)\.\s+(.+)",  # "1. Introduction"
    ]
    
    # Topic bullet patterns
    TOPIC_PATTERNS = [
        r"^\s*[-•●○]\s*(.+)",
        r"^\s*\d+\.\d+\s*(.+)",  # "1.1 Topic"
        r"^\s*[a-z]\)\s*(.+)",   # "a) Topic"
    ]
    
    def __init__(self):
        self.unit_regex = [re.compile(p, re.IGNORECASE) for p in self.UNIT_PATTERNS]
        self.topic_regex = [re.compile(p, re.MULTILINE) for p in self.TOPIC_PATTERNS]
    
    def parse(self, text: str, course_name: str = "Untitled Course") -> ParsedSyllabus:
        """
        Parse syllabus text into structured units.
        
        Args:
            text: Raw syllabus text
            course_name: Name of the course
            
        Returns:
            ParsedSyllabus with units and topics
        """
        lines = text.split('\n')
        syllabus = ParsedSyllabus(course_name=course_name)
        
        current_unit = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match unit header
            unit_match = self._match_unit(line)
            if unit_match:
                if current_unit:
                    syllabus.units.append(current_unit)
                current_unit = Unit(
                    number=int(unit_match[0]),
                    title=unit_match[1].strip()
                )
                continue
            
            # If we have a current unit, try to match topics
            if current_unit:
                topic_match = self._match_topic(line)
                if topic_match:
                    # Extract keywords from topic name
                    keywords = self._extract_keywords(topic_match)
                    current_unit.topics.append(Topic(
                        name=topic_match,
                        keywords=keywords
                    ))
        
        # Add last unit
        if current_unit:
            syllabus.units.append(current_unit)
        
        return syllabus
    
    def _match_unit(self, line: str) -> Optional[tuple]:
        """Try to match line as unit header."""
        for pattern in self.unit_regex:
            match = pattern.match(line)
            if match:
                return match.groups()
        return None
    
    def _match_topic(self, line: str) -> Optional[str]:
        """Try to match line as topic bullet."""
        for pattern in self.topic_regex:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
        
        # If no bullet pattern, treat short lines as potential topics
        if len(line) < 100 and not line.endswith(':'):
            return line
        
        return None
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """Extract important keywords from topic text."""
        # Remove common stop words
        stop_words = {'and', 'or', 'the', 'a', 'an', 'in', 'of', 'to', 'for', 'with', 'on'}
        words = re.findall(r'\b[a-zA-Z]{3,}\b', topic.lower())
        return [w for w in words if w not in stop_words][:5]
    
    def get_all_topics_text(self, syllabus: ParsedSyllabus) -> List[str]:
        """Get all topics as text chunks for embedding."""
        chunks = []
        for unit in syllabus.units:
            # Add unit header as context
            unit_header = f"Unit {unit.number}: {unit.title}"
            for topic in unit.topics:
                chunk = f"{unit_header} - {topic.name}"
                chunks.append(chunk)
        return chunks


# CLI for testing
if __name__ == "__main__":
    sample = """
    Unit 1: Introduction to Computer Science
    - History of computing
    - Basic computer architecture
    - Programming paradigms
    
    Unit 2: Data Structures
    - Arrays and linked lists
    - Stacks and queues
    - Trees and graphs
    
    Unit 3: Algorithms
    - Sorting algorithms
    - Searching algorithms
    - Dynamic programming
    """
    
    parser = SyllabusParser()
    result = parser.parse(sample, "CS101")
    
    import json
    print(json.dumps(result.to_dict(), indent=2))
