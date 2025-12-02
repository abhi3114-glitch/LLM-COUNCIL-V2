"""Client for Google Gemini API."""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from .config import GOOGLE_API_KEY

# Configure the library
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

async def query_gemini(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a Gemini model via Google's API.
    
    Args:
        model: Model identifier (e.g., "gemini-2.0-flash-exp")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout (not strictly used by genai lib but kept for signature compatibility)
        
    Returns:
        Response dict with 'content' and optional 'reasoning_details', or None if failed
    """
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found.")
        return None

    try:
        # Extract system message if present
        system_instruction = None
        prompt_parts = []

        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                system_instruction = content
            elif role == 'user':
                prompt_parts.append(content)
            elif role == 'assistant':
                prompt_parts.append(f"Model: {content}")

        # Join all parts for the final prompt if it's not just a single message
        final_prompt = "\n\n".join(prompt_parts)

        # Initialize model
        generative_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction
        )

        # Generate content
        response = await generative_model.generate_content_async(final_prompt)
        
        # Check if response was blocked
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            print(f"Gemini blocked request: {response.prompt_feedback.block_reason}")
            return None
            
        try:
            return {
                'content': response.text,
                'reasoning_details': None
            }
        except ValueError:
            # If response was blocked by safety settings but no text is available
            print(f"Gemini response error (likely safety block): {response.candidates}")
            return None

    except Exception as e:
        print(f"Error querying Gemini model {model}: {e}")
        return None
