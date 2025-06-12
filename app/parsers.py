# app/parsers.py
"""
Contains functions for parsing text from various file formats (.txt, .docx, .pdf).
Includes OCR fallback for PDFs.
"""
import docx
import fitz # PyMuPDF
from .ocr import run_ocr, is_tesseract_available

def extract_text(file_path: str) -> str:
    """
    Extracts text from a given file path based on its extension.
    """
    try:
        if file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        elif file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif file_path.endswith(".pdf"):
            text = ""
            with fitz.open(file_path) as doc:
                text = "".join(page.get_text() for page in doc).strip()
            
            # If PDF text is minimal, it might be image-based. Fallback to OCR if possible.
            if len(text) < 100 and is_tesseract_available():
                return run_ocr(file_path)
            return text
        else:
            raise ValueError(f"Unsupported file type: {file_path.split('.')[-1]}")
    except Exception as e:
        raise IOError(f"Failed to read or parse file: {e}")