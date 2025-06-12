# app/utils.py
"""
Contains helper utility functions for the application.
"""
import re

def parse_structured_summary(raw_text: str) -> dict:
    """
    Parses the raw text output from the LLM to extract Title, TLDR, and Summary.
    """
    data = {'title': '', 'tldr': '', 'summary': ''}
    
    # Use regular expressions to find the content for each section.
    # The (?s) flag allows '.' to match newline characters.
    
    title_match = re.search(r"TITLE:(.*?)(TLDR:|SUMMARY:|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if title_match:
        data['title'] = title_match.group(1).strip()

    tldr_match = re.search(r"TLDR:(.*?)(SUMMARY:|$)", raw_text, re.DOTALL | re.IGNORECASE)
    if tldr_match:
        data['tldr'] = tldr_match.group(1).strip()

    summary_match = re.search(r"SUMMARY:(.*)", raw_text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        data['summary'] = summary_match.group(1).strip()

    # Fallback if parsing fails, just return the whole text as the summary
    if not data['title'] and not data['tldr'] and not data['summary']:
        data['summary'] = raw_text.strip()

    return data