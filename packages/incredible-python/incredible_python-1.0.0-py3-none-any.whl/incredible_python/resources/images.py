"""
Image generation resource for Incredible SDK.
Uses Fireworks AI FLUX.1 Kontext [pro] model.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


@dataclass
class ImageGenerationResponse:
    """Response from image generation endpoint."""
    
    success: bool
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    request_id: Optional[str] = None
    seed: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None


class Images:
    """
    Image generation resource using Fireworks AI FLUX.1 Kontext [pro].
    
    Example:
        ```python
        from incredible_python import Incredible
        
        client = Incredible(api_key="your-api-key")
        
        # Generate an image
        response = client.generate_image._create(
            prompt="A beautiful sunset over mountains",
            aspect_ratio="16:9",
            output_format="jpeg"
        )
        
        print(f"Image URL: {response.image_url}")
        ```
    """
    
    def __init__(self, client) -> None:
        self._client = client
    
    def __call__(
        self,
        prompt: str,
        **kwargs
    ) -> ImageGenerationResponse:
        """
        Shorthand for _create() - allows calling client.generate_image(...) directly.
        
        Example:
            ```python
            # Instead of client.generate_image._create(...)
            image = client.generate_image(
                prompt="A beautiful sunset",
                aspect_ratio="16:9"
            )
            ```
        """
        return self._create(prompt=prompt, **kwargs)
    
    def _create(
        self,
        *,
        prompt: str,
        aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"] = "16:9",
        output_format: Literal["jpeg", "png"] = "jpeg",
        seed: Optional[int] = None,
        prompt_upsampling: bool = False,
        safety_tolerance: int = 2,
        timeout: Optional[float] = None,
    ) -> ImageGenerationResponse:
        """
        Generate an image using Fireworks AI's FLUX.1 Kontext [pro] model.
        
        This endpoint uses the FLUX.1 Kontext [pro] model, which is a state-of-the-art
        image generation model that produces high-quality images from text descriptions.
        
        Args:
            prompt: Text description of the desired image (required)
            aspect_ratio: Aspect ratio of the output image. 
                         Valid values: "1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"
                         Default: "16:9"
            output_format: Output format, either "jpeg" or "png". Default: "jpeg"
            seed: Random seed for reproducibility (optional)
            prompt_upsampling: Whether to enhance the prompt for more creative generation.
                              Default: False
            safety_tolerance: Content moderation level (0-6, where 0 is most strict).
                            Default: 2
            timeout: Request timeout in seconds (optional)
        
        Returns:
            ImageGenerationResponse with:
                - success: Whether generation was successful
                - image_url: URL to the generated image
                - image_base64: Base64-encoded image data (if available)
                - request_id: Request ID from Fireworks API
                - seed: Seed used for generation
        
        Raises:
            ValidationError: If request parameters are invalid
            APIError: If the API request fails
            APITimeoutError: If the request times out
        
        Example:
            ```python
            response = client.generate_image._create(
                prompt="A serene lake at sunset with mountains in background",
                aspect_ratio="16:9",
                output_format="jpeg",
                seed=42
            )
            
            if response.success:
                print(f"Generated image: {response.image_url}")
                print(f"Seed used: {response.seed}")
            ```
        """
        if not prompt or not prompt.strip():
            from .._exceptions import ValidationError
            raise ValidationError("prompt cannot be empty")
        
        # Validate aspect_ratio
        valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]
        if aspect_ratio not in valid_ratios:
            from .._exceptions import ValidationError
            raise ValidationError(f"aspect_ratio must be one of {valid_ratios}")
        
        # Validate output_format
        if output_format.lower() not in ["jpeg", "png"]:
            from .._exceptions import ValidationError
            raise ValidationError("output_format must be 'jpeg' or 'png'")
        
        # Validate safety_tolerance
        if safety_tolerance < 0 or safety_tolerance > 6:
            from .._exceptions import ValidationError
            raise ValidationError("safety_tolerance must be between 0 and 6")
        
        # Build request payload
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format.lower(),
            "prompt_upsampling": prompt_upsampling,
            "safety_tolerance": safety_tolerance,
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        # Make request (may take several minutes for image generation)
        if timeout is None:
            timeout = 300.0  # 5 minutes default for image generation
        
        response = self._client.request(
            "POST",
            "/v1/generate-image",
            json=payload,
            timeout=timeout
        )
        
        data = response.json()
        
        return ImageGenerationResponse(
            success=data.get("success", False),
            image_url=data.get("image_url"),
            image_base64=data.get("image_base64"),
            request_id=data.get("request_id"),
            seed=data.get("seed"),
            raw_response=data
        )

