"""
Research resource for Incredible SDK.
Provides web search and deep research capabilities using Exa.AI.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


@dataclass
class Citation:
    """Citation from research."""
    
    url: str
    title: str


@dataclass
class DeepResearchResponse:
    """Response from deep research endpoint."""
    
    success: bool
    research_id: str
    status: str
    output: Dict[str, Any]
    citations: Optional[List[Citation]] = None
    searches_performed: Optional[int] = None
    pages_read: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None


class DeepResearch:    
    def __init__(self, client) -> None:
        self._client = client
    
    def __call__(
        self,
        instructions: str,
        **kwargs
    ):
        """
        Shorthand for deep_research() - allows calling client.deep_research(...) directly.
        
        Example:
            ```python
            # Instead of client.deep_research._create(...)
            report = client.deep_research(
                instructions="Python tutorials",
                num_results=10
            )
            ```
        """
        return self._create(instructions=instructions, **kwargs)
    
    def _create(
        self,
        *,
        instructions: str,
        output_schema: Optional[Dict[str, Any]] = None,
        model: Literal["exa-research", "exa-research-pro"] = "exa-research",
        use_cache: bool = True,
        timeout: Optional[float] = None,
    ) -> DeepResearchResponse:
        """
        Perform deep research using Exa.AI.
        
        This endpoint creates a research task that performs multi-step web research,
        synthesizing information into a structured report with citations.
        
        Args:
            instructions: Research task description (required)
            output_schema: Optional JSON schema for structured output
            model: Model to use - "exa-research" or "exa-research-pro" (default: "exa-research")
            use_cache: Use cached results for identical requests (default: True)
            timeout: Request timeout in seconds (optional, default: 600 = 10 minutes)
        
        Returns:
            DeepResearchResponse with:
                - success: Whether research was successful
                - research_id: Unique research task ID
                - status: Research status (e.g., "completed")
                - output: Structured output (matches schema if provided)
                - citations: List of sources cited
                - searches_performed: Number of searches performed
                - pages_read: Number of pages analyzed
        
        Raises:
            ValidationError: If request parameters are invalid
            APIError: If the API request fails
        
        Example:
            ```python
            # Free-form research
            report = client.research.deep_research(
                instructions="Research the latest trends in renewable energy"
            )
            
            print(f"Research ID: {report.research_id}")
            print(f"Output: {report.output}")
            print(f"Citations: {len(report.citations)}")
            
            # Structured research with output schema
            schema = {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "key_findings": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "market_size": {"type": "number"}
                },
                "required": ["summary", "key_findings"]
            }
            
            report = client.research.deep_research(
                instructions="Analyze the AI chip market",
                output_schema=schema,
                model="exa-research-pro"
            )
            
            print(f"Summary: {report.output['summary']}")
            for finding in report.output['key_findings']:
                print(f"- {finding}")
            ```
        
        Note:
            - Deep research may take several minutes (default timeout: 10 minutes)
            - The "exa-research-pro" model provides more comprehensive results
            - Citations include source URLs and titles
            - Searches and pages read count toward API usage
        """
        if not instructions or not instructions.strip():
            from .._exceptions import ValidationError
            raise ValidationError("instructions cannot be empty")
        
        if model not in ["exa-research", "exa-research-pro"]:
            from .._exceptions import ValidationError
            raise ValidationError("model must be 'exa-research' or 'exa-research-pro'")
        
        # Build request payload
        payload: Dict[str, Any] = {
            "instructions": instructions,
            "model": model,
            "use_cache": use_cache,
        }
        
        if output_schema:
            payload["output_schema"] = output_schema
        
        # Make request (research can take a long time)
        if timeout is None:
            timeout = 600.0  # 10 minutes default for deep research
        
        response = self._client.request(
            "POST",
            "/v1/deep-research",
            json=payload,
            timeout=timeout
        )
        
        data = response.json()
        
        # Parse citations
        citations = None
        if data.get("citations"):
            citations = [
                Citation(
                    url=cite.get("url", ""),
                    title=cite.get("title", "")
                )
                for cite in data["citations"]
            ]
        
        return DeepResearchResponse(
            success=data.get("success", False),
            research_id=data.get("research_id", ""),
            status=data.get("status", ""),
            output=data.get("output", {}),
            citations=citations,
            searches_performed=data.get("searches_performed"),
            pages_read=data.get("pages_read"),
            raw_response=data
        )

