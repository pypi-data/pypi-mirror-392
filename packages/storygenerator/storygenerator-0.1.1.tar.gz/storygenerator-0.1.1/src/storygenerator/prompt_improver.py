"""Prompt improvement system based on evaluation feedback."""

import re
from typing import Set

from storygenerator.gemini_client import GeminiClient
from storygenerator.evaluation import EvaluationResult


def validate_placeholders(prompt: str, required_placeholders: Set[str]) -> tuple[bool, Set[str]]:
    """
    Validate that all required placeholders are present in the prompt.
    
    Args:
        prompt: The prompt text to validate
        required_placeholders: Set of required placeholder names (without braces)
    
    Returns:
        Tuple of (is_valid, missing_placeholders)
    """
    # Find all placeholders in the prompt
    found_placeholders = set(re.findall(r'\{(\w+)\}', prompt))
    
    # Check for missing placeholders
    missing_placeholders = required_placeholders - found_placeholders
    
    is_valid = len(missing_placeholders) == 0
    return is_valid, missing_placeholders


def extract_placeholders(prompt: str) -> Set[str]:
    """
    Extract all placeholder names from a prompt template.
    
    Args:
        prompt: The prompt text to extract from
    
    Returns:
        Set of placeholder names (without braces)
    """
    return set(re.findall(r'\{(\w+)\}', prompt))


async def suggest_improvements(
    current_prompt: str,
    evaluation: EvaluationResult,
    mode: str,
    gemini_client: GeminiClient,
    max_retries: int = 5,
) -> str:
    """
    Suggest improvements to a prompt based on evaluation feedback.
    Retries automatically if LLM forgets required placeholders.
    
    Args:
        current_prompt: The current prompt template
        evaluation: Evaluation results with scores and explanations
        mode: Type of prompt ('outline' or 'pages')
        gemini_client: Gemini client for API calls
        max_retries: Maximum number of retry attempts (default: 5)
    
    Returns:
        Improved prompt text
    
    Raises:
        ValueError: If all retries are exhausted and placeholders still missing
    """
    # Extract required placeholders from current prompt
    required_placeholders = extract_placeholders(current_prompt)
    
    # Build feedback summary
    scores_summary = "\n".join([
        f"- {category}: {score}/5 - {getattr(evaluation, category).explanation}"
        for category, score in evaluation.get_scores_dict().items()
    ])
    
    average_score = evaluation.get_average_score()
    
    # Get improvement suggestions for low-scoring categories
    improvement_suggestions = evaluation.get_improvement_suggestions()
    suggestions_text = ""
    if improvement_suggestions:
        suggestions_text = "\n\nSPECIFIC IMPROVEMENT SUGGESTIONS (for categories scoring 3 or lower):\n"
        for category, suggestion in improvement_suggestions.items():
            suggestions_text += f"- {category}: {suggestion}\n"
    
    # Base improvement prompt
    base_prompt = f"""You are an expert prompt engineer specializing in children's story generation.

CURRENT PROMPT TEMPLATE:
{current_prompt}

EVALUATION RESULTS (Average: {average_score:.2f}/5):
{scores_summary}{suggestions_text}

TASK:
Based on the evaluation feedback and improvement suggestions above, suggest an IMPROVED version of the prompt template that addresses the weaknesses identified.

REQUIREMENTS:
1. The improved prompt MUST preserve ALL existing placeholders exactly: {', '.join(sorted(required_placeholders))}
2. Focus on addressing the lowest-scoring categories and implementing the improvement suggestions
3. Keep the prompt structure and format similar
4. Add or modify instructions to improve weak areas based on the suggestions
5. Remove or revise instructions that may have caused issues
6. Maintain clarity and specificity

OUTPUT FORMAT:
Provide ONLY the improved prompt text. Do not include explanations, markdown formatting, or additional commentary.
Start directly with the prompt content."""

    additional_feedback = ""
    
    # Retry loop
    for attempt in range(max_retries):
        # Build full prompt with any additional feedback from previous failures
        full_prompt = base_prompt
        if additional_feedback:
            full_prompt += f"\n\n{additional_feedback}"
        
        # Generate improved prompt
        improved_prompt, _ = await gemini_client.generate_text(
            prompt=full_prompt,
            system_prompt="You are an expert prompt engineer. Provide only the improved prompt text, nothing else.",
            model="gemini-2.5-flash",
            max_tokens=1500,
        )
        
        # Clean up the response (remove markdown if present)
        improved_prompt = improved_prompt.strip()
        
        # Remove markdown code blocks if present
        code_block_match = re.search(r'```(?:\w+)?\s*(.*?)\s*```', improved_prompt, re.DOTALL)
        if code_block_match:
            improved_prompt = code_block_match.group(1).strip()
        
        # Validate placeholders
        is_valid, missing = validate_placeholders(improved_prompt, required_placeholders)
        
        if is_valid:
            # Success! Return the improved prompt
            return improved_prompt
        
        # Failed validation - prepare feedback for retry
        found = extract_placeholders(improved_prompt)
        additional_feedback = f"""
❌ ERROR: Your previous attempt was REJECTED because you forgot required placeholders.

MISSING PLACEHOLDERS: {', '.join(sorted(missing))}
PLACEHOLDERS YOU INCLUDED: {', '.join(sorted(found)) if found else 'NONE'}
REQUIRED PLACEHOLDERS: {', '.join(sorted(required_placeholders))}

You MUST include ALL required placeholders in curly braces exactly as shown above.
Try again and make sure EVERY placeholder from the original prompt is preserved."""
    
    # All retries exhausted
    raise ValueError(
        f"Failed to improve prompt after {max_retries} attempts. "
        f"LLM consistently failed to preserve placeholders: {missing}"
    )

