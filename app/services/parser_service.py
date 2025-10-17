import fitz  # PyMuPDF
from fastapi import UploadFile

async def parse_resume(file: UploadFile) -> str:
    """
    Asynchronously parses the content of an uploaded resume file (PDF) into raw text.
    """
    try:
        # Read the file content into memory
        file_content = await file.read()
        
        # Open the PDF from the byte stream
        with fitz.open(stream=file_content, filetype="pdf") as doc:
            text = "".join(page.get_text() for page in doc)
        
        return text
    except Exception as e:
        # In a real app, you'd want more sophisticated logging here
        print(f"Error parsing PDF {file.filename}: {e}")
        return "" # Return empty string on failure
