"""Client for Groq API."""

from groq import AsyncGroq
from typing import List, Dict, Any, Optional
from .config import GROQ_API_KEY

async def query_groq(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a model via Groq API.
    
    Args:
        model: Model identifier (e.g., "llama-3.3-70b-versatile")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout
        
    Returns:
        Response dict with 'content', or None if failed
    """
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY not found.")
        return None

    try:
        client = AsyncGroq(api_key=GROQ_API_KEY)
        
        completion = await client.chat.completions.create(
            model=model,
            messages=messages,
            timeout=timeout
        )
        
        return {
            'content': completion.choices[0].message.content,
            'reasoning_details': None
        }

    except Exception as e:
        print(f"Error querying Groq model {model}: {e}")
        return None
