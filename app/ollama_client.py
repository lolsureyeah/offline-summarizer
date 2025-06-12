# app/ollama_client.py
"""
Manages communication with the local Ollama API server.
"""
import requests
import json

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def call_ollama_summarize(text: str, model: str, target_word_count: int, keywords: list) -> str:
    """
    Sends text to the Ollama API for summarization using a specified model and advanced prompt.
    """
    # Create the keyword part of the prompt only if keywords are provided
    keyword_instruction = ""
    if keywords:
        keyword_instruction = f"3. **Keyword Focus:** The SUMMARY must pay special attention to and prioritize the context surrounding the following keywords: {', '.join(keywords)}."
    else:
        keyword_instruction = "3. **Keyword Focus:** No specific keywords provided; create a general summary."

    # The New Advanced Prompt
    prompt = f"""
    You are an expert research assistant. Your task is to analyze the following document and generate a structured summary based on several rules. Your response MUST strictly follow the specified format.

    **Rules:**
    1.  **Structure:** Your entire response must be in the following format, with each part clearly labeled on a new line:
        TITLE: [A concise, descriptive title for the document]
        TLDR: [A one or two-sentence "Too Long; Didn't Read" summary]
        SUMMARY: [The main, detailed summary]

    2.  **Length:** The main SUMMARY section must be approximately {target_word_count} words long.
    
    {keyword_instruction}

    Do not add any conversational fluff, introductions, or conclusions outside of this structure.

    **Document to Analyze:**
    ---
    {text}
    ---
    """
    
    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"model": model, "prompt": prompt, "stream": False}),
            timeout=600 # 10 minute timeout for long documents
        )
        response.raise_for_status()
        return json.loads(response.text)["response"]
        
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Ollama service. Please ensure Ollama is running.")
    except requests.exceptions.RequestException as e:
        raise IOError(f"An API error occurred: {e}")