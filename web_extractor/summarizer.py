"""
LLM Summarization & Insight Generator

Uses Groq API with Llama 3.3 70B to synthesize content from web search, 
images, and YouTube videos into structured insights.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class TopicInsights:
    """Structured insights for a topic."""
    topic: str
    key_concepts: List[str] = field(default_factory=list)
    step_by_step_explanation: List[str] = field(default_factory=list)
    practical_todos: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    learning_roadmap: List[str] = field(default_factory=list)
    further_resources: List[Dict[str, str]] = field(default_factory=list)
    summary: str = ""
    sources_used: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GroqSummarizer:
    """LLM-powered content summarizer using Groq API with Llama 3.3."""
    
    # Use Llama 3.3 70B for best quality
    MODEL = "llama-3.3-70b-versatile"
    
    SYSTEM_PROMPT = """You are an expert educational content synthesizer. Your task is to analyze 
content from multiple sources (web articles, YouTube videos, images) and generate structured, 
actionable insights for someone learning a new topic.

Always provide:
1. KEY CONCEPTS - Core ideas that must be understood (5-8 items)
2. STEP-BY-STEP EXPLANATION - How the topic works in logical sequence (5-7 steps)
3. PRACTICAL TO-DOS - Hands-on actions to apply the knowledge (5-7 items)
4. COMMON MISTAKES - Pitfalls to avoid when learning/applying this topic (4-6 items)
5. LEARNING ROADMAP - Suggested progression from beginner to advanced (4-6 stages)
6. SUMMARY - 2-3 sentence overview

Be concise, practical, and focus on actionable knowledge.
Format your response as valid JSON with these exact keys:
{
    "key_concepts": ["concept1", "concept2", ...],
    "step_by_step_explanation": ["step1", "step2", ...],
    "practical_todos": ["todo1", "todo2", ...],
    "common_mistakes": ["mistake1", "mistake2", ...],
    "learning_roadmap": ["stage1", "stage2", ...],
    "summary": "2-3 sentence overview"
}

IMPORTANT: Return ONLY valid JSON, no other text."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq summarizer.
        
        Args:
            api_key: Groq API key. Reads from GROQ_API_KEY env var if not provided.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it in .env or pass to constructor.")
        
        # Initialize Groq client
        from groq import Groq
        self.client = Groq(api_key=self.api_key)
    
    def _format_web_content(self, web_data: Dict[str, Any]) -> str:
        """Format web search results for LLM input."""
        content = []
        
        # Wikipedia
        for item in web_data.get("wikipedia", []):
            content.append(f"[Wikipedia] {item.get('title', '')}: {item.get('description', '')}")
        
        # Research papers
        for item in web_data.get("research_papers", []):
            content.append(f"[Research] {item.get('title', '')}: {item.get('description', '')}")
        
        # Documentation
        for item in web_data.get("documentation", []):
            content.append(f"[Docs] {item.get('title', '')}: {item.get('description', '')}")
        
        # Tutorials
        for item in web_data.get("tutorials", []):
            content.append(f"[Tutorial] {item.get('title', '')}: {item.get('description', '')}")
        
        # Blogs
        for item in web_data.get("blogs", []):
            content.append(f"[Blog] {item.get('title', '')}: {item.get('description', '')}")
        
        # Other
        for item in web_data.get("other", []):
            content.append(f"[Web] {item.get('title', '')}: {item.get('description', '')}")
        
        return "\n".join(content)
    
    def _format_youtube_content(self, yt_data: Dict[str, Any]) -> str:
        """Format YouTube search results for LLM input."""
        content = []
        
        for video in yt_data.get("videos", []):
            views = video.get("views", 0)
            view_str = f"{views/1000000:.1f}M" if views > 1000000 else f"{views/1000:.0f}K"
            content.append(
                f"[Video: {view_str} views] {video.get('title', '')} by {video.get('channel', '')}: "
                f"{video.get('description', '')[:300]}"
            )
        
        return "\n".join(content)
    
    def _format_image_content(self, img_data: Dict[str, Any]) -> str:
        """Format image search results for LLM input."""
        content = []
        
        for img in img_data.get("images", []):
            content.append(f"[Image] {img.get('title', '')} from {img.get('source', '')}")
        
        return "\n".join(content)
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM JSON response."""
        try:
            # Clean up response - find JSON block
            text = response_text.strip()
            
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Fallback: return raw text as summary
            return {
                "key_concepts": [],
                "step_by_step_explanation": [],
                "practical_todos": [],
                "common_mistakes": [],
                "learning_roadmap": [],
                "summary": response_text[:500]
            }
    
    def generate_insights(
        self,
        topic: str,
        web_data: Optional[Dict[str, Any]] = None,
        youtube_data: Optional[Dict[str, Any]] = None,
        image_data: Optional[Dict[str, Any]] = None
    ) -> TopicInsights:
        """
        Generate comprehensive insights for a topic from multiple sources.
        
        Args:
            topic: The topic being researched
            web_data: Results from Brave web search
            youtube_data: Results from YouTube search
            image_data: Results from image search
            
        Returns:
            TopicInsights with structured knowledge
        """
        # Build content sections
        sections = []
        sources_used = {}
        
        if web_data:
            web_content = self._format_web_content(web_data)
            if web_content:
                sections.append(f"=== WEB CONTENT ===\n{web_content}")
                sources_used["web"] = len(web_data.get("tutorials", [])) + len(web_data.get("blogs", [])) + len(web_data.get("documentation", []))
        
        if youtube_data:
            yt_content = self._format_youtube_content(youtube_data)
            if yt_content:
                sections.append(f"=== YOUTUBE VIDEOS ===\n{yt_content}")
                sources_used["youtube"] = len(youtube_data.get("videos", []))
        
        if image_data:
            img_content = self._format_image_content(image_data)
            if img_content:
                sections.append(f"=== RELATED IMAGES ===\n{img_content}")
                sources_used["images"] = len(image_data.get("images", []))
        
        if not sections:
            raise ValueError("No content provided for summarization")
        
        # Build user prompt
        user_prompt = f"""Topic: {topic}

From the following content gathered from multiple sources, generate structured insights.

{chr(10).join(sections)}

Analyze all content and extract actionable knowledge. Return ONLY valid JSON."""

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse response
        response_text = response.choices[0].message.content
        parsed = self._parse_llm_response(response_text)
        
        # Build further resources
        resources = []
        if web_data:
            for item in web_data.get("tutorials", [])[:3]:
                resources.append({"title": item.get("title", ""), "url": item.get("url", ""), "type": "tutorial"})
            for item in web_data.get("documentation", [])[:2]:
                resources.append({"title": item.get("title", ""), "url": item.get("url", ""), "type": "docs"})
        if youtube_data:
            for video in youtube_data.get("videos", [])[:3]:
                resources.append({"title": video.get("title", ""), "url": video.get("url", ""), "type": "video"})
        
        return TopicInsights(
            topic=topic,
            key_concepts=parsed.get("key_concepts", []),
            step_by_step_explanation=parsed.get("step_by_step_explanation", []),
            practical_todos=parsed.get("practical_todos", []),
            common_mistakes=parsed.get("common_mistakes", []),
            learning_roadmap=parsed.get("learning_roadmap", []),
            further_resources=resources,
            summary=parsed.get("summary", ""),
            sources_used=sources_used
        )


class TopicResearcher:
    """Complete topic research pipeline combining search + summarization."""
    
    def __init__(
        self,
        brave_api_key: Optional[str] = None,
        youtube_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None
    ):
        """Initialize all API clients."""
        from web_extractor.brave_search import BraveSearchClient
        from web_extractor.youtube_search import YouTubeSearchClient
        
        self.brave = BraveSearchClient(api_key=brave_api_key)
        self.youtube = YouTubeSearchClient(api_key=youtube_api_key)
        self.summarizer = GroqSummarizer(api_key=groq_api_key)
    
    def research_topic(
        self,
        topic: str,
        web_count: int = 15,
        youtube_count: int = 5,
        image_count: int = 5
    ) -> Dict[str, Any]:
        """
        Complete topic research: search + summarize.
        
        Args:
            topic: Topic to research
            web_count: Number of web results
            youtube_count: Number of YouTube videos
            image_count: Number of images
            
        Returns:
            Complete research results with insights
        """
        # Fetch all data
        web_data = self.brave.discover_topic(topic, web_count=web_count, image_count=0).to_dict()
        youtube_data = self.youtube.discover_videos(topic, max_results=youtube_count).to_dict()
        image_data = {"images": [r.to_dict() for r in self.brave.search_images(topic, image_count)]}
        
        # Generate insights
        insights = self.summarizer.generate_insights(
            topic,
            web_data=web_data,
            youtube_data=youtube_data,
            image_data=image_data
        )
        
        return {
            "topic": topic,
            "insights": insights.to_dict(),
            "raw_data": {
                "web": web_data,
                "youtube": youtube_data,
                "images": image_data
            }
        }


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Topic Research & Summarization")
    parser.add_argument("topic", help="Topic to research")
    parser.add_argument("--web", type=int, default=15, help="Number of web results")
    parser.add_argument("--youtube", type=int, default=5, help="Number of YouTube videos")
    parser.add_argument("--images", type=int, default=5, help="Number of images")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    researcher = TopicResearcher()
    result = researcher.research_topic(
        args.topic,
        web_count=args.web,
        youtube_count=args.youtube,
        image_count=args.images
    )
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))
