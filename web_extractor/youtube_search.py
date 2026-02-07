"""
YouTube Data API Client

Searches for educational videos by topic, ordered by view count,
with duration and relevance filtering.
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


class VideoDuration(Enum):
    """Video duration filter options."""
    ANY = "any"
    SHORT = "short"      # < 4 minutes
    MEDIUM = "medium"    # 4-20 minutes
    LONG = "long"        # > 20 minutes


class VideoOrder(Enum):
    """Video ordering options."""
    RELEVANCE = "relevance"
    VIEW_COUNT = "viewCount"
    DATE = "date"
    RATING = "rating"


@dataclass
class YouTubeVideo:
    """YouTube video result."""
    title: str
    video_id: str
    views: int
    likes: int
    channel: str
    channel_id: str
    description: str
    thumbnail: str
    duration: str
    published_at: str
    url: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class YouTubeSearchResult:
    """Complete YouTube search result."""
    query: str
    total_results: int
    videos: List[YouTubeVideo] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total_results": self.total_results,
            "videos": [v.to_dict() for v in self.videos]
        }


class YouTubeSearchClient:
    """Client for YouTube Data API v3."""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    
    # Quality education channels to prioritize
    QUALITY_CHANNELS = [
        "3Blue1Brown", "Fireship", "Computerphile", "Numberphile",
        "MIT OpenCourseWare", "Stanford", "Google", "Microsoft",
        "freeCodeCamp.org", "Traversy Media", "The Coding Train",
        "Sentdex", "Tech With Tim", "Corey Schafer", "ArjanCodes"
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize YouTube client.
        
        Args:
            api_key: YouTube Data API key. Reads from YOUTUBE_API_KEY env var if not provided.
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found. Set it in .env or pass to constructor.")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request to YouTube."""
        params["key"] = self.api_key
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def _parse_duration(self, duration: str) -> str:
        """
        Parse ISO 8601 duration to human readable format.
        Example: PT1H2M10S -> 1:02:10
        """
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return duration
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _parse_view_count(self, count: str) -> int:
        """Parse view count string to integer."""
        try:
            return int(count)
        except (ValueError, TypeError):
            return 0
    
    def search_videos(
        self,
        query: str,
        max_results: int = 10,
        order: VideoOrder = VideoOrder.VIEW_COUNT,
        duration: VideoDuration = VideoDuration.ANY,
        relevance_language: str = "en",
        type_filter: str = "video"
    ) -> List[str]:
        """
        Search for videos by query.
        
        Args:
            query: Search query
            max_results: Number of results (max 50)
            order: Sort order (viewCount, relevance, date, rating)
            duration: Duration filter (short, medium, long, any)
            relevance_language: Language preference
            type_filter: Type of results (video only)
            
        Returns:
            List of video IDs
        """
        params = {
            "part": "snippet",
            "q": query,
            "type": type_filter,
            "maxResults": min(max_results, 50),
            "order": order.value,
            "relevanceLanguage": relevance_language,
            "safeSearch": "moderate"
        }
        
        if duration != VideoDuration.ANY:
            params["videoDuration"] = duration.value
        
        data = self._make_request("search", params)
        
        video_ids = []
        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)
        
        return video_ids
    
    def get_video_details(self, video_ids: List[str]) -> List[YouTubeVideo]:
        """
        Get detailed video information.
        
        Args:
            video_ids: List of video IDs
            
        Returns:
            List of YouTubeVideo objects
        """
        if not video_ids:
            return []
        
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(video_ids)
        }
        
        data = self._make_request("videos", params)
        
        videos = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            
            video = YouTubeVideo(
                title=snippet.get("title", ""),
                video_id=item.get("id", ""),
                views=self._parse_view_count(stats.get("viewCount", "0")),
                likes=self._parse_view_count(stats.get("likeCount", "0")),
                channel=snippet.get("channelTitle", ""),
                channel_id=snippet.get("channelId", ""),
                description=snippet.get("description", "")[:500],
                thumbnail=snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                duration=self._parse_duration(content.get("duration", "")),
                published_at=snippet.get("publishedAt", ""),
                url=f"https://www.youtube.com/watch?v={item.get('id', '')}",
                metadata={
                    "comment_count": self._parse_view_count(stats.get("commentCount", "0")),
                    "is_quality_channel": snippet.get("channelTitle", "") in self.QUALITY_CHANNELS
                }
            )
            videos.append(video)
        
        return videos
    
    def discover_videos(
        self,
        topic: str,
        max_results: int = 10,
        order: VideoOrder = VideoOrder.VIEW_COUNT,
        duration: VideoDuration = VideoDuration.ANY
    ) -> YouTubeSearchResult:
        """
        Discover educational videos for a topic.
        
        Args:
            topic: Topic to search
            max_results: Number of results
            order: Sort order
            duration: Duration filter
            
        Returns:
            YouTubeSearchResult with video details
        """
        # Search for video IDs
        video_ids = self.search_videos(
            query=topic,
            max_results=max_results,
            order=order,
            duration=duration
        )
        
        # Get detailed video info
        videos = self.get_video_details(video_ids)
        
        # Sort by views if order is viewCount
        if order == VideoOrder.VIEW_COUNT:
            videos.sort(key=lambda v: v.views, reverse=True)
        
        return YouTubeSearchResult(
            query=topic,
            total_results=len(videos),
            videos=videos
        )
    
    def search_tutorials(self, topic: str, max_results: int = 10) -> YouTubeSearchResult:
        """Search for tutorials on a topic."""
        return self.discover_videos(
            topic=f"{topic} tutorial",
            max_results=max_results,
            order=VideoOrder.VIEW_COUNT,
            duration=VideoDuration.MEDIUM
        )
    
    def search_courses(self, topic: str, max_results: int = 10) -> YouTubeSearchResult:
        """Search for full course videos on a topic."""
        return self.discover_videos(
            topic=f"{topic} full course",
            max_results=max_results,
            order=VideoOrder.VIEW_COUNT,
            duration=VideoDuration.LONG
        )
    
    def search_shorts(self, topic: str, max_results: int = 10) -> YouTubeSearchResult:
        """Search for short explainer videos on a topic."""
        return self.discover_videos(
            topic=f"{topic} explained",
            max_results=max_results,
            order=VideoOrder.VIEW_COUNT,
            duration=VideoDuration.SHORT
        )


# CLI interface
if __name__ == "__main__":
    import json
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Video Discovery")
    parser.add_argument("topic", help="Topic to search")
    parser.add_argument("--max", type=int, default=10, help="Max results")
    parser.add_argument("--order", choices=["viewCount", "relevance", "date", "rating"], 
                        default="viewCount", help="Sort order")
    parser.add_argument("--duration", choices=["any", "short", "medium", "long"],
                        default="any", help="Duration filter")
    parser.add_argument("--output", type=str, help="Output JSON file")
    
    args = parser.parse_args()
    
    client = YouTubeSearchClient()
    result = client.discover_videos(
        args.topic,
        max_results=args.max,
        order=VideoOrder(args.order),
        duration=VideoDuration(args.duration)
    )
    
    output = result.to_dict()
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(output, indent=2))
