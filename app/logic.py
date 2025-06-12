# app/logic.py
"""
Orchestrates the main application logic, connecting parsing, summarization, and utilities.
"""
from .parsers import extract_text
from .ollama_client import call_ollama_summarize
from .utils import enforce_word_limit

def generate_summary(file_path: str, update_status: callable) -> str:
    """
    The main workflow for generating a document summary.

    Args:
        file_path (str): The absolute path to the document.
        update_status (callable): A function to send status updates to the GUI.

    Returns:
        str: The final, length-validated summary.
    
    Raises:
        Exception: Propagates exceptions from downstream modules to be caught by the GUI.
    """
    try:
        # Step 1: Extract text from the file
        update_status("Step 1/4: Parsing document...")
        full_text = extract_text(file_path)
        
        if not full_text or len(full_text.strip()) < 50:
             raise ValueError("Document is empty or could not be read. For image-based PDFs, ensure Tesseract is installed.")
            
        # Step 2: Call the local model via Ollama
        update_status("Step 2/4: Summarizing with local LLM (this may take a moment)...")
        # --- IMPORTANT: CHOOSE YOUR MODEL HERE ---
        # model_to_use = "gemma:2b"
        model_to_use = "llama3.2:3b"
        # model_to_use = "dolphin-llama3:8b" # A good, uncensored choice
        raw_summary = call_ollama_summarize(full_text, model=model_to_use)
        
        if not raw_summary:
            raise ValueError("The model returned an empty summary.")

        # Step 3: Enforce the 1000-word limit
        update_status("Step 3/4: Finalizing summary...")
        final_summary = enforce_word_limit(raw_summary, limit=1000)
        
        update_status("Step 4/4: Done!")
        return final_summary
        
    except Exception as e:
        # Re-raise the exception to be handled by the GUI's error display
        raise e