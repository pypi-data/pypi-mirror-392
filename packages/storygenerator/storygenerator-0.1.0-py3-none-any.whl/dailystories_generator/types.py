"""Type definitions for the story generator."""

from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Awaitable


class UpdateType(str, Enum):
    """Status update types during story generation."""
    
    GENERATING_OUTLINE = "generating_outline"
    OUTLINE_COMPLETE = "outline_complete"
    GENERATING_PAGE = "generating_page"
    PAGE_COMPLETE = "page_complete"
    GENERATING_COVER = "generating_cover"
    COVER_COMPLETE = "cover_complete"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Update:
    """
    Represents a status update during story generation.
    
    Attributes:
        type: The type of update
        data: Additional data specific to this update (e.g., page_number, tokens)
        artifacts: The current artifacts at this stage (incremental or cumulative)
    """
    
    type: UpdateType
    data: dict[str, Any]
    artifacts: dict[str, Any]


# Type alias for the callback function
UpdateCallback = Callable[[Update], Awaitable[None]]

