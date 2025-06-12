# app/ollama_client.py
"""
Manages communication with the local Ollama API server.
"""
import requests
import json

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def _call_ollama(payload: dict) -> str:
    """Helper function to make the API call and handle errors."""
    try:
        response = requests.post(
            OLLAMA_ENDPOINT,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=600  # 10 minute timeout
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Ollama. Is it running?")
    except requests.exceptions.RequestException as e:
        raise IOError(f"An API error occurred: {e}")

def call_ollama_summarize(text: str, model: str, target_word_count: int, keywords: list) -> str:
    """Sends text to Ollama for summarization using a specified model and advanced prompt."""
    keyword_instruction = f"The SUMMARY must pay special attention to the context surrounding these keywords: {', '.join(keywords)}." if keywords else "Create a general summary."

    prompt = f"""
    You are an expert research assistant. Your task is to analyze the following document and generate a structured summary based on several rules. Your response MUST strictly follow the specified format.

    **Rules:**
    1.  **Structure:** Your entire response must be in the following format, with each part clearly labeled on a new line:
        TITLE: [A concise, descriptive title for the document]
        TLDR: [A one or two-sentence "Too Long; Didn't Read" summary]
        SUMMARY: [The main, detailed summary]
    2.  **Length:** The main SUMMARY section must be approximately {target_word_count} words long.
    3.  **Keyword Focus:** {keyword_instruction}

    Do not add any conversational fluff or introductions outside of this structure.

    **Document to Analyze:**
    ---
    {text}
    ---
    """
    payload = {"model": model, "prompt": prompt, "stream": False}
    return _call_ollama(payload)

def call_ollama_qna(text: str, model: str, question: str) -> str:
    """Sends text and a question to Ollama for a specific answer."""
    prompt = f"""
    You are an expert research assistant. Your task is to answer the user's question based *only* on the information provided in the document below.
    If the answer is not contained within the document, you must state: "The answer to this question could not be found in the provided document."
    Do not use any external knowledge.

    **User's Question:**
    {question}

    **Document to Analyze:**
    ---
    {text}
    ---
    """
    payload = {"model": model, "prompt": prompt, "stream": False}
    return _call_ollama(payload)