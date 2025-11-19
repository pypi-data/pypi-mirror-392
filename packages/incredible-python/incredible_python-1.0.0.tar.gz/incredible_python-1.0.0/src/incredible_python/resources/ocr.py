"""OCR resource for extracting text from images and PDFs.

Powered by Mistral Document AI for high-quality text extraction.
"""

from __future__ import annotations

import base64
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class OCRPage:
    """A single page from OCR processing.
    
    Attributes:
        page_number: Page number (1-indexed)
        text: Extracted text from the page
        success: Whether extraction succeeded
        raw_response: Raw OCR response data
    """
    page_number: int
    text: str
    success: bool
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class OCRImageResponse:
    """Response from image OCR.
    
    Attributes:
        success: Whether extraction succeeded
        text: Extracted text
        method: OCR method used (e.g., "mistral_document_ai")
        raw_response: Raw OCR response data
        error: Error message if failed
    """
    success: bool
    text: str
    method: str
    raw_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class OCRPDFResponse:
    """Response from PDF OCR.
    
    Attributes:
        success: Whether extraction succeeded
        text: Concatenated text from all pages
        method: Extraction method ("text_extraction" or "mistral_document_ai")
        pages_processed: Number of pages processed
        total_pages: Total pages in PDF
        pages: List of per-page results
        error: Error message if failed
    """
    success: bool
    text: str
    method: str
    pages_processed: int
    total_pages: int
    pages: List[OCRPage]
    error: Optional[str] = None


class OCR:
    """OCR resource for text extraction from images and PDFs.
    
    Provides simple, powerful OCR capabilities powered by Mistral Document AI.
    
    Example:
        >>> client = Incredible()
        >>> 
        >>> # Check OCR health
        >>> health = client.ocr.health()
        >>> print(health["ocr_enabled"])
        >>> 
        >>> # Extract from image
        >>> with open("document.png", "rb") as f:
        ...     result = client.ocr.extract_from_image(f.read())
        >>> print(result.text)
        >>> 
        >>> # Extract from PDF
        >>> with open("document.pdf", "rb") as f:
        ...     result = client.ocr.extract_from_pdf(f.read(), max_pages=10)
        >>> print(result.text)
    """
    
    def __init__(self, client) -> None:
        self._client = client
    
    def health(self) -> Dict[str, Any]:
        """Check OCR service health and configuration.
        
        Returns:
            Dictionary with service status and configuration:
                - status: "ok"
                - ocr_enabled: Whether OCR is configured
                - model: OCR model name (if enabled)
                - message: Status message
        
        Example:
            >>> health = client.ocr.health()
            >>> if health["ocr_enabled"]:
            ...     print(f"OCR ready with model: {health['model']}")
            ... else:
            ...     print("OCR not configured")
        """
        response = self._client.request("GET", "/ocr/health")
        return response.json()
    
    def extract_from_image(
        self,
        image: bytes | str,
        image_format: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> OCRImageResponse:
        """Extract text from an image using OCR.
        
        Args:
            image: Image bytes or base64-encoded string
            image_format: Image format ("png", "jpeg", "jpg"). Optional.
            timeout: Request timeout in seconds. Optional.
        
        Returns:
            OCRImageResponse with extracted text and metadata
        
        Raises:
            APIError: If OCR service is not configured or request fails
            ValidationError: If image data is invalid
        
        Example:
            >>> # From file
            >>> with open("receipt.png", "rb") as f:
            ...     result = client.ocr.extract_from_image(f.read())
            >>> print(f"Extracted: {result.text}")
            >>> 
            >>> # From base64
            >>> base64_image = "iVBORw0KG..."
            >>> result = client.ocr.extract_from_image(base64_image)
            >>> 
            >>> # Check success
            >>> if result.success:
            ...     print(result.text)
            ... else:
            ...     print(f"Error: {result.error}")
        """
        # Prepare payload
        if isinstance(image, bytes):
            # Convert bytes to base64
            image_base64 = base64.b64encode(image).decode('utf-8')
        else:
            # Assume it's already base64
            image_base64 = image
        
        payload: Dict[str, Any] = {
            "image": image_base64
        }
        
        if image_format:
            payload["image_format"] = image_format
        
        # Make request
        response = self._client.request(
            "POST",
            "/ocr/image",
            json=payload,
            timeout=timeout,
        )
        
        data = response.json()
        
        return OCRImageResponse(
            success=data.get("success", False),
            text=data.get("text", ""),
            method=data.get("method", ""),
            raw_response=data.get("raw_response"),
            error=data.get("error")
        )
    
    def extract_from_pdf(
        self,
        pdf: bytes | str,
        max_pages: Optional[int] = None,
        dpi: int = 200,
        timeout: Optional[float] = None,
    ) -> OCRPDFResponse:
        """Extract text from a PDF using OCR.
        
        Automatically detects if PDF has text or is scanned:
        - Text PDFs: Fast extraction without OCR
        - Scanned PDFs: Full OCR processing
        
        Args:
            pdf: PDF bytes or base64-encoded string
            max_pages: Maximum pages to process. Optional (processes all).
            dpi: Image resolution for OCR (default: 200). Higher = better quality.
            timeout: Request timeout in seconds. Optional.
        
        Returns:
            OCRPDFResponse with extracted text and per-page results
        
        Raises:
            APIError: If OCR service is not configured or request fails
            ValidationError: If PDF data is invalid
        
        Example:
            >>> # Extract entire PDF
            >>> with open("document.pdf", "rb") as f:
            ...     result = client.ocr.extract_from_pdf(f.read())
            >>> print(f"Pages: {result.pages_processed}/{result.total_pages}")
            >>> print(f"Text: {result.text}")
            >>> 
            >>> # Extract first 10 pages only
            >>> with open("long_doc.pdf", "rb") as f:
            ...     result = client.ocr.extract_from_pdf(
            ...         f.read(),
            ...         max_pages=10,
            ...         dpi=300  # Higher quality
            ...     )
            >>> 
            >>> # Access per-page results
            >>> for page in result.pages:
            ...     print(f"Page {page.page_number}: {len(page.text)} chars")
            >>> 
            >>> # Check extraction method
            >>> if result.method == "text_extraction":
            ...     print("Fast text extraction (not scanned)")
            >>> else:
            ...     print("OCR used (scanned PDF)")
        """
        # Prepare payload
        if isinstance(pdf, bytes):
            # Convert bytes to base64
            pdf_base64 = base64.b64encode(pdf).decode('utf-8')
        else:
            # Assume it's already base64
            pdf_base64 = pdf
        
        payload: Dict[str, Any] = {
            "pdf": pdf_base64,
            "dpi": dpi
        }
        
        if max_pages is not None:
            payload["max_pages"] = max_pages
        
        # Make request
        response = self._client.request(
            "POST",
            "/ocr/pdf",
            json=payload,
            timeout=timeout,
        )
        
        data = response.json()
        
        # Parse pages
        pages = []
        for page_data in data.get("pages", []):
            pages.append(OCRPage(
                page_number=page_data.get("page_number", 0),
                text=page_data.get("text", ""),
                success=page_data.get("success", False),
                raw_response=page_data.get("raw_response")
            ))
        
        return OCRPDFResponse(
            success=data.get("success", False),
            text=data.get("text", ""),
            method=data.get("method", ""),
            pages_processed=data.get("pages_processed", 0),
            total_pages=data.get("total_pages", 0),
            pages=pages,
            error=data.get("error")
        )

