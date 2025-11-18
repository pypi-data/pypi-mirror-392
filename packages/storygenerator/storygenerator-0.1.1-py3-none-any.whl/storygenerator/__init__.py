"""DailyStories Generator - A library for generating children's storybooks with Gemini AI."""

from storygenerator.types import UpdateType, Update
from storygenerator.models import (
    ReferenceImage,
    GenerationRequest,
    StoryArtifact,
    PageArtifact,
)
from storygenerator.generator import StoryGenerator

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

