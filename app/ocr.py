# app/ocr.py
"""
Handles Optical Character Recognition (OCR) functionality using Tesseract.
"""
import pytesseract
import fitz # PyMuPDF
from PIL import Image
import io
import shutil

def is_tesseract_available() -> bool:
    """Check if Tesseract executable is in the system's PATH."""
    return shutil.which('tesseract') is not None

def run_ocr(file_path: str) -> str:
    """
    Performs OCR on a PDF file, converting its pages to images and extracting text.
    """
    if not is_tesseract_available():
        # This check is defensive; the GUI should prevent calling this if Tesseract is not found.
        raise RuntimeError("Tesseract is not installed or not in PATH.")
    
    full_text = []
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Use a higher DPI for better OCR accuracy on small text
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(image)
            full_text.append(text)
    return "\n".join(full_text)