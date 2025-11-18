"""Main story generator implementation."""

from typing import Optional
from datetime import datetime, timezone

from dailystories_generator.models import (
    GenerationRequest,
    StoryArtifact,
    PageArtifact,
)
from dailystories_generator.types import Update, UpdateType, UpdateCallback
from dailystories_generator.gemini_client import GeminiClient
from dailystories_generator import prompts


class StoryGenerator:
    """Main story generator using Gemini AI."""
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize the story generator.
        
        Args:
            gemini_api_key: Google API key for Gemini
        """
        self.client = GeminiClient(api_key=gemini_api_key)
    
    async def generate(
        self,
        request: GenerationRequest,
        on_update: UpdateCallback,
    ) -> StoryArtifact:
        """
        Generate a complete story.
        
        Args:
            request: The generation request parameters
            on_update: Async callback for status updates
        
        Returns:
            Complete story artifact with all pages and metadata
        
        Raises:
            Exception: If generation fails at any stage
        """
        total_text_tokens = 0
        total_image_tokens = 0
        
        try:
            # Step 1: Generate outline
            await on_update(Update(
                type=UpdateType.GENERATING_OUTLINE,
                data={},
                artifacts={},
            ))
            
            outline_prompt = prompts.get_story_outline_prompt().format(
                num_pages=request.num_pages,
                last_adventure_page=request.num_pages - 2,
                title=request.title,
                child_name=request.child_name or "the child",
                child_age=request.child_age or 6,
                language=request.language,
                summary=request.summary,
            )
            
            story_outline, outline_tokens = await self.client.generate_text(
                prompt=outline_prompt,
                system_prompt="You are a master author of children's stories, skilled at crafting engaging and well-structured outlines.",
                model="gemini-2.5-flash",
                max_tokens=1000,
            )
            
            total_text_tokens += outline_tokens
            
            await on_update(Update(
                type=UpdateType.OUTLINE_COMPLETE,
                data={
                    "outline": story_outline,
                    "tokens": outline_tokens,
                },
                artifacts={
                    "outline": story_outline,
                },
            ))
            
            # If outline_only mode, return early with just the outline
            if request.outline_only:
                story_artifact = StoryArtifact(
                    outline=story_outline,
                    pages=[],
                    cover_image_data=None,
                    total_text_tokens=total_text_tokens,
                    total_image_tokens=0,
                )
                
                await on_update(Update(
                    type=UpdateType.COMPLETE,
                    data={
                        "total_text_tokens": total_text_tokens,
                        "total_image_tokens": 0,
                        "total_tokens": total_text_tokens,
                        "outline_only": True,
                    },
                    artifacts={
                        "story": story_artifact,
                    },
                ))
                
                return story_artifact
            
            # Step 2: Generate pages
            pages: list[PageArtifact] = []
            story_so_far = ""
            
            for page_number in range(1, request.num_pages + 1):
                await on_update(Update(
                    type=UpdateType.GENERATING_PAGE,
                    data={"page_number": page_number},
                    artifacts={
                        "outline": story_outline,
                        "pages": pages,
                    },
                ))
                
                # Generate page text
                page_prompt = prompts.get_story_page_prompt().format(
                    page_number=page_number,
                    story_outline=story_outline,
                    story_so_far=story_so_far,
                    child_age=request.child_age or 6,
                    language=request.language,
                )
                
                page_text, page_text_tokens = await self.client.generate_text(
                    prompt=page_prompt,
                    system_prompt="You are an assistant that writes a single page of a children's book based on an outline. Only write the text for the page itself, nothing else. Write around 200 words.",
                    model="gemini-2.5-flash",
                    max_tokens=400,
                )
                
                story_so_far += f"Page {page_number}: {page_text}\\n"
                total_text_tokens += page_text_tokens
                
                # Generate image if requested
                image_data: Optional[bytes] = None
                image_tokens = 0
                
                if request.generate_images:
                    # Generate image summary/prompt
                    image_prompt, image_summary_tokens = await self.client.generate_image_prompt(
                        page_text=page_text,
                        illustration_style=request.illustration_style,
                    )
                    total_text_tokens += image_summary_tokens
                    
                    # Generate image
                    image_data, image_tokens = await self.client.generate_image(
                        prompt=f"{image_prompt} Style: {request.illustration_style}.",
                        reference_images=request.reference_images if request.reference_images else None,
                    )
                    total_image_tokens += image_tokens
                
                # Create page artifact
                page_artifact = PageArtifact(
                    page_number=page_number,
                    text_content=page_text,
                    image_data=image_data,
                    text_tokens=page_text_tokens,
                    image_tokens=image_tokens,
                )
                pages.append(page_artifact)
                
                await on_update(Update(
                    type=UpdateType.PAGE_COMPLETE,
                    data={
                        "page_number": page_number,
                        "text_tokens": page_text_tokens,
                        "image_tokens": image_tokens,
                    },
                    artifacts={
                        "outline": story_outline,
                        "pages": pages,
                        "current_page": page_artifact,
                    },
                ))
            
            # Step 3: Generate cover if images are enabled
            cover_image_data: Optional[bytes] = None
            
            if request.generate_images:
                await on_update(Update(
                    type=UpdateType.GENERATING_COVER,
                    data={},
                    artifacts={
                        "outline": story_outline,
                        "pages": pages,
                    },
                ))
                
                # Generate cover prompt
                cover_prompt, cover_summary_tokens = await self.client.generate_cover_prompt(
                    story_outline=story_outline,
                    illustration_style=request.illustration_style,
                    title=request.title,
                )
                total_text_tokens += cover_summary_tokens
                
                # Generate cover image
                cover_image_data, cover_image_tokens = await self.client.generate_image(
                    prompt=cover_prompt,
                    reference_images=request.reference_images if request.reference_images else None,
                )
                total_image_tokens += cover_image_tokens
                
                await on_update(Update(
                    type=UpdateType.COVER_COMPLETE,
                    data={
                        "cover_tokens": cover_image_tokens,
                    },
                    artifacts={
                        "outline": story_outline,
                        "pages": pages,
                        "cover_image_data": cover_image_data,
                    },
                ))
            
            # Step 4: Create final artifact
            story_artifact = StoryArtifact(
                outline=story_outline,
                pages=pages,
                cover_image_data=cover_image_data,
                total_text_tokens=total_text_tokens,
                total_image_tokens=total_image_tokens,
            )
            
            await on_update(Update(
                type=UpdateType.COMPLETE,
                data={
                    "total_text_tokens": total_text_tokens,
                    "total_image_tokens": total_image_tokens,
                    "total_tokens": total_text_tokens + total_image_tokens,
                },
                artifacts={
                    "story": story_artifact,
                },
            ))
            
            return story_artifact
            
        except Exception as e:
            # Send failure update
            await on_update(Update(
                type=UpdateType.FAILED,
                data={
                    "error": str(e),
                    "total_text_tokens": total_text_tokens,
                    "total_image_tokens": total_image_tokens,
                },
                artifacts={},
            ))
            raise

