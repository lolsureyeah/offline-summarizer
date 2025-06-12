# app/ollama_client.py
"""
Manages communication with the local Ollama API server.
"""
import requests
import json

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def call_ollama_summarize(text: str, model: str) -> str:
    """
    Sends text to the Ollama API for summarization using a specified model.
    """
    prompt = f"""
    Based on the following document, provide a comprehensive and coherent summary.
    The summary should accurately reflect the key arguments, findings, and conclusions of the document.
    It should be approximately 800 to 1000 words in length. Do not add any conversational fluff or introductions like "Here is the summary".

    Document:
    {text}
    """
    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=json.dumps({"model": model, "prompt": prompt, "stream": False}),
            timeout=600 # 10 minute timeout for long documents
        )
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        return json.loads(response.text)["response"]
        
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Ollama service. Please ensure Ollama is running.")
    except requests.exceptions.RequestException as e:
        raise IOError(f"An API error occurred: {e}")