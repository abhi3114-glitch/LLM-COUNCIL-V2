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
