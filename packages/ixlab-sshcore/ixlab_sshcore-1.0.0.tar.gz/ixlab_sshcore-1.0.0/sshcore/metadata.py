"""Metadata parsing and formatting for SSH host tags."""

from typing import Dict, List, Tuple, Optional


def parse_metadata_comment(line: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse metadata comment lines that precede Host blocks."""
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None, None
    
    content = stripped[1:].strip()
    if not content.startswith("@"):
        return None, None
    
    if ":" not in content:
        return None, None
    
    key, value = content[1:].split(":", 1)
    return key.strip().lower(), value.strip()


def parse_tags(value: str) -> List[str]:
    """
    Parse comma-separated tags from a value string.
    
    Args:
        value: Comma-separated tag string
    
    Returns:
        List of tag strings with whitespace trimmed
    
    Example:
        "prod, web, critical" -> ["prod", "web", "critical"]
    """
    if not value:
        return []
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def format_metadata_comments(tags: List[str]) -> List[str]:
    """Return comment lines that encode the tags attached to a host."""

    if not tags:
        return []
    tags_str = ", ".join(tags)
    return [f"# @tags: {tags_str}"]
