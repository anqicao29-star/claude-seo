"""User-facing output cleanup for the local workbench."""

from __future__ import annotations

import re


PROMOTIONAL_FOOTER = re.compile(
    r"(?:\n?[━]{10,}\s*\n)?"
    r"Built by agricidaniel[^\n]*AI Marketing Hub community\s*\n"
    r"🆓\s*Free\s*[→>-]+\s*https://www\.skool\.com/ai-marketing-hub\s*\n"
    r"⚡\s*Pro\s*[→>-]+\s*https://www\.skool\.com/ai-marketing-hub-pro"
    r"(?:\s*\n[━]{10,})?",
    re.IGNORECASE,
)


def clean_assistant_text(text: str) -> str:
    """Remove the upstream promotional footer from workbench answers."""
    return PROMOTIONAL_FOOTER.sub("", text).rstrip()
