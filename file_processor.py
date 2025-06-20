import os
from docx import Document
import PyPDF2

def extract_text(file, file_path):
    """
    Extracts text from supported file types (.txt, .docx, .pdf).
    Args:
        file: Uploaded file object from Streamlit.
        file_path: Path where the file is saved locally.
    Returns:
        Extracted text as a string.
    Raises:
        ValueError: If file type is unsupported.
    """
    file_ext = os.path.splitext(file.name)[1].lower()
    
    # Handle .txt files: Simple text reading with error handling
    if file_ext == '.txt':
        try:
            return file.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return f"Error reading TXT: {str(e)}"
    
    # Handle .docx files: Extract paragraphs using python-docx
    elif file_ext == '.docx':
        try:
            doc = Document(file_path)
            text = ' '.join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
            return text if text else "No readable content found in DOCX."
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    # Handle .pdf files: Extract text from all pages using PyPDF2
    elif file_ext == '.pdf':
        try:
            reader = PyPDF2.PdfReader(file_path)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + ' '
            return text.strip() if text.strip() else "No readable content found in PDF."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
    
    else:
        raise ValueError(f"Unsupported file type: {file_ext}. Supported types: .txt, .docx, .pdf")

def save_file(file, user_dir):
    """
    Saves an uploaded file to the user's directory.
    Args:
        file: Uploaded file object from Streamlit.
        user_dir: Directory path specific to the user (e.g., uploads/username/).
    Returns:
        Full path of the saved file.
    """
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)  # Create user-specific directory if it doesn't exist
    file_path = os.path.join(user_dir, file.name)
    try:
        with open(file_path, 'wb') as f:
            f.write(file.getbuffer())  # Write the file to disk
        return file_path
    except Exception as e:
        raise ValueError(f"Error saving file '{file.name}': {str(e)}")