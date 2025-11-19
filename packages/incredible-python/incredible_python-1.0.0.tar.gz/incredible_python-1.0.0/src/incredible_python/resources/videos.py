"""
Video generation resource for Incredible SDK.
Uses Google Vertex AI's VEO 3.0 fast API.
"""

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


@dataclass
class VideoGenerationResponse:
    """Response from video generation endpoint."""
    
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None  # Data URI with base64-encoded video
    status: Optional[str] = None
    prompt: Optional[str] = None
    duration: Optional[int] = None  # Duration in seconds (always 8 for VEO 3.0 fast)
    raw_response: Optional[Dict[str, Any]] = None


class Videos:
    """
    Video generation resource using Google Vertex AI's VEO 3.0 fast API.
    
    All videos are 8 seconds long and generated at high quality.
    
    Example:
        ```python
        from incredible_python import Incredible
        
        client = Incredible(api_key="your-api-key")
        
        # Generate a video
        response = client.videos.generate(
            prompt="A serene beach at sunset with waves gently crashing",
            size="1280x720"
        )
        
        if response.success:
            print(f"Video URL: {response.video_url}")
            print(f"Duration: {response.duration} seconds")
        ```
    """
    
    def __init__(self, client) -> None:
        self._client = client
    
    def __call__(
        self,
        prompt: str,
        **kwargs
    ):
        """
        Shorthand for generate() - allows calling client.videos(...) directly.
        
        Example:
            ```python
            # Instead of client.generate_video._create(...)
            video = client.generate_video(
                prompt="Ocean waves at sunset",
                size="1280x720"
            )
            ```
        """
        return self._create(prompt=prompt, **kwargs)
    
    def _create(
        self,
        *,
        prompt: str,
        size: Literal["1280x720", "720x1280", "1920x1080", "1080x1920", "1024x1024"] = "1280x720",
        input_reference: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> VideoGenerationResponse:
        """
        Generate a video using Google Vertex AI's VEO 3.0 fast model.
        
        This endpoint uses the VEO 3.0 fast model, which is a state-of-the-art
        video generation model that produces high-quality 8-second videos from
        text descriptions.
        
        Args:
            prompt: Text description of the desired video (required)
            size: Video dimensions. Valid values:
                  - "1280x720" - 720p landscape (default)
                  - "720x1280" - 720p portrait
                  - "1920x1080" - 1080p landscape
                  - "1080x1920" - 1080p portrait
                  - "1024x1024" - Square
            input_reference: Optional base64-encoded reference image for image-to-video
            timeout: Request timeout in seconds (optional, default: 600 = 10 minutes)
        
        Returns:
            VideoGenerationResponse with:
                - success: Whether generation was successful
                - video_id: Operation ID from Vertex AI
                - video_url: Data URI with base64-encoded MP4 video
                - status: Generation status (e.g., "completed")
                - prompt: The prompt that was used
                - duration: Video duration in seconds (always 8)
        
        Raises:
            ValidationError: If request parameters are invalid
            APIError: If the API request fails
            APITimeoutError: If the request times out
        
        Example:
            ```python
            # Text-to-video
            response = client.generate_video._create(
                prompt="A serene beach at sunset with waves crashing",
                size="1920x1080"
            )
            
            if response.success:
                print(f"Video generated: {response.video_id}")
                print(f"Duration: {response.duration} seconds")
                
                # Save video from data URI
                import base64
                if response.video_url and response.video_url.startswith("data:video/mp4;base64,"):
                    video_base64 = response.video_url.split(",", 1)[1]
                    video_data = base64.b64decode(video_base64)
                    with open("generated_video.mp4", "wb") as f:
                        f.write(video_data)
            
            # Image-to-video with reference image
            with open("reference.jpg", "rb") as f:
                import base64
                reference_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            response = client.generate_video._create(
                prompt="Zoom into this scene dramatically",
                size="1280x720",
                input_reference=reference_b64
            )
            ```
        
        Note:
            - Video generation may take up to 10 minutes
            - All videos are 8 seconds long (VEO 3.0 fast limitation)
            - Videos are returned as base64-encoded data URIs
            - Larger resolutions (1080p) will take longer to generate
        """
        if not prompt or not prompt.strip():
            from .._exceptions import ValidationError
            raise ValidationError("prompt cannot be empty")
        
        # Validate size
        valid_sizes = ["1280x720", "720x1280", "1920x1080", "1080x1920", "1024x1024"]
        if size not in valid_sizes:
            from .._exceptions import ValidationError
            raise ValidationError(f"size must be one of {valid_sizes}")
        
        # Validate input_reference if provided
        if input_reference:
            try:
                import base64
                # Try to decode to validate
                base64.b64decode(input_reference)
            except Exception:
                from .._exceptions import ValidationError
                raise ValidationError("input_reference must be valid base64-encoded image data")
        
        # Build request payload
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "size": size,
        }
        
        if input_reference is not None:
            payload["input_reference"] = input_reference
        
        # Make request (video generation takes a long time)
        if timeout is None:
            timeout = 600.0  # 10 minutes default for video generation
        
        response = self._client.request(
            "POST",
            "/v1/generate-video",
            json=payload,
            timeout=timeout
        )
        
        data = response.json()
        
        return VideoGenerationResponse(
            success=data.get("success", False),
            video_id=data.get("video_id"),
            video_url=data.get("video_url"),
            status=data.get("status"),
            prompt=data.get("prompt"),
            duration=data.get("duration"),
            raw_response=data
        )

