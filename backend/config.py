"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Council members - list of OpenRouter model identifiers
COUNCIL_MODELS = [
    "llama-3.3-70b-versatile", # Groq
    "llama-3.1-8b-instant",    # Groq
    "gemini-2.0-flash",        # Google
    "gemini-2.5-flash",        # Google
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "gemini-2.5-flash"

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
