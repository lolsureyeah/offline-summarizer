# app/logic.py
"""
Orchestrates the main application logic, connecting parsing, summarization, and utilities.
"""
from .parsers import extract_text
from .ollama_client import call_ollama_summarize
from .utils import parse_structured_summary

def generate_summary(file_path: str, length_percentage_str: str, keywords_str: str, update_status: callable) -> str:
    """
    The main workflow for generating a document summary with advanced options.
    """
    try:
        # Step 1: Extract text from the file
        update_status("Step 1/3: Parsing document...")
        full_text = extract_text(file_path)
        
        if not full_text or len(full_text.strip()) < 50:
             raise ValueError("Document is empty or could not be read. For image-based PDFs, ensure Tesseract is installed.")
        
        source_word_count = len(full_text.split())

        # Safely calculate target word count, default to 20% if input is empty or invalid
        try:
            length_percentage = float(length_percentage_str) / 100 if length_percentage_str else 0.2
            if not (0.01 <= length_percentage <= 1.0):
                length_percentage = 0.2
            target_word_count = int(source_word_count * length_percentage)
        except (ValueError, TypeError):
            target_word_count = int(source_word_count * 0.2)
        
        # Parse keywords string into a list
        keywords = [keyword.strip() for keyword in keywords_str.split(',')] if keywords_str else []

        # Step 2: Call the local model via Ollama with all parameters
        update_status("Step 2/3: Summarizing with local LLM (this may take a moment)...")
        model_to_use = "llama3.2:3b" # You can still change this easily
        raw_output = call_ollama_summarize(full_text, model_to_use, target_word_count, keywords)
        
        if not raw_output:
            raise ValueError("The model returned an empty response.")

        # Step 3: Parse the structured output and format it
        update_status("Step 3/3: Formatting summary...")
        parsed_data = parse_structured_summary(raw_output)

        final_formatted_summary = (
            f"TITLE: {parsed_data.get('title', 'N/A')}\n\n"
            f"TL;DR: {parsed_data.get('tldr', 'N/A')}\n\n"
            f"------------------------------------\n\n"
            f"SUMMARY:\n{parsed_data.get('summary', 'N/A')}"
        )
        
        return final_formatted_summary
        
    except Exception as e:
        raise e