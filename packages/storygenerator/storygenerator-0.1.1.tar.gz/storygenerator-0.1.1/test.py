#!/usr/bin/env python3
"""
Test script for dailystories-generator library.

Usage:
    # Set your API key
    export GOOGLE_API_KEY="your-gemini-api-key-here"
    
    # Run the test
    python test.py
    
    # Or run without images (faster)
    python test.py --no-images
    
    # Or generate only the outline (for iteration)
    python test.py --outline-only
"""

import asyncio
import os
import sys
from pathlib import Path

# Add package to path for local testing
package_path = Path(__file__).parent / "src"
sys.path.insert(0, str(package_path))

from storygenerator import (
    StoryGenerator,
    GenerationRequest,
    ReferenceImage,
    Update,
    UpdateType,
)


class Colors:
    """ANSI color codes for pretty output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


async def test_story_generation():
    """Test the story generator with a simple story."""
    
    # Get API key from environment
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(f"{Colors.FAIL}❌ Error: GOOGLE_API_KEY environment variable not set{Colors.ENDC}")
        print(f"{Colors.WARNING}Set it with: export GOOGLE_API_KEY='your-key-here'{Colors.ENDC}")
        return False
    
    # Check for flags
    generate_images = "--no-images" not in sys.argv
    outline_only = "--outline-only" in sys.argv
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 Testing DailyStories Generator{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    # Initialize generator
    print(f"{Colors.OKBLUE}📦 Initializing StoryGenerator...{Colors.ENDC}")
    generator = StoryGenerator(gemini_api_key=api_key)
    print(f"{Colors.OKGREEN}✓ Generator initialized{Colors.ENDC}\n")
    
    # Create test request
    print(f"{Colors.OKBLUE}📝 Creating generation request...{Colors.ENDC}")
    request = GenerationRequest(
        title="Ludwig i legobyen",
        summary="Ludwig er en legomann i legobyen. Han leker med vennen Theodor, og de finner en rar drage.",
        num_pages=5,
        child_name="Ludwig",
        child_age=6,
        language="Norwegian",
        illustration_style="colorful cartoon",
        generate_images=generate_images,
        reference_images=[],  # No reference images for testing
        outline_only=outline_only,
    )
    
    print(f"{Colors.OKGREEN}✓ Request created:{Colors.ENDC}")
    print(f"  • Title: {request.title}")
    print(f"  • Pages: {request.num_pages}")
    print(f"  • Images: {'Yes' if request.generate_images else 'No'}")
    print(f"  • Language: {request.language}")
    print(f"  • Mode: {'Outline only' if request.outline_only else 'Full story'}\n")
    
    # Track progress
    progress = {
        "outline": None,
        "pages": [],
        "cover_image_size": 0,
        "total_tokens": 0,
    }
    
    # Define callback
    async def on_update(update: Update) -> None:
        """Handle updates from the generator."""
        
        if update.type == UpdateType.GENERATING_OUTLINE:
            print(f"{Colors.OKCYAN}⏳ Generating story outline...{Colors.ENDC}")
        
        elif update.type == UpdateType.OUTLINE_COMPLETE:
            progress["outline"] = update.data.get("outline", "")
            tokens = update.data.get("tokens", 0)
            print(f"{Colors.OKGREEN}✓ Outline complete ({tokens} tokens){Colors.ENDC}")
            print(f"{Colors.WARNING}📋 Outline:{Colors.ENDC}")
            for line in progress["outline"].split('\n'):
                if line.strip():
                    print(f"  {line}")
            print()
        
        elif update.type == UpdateType.GENERATING_PAGE_TEXT:
            page_num = update.data.get("page_number")
            print(f"{Colors.OKCYAN}⏳ Generating text for page {page_num}...{Colors.ENDC}")
        
        elif update.type == UpdateType.PAGE_TEXT_COMPLETE:
            page = update.artifacts.get("current_page")
            if page:
                text_preview = page.text_content[:100] + "..." if len(page.text_content) > 100 else page.text_content
                print(f"{Colors.OKGREEN}✓ Page {page.page_number} text complete ({page.text_tokens} tokens){Colors.ENDC}")
                print(f"  {Colors.WARNING}Text:{Colors.ENDC} {text_preview}")
                print()
        
        elif update.type == UpdateType.GENERATING_PAGE_IMAGE:
            page_num = update.data.get("page_number")
            print(f"{Colors.OKCYAN}  ⏳ Generating image for page {page_num}...{Colors.ENDC}")
        
        elif update.type == UpdateType.PAGE_IMAGE_COMPLETE:
            page = update.artifacts.get("page")
            if page:
                image_info = f"{len(page.image_data):,} bytes" if page.image_data else "no image"
                print(f"{Colors.OKGREEN}  ✓ Page {page.page_number} image complete ({page.image_tokens} tokens, {image_info}){Colors.ENDC}")
                print()
        
        elif update.type == UpdateType.GENERATING_COVER:
            print(f"{Colors.OKCYAN}⏳ Generating cover image...{Colors.ENDC}")
        
        elif update.type == UpdateType.COVER_COMPLETE:
            cover_data = update.artifacts.get("cover_image_data")
            if cover_data:
                progress["cover_image_size"] = len(cover_data)
                print(f"{Colors.OKGREEN}✓ Cover complete ({len(cover_data)} bytes){Colors.ENDC}\n")
        
        elif update.type == UpdateType.COMPLETE:
            progress["total_tokens"] = update.data.get("total_tokens", 0)
            is_outline_only = update.data.get("outline_only", False)
            print(f"\n{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
            if is_outline_only:
                print(f"{Colors.OKGREEN}🎉 Outline generation complete!{Colors.ENDC}")
            else:
                print(f"{Colors.OKGREEN}🎉 Story generation complete!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'='*60}{Colors.ENDC}")
        
        elif update.type == UpdateType.FAILED:
            error = update.data.get("error", "Unknown error")
            print(f"\n{Colors.FAIL}{'='*60}{Colors.ENDC}")
            print(f"{Colors.FAIL}❌ Generation failed: {error}{Colors.ENDC}")
            print(f"{Colors.FAIL}{'='*60}{Colors.ENDC}")
    
    # Generate the story
    try:
        print(f"{Colors.BOLD}Starting generation...{Colors.ENDC}\n")
        story = await generator.generate(request, on_update=on_update)
        
        # Print summary
        print(f"\n{Colors.HEADER}📊 Generation Summary{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"  • Outline length: {len(story.outline)} chars")
        
        if outline_only:
            print(f"  • Mode: Outline only")
            print(f"  • Total tokens: {story.total_text_tokens}")
        else:
            print(f"  • Pages generated: {len(story.pages)}")
            print(f"  • Total text tokens: {story.total_text_tokens}")
            print(f"  • Total image tokens: {story.total_image_tokens}")
            print(f"  • Total tokens: {story.total_text_tokens + story.total_image_tokens}")
            
            if story.cover_image_data:
                print(f"  • Cover image size: {len(story.cover_image_data)} bytes")
            else:
                print(f"  • Cover image: None")
        
        # Write story to markdown file
        output_file = Path(__file__).parent / "story.md"
        print(f"\n{Colors.OKBLUE}📝 Writing story to {output_file.name}...{Colors.ENDC}")
        
        # Save images to files if present
        image_files_saved = []
        if not outline_only and story.cover_image_data:
            cover_file = Path(__file__).parent / "cover.png"
            with open(cover_file, "wb") as img_file:
                img_file.write(story.cover_image_data)
            image_files_saved.append("cover.png")
            print(f"{Colors.OKBLUE}  💾 Saved cover.png{Colors.ENDC}")
        
        for page in story.pages:
            if page.image_data:
                image_file = Path(__file__).parent / f"page_{page.page_number}.png"
                with open(image_file, "wb") as img_file:
                    img_file.write(page.image_data)
                image_files_saved.append(f"page_{page.page_number}.png")
                print(f"{Colors.OKBLUE}  💾 Saved page_{page.page_number}.png{Colors.ENDC}")
        
        with open(output_file, "w", encoding="utf-8") as f:
            # Write title
            f.write(f"# {request.title}\n\n")
            
            # Add cover image if present
            if not outline_only and story.cover_image_data:
                f.write("![Cover](./cover.png)\n\n")
            
            # Write metadata
            f.write(f"**Child:** {request.child_name}, age {request.child_age}\n")
            f.write(f"**Language:** {request.language}\n")
            f.write(f"**Style:** {request.illustration_style}\n")
            
            if outline_only:
                f.write(f"**Mode:** Outline only\n")
                f.write(f"**Total Tokens:** {story.total_text_tokens}\n\n")
            else:
                f.write(f"**Pages:** {len(story.pages)}\n")
                f.write(f"**Total Tokens:** {story.total_text_tokens + story.total_image_tokens}\n\n")
            
            # Write outline
            f.write("---\n\n")
            f.write("## Outline\n\n")
            f.write(story.outline)
            f.write("\n\n")
            
            # Write story pages (only if not outline_only mode)
            if not outline_only:
                f.write("---\n\n")
                f.write("## Story\n\n")
                
                for page in story.pages:
                    f.write(f"### Page {page.page_number}\n\n")
                    
                    # Add image if present
                    if page.image_data:
                        f.write(f"![Page {page.page_number} illustration](./page_{page.page_number}.png)\n\n")
                    
                    f.write(page.text_content)
                    f.write("\n\n")
                
                # Add footer
                f.write("---\n\n")
                f.write(f"*Generated with {story.total_text_tokens} text tokens ")
                f.write(f"and {story.total_image_tokens} image tokens*\n")
            else:
                # Add footer for outline-only mode
                f.write("---\n\n")
                f.write(f"*Outline generated with {story.total_text_tokens} tokens*\n")
        
        print(f"{Colors.OKGREEN}✓ Story saved to {output_file.name}{Colors.ENDC}")
        if image_files_saved:
            print(f"{Colors.OKGREEN}✓ {len(image_files_saved)} image(s) saved{Colors.ENDC}")
        print(f"\n{Colors.OKGREEN}✅ Test completed successfully!{Colors.ENDC}\n")
        return True
        
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Test failed with error:{Colors.ENDC}")
        print(f"{Colors.FAIL}{type(e).__name__}: {e}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the test."""
    print(f"{Colors.OKCYAN}DailyStories Generator - Test Script{Colors.ENDC}")
    
    # Run the async test
    success = asyncio.run(test_story_generation())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

