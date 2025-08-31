"""
Utility module to check if GPT responses are vague or too long.
"""

import re
from typing import List


def is_vague_response(response: str) -> bool:
    """
    Check if a response is vague based on certain criteria.
    
    Args:
        response (str): The response text to check
        
    Returns:
        bool: True if response is vague, False otherwise
    """
    # Convert to lowercase for case-insensitive matching
    response_lower = response.lower()
    
    # List of vague phrases that indicate uncertainty
    vague_phrases = [
        "not sure",
        "i'm not sure",
        "i don't know",
        "depends",
        "it depends",
        "maybe",
        "possibly",
        "perhaps",
        "could be",
        "might be",
        "i think",
        "i believe",
        "in my opinion",
        "generally",
        "typically",
        "usually",
        "sometimes",
        "often",
        "frequently",
        "rarely",
        "hard to say",
        "difficult to determine",
        "unclear",
        "ambiguous",
        "vague",
        "complex",
        "complicated",
        "varies",
        "varies depending",
        "context dependent"
    ]
    
    # Check for vague phrases
    for phrase in vague_phrases:
        if phrase in response_lower:
            return True
    
    # Check if response is too long (more than 100 words)
    word_count = len(response.split())
    if word_count > 100:
        return True
    
    # Check for excessive hedging words
    hedging_words = ["maybe", "perhaps", "possibly", "might", "could", "would", "should"]
    hedging_count = sum(1 for word in hedging_words if word in response_lower)
    if hedging_count >= 3:
        return True
    
    return False


def get_response_quality_score(response: str) -> float:
    """
    Get a quality score for the response (0-1, where 1 is best).
    
    Args:
        response (str): The response text to score
        
    Returns:
        float: Quality score between 0 and 1
    """
    if is_vague_response(response):
        return 0.0
    
    # Basic scoring based on response length and content
    word_count = len(response.split())
    
    # Prefer responses between 10-50 words
    if 10 <= word_count <= 50:
        return 1.0
    elif 5 <= word_count < 10:
        return 0.8
    elif 50 < word_count <= 100:
        return 0.6
    else:
        return 0.3 