# app/logic.py
"""
Orchestrates the main application logic, connecting parsing, summarization, and utilities.
"""
import subprocess
from .parsers import extract_text
from .ollama_client import call_ollama_summarize, call_ollama_qna
from .utils import parse_structured_summary

def get_ollama_models():
    """Gets the list of currently installed Ollama models by running `ollama list`."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True, encoding='utf-8')
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1: return []
        model_names = [line.split()[0] for line in lines[1:]]
        return model_names
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []

def process_document(params: dict) -> str:
    """
    Main workflow router. Processes document for Summarization or Q&A based on user input.
    """
    try:
        update_status = params["update_status"]
        file_path = params["file_path"]
        model = params["model"]
        question = params["question_str"]
        
        update_status("Step 1/3: Parsing document...")
        full_text = extract_text(file_path)
        if not full_text or len(full_text.strip()) < 50:
             raise ValueError("Document empty or unreadable. For scanned PDFs, ensure Tesseract is installed.")
        
        update_status("Step 2/3: Communicating with local LLM...")
        
        # --- THIS IS THE CORRECTED LOGIC ---
        # Decide mode based on whether a question was asked.
        if question and question.strip():
            # --- Q&A Logic ---
            answer = call_ollama_qna(full_text, model, question)
            update_status("Step 3/3: Formatting answer...")
            return f"QUESTION: {question}\n\n------------------------------------\n\nANSWER:\n{answer}"
        else:
            # --- Summarization Logic ---
            source_word_count = len(full_text.split())
            try:
                length_percentage_str = params["length_str"]
                length_percentage = float(length_percentage_str) / 100 if length_percentage_str else 0.2
                if not (0.01 <= length_percentage <= 1.0): length_percentage = 0.2
                target_word_count = int(source_word_count * length_percentage)
            except (ValueError, TypeError):
                target_word_count = int(source_word_count * 0.2)
            
            keywords_str = params["keywords_str"]
            keywords = [keyword.strip() for keyword in keywords_str.split(',') if keyword.strip()] if keywords_str else []
            
            raw_output = call_ollama_summarize(full_text, model, target_word_count, keywords)
            
            update_status("Step 3/3: Formatting summary...")
            parsed_data = parse_structured_summary(raw_output)
            final_formatted_output = (
                f"TITLE: {parsed_data.get('title', 'N/A')}\n\n"
                f"TL;DR: {parsed_data.get('tldr', 'N/A')}\n\n"
                f"------------------------------------\n\n"
                f"SUMMARY:\n{parsed_data.get('summary', 'N/A')}"
            )
            return final_formatted_output
        
    except Exception as e:
        raise e