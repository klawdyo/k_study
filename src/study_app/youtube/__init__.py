"""YouTube helpers used to build lessons: search, captions, local transcription."""
import re

VIDEO_ID = re.compile(r"(?:v=|youtu\.be/|embed/)([\w-]{11})")


def extract_id(text: str) -> str:
    """Accepts an 11-character video id or a YouTube URL."""
    m = VIDEO_ID.search(text)
    if m:
        return m.group(1)
    if re.fullmatch(r"[\w-]{11}", text):
        return text
    raise ValueError(f"not a YouTube video: {text}")
