"""Evaluation system for story content quality assessment."""

from pydantic import BaseModel, Field
from typing import Dict

from dailystories_generator.gemini_client import GeminiClient


# Category definitions for evaluation
EVALUATION_CATEGORIES = {
    "creativity": "Originality and imaginativeness of ideas, scenarios, and solutions",
    "age_appropriateness": "Content, vocabulary, and themes suitable for target age (6 years)",
    "coherence": "Logical flow, consistency, and clarity of narrative",
    "engagement": "How captivating and interesting the content is for young readers",
    "language_quality": "Grammar, sentence structure, and writing style quality",
    "plot_structure": "Clear beginning/middle/end, proper pacing of events",
    "character_development": "Growth, personality, and relatability of characters",
    "character_introduction": "How well characters are introduced and established. For the story outline, this should come before we start defining the pages in the outline to shape and form the pages.",
    "emotional_resonance": "Emotional depth and impact of the story",
    "pacing": "Speed and rhythm of story progression, scene transitions",
    "tone_consistency": "Maintaining warm, optimistic, age-appropriate tone throughout",
}


class CategoryScore(BaseModel):
    """Score for a single evaluation category."""
    
    score: int = Field(..., ge=1, le=5, description="Score from 1-5")
    explanation: str = Field(..., description="Explanation for the score")
    improvement_suggestion: str = Field(default="", description="Suggestion for improvement (only if score <= 3)")


class EvaluationResult(BaseModel):
    """Complete evaluation result with all category scores."""
    
    creativity: CategoryScore
    age_appropriateness: CategoryScore
    coherence: CategoryScore
    engagement: CategoryScore
    language_quality: CategoryScore
    plot_structure: CategoryScore
    character_development: CategoryScore
    character_introduction: CategoryScore
    emotional_resonance: CategoryScore
    pacing: CategoryScore
    tone_consistency: CategoryScore
    
    def get_scores_dict(self) -> Dict[str, int]:
        """Get a dictionary of category names to scores."""
        return {
            "creativity": self.creativity.score,
            "age_appropriateness": self.age_appropriateness.score,
            "coherence": self.coherence.score,
            "engagement": self.engagement.score,
            "language_quality": self.language_quality.score,
            "plot_structure": self.plot_structure.score,
            "character_development": self.character_development.score,
            "character_introduction": self.character_introduction.score,
            "emotional_resonance": self.emotional_resonance.score,
            "pacing": self.pacing.score,
            "tone_consistency": self.tone_consistency.score,
        }
    
    def get_average_score(self) -> float:
        """Calculate the average score across all categories."""
        scores = self.get_scores_dict().values()
        return sum(scores) / len(scores)
    
    def all_scores_above_threshold(self, threshold: int = 4) -> bool:
        """Check if all category scores are above the threshold."""
        return all(score >= threshold for score in self.get_scores_dict().values())
    
    def get_improvement_suggestions(self) -> dict[str, str]:
        """Get improvement suggestions for categories scoring 3 or lower."""
        suggestions = {}
        for category, score in self.get_scores_dict().items():
            if score <= 3:
                category_score = getattr(self, category)
                if category_score.improvement_suggestion:
                    suggestions[category] = category_score.improvement_suggestion
        return suggestions


async def evaluate_content(
    content: str,
    mode: str,
    child_age: int,
    gemini_client: GeminiClient,
) -> EvaluationResult:
    """
    Evaluate story content across all quality categories.
    
    Args:
        content: The story content to evaluate (outline or pages)
        mode: Type of content ('outline' or 'pages')
        child_age: Target age for the story
        gemini_client: Gemini client for API calls
    
    Returns:
        EvaluationResult with scores and explanations for all categories
    """
    # Build the evaluation prompt
    categories_text = "\n".join([
        f"{i+1}. **{cat}**: {desc}"
        for i, (cat, desc) in enumerate(EVALUATION_CATEGORIES.items())
    ])
    
    evaluation_prompt = f"""You are a world class expert evaluator of children's story content.
You know how one really write great stories for children, based on science. What matters for the child
to really enjoy the story, and how to best introduce characters, have a good plot, and have a good story.
Usually there is some moral in each story, so the child learns something. You are quite strict and the best
stories are the only acceptable ones.

Please evaluate the following {mode} for a children's story targeted at age {child_age}.

CONTENT TO EVALUATE:
{content}

EVALUATION CATEGORIES:
{categories_text}

For EACH category, provide:
1. A score from 1 to 5 (where 1 = very poor, 2 = poor, 3 = acceptable, 4 = good, 5 = excellent)
2. A detailed explanation (2-3 sentences) justifying the score
3. If the score is 3 or lower, provide a specific improvement suggestion (1-2 sentences) on how to improve this category

Please respond in the following JSON format:
{{
  "creativity": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "age_appropriateness": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "coherence": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "engagement": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "language_quality": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "plot_structure": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "character_development": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "character_introduction": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "emotional_resonance": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "pacing": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}},
  "tone_consistency": {{"score": X, "explanation": "...", "improvement_suggestion": "..." (only if score <= 3)}}
}}

Note: For categories with score 4 or 5, you can omit "improvement_suggestion" or set it to empty string.

Be honest and constructive in your evaluation. Identify both strengths and areas for improvement."""

    # Generate evaluation using Gemini
    response, _ = await gemini_client.generate_text(
        prompt=evaluation_prompt,
        system_prompt="You are an expert in children's literature and story evaluation. Provide detailed, constructive feedback. Always respond with valid JSON only, no additional text.",
        model="gemini-2.5-flash",
        max_tokens=2000,
    )
    
    # Parse the JSON response (may have markdown code blocks)
    import json
    import re
    
    # Try to extract JSON from markdown code blocks if present
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        # Assume the entire response is JSON
        json_str = response.strip()
    
    evaluation_data = json.loads(json_str)
    
    # Create and return EvaluationResult
    return EvaluationResult(**evaluation_data)

