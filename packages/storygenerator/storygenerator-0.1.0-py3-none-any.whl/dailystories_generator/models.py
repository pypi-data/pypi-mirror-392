"""Pydantic models for story generation requests and artifacts."""

from pydantic import BaseModel, Field
from typing import Optional


class ReferenceImage(BaseModel):
    """
    Reference image for inspiration during image generation.
    
    Attributes:
        image_data: Base64 encoded image string (e.g., "data:image/jpeg;base64,...")
        label: Text description/label for this image (e.g., "main character", "forest setting")
    """
    
    image_data: str = Field(..., description="Base64 encoded image with data URI prefix")
    label: str = Field(..., description="Descriptive label for this reference image")


class GenerationRequest(BaseModel):
    """
    Request parameters for story generation.
    
    Attributes:
        title: The title of the story
        summary: Brief summary or theme of the story
        num_pages: Number of pages to generate
        child_name: Name of the child protagonist (optional)
        child_age: Age of the target child reader (optional)
        language: Language for the story (default: English)
        illustration_style: Style description for illustrations (e.g., "watercolor", "cartoon")
        generate_images: Whether to generate images (default: True)
        reference_images: List of reference images for inspiration (default: empty list)
        outline_only: Whether to generate only the outline and skip page generation (default: False)
    """
    
    title: str
    summary: str
    num_pages: int = Field(..., ge=1, le=50)
    child_name: Optional[str] = None
    child_age: Optional[int] = Field(None, ge=1, le=18)
    language: str = "English"
    illustration_style: str = "watercolor"
    generate_images: bool = True
    reference_images: list[ReferenceImage] = Field(default_factory=list)
    outline_only: bool = False


class PageArtifact(BaseModel):
    """
    Artifact for a single page of the story.
    
    Attributes:
        page_number: The page number (1-indexed)
        text_content: The text content of the page
        image_data: Raw image bytes (None if generate_images=False)
        text_tokens: Number of tokens used for text generation
        image_tokens: Number of tokens used for image generation
    """
    
    page_number: int
    text_content: str
    image_data: Optional[bytes] = None
    text_tokens: int = 0
    image_tokens: int = 0
    
    class Config:
        # Allow bytes in the model
        arbitrary_types_allowed = True


class StoryArtifact(BaseModel):
    """
    Complete story artifact with all pages and metadata.
    
    Attributes:
        outline: The story outline
        pages: List of page artifacts
        cover_image_data: Raw cover image bytes (None if generate_images=False)
        total_text_tokens: Total tokens used for text generation
        total_image_tokens: Total tokens used for image generation
    """
    
    outline: str
    pages: list[PageArtifact] = Field(default_factory=list)
    cover_image_data: Optional[bytes] = None
    total_text_tokens: int = 0
    total_image_tokens: int = 0
    
    class Config:
        # Allow bytes in the model
        arbitrary_types_allowed = True

