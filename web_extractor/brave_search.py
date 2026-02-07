"""
Brave Search API Client

Fetches web, news, images, and video results for topic-based discovery.
Categorizes results into Wikipedia, research papers, guides, tutorials, etc.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class SourceCategory(Enum):
    """Categories for search results."""
    WIKIPEDIA = "wikipedia"
    RESEARCH_PAPER = "research_paper"
    STUDY_GUIDE = "study_guide"
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    NEWS = "news"
    VIDEO = "video"
    IMAGE = "image"
    BLOG = "blog"
    FORUM = "forum"
    OTHER = "other"


@dataclass
class SearchResult:
    """Single search result."""
    title: str
    url: str
    description: str
    source: str  # Domain or source name
    category: str  # SourceCategory value
    result_type: str = "web"  # web, news, image, video
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DiscoveryResult:
    """Complete discovery result for a topic."""
    query: str
    total_results: int
    wikipedia: List[SearchResult] = field(default_factory=list)
    research_papers: List[SearchResult] = field(default_factory=list)
    study_guides: List[SearchResult] = field(default_factory=list)
    documentation: List[SearchResult] = field(default_factory=list)
    tutorials: List[SearchResult] = field(default_factory=list)
    news: List[SearchResult] = field(default_factory=list)
    videos: List[SearchResult] = field(default_factory=list)
    images: List[SearchResult] = field(default_factory=list)
    blogs: List[SearchResult] = field(default_factory=list)
    other: List[SearchResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total_results": self.total_results,
            "filter_stats": self.metadata,
            "wikipedia": [r.to_dict() for r in self.wikipedia],
            "research_papers": [r.to_dict() for r in self.research_papers],
            "study_guides": [r.to_dict() for r in self.study_guides],
            "documentation": [r.to_dict() for r in self.documentation],
            "tutorials": [r.to_dict() for r in self.tutorials],
            "news": [r.to_dict() for r in self.news],
            "videos": [r.to_dict() for r in self.videos],
            "images": [r.to_dict() for r in self.images],
            "blogs": [r.to_dict() for r in self.blogs],
            "other": [r.to_dict() for r in self.other]
        }


class BraveSearchClient:
    """Client for Brave Search API."""
    
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    # Domains to BLOCK (noisy, thin content)
    BLOCKED_DOMAINS = [
        "quora.com",
        "reddit.com",
        "pinterest.com",
        "facebook.com",
        "twitter.com",
        "x.com",
        "instagram.com",
        "tiktok.com",
        "linkedin.com/posts",
        "yahoo.answers",
        "answers.com",
        "ask.com",
        "ehow.com",
        "wikihow.com"  # Often thin content
    ]
    
    # Quality domains to PRIORITIZE
    QUALITY_DOMAINS = [
        # Documentation
        "docs.python.org", "docs.microsoft.com", "developer.mozilla.org",
        "docs.aws.amazon.com", "cloud.google.com/docs", "docs.oracle.com",
        # Engineering blogs
        "engineering.fb.com", "netflixtechblog.com", "blog.google",
        "aws.amazon.com/blogs", "engineering.linkedin.com", "uber.com/blog",
        "stripe.com/blog", "dropbox.tech", "engineering.atspotify.com",
        # Research & Academic
        "arxiv.org", "scholar.google.com", "researchgate.net",
        "semanticscholar.org", "acm.org", "ieee.org", "nature.com",
        # Quality tutorials
        "realpython.com", "freecodecamp.org", "digitalocean.com/community",
        "baeldung.com", "tutorialspoint.com", "geeksforgeeks.org",
        # Reference
        "wikipedia.org", "stackoverflow.com", "stackexchange.com"
    ]
    
    # Domain patterns for categorization
    CATEGORY_PATTERNS = {
        SourceCategory.WIKIPEDIA: ["wikipedia.org", "wikimedia.org"],
        SourceCategory.RESEARCH_PAPER: [
            "arxiv.org", "scholar.google", "researchgate.net", "ieee.org",
            "acm.org", "springer.com", "sciencedirect.com", "nature.com",
            "ncbi.nlm.nih.gov", "pubmed", "semanticscholar.org", "jstor.org"
        ],
        SourceCategory.STUDY_GUIDE: [
            "coursera.org", "edx.org", "udemy.com", "khanacademy.org",
            "studyguide", "study-guide", "cheatsheet", "learnxinyminutes",
            "geeksforgeeks.org", "w3schools.com", "tutorialspoint.com"
        ],
        SourceCategory.DOCUMENTATION: [
            "docs.", ".readthedocs.", "documentation", "developer.",
            "devdocs.io", "mozilla.org/docs", "python.org/doc"
        ],
        SourceCategory.TUTORIAL: [
            "tutorial", "how-to", "howto", "guide", "learn",
            "freecodecamp.org", "codecademy.com", "realpython.com"
        ],
        SourceCategory.BLOG: [
            "medium.com", "dev.to", "hashnode", "substack.com",
            "blog.", "wordpress.com", "blogger.com", "towardsdatascience.com",
            "engineering.", "techblog", "tech-blog"
        ],
        SourceCategory.FORUM: [
            "stackoverflow.com", "stackexchange.com", "discourse", "forum"
        ]
    }
    
    def __init__(self, api_key: Optional[str] = None, filter_noisy: bool = True):
        """
        Initialize Brave Search client.
        
        Args:
            api_key: Brave API key. If not provided, reads from BRAVE_API_KEY env var.
            filter_noisy: If True, filter out noisy/blocked domains.
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not found. Set it in .env or pass to constructor.")
        
        self.filter_noisy = filter_noisy
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
    
    def _is_blocked(self, url: str) -> bool:
        """Check if URL is from a blocked domain."""
        url_lower = url.lower()
        for domain in self.BLOCKED_DOMAINS:
            if domain in url_lower:
                return True
        return False
    
    def _is_quality_domain(self, url: str) -> bool:
        """Check if URL is from a quality domain."""
        url_lower = url.lower()
        for domain in self.QUALITY_DOMAINS:
            if domain in url_lower:
                return True
        return False
    
    def _extract_base_domain(self, url: str) -> str:
        """Extract base domain from URL for deduplication."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            # Get domain without subdomain (simplified)
            parts = parsed.netloc.split(".")
            if len(parts) >= 2:
                return ".".join(parts[-2:])
            return parsed.netloc
        except:
            return url
    
    def _filter_and_dedupe(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Filter blocked domains and deduplicate by domain.
        
        Args:
            results: List of search results
            
        Returns:
            Filtered and deduplicated results
        """
        seen_domains = set()
        filtered = []
        
        for result in results:
            # Skip blocked domains
            if self.filter_noisy and self._is_blocked(result.url):
                continue
            
            # Deduplicate by domain
            base_domain = self._extract_base_domain(result.url)
            if base_domain in seen_domains:
                continue
            
            seen_domains.add(base_domain)
            
            # Add quality flag to metadata
            result.metadata["is_quality"] = self._is_quality_domain(result.url)
            
            filtered.append(result)
        
        # Sort by quality (quality domains first)
        filtered.sort(key=lambda r: (not r.metadata.get("is_quality", False), r.title))
        
        return filtered
    
    def _categorize_url(self, url: str, title: str = "", description: str = "") -> SourceCategory:
        """Categorize a URL based on domain patterns."""
        url_lower = url.lower()
        text_lower = f"{title} {description}".lower()
        
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern in url_lower or pattern in text_lower:
                    return category
        
        return SourceCategory.OTHER
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request to Brave Search."""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def search_web(self, query: str, count: int = 20) -> List[SearchResult]:
        """
        Search the web for a query.
        
        Args:
            query: Search query
            count: Number of results (max 20)
            
        Returns:
            List of SearchResult objects
        """
        params = {
            "q": query,
            "count": min(count, 20),
            "text_decorations": False,
            "search_lang": "en"
        }
        
        data = self._make_request("web/search", params)
        results = []
        
        for item in data.get("web", {}).get("results", []):
            url = item.get("url", "")
            title = item.get("title", "")
            description = item.get("description", "")
            
            category = self._categorize_url(url, title, description)
            
            result = SearchResult(
                title=title,
                url=url,
                description=description,
                source=item.get("meta_url", {}).get("hostname", ""),
                category=category.value,
                result_type="web",
                metadata={
                    "favicon": item.get("meta_url", {}).get("favicon", ""),
                    "age": item.get("age", "")
                }
            )
            results.append(result)
        
        return results
    
    def search_news(self, query: str, count: int = 10) -> List[SearchResult]:
        """Search news articles."""
        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": "en"
        }
        
        data = self._make_request("news/search", params)
        results = []
        
        for item in data.get("results", []):
            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                description=item.get("description", ""),
                source=item.get("meta_url", {}).get("hostname", ""),
                category=SourceCategory.NEWS.value,
                result_type="news",
                metadata={
                    "age": item.get("age", ""),
                    "thumbnail": item.get("thumbnail", {}).get("src", "")
                }
            )
            results.append(result)
        
        return results
    
    def search_images(self, query: str, count: int = 10) -> List[SearchResult]:
        """Search images."""
        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": "en"
        }
        
        try:
            data = self._make_request("images/search", params)
            results = []
            
            for item in data.get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    description=item.get("source", ""),
                    source=item.get("source", ""),
                    category=SourceCategory.IMAGE.value,
                    result_type="image",
                    metadata={
                        "thumbnail": item.get("thumbnail", {}).get("src", ""),
                        "properties": item.get("properties", {})
                    }
                )
                results.append(result)
            
            return results
        except Exception as e:
            print(f"Image search failed: {e}")
            return []
    
    def search_videos(self, query: str, count: int = 10) -> List[SearchResult]:
        """Search videos."""
        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": "en"
        }
        
        try:
            data = self._make_request("videos/search", params)
            results = []
            
            for item in data.get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    description=item.get("description", ""),
                    source=item.get("meta_url", {}).get("hostname", ""),
                    category=SourceCategory.VIDEO.value,
                    result_type="video",
                    metadata={
                        "thumbnail": item.get("thumbnail", {}).get("src", ""),
                        "age": item.get("age", ""),
                        "creator": item.get("creator", "")
                    }
                )
                results.append(result)
            
            return results
        except Exception as e:
            print(f"Video search failed: {e}")
            return []
    
    def discover_topic(
        self,
        topic: str,
        web_count: int = 20,
        news_count: int = 5,
        image_count: int = 5,
        video_count: int = 5
    ) -> DiscoveryResult:
        """
        Comprehensive topic discovery.
        
        Fetches web, news, images, and videos, then categorizes all results.
        
        Args:
            topic: Topic to discover
            web_count: Number of web results
            news_count: Number of news results
            image_count: Number of image results
            video_count: Number of video results
            
        Returns:
            DiscoveryResult with categorized content
        """
        # Fetch all result types
        web_results = self.search_web(topic, web_count)
        news_results = self.search_news(topic, news_count)
        image_results = self.search_images(topic, image_count)
        video_results = self.search_videos(topic, video_count)
        
        # Filter and deduplicate web results
        web_results = self._filter_and_dedupe(web_results)
        
        # Create discovery result
        discovery = DiscoveryResult(
            query=topic,
            total_results=len(web_results) + len(news_results) + len(image_results) + len(video_results),
        )
        
        # Track filtered stats
        discovery.metadata = {
            "filtered": True,
            "blocked_domains": self.BLOCKED_DOMAINS,
            "quality_domains_count": sum(1 for r in web_results if r.metadata.get("is_quality"))
        }
        
        # Categorize web results
        for result in web_results:
            category = result.category
            if category == SourceCategory.WIKIPEDIA.value:
                discovery.wikipedia.append(result)
            elif category == SourceCategory.RESEARCH_PAPER.value:
                discovery.research_papers.append(result)
            elif category == SourceCategory.STUDY_GUIDE.value:
                discovery.study_guides.append(result)
            elif category == SourceCategory.DOCUMENTATION.value:
                discovery.documentation.append(result)
            elif category == SourceCategory.TUTORIAL.value:
                discovery.tutorials.append(result)
            elif category == SourceCategory.BLOG.value:
                discovery.blogs.append(result)
            else:
                discovery.other.append(result)
        
        # Add news, images, videos
        discovery.news.extend(news_results)
        discovery.images.extend(image_results)
        discovery.videos.extend(video_results)
        
        return discovery
    
    def search_wikipedia(self, topic: str, count: int = 5) -> List[SearchResult]:
        """Search specifically for Wikipedia articles."""
        query = f"site:wikipedia.org {topic}"
        return self.search_web(query, count)
    
    def search_research_papers(self, topic: str, count: int = 10) -> List[SearchResult]:
        """Search for research papers."""
        query = f"{topic} (site:arxiv.org OR site:scholar.google.com OR site:researchgate.net OR site:semanticscholar.org)"
        return self.search_web(query, count)
    
    def search_study_guides(self, topic: str, count: int = 10) -> List[SearchResult]:
        """Search for study guides and tutorials."""
        query = f"{topic} tutorial OR guide OR learn OR course"
        results = self.search_web(query, count)
        # Filter to only study-related categories
        return [r for r in results if r.category in [
            SourceCategory.STUDY_GUIDE.value,
            SourceCategory.TUTORIAL.value,
            SourceCategory.DOCUMENTATION.value
        ]]


# CLI interface
if __name__ == "__main__":
    import json
    import argparse
    
    parser = argparse.ArgumentParser(description="Brave Search Topic Discovery")
    parser.add_argument("topic", help="Topic to discover")
    parser.add_argument("--web", type=int, default=20, help="Number of web results")
    parser.add_argument("--news", type=int, default=5, help="Number of news results")
    parser.add_argument("--images", type=int, default=5, help="Number of image results")
    parser.add_argument("--videos", type=int, default=5, help="Number of video results")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    client = BraveSearchClient()
    result = client.discover_topic(
        args.topic,
        web_count=args.web,
        news_count=args.news,
        image_count=args.images,
        video_count=args.videos
    )
    
    output = result.to_dict()
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(output, indent=2))
