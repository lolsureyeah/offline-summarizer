# app/utils.py
"""
Contains helper utility functions for the application.
"""

def enforce_word_limit(text: str, limit: int = 1000) -> str:
    """
    Truncates text to a word limit, attempting to respect sentence boundaries.
    """
    words = text.split()
    if len(words) <= limit:
        return text
    
    # Truncate to the word limit
    truncated_text = " ".join(words[:limit])
    
    # Find the last sentence-ending punctuation
    # We search in reverse to find the last complete sentence.
    last_punc_index = -1
    for punc in ['.', '!', '?']:
        index = truncated_text.rfind(punc)
        if index > last_punc_index:
            last_punc_index = index
            
    if last_punc_index != -1:
        # Return text up to and including the last punctuation mark
        return truncated_text[:last_punc_index + 1]
    else:
        # If no sentence end is found, add an ellipsis
        return truncated_text + "..."