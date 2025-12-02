"""Unified LLM Client for routing requests to different providers."""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from .config import OPENROUTER_API_KEY, OPENROUTER_API_URL
from .gemini_client import query_gemini
from .groq_client import query_groq


async def query_openrouter(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """Query OpenRouter API (fallback/default)."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173", # Optional, for including your app on openrouter.ai rankings
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Error querying OpenRouter model {model}: {e}")
        return None


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0
) -> Optional[Dict[str, Any]]:
    """
    Query a single model, routing to the appropriate provider.
    """
    # Routing Logic
    if "gemini" in model.lower() and "/" not in model:
        # Direct Google Gemini (e.g. "gemini-2.0-flash-exp")
        return await query_gemini(model, messages, timeout)
    
    if any(x in model.lower() for x in ["llama", "mixtral", "gemma"]) and "/" not in model:
        # Direct Groq (e.g. "llama-3.3-70b-versatile")
        # Note: Groq models usually don't have a slash, OpenRouter ones do (provider/model)
        return await query_groq(model, messages, timeout)

    # Default to OpenRouter
    return await query_openrouter(model, messages, timeout)


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.
    """
    # Create tasks for all models
    tasks = [query_model(model, messages) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
