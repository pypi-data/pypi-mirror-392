"""DailyStories Generator - A library for generating children's storybooks with Gemini AI."""

from dailystories_generator.types import UpdateType, Update
from dailystories_generator.models import (
    ReferenceImage,
    GenerationRequest,
    StoryArtifact,
    PageArtifact,
)
from dailystories_generator.generator import StoryGenerator

__all__ = [
    "UpdateType",
    "Update",
    "ReferenceImage",
    "GenerationRequest",
    "StoryArtifact",
    "PageArtifact",
    "StoryGenerator",
]

__version__ = "0.1.0"

