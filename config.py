
import os
from dotenv import load_dotenv

load_dotenv()

PAGE_TITLE = "Social Studio AI"

# Groq models (configured internally)
TEXT_MODEL = "openai/gpt-oss-20b"
VISION_MODEL = "qwen/qwen3.8-27b"

# Image upload limit
MAX_IMAGE_MB = int(os.getenv("MAX_IMAGE_MB", "8"))

# User-facing choices
PLATFORMS = [
    "Instagram",
    "LinkedIn",
    "Facebook",
    "X (Twitter)",
    "YouTube Community",
    "Pinterest"
]

TONES = [
    "Professional",
    "Casual",
    "Friendly",
    "Persuasive",
    "Inspirational",
    "Humorous",
    "Educational",
    "Creative"
]

LENGTHS = [
    "Short",
    "Medium",
    "Long"
]
