"""
Utilities package for document comparison functionality.
"""

from .file_handler import extract_text_from_file, normalize_text, get_file_info
from .text_comparer import compare_texts

__all__ = [
    'extract_text_from_file',
    'normalize_text', 
    'get_file_info',
    'compare_texts'
]
