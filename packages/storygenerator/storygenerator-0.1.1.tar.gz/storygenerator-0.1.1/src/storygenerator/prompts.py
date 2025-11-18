"""Story generation prompts."""

from pathlib import Path
import importlib.resources


def _load_prompt_template(template_name: str) -> str:
    """Load a prompt template from the prompt_templates directory.
    
    Works in both development and installed package scenarios.
    """
    # Try development path first (for local testing)
    dev_path = Path(__file__).parent.parent.parent / "prompt_templates" / template_name
    if dev_path.exists():
        return dev_path.read_text(encoding="utf-8")
    
    # Try installed package path using importlib.resources
    try:
        # When installed, prompt_templates should be in the package directory
        package = importlib.resources.files("storygenerator")
        template_file = package / "prompt_templates" / template_name
        return template_file.read_text(encoding="utf-8")
    except (ImportError, FileNotFoundError):
        # Fallback: try relative to package directory
        package_dir = Path(__file__).parent
        fallback_path = package_dir / "prompt_templates" / template_name
        if fallback_path.exists():
            return fallback_path.read_text(encoding="utf-8")
        
        raise FileNotFoundError(
            f"Prompt template '{template_name}' not found.\n"
            f"Tried:\n"
            f"  - {dev_path}\n"
            f"  - package resource: storygenerator/prompt_templates/{template_name}\n"
            f"  - {fallback_path}"
        )


def get_story_outline_prompt() -> str:
    """Get the current story outline prompt (reloads from file each time)."""
    return _load_prompt_template("story_outline_prompt.txt")


def get_story_page_prompt() -> str:
    """Get the current story page prompt (reloads from file each time)."""
    return _load_prompt_template("story_page_prompt.txt")


# For backwards compatibility, load prompts at module level
# But these will be stale if files are updated during runtime
STORY_OUTLINE_PROMPT = _load_prompt_template("story_outline_prompt.txt")
STORY_PAGE_PROMPT = _load_prompt_template("story_page_prompt.txt")

