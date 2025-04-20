import fitz 
import tiktoken

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with fitz.open(pdf_path) as doc:
            text = " ".join(page.get_text() for page in doc)
        encoding = tiktoken.get_encoding("cl100k_base")
        return text, len(encoding.encode(text))
    except Exception as e:
        return None, f"Error extracting text: {str(e)}"