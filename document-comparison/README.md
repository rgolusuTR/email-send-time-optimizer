# Document Comparison Tool

A powerful web application built with Python and Streamlit that allows users to compare two documents or text inputs and highlights differences with advanced color coding.

## Features

- **Multiple Input Methods**:

  - File upload for documents (TXT, DOCX, PDF)
  - Direct text input via text areas

- **Advanced Comparison Views**:

  - **Unified Diff**: Traditional diff format with line-by-line comparison
  - **Side-by-Side**: Visual side-by-side comparison with character-level highlighting
  - **Context Diff**: Context-based diff showing surrounding lines

- **Color-Coded Highlighting**:

  - 🟢 **Green**: Added content
  - 🔴 **Red**: Removed content
  - 🟡 **Yellow**: Modified content
  - 🔵 **Blue**: Context lines

- **File Support**:

  - Text files (.txt)
  - Word documents (.docx)
  - PDF files (.pdf)

- **User-Friendly Interface**:
  - Clean, modern design
  - Responsive layout
  - Real-time statistics
  - Interactive sidebar settings

## Installation

1. **Clone or download the project**:

   ```bash
   cd document-comparison
   ```

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:

   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to the URL shown in the terminal (typically `http://localhost:8501`)

3. **Choose your comparison method**:

   - **File Comparison**: Upload two documents to compare
   - **Text Comparison**: Paste or type text directly into the text areas

4. **Select comparison view** from the sidebar:

   - Unified Diff for traditional diff format
   - Side-by-Side for visual comparison
   - Context Diff for context-aware comparison

5. **Click the Compare button** to see the results with color-coded differences

## Project Structure

```
document-comparison/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── utils/
    ├── __init__.py       # Package initialization
    ├── file_handler.py   # File processing utilities
    └── text_comparer.py  # Text comparison and highlighting
```

## Dependencies

- **streamlit**: Web application framework
- **python-docx**: Word document processing
- **PyPDF2**: PDF text extraction
- **pandas**: Data manipulation (used by Streamlit)

## How It Works

1. **File Processing**: The application extracts text from various file formats using specialized libraries
2. **Text Normalization**: Texts are normalized for consistent comparison (line endings, whitespace)
3. **Comparison Algorithm**: Uses Python's `difflib` library for robust text comparison
4. **HTML Generation**: Generates styled HTML with color-coded differences
5. **Display**: Renders the results in the Streamlit interface

## Features in Detail

### File Upload

- Supports multiple file formats
- Shows file information (name, size, type)
- Handles encoding issues gracefully

### Text Comparison

- Line-by-line comparison
- Character-level highlighting for modified lines
- Multiple diff formats for different use cases

### Visual Design

- Modern, responsive interface
- Color-coded differences for easy identification
- Statistics and file information display
- Customizable comparison views

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed

   ```bash
   pip install -r requirements.txt
   ```

2. **File Reading Errors**: Ensure uploaded files are not corrupted and are in supported formats

3. **Memory Issues**: For very large documents, consider breaking them into smaller sections

### Supported File Types

- **.txt**: Plain text files with various encodings
- **.docx**: Microsoft Word documents (not .doc)
- **.pdf**: PDF files with extractable text

## Contributing

Feel free to contribute to this project by:

- Reporting bugs
- Suggesting new features
- Submitting pull requests
- Improving documentation

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses Python's `difflib` for text comparison
- File processing with `python-docx` and `PyPDF2`
