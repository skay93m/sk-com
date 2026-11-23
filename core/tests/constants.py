"""Shared contract constants for post, view, static-export, and browser checks."""

FORBIDDEN_BOUNDARY_TEXT = (
    "I am a pharmacist who prefers lasting fixes",
    "AI use: AI tools assist",
    "Personal analysis, not clinical advice",
    "sk-boundary",
)

FORBIDDEN_AI_DISCLOSURE_TEXT = "No separate AI contribution metadata"

HELLO_WORLD_AI_DISCLOSURE = (
    "I drafted this with AI assistance. The idea and words are mine. "
    "Inspired by Che Det's writing style."
)

AI_CONTRIBUTION_LABEL = "AI contribution"
REVISION_HISTORY_LABEL = "Revision history"
AI_CONTRIBUTION_SUMMARY = f"<summary>{AI_CONTRIBUTION_LABEL}</summary>"
REVISION_HISTORY_SUMMARY = f"<summary>{REVISION_HISTORY_LABEL}</summary>"
