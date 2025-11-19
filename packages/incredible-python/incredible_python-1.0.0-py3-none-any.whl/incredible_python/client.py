from __future__ import annotations

from typing import Mapping, Optional, cast

from ._base_client import BaseClient
from .resources.messages import Messages
from .resources.models import Models
from .resources.integrations import Integrations
from .resources.completions import Completions
from .resources.ocr import OCR
from .resources.images import Images
from .resources.videos import Videos
from .resources.deep_research import DeepResearch
from .resources.web_search import WebSearch
from .resources.agent import Agent
from .resources.answer import Answer
from .resources.conversation import Conversation


class Incredible(BaseClient):
    """Anthropic-compatible client for the Incredible API.
    
    Provides access to all Incredible API endpoints through a clean interface.
    
    ✨ ALL RESOURCES ARE NOW CALLABLE!
    
    Attributes:
        messages: Chat completions (Anthropic-style) - CALLABLE!
        completions: Text completions (OpenAI-style) - CALLABLE!
        models: Available models
        integrations: Third-party integrations
        ocr: OCR for text extraction from images/PDFs
        images: Image generation - CALLABLE!
        videos: Video generation - CALLABLE!
        research: Web search and deep research  - CALLABLE!
        agent: Agentic conversation with tool calling (Kimi K2 Thinking) - CALLABLE!
        answer: Simple Q&A with optional structured output (Minimax M2) - CALLABLE!
        conversation: Multi-turn conversations (DeepSeek v3.1) - CALLABLE!
    
    Example:
        >>> from incredible_python import Incredible
        >>> client = Incredible(api_key="your-api-key")
        >>> 
        >>> # Answer - callable!
        >>> response = client.answer(query="What is 2+2?")
        >>> print(response.answer)
        >>> 
        >>> # Messages - callable!
        >>> response = client.messages(
        ...     model="small-1",
        ...     max_tokens=100,
        ...     messages=[{"role": "user", "content": "Hello"}]
        ... )
        >>> print(response.content[0]['text'])
        >>> 
        >>> # Images - callable!
        >>> image = client.images(prompt="A sunset", aspect_ratio="16:9")
        >>> print(image.image_url)
        >>> 
        >>> # Videos - callable!
        >>> video = client.videos(prompt="Ocean waves", size="1280x720")
        >>> print(video.video_url)
        >>> 
        >>> # Research - callable!
        >>> results = client.research(query="Python tutorials", num_results=10)
        >>> for result in results.results:
        ...     print(result.title)
        >>> 
        >>> # Completions - callable!
        >>> response = client.completions(prompt="Once upon a time", model="small-1", max_tokens=50)
        >>> print(response.choices[0].text)
        >>> 
        >>> # Conversation - callable!
        >>> response = client.conversation(
        ...     messages=[
        ...         {"role": "user", "content": "Hi"},
        ...         {"role": "assistant", "content": "Hello!"},
        ...         {"role": "user", "content": "How are you?"}
        ...     ]
        ... )
        >>> print(response.response)
        >>> 
        >>> # Agent - callable!
        >>> response = client.agent(
        ...     messages=[{"role": "user", "content": "Calculate 5+5"}],
        ...     tools=[{"name": "calculator", "description": "...", "input_schema": {...}}]
        ... )
        >>> for call in response.tool_calls:
        ...     print(f"Tool: {call.name}")
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float | None = None,
        max_retries: int = BaseClient.DEFAULT_MAX_RETRIES,
        default_headers: Optional[dict[str, str]] = None,
        default_query: Optional[dict[str, object]] = None,
        http_client=None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout or BaseClient.DEFAULT_TIMEOUT,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
        )
        # Legacy resources
        self.messages = Messages(self)
        self.completions = Completions(self)
        self.models = Models(self)
        self.integrations = Integrations(self)
        
        # New resources
        self.answer = Answer(self)
        self.conversation = Conversation(self)
        self.agent = Agent(self)
        self.web_search = WebSearch(self)
        self.deep_research = DeepResearch(self)
        self.generate_image = Images(self)
        self.generate_video = Videos(self)
        self.ocr = OCR(self)

    def with_options(
        self,
        *,
        timeout: Optional[float] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
    ) -> "Incredible":
        client = cast(
            Incredible,
            super().with_options(
            timeout=timeout,
            default_headers=default_headers,
            default_query=default_query,
            ),
        )
        # Legacy resources
        client.messages = Messages(client)
        client.completions = Completions(client)
        client.models = Models(client)
        client.integrations = Integrations(client)
        
        # New resources
        client.answer = Answer(client)
        client.conversation = Conversation(client)
        client.agent = Agent(client)
        client.web_search = WebSearch(client)
        client.deep_research = DeepResearch(client)
        client.generate_image = Images(client)
        client.generate_video = Videos(client)
        client.ocr = OCR(client)

        return client
