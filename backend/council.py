"""3-stage LLM Council orchestration."""

from typing import List, Dict, Any, Tuple
from .llm_client import query_models_parallel, query_model
from .config import COUNCIL_MODELS, CHAIRMAN_MODEL


async def stage1_collect_responses(
    user_query: str, 
    active_models: List[str] = None,
    history: List[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Stage 1: Collect individual responses from all council models.

    Args:
        user_query: The user's question
        active_models: Optional list of models to use. If None, uses all COUNCIL_MODELS.
        history: Optional list of previous messages [{"role": "user", "content": "..."}, ...]

    Returns:
        List of dicts with 'model' and 'response' keys
    """
    messages = []
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": user_query})
    
    models_to_query = active_models if active_models else COUNCIL_MODELS

    # Query all models in parallel
    responses = await query_models_parallel(models_to_query, messages)

    # Format results
    stage1_results = []
    for model, response in responses.items():
        if response is not None:  # Only include successful responses
            stage1_results.append({
                "model": model,
                "response": response.get('content', '')
            })

    return stage1_results


async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    active_models: List[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2: Each model ranks the anonymized responses.

    Args:
        user_query: The original user query
        stage1_results: Results from Stage 1

    Returns:
        Tuple of (rankings list, label_to_model mapping)
    """
    # Create anonymized labels for responses (Response A, Response B, etc.)
    labels = [chr(65 + i) for i in range(len(stage1_results))]  # A, B, C, ...

    # Create mapping from label to model name
    label_to_model = {
        f"Response {label}": result['model']
        for label, result in zip(labels, stage1_results)
    }

    # Build the ranking prompt
    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    ranking_prompt = f"""You are evaluating different responses to the following question:

Question: {user_query}

Here are the responses from different models (anonymized):

{responses_text}

Your task:
1. First, evaluate each response individually. For each response, explain what it does well and what it does poorly.
2. Then, at the very end of your response, provide a final ranking.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows:
- Start with the line "FINAL RANKING:" (all caps, with colon)
- Then list the responses from best to worst as a numbered list
- Each line should be: number, period, space, then ONLY the response label (e.g., "1. Response A")
- Do not add any other text or explanations in the ranking section

Example of the correct format for your ENTIRE response:

Response A provides good detail on X but misses Y...
Response B is accurate but lacks depth on Z...
Response C offers the most comprehensive answer...

FINAL RANKING:
1. Response C
2. Response A
3. Response B

Now provide your evaluation and ranking:"""

    messages = [{"role": "user", "content": ranking_prompt}]
    
    models_to_query = active_models if active_models else COUNCIL_MODELS

    # Get rankings from all council models in parallel
    responses = await query_models_parallel(models_to_query, messages)

    # Format results
    stage2_results = []
    for model, response in responses.items():
        if response is not None:
            full_text = response.get('content', '')
            parsed = parse_ranking_from_text(full_text)
            stage2_results.append({
                "model": model,
                "ranking": full_text,
                "parsed_ranking": parsed
            })

    return stage2_results, label_to_model


async def stage2_debate(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    active_models: List[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2 (Debate Mode): Models critique each other's responses before ranking.
    """
    # Create anonymized labels
    labels = [chr(65 + i) for i in range(len(stage1_results))]
    
    label_to_model = {
        f"Response {label}": result['model']
        for label, result in zip(labels, stage1_results)
    }

    responses_text = "\n\n".join([
        f"Response {label}:\n{result['response']}"
        for label, result in zip(labels, stage1_results)
    ])

    debate_prompt = f"""You are participating in a rigorous debate to answer the following question:

Question: {user_query}

Here are the proposed answers from other participants (anonymized):

{responses_text}

Your task is to CRITIQUE these responses.
1. Identify any factual errors, logical fallacies, or missing context in each response.
2. Compare them directly. Which one offers the best evidence? Which one is the most helpful?
3. Be critical but constructive.

AFTER your critique, you must provide a FINAL RANKING based on your analysis.

IMPORTANT: Your final ranking MUST be formatted EXACTLY as follows at the very end:
FINAL RANKING:
1. Response X
2. Response Y
...

Now, provide your critique and ranking:"""

    messages = [{"role": "user", "content": debate_prompt}]
    
    models_to_query = active_models if active_models else COUNCIL_MODELS

    # Get critiques from all council models
    responses = await query_models_parallel(models_to_query, messages)

    stage2_results = []
    for model, response in responses.items():
        if response is not None:
            full_text = response.get('content', '')
            parsed = parse_ranking_from_text(full_text)
            stage2_results.append({
                "model": model,
                "ranking": full_text, # This now contains the critique + ranking
                "parsed_ranking": parsed
            })

    return stage2_results, label_to_model


async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]],
    history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response.

    Args:
        user_query: The original user query
        stage1_results: Individual model responses from Stage 1
        stage2_results: Rankings from Stage 2
        history: Optional conversation history

    Returns:
        Dict with 'model' and 'response' keys
    """
    # Build comprehensive context for chairman
    stage1_text = "\n\n".join([
        f"Model: {result['model']}\nResponse: {result['response']}"
        for result in stage1_results
    ])

    stage2_text = "\n\n".join([
        f"Model: {result['model']}\nRanking: {result['ranking']}"
        for result in stage2_results
    ])

    chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have provided responses to a user's question, and then ranked each other's responses.

Original Question: {user_query}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task as Chairman is to synthesize all of this information into a single, comprehensive, accurate answer to the user's original question. Consider:
- The individual responses and their insights
- The peer rankings and what they reveal about response quality
- Any patterns of agreement or disagreement

Provide a clear, well-reasoned final answer that represents the council's collective wisdom:"""

    messages = []
    if history:
        # We need to be careful here. The prompt above includes the current user query.
        # If we just prepend history, the LLM might get confused about what the "current" task is
        # vs the history. 
        # A better approach for the Chairman is to see the history as context, 
        # but the *current* message is the synthesis instruction.
        messages.extend(history)
    
    messages.append({"role": "user", "content": chairman_prompt})

    # Query the chairman model
    response = await query_model(CHAIRMAN_MODEL, messages)

    if response is None:
        # Fallback if chairman fails
        return {
            "model": CHAIRMAN_MODEL,
            "response": "Error: Unable to generate final synthesis."
        }

    return {
        "model": CHAIRMAN_MODEL,
        "response": response.get('content', '')
    }


def parse_ranking_from_text(ranking_text: str) -> List[str]:
    """
    Parse the FINAL RANKING section from the model's response.

    Args:
        ranking_text: The full text response from the model

    Returns:
        List of response labels in ranked order
    """
    import re

    # Look for "FINAL RANKING:" section (case insensitive)
    match = re.search(r'FINAL RANKING:', ranking_text, re.IGNORECASE)
    if match:
        # Extract everything after "FINAL RANKING:"
        ranking_section = ranking_text[match.end():]
        
        # Try to extract numbered list format (e.g., "1. Response A")
        # This pattern looks for: number, period, optional space, "Response X"
        numbered_matches = re.findall(r'\d+\.\s*Response [A-Z]', ranking_section, re.IGNORECASE)
        if numbered_matches:
            # Extract just the "Response X" part, normalizing case
            return [re.search(r'Response [A-Z]', m, re.IGNORECASE).group().title() for m in numbered_matches]

        # Fallback: Extract all "Response X" patterns in order from the section
        matches = re.findall(r'Response [A-Z]', ranking_section, re.IGNORECASE)
        if matches:
             return [m.title() for m in matches]

    # Fallback: try to find any "Response X" patterns in order from the whole text
    # But be careful not to pick up mentions in the critique text if possible
    # Ideally we only want the final list. 
    # If we failed to find the section, we might just return empty or try to guess.
    # Let's try to find the last occurrence of a list-like structure.
    
    matches = re.findall(r'Response [A-Z]', ranking_text, re.IGNORECASE)
    # If we have many matches, it's risky. But better than nothing.
    return [m.title() for m in matches]


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Calculate aggregate rankings across all models.

    Args:
        stage2_results: Rankings from each model
        label_to_model: Mapping from anonymous labels to model names

    Returns:
        List of dicts with model name and average rank, sorted best to worst
    """
    from collections import defaultdict

    # Track positions for each model
    model_positions = defaultdict(list)

    for ranking in stage2_results:
        ranking_text = ranking['ranking']

        # Parse the ranking from the structured format
        parsed_ranking = parse_ranking_from_text(ranking_text)

        for position, label in enumerate(parsed_ranking, start=1):
            if label in label_to_model:
                model_name = label_to_model[label]
                model_positions[model_name].append(position)

    # Calculate average position for each model
    aggregate = []
    for model, positions in model_positions.items():
        if positions:
            avg_rank = sum(positions) / len(positions)
            aggregate.append({
                "model": model,
                "average_rank": round(avg_rank, 2),
                "rankings_count": len(positions)
            })

    # Sort by average rank (lower is better)
    aggregate.sort(key=lambda x: x['average_rank'])

    return aggregate


async def generate_conversation_title(user_query: str) -> str:
    """
    Generate a short title for a conversation based on the first user message.

    Args:
        user_query: The first user message

    Returns:
        A short title (3-5 words)
    """
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following question.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Question: {user_query}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]

    # Use gemini-2.5-flash for title generation (fast and cheap)
    response = await query_model("google/gemini-2.5-flash", messages, timeout=30.0)

    if response is None:
        # Fallback to a generic title
        return "New Conversation"

    title = response.get('content', 'New Conversation').strip()

    # Clean up the title - remove quotes, limit length
    title = title.strip('"\'')

    # Truncate if too long
    if len(title) > 50:
        title = title[:47] + "..."

    return title


async def run_full_council(
    user_query: str, 
    active_models: List[str] = None, 
    debate_mode: bool = False,
    history: List[Dict[str, str]] = None
) -> Tuple[List, List, Dict, Dict]:
    """
    Run the complete 3-stage council process.

    Args:
        user_query: The user's question
        active_models: Optional list of active models
        debate_mode: Whether to run debate mode
        history: Optional conversation history

    Returns:
        Tuple of (stage1_results, stage2_results, stage3_result, metadata)
    """
    # Stage 1: Collect individual responses
    stage1_results = await stage1_collect_responses(user_query, active_models, history)

    # If no models responded successfully, return error
    if not stage1_results:
        return [], [], {
            "model": "error",
            "response": "All models failed to respond. Please try again."
        }, {}

    # Stage 2: Collect rankings (or Debate)
    if debate_mode:
        stage2_results, label_to_model = await stage2_debate(user_query, stage1_results, active_models)
    else:
        stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results, active_models)

    # Calculate aggregate rankings
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

    # Stage 3: Synthesize final answer
    stage3_result = await stage3_synthesize_final(
        user_query,
        stage1_results,
        stage2_results,
        history
    )

    # Prepare metadata
    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings
    }

    return stage1_results, stage2_results, stage3_result, metadata
