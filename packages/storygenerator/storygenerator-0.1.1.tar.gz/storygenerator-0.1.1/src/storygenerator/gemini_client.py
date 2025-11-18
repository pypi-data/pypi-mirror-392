"""Gemini API client for text and image generation."""

import base64
from typing import Optional
import google.generativeai as genai

from storygenerator.models import ReferenceImage


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, api_key: str):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Google API key for Gemini
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)  # type: ignore[attr-defined]
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: str,
        model: str = "gemini-2.5-flash",
        max_tokens: int = 1000,
    ) -> tuple[str, int]:
        """
        Generate text using Gemini.
        
        Args:
            prompt: The user prompt
            system_prompt: The system instruction
            model: The Gemini model to use
            max_tokens: Maximum tokens (kept for compatibility, not directly used by Gemini)
        
        Returns:
            Tuple of (generated_text, total_tokens)
        """
        gemini_model = genai.GenerativeModel(model)  # type: ignore[attr-defined]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Count prompt tokens
        prompt_tokens_response = await gemini_model.count_tokens_async(full_prompt)
        prompt_tokens = prompt_tokens_response.total_tokens
        
        # Generate content
        response = await gemini_model.generate_content_async(full_prompt)
        
        try:
            # Extract text and count output tokens
            response_text = response.text
            response_tokens_response = await gemini_model.count_tokens_async(response_text)
            response_tokens = response_tokens_response.total_tokens
        except Exception as e:
            print(f"Error counting tokens: {e}")
            response_tokens = 0
        
        return response_text, prompt_tokens + response_tokens
    
    async def generate_image(
        self,
        prompt: str,
        reference_images: list[ReferenceImage] | None = None,
        model: str = "gemini-2.5-flash-image",
    ) -> tuple[bytes | None, int]:
        """
        Generate an image using Gemini.
        
        Args:
            prompt: The image generation prompt
            reference_images: Optional list of reference images with labels
            model: The Gemini image model to use
        
        Returns:
            Tuple of (image_bytes, tokens_used)
            Returns (None, 0) if generation fails
        """
        gemini_model = genai.GenerativeModel(model)  # type: ignore[attr-defined]
        
        # Prepare content list
        content_parts: list[str | dict[str, Any]] = []
        
        # Add reference images if provided
        if reference_images:
            for ref_img in reference_images:
                try:
                    # Extract mime type and data from base64 string
                    # e.g., "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
                    header, encoded = ref_img.image_data.split(",", 1)
                    mime_type = header.split(":")[1].split(";")[0]
                    image_data = base64.b64decode(encoded)
                    
                    reference_image_part = {
                        "mime_type": mime_type,
                        "data": image_data,
                    }
                    
                    content_parts.append(reference_image_part)
                    
                    # Add label as context
                    content_parts.append(f"Reference image: {ref_img.label}")
                except Exception as e:
                    print(f"WARNING: Could not decode reference image '{ref_img.label}'. Error: {e}")
        
        # Add the main prompt
        if reference_images:
            prompt_with_context = (
                "Use the provided reference images for inspiration. " + prompt
            )
            content_parts.append(prompt_with_context)
        else:
            content_parts.append(prompt)
        
        try:
            # Generate image
            response = await gemini_model.generate_content_async(contents=content_parts)
            
            # Extract image data
            raw_image_data = None
            for part in response.parts:
                if part.inline_data:
                    raw_image_data = part.inline_data.data
                    break
            
            if not raw_image_data:
                # Log detailed feedback if available
                feedback = (
                    response.prompt_feedback
                    if hasattr(response, "prompt_feedback")
                    else "No feedback available"
                )
                print(
                    f"WARNING: No image data found in Gemini response. "
                    f"Prompt Feedback: {feedback}"
                )
                return None, 0
            
            # For simplicity, returning 1 token for now
            # This can be refined if Gemini provides token usage for images
            return raw_image_data, 1
            
        except Exception as e:
            print(f"ERROR generating image with Gemini: {e}")
            return None, 0
    
    async def generate_image_prompt(
        self,
        page_text: str,
        illustration_style: str,
        model: str = "gemini-2.5-flash",
    ) -> tuple[str, int]:
        """
        Generate a DALL-E style image prompt from page text.
        
        Args:
            page_text: The text content of the page
            illustration_style: The desired illustration style
            model: The Gemini model to use
        
        Returns:
            Tuple of (image_prompt, tokens_used)
        """
        prompt = f"Create a detailed image generation prompt for a '{illustration_style}' style illustration for the following page:\n\n{page_text}"
        system_prompt = "You are an assistant that creates detailed image generation prompts for illustrations based on story text. Focus on visual details, composition, and atmosphere."
        
        return await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            max_tokens=300,
        )
    
    async def generate_cover_prompt(
        self,
        story_outline: str,
        illustration_style: str,
        title: str,
        model: str = "gemini-2.5-flash",
    ) -> tuple[str, int]:
        """
        Generate a cover image prompt from the story outline.
        
        Args:
            story_outline: The complete story outline
            illustration_style: The desired illustration style
            title: The story title
            model: The Gemini model to use
        
        Returns:
            Tuple of (cover_prompt, tokens_used)
        """
        prompt = f"Create a short, exciting image generation prompt for a '{illustration_style}' style book cover for a story with this outline:\n\n{story_outline}"
        system_prompt = "You are an assistant that creates engaging book cover image prompts based on a story outline. Focus on capturing the essence of the story visually."
        
        cover_prompt, tokens = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            max_tokens=300,
        )
        
        # Add title to the prompt
        cover_prompt_with_title = f"{cover_prompt} Style: {illustration_style}. Title: '{title}'."
        
        return cover_prompt_with_title, tokens


# Import Any for type hints
from typing import Any

