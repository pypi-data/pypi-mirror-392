"""
Research resource for Incredible SDK.
Provides web search and deep research capabilities using Exa.AI.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


@dataclass
class SearchResult:
    """Individual search result from web search."""
    
    title: str
    url: str
    published_date: Optional[str] = None
    author: Optional[str] = None
    score: float = 0.0
    text: Optional[str] = None
    highlights: Optional[List[str]] = None
    summary: Optional[str] = None


@dataclass
class WebSearchResponse:
    """Response from web search endpoint."""
    
    success: bool
    results: List[SearchResult]
    autoprompt_string: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class WebSearch:
  
    
    def __init__(self, client) -> None:
        self._client = client
    
    def __call__(
        self,
        query: str,
        **kwargs
    ):
        """
        Shorthand for web_search() - allows calling client.web_search(...) directly.
        
        Example:
            ```python
            # Instead of client.web_search._create(...)
            results = client.web_search(
                query="Python tutorials",
                num_results=10
            )
            ```
        """
        return self._create(query=query, **kwargs)
    
    def _create(
        self,
        *,
        query: str,
        num_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: bool = True,
        search_type: Literal["neural", "keyword"] = "neural",
        category: Optional[str] = None,
        get_text: bool = False,
        get_highlights: bool = False,
        get_summary: bool = False,
        timeout: Optional[float] = None,
    ) -> WebSearchResponse:
        """
        Perform web search using Exa.AI.
        
        Args:
            query: The search query (required)
            num_results: Number of results to return (1-100, default: 10)
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
            start_published_date: Filter results published after this date (YYYY-MM-DD)
            end_published_date: Filter results published before this date (YYYY-MM-DD)
            use_autoprompt: Use Exa's autoprompt to enhance query (default: True)
            search_type: Search type - "neural" (semantic) or "keyword" (default: "neural")
            category: Filter by category (e.g., "company", "research paper")
            get_text: Retrieve full text content for each result
            get_highlights: Get key highlights from each result
            get_summary: Get AI-generated summary for each result
            timeout: Request timeout in seconds (optional)
        
        Returns:
            WebSearchResponse with:
                - success: Whether search was successful
                - results: List of search results
                - autoprompt_string: Enhanced query if autoprompt was used
        
        Raises:
            ValidationError: If request parameters are invalid
            APIError: If the API request fails
        
        Example:
            ```python
            # Basic search
            results = client.research.web_search(
                query="Latest AI developments",
                num_results=5
            )
            
            for result in results.results:
                print(f"{result.title}: {result.url}")
            
            # Advanced search with content
            results = client.research.web_search(
                query="Machine learning research",
                num_results=10,
                include_domains=["arxiv.org", "nature.com"],
                start_published_date="2024-01-01",
                get_text=True,
                get_summary=True
            )
            
            for result in results.results:
                print(f"{result.title}")
                print(f"Summary: {result.summary}")
            ```
        """
        if not query or not query.strip():
            from .._exceptions import ValidationError
            raise ValidationError("query cannot be empty")
        
        if num_results < 1 or num_results > 100:
            from .._exceptions import ValidationError
            raise ValidationError("num_results must be between 1 and 100")
        
        if search_type not in ["neural", "keyword"]:
            from .._exceptions import ValidationError
            raise ValidationError("search_type must be 'neural' or 'keyword'")
        
        # Build request payload
        payload: Dict[str, Any] = {
            "query": query,
            "num_results": num_results,
            "use_autoprompt": use_autoprompt,
            "type": search_type,
        }
        
        # Optional parameters
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        if start_published_date:
            payload["start_published_date"] = start_published_date
        if end_published_date:
            payload["end_published_date"] = end_published_date
        if category:
            payload["category"] = category
        
        # Content retrieval options
        if get_text or get_highlights or get_summary:
            payload["contents"] = {}
            if get_text:
                payload["contents"]["text"] = True
            if get_highlights:
                payload["contents"]["highlights"] = True
            if get_summary:
                payload["contents"]["summary"] = True
        
        # Make request
        response = self._client.request(
            "POST",
            "/v1/web-search",
            json=payload,
            timeout=timeout
        )
        
        data = response.json()
        
        # Parse results
        results = []
        for result_data in data.get("results", []):
            result = SearchResult(
                title=result_data.get("title", ""),
                url=result_data.get("url", ""),
                published_date=result_data.get("published_date"),
                author=result_data.get("author"),
                score=result_data.get("score", 0.0),
                text=result_data.get("text"),
                highlights=result_data.get("highlights"),
                summary=result_data.get("summary")
            )
            results.append(result)
        
        return WebSearchResponse(
            success=data.get("success", False),
            results=results,
            autoprompt_string=data.get("autoprompt_string"),
            raw_response=data
        )
