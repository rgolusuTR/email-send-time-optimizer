"""
File handler module for extracting text from various document formats.
"""

import docx
import PyPDF2
import io
import streamlit as st


def extract_text_from_file(uploaded_file):
    """
    Extract text from various file formats.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Extracted text content
        
    Raises:
        ValueError: If file type is not supported
    """
    try:
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        if file_type == 'txt':
            # Handle text files with different encodings
            try:
                return uploaded_file.getvalue().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return uploaded_file.getvalue().decode('latin-1')
                except UnicodeDecodeError:
                    return uploaded_file.getvalue().decode('cp1252')
        
        elif file_type == 'docx':
            # Handle Word documents
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            text_content = []
            for para in doc.paragraphs:
                if para.text.strip():  # Only add non-empty paragraphs
                    text_content.append(para.text)
            return '\n'.join(text_content)
        
        elif file_type == 'pdf':
            # Handle PDF documents
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text_content = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content.append(page_text)
            return '\n'.join(text_content)
        
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        return ""


def normalize_text(text):
    """
    Minimal text normalization that preserves whitespace differences.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Minimally normalized text
    """
    if not text:
        return ""
    
    # Only normalize line endings, preserve all other whitespace
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text


def get_file_info(uploaded_file):
    """
    Get basic information about the uploaded file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        dict: File information
    """
    if uploaded_file is None:
        return None
    
    return {
        'name': uploaded_file.name,
        'size': uploaded_file.size,
        'type': uploaded_file.type,
        'extension': uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else 'unknown'
    }
