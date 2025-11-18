#!/usr/bin/env python3
"""
Prompt optimization script for iterative improvement based on evaluation feedback.

Usage:
    # Set your API key
    export GOOGLE_API_KEY="your-gemini-api-key-here"
    
    # Run 50 iterations optimizing outline prompt
    python optimize_prompts.py --mode outline --iterations 50 --child-name Ludwig --child-age 6
    
    # Run 20 iterations optimizing page prompt
    python optimize_prompts.py --mode pages --iterations 20 --child-name Emma --child-age 7
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# Add package to path for local testing
package_path = Path(__file__).parent / "src"
sys.path.insert(0, str(package_path))

from storygenerator import (
    StoryGenerator,
    GenerationRequest,
    Update,
    UpdateType,
)
from storygenerator.gemini_client import GeminiClient
from storygenerator.evaluation import evaluate_content
from storygenerator.prompt_improver import suggest_improvements
from storygenerator.statistics_tracker import StatisticsTracker


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


async def generate_story_content(
    generator: StoryGenerator,
    request: GenerationRequest,
    mode: str,
) -> str:
    """
    Generate story content based on mode.
    
    Args:
        generator: StoryGenerator instance
        request: Generation request
        mode: 'outline' or 'pages'
    
    Returns:
        Generated content as string
    """
    async def silent_update(update: Update) -> None:
        """Silent update callback."""
        pass
    
    if mode == "outline":
        # Generate only outline
        request.outline_only = True
        story = await generator.generate(request, on_update=silent_update)
        return story.outline
    else:  # pages mode
        # Generate full story
        request.outline_only = False
        request.generate_images = False  # Skip images for optimization
        story = await generator.generate(request, on_update=silent_update)
        
        # Combine all pages into one text
        pages_text = "\n\n".join([
            f"Page {page.page_number}:\n{page.text_content}"
            for page in story.pages
        ])
        return pages_text


async def optimize_prompts(
    mode: str,
    iterations: int,
    child_name: str,
    child_age: int,
    title: str,
    summary: str,
    num_pages: int,
    language: str,
) -> None:
    """
    Main optimization loop.
    
    Args:
        mode: 'outline' or 'pages'
        iterations: Number of optimization iterations
        child_name: Child's name for story
        child_age: Child's age
        title: Story title
        summary: Story summary/theme
        num_pages: Number of pages
        language: Story language
    """
    # Get API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print(f"{Colors.FAIL}❌ Error: GOOGLE_API_KEY environment variable not set{Colors.ENDC}")
        print(f"{Colors.WARNING}Set it with: export GOOGLE_API_KEY='your-key-here'{Colors.ENDC}")
        return
    
    # Initialize components
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}🚀 Prompt Optimization System{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
    
    print(f"{Colors.OKBLUE}Mode: {mode}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}Iterations: {iterations}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}Test story: {title} (age {child_age}){Colors.ENDC}\n")
    
    generator = StoryGenerator(gemini_api_key=api_key)
    gemini_client = GeminiClient(api_key=api_key)
    
    # Setup paths
    package_root = Path(__file__).parent
    prompt_template_path = package_root / "prompt_templates" / (
        "story_outline_prompt.txt" if mode == "outline" else "story_page_prompt.txt"
    )
    statistics_path = package_root / "statistics.csv"
    
    # Initialize statistics tracker
    tracker = StatisticsTracker(statistics_path)
    
    # Create log file for this optimization run (overwrites previous)
    log_path = package_root / "optimization.log"
    log_file = open(log_path, 'w', encoding='utf-8')
    
    def log(message: str) -> None:
        """Write to both console and log file."""
        print(message)
        log_file.write(message + '\n')
        log_file.flush()
    
    log(f"{'='*80}\n")
    log(f"PROMPT OPTIMIZATION RUN\n")
    log(f"Mode: {mode}\n")
    log(f"Iterations: {iterations}\n")
    log(f"Test Story: {title} (age {child_age}, language: {language})\n")
    log(f"Child Name: {child_name}\n")
    log(f"Summary: {summary}\n")
    log(f"Number of Pages: {num_pages}\n")
    log(f"Started: {datetime.now().isoformat()}\n")
    log(f"{'='*80}\n\n")
    
    print(f"{Colors.OKGREEN}✓ Initialized components{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Prompt template: {prompt_template_path.name}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Statistics: {statistics_path.name}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Log file: {log_path.name}{Colors.ENDC}\n")
    
    # Load initial prompt
    current_prompt = prompt_template_path.read_text(encoding="utf-8")
    log(f"INITIAL PROMPT:\n{current_prompt}\n")
    log(f"{'='*80}\n\n")
    
    # Create test request
    request = GenerationRequest(
        title=title,
        summary=summary,
        num_pages=num_pages,
        child_name=child_name,
        child_age=child_age,
        language=language,
        illustration_style="colorful cartoon",
        generate_images=False,
    )
    
    # Main optimization loop
    for iteration in range(1, iterations + 1):
        log(f"\n{'='*80}\n")
        log(f"ITERATION {iteration}/{iterations}\n")
        log(f"{'='*80}\n\n")
        
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}Iteration {iteration}/{iterations}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        # Step 1: Generate content
        log(f"STEP 1: GENERATING {mode.upper()}\n")
        print(f"{Colors.OKCYAN}⏳ Step 1/4: Generating {mode}...{Colors.ENDC}")
        try:
            content = await generate_story_content(generator, request, mode)
            log(f"✓ Generated {len(content)} characters\n")
            log(f"GENERATED CONTENT:\n{content}\n")
            log(f"{'-'*80}\n\n")
            print(f"{Colors.OKGREEN}✓ Generated {len(content)} characters{Colors.ENDC}\n")
        except Exception as e:
            log(f"❌ Generation failed: {e}\n\n")
            print(f"{Colors.FAIL}❌ Generation failed: {e}{Colors.ENDC}\n")
            continue
        
        # Step 2: Evaluate content
        log(f"STEP 2: EVALUATING CONTENT\n")
        print(f"{Colors.OKCYAN}⏳ Step 2/4: Evaluating content...{Colors.ENDC}")
        try:
            evaluation = await evaluate_content(content, mode, child_age, gemini_client)
            avg_score = evaluation.get_average_score()
            log(f"✓ Evaluation complete - Average: {avg_score:.2f}/5\n\n")
            log(f"EVALUATION RESULTS:\n")
            
            scores = evaluation.get_scores_dict()
            for category, score in scores.items():
                category_score = getattr(evaluation, category)
                log(f"  {category}: {score}/5")
                log(f"    Explanation: {category_score.explanation}")
                if score <= 3 and category_score.improvement_suggestion:
                    log(f"    Improvement Suggestion: {category_score.improvement_suggestion}")
                log(f"\n")
                color = Colors.OKGREEN if score >= 4 else (Colors.WARNING if score >= 3 else Colors.FAIL)
                print(f"  {color}{category}: {score}/5{Colors.ENDC}")
            
            log(f"\nAverage Score: {avg_score:.2f}/5\n")
            log(f"{'-'*80}\n\n")
            print(f"{Colors.OKGREEN}✓ Evaluation complete - Average: {avg_score:.2f}/5{Colors.ENDC}\n")
            print()
            
        except Exception as e:
            log(f"❌ Evaluation failed: {e}\n\n")
            print(f"{Colors.FAIL}❌ Evaluation failed: {e}{Colors.ENDC}\n")
            continue
        
        # Step 3: Log statistics
        log(f"STEP 3: LOGGING STATISTICS\n")
        print(f"{Colors.OKCYAN}⏳ Step 3/4: Logging statistics...{Colors.ENDC}")
        try:
            tracker.log_iteration(mode, iteration, iteration, evaluation)
            log(f"✓ Statistics logged to CSV\n")
            log(f"{'-'*80}\n\n")
            print(f"{Colors.OKGREEN}✓ Statistics logged{Colors.ENDC}\n")
        except Exception as e:
            log(f"❌ Logging failed: {e}\n\n")
            print(f"{Colors.FAIL}❌ Logging failed: {e}{Colors.ENDC}\n")
        
        # Step 4: Improve prompt (skip on last iteration or if all scores are 4+)
        if iteration < iterations:
            # Check if all scores are 4 or above
            if evaluation.all_scores_above_threshold(threshold=4):
                log(f"STEP 4: SKIPPED (All scores are 4 or above - optimization complete!)\n")
                log(f"{'-'*80}\n\n")
                log(f"🎉 OPTIMIZATION COMPLETE - All categories scored 4 or above!\n")
                log(f"Stopping optimization early at iteration {iteration}/{iterations}\n\n")
                print(f"{Colors.OKGREEN}✓ All scores are 4 or above - optimization complete!{Colors.ENDC}")
                print(f"{Colors.OKGREEN}Stopping optimization early at iteration {iteration}/{iterations}{Colors.ENDC}\n")
                break
            else:
                log(f"STEP 4: IMPROVING PROMPT\n")
                print(f"{Colors.OKCYAN}⏳ Step 4/4: Generating improved prompt...{Colors.ENDC}")
                
                # Log improvement suggestions
                improvement_suggestions = evaluation.get_improvement_suggestions()
                if improvement_suggestions:
                    log(f"IMPROVEMENT SUGGESTIONS:\n")
                    for category, suggestion in improvement_suggestions.items():
                        log(f"  {category}: {suggestion}\n")
                    log(f"\n")
                
                try:
                    improved_prompt = await suggest_improvements(
                        current_prompt, evaluation, mode, gemini_client
                    )
                    
                    log(f"✓ Prompt improvement successful\n")
                    log(f"IMPROVED PROMPT:\n{improved_prompt}\n")
                    log(f"{'-'*80}\n\n")
                    
                    # Save improved prompt
                    prompt_template_path.write_text(improved_prompt, encoding="utf-8")
                    current_prompt = improved_prompt
                    
                    print(f"{Colors.OKGREEN}✓ Prompt improved and saved{Colors.ENDC}\n")
                    
                except Exception as e:
                    log(f"❌ Improvement failed: {e}\n")
                    log(f"⚠️  Continuing with current prompt\n\n")
                    print(f"{Colors.FAIL}❌ Improvement failed: {e}{Colors.ENDC}")
                    print(f"{Colors.WARNING}⚠️  Continuing with current prompt{Colors.ENDC}\n")
        else:
            log(f"STEP 4: SKIPPED (Final iteration)\n")
            log(f"{'-'*80}\n\n")
            print(f"{Colors.OKBLUE}ℹ️  Final iteration - skipping prompt improvement{Colors.ENDC}\n")
        
        # Small delay between iterations
        if iteration < iterations:
            await asyncio.sleep(1)
    
    # Final summary
    log(f"\n{'='*80}\n")
    log(f"OPTIMIZATION COMPLETE\n")
    log(f"Completed: {datetime.now().isoformat()}\n")
    log(f"Total Iterations: {iterations}\n")
    log(f"Final prompt saved to: {prompt_template_path}\n")
    log(f"Statistics saved to: {statistics_path}\n")
    log(f"{'='*80}\n")
    log_file.close()
    
    print(f"\n{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}🎉 Optimization complete!{Colors.ENDC}")
    print(f"{Colors.OKGREEN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Completed {iterations} iterations{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Statistics saved to: {statistics_path}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Final prompt saved to: {prompt_template_path}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}✓ Log file saved to: {log_path}{Colors.ENDC}\n")


def main():
    """Parse arguments and run optimization."""
    parser = argparse.ArgumentParser(
        description="Optimize story generation prompts through iterative evaluation"
    )
    
    parser.add_argument(
        "--mode",
        choices=["outline", "pages"],
        required=True,
        help="Type of prompt to optimize"
    )
    
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of optimization iterations (default: 10)"
    )
    
    parser.add_argument(
        "--child-name",
        default="Alex",
        help="Child's name for test story (default: Alex)"
    )
    
    parser.add_argument(
        "--child-age",
        type=int,
        default=6,
        help="Child's age for test story (default: 6)"
    )
    
    parser.add_argument(
        "--title",
        default="The Magical Adventure",
        help="Story title (default: The Magical Adventure)"
    )
    
    parser.add_argument(
        "--summary",
        default="A child discovers a magical object and goes on an adventure",
        help="Story summary/theme"
    )
    
    parser.add_argument(
        "--num-pages",
        type=int,
        default=5,
        help="Number of pages (default: 5)"
    )
    
    parser.add_argument(
        "--language",
        default="English",
        help="Story language (default: English)"
    )
    
    args = parser.parse_args()
    
    # Run optimization
    asyncio.run(optimize_prompts(
        mode=args.mode,
        iterations=args.iterations,
        child_name=args.child_name,
        child_age=args.child_age,
        title=args.title,
        summary=args.summary,
        num_pages=args.num_pages,
        language=args.language,
    ))


if __name__ == "__main__":
    main()

