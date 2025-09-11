"""
Document Comparison Web Application using Streamlit
"""

import streamlit as st
import pandas as pd
from utils.file_handler import extract_text_from_file, normalize_text, get_file_info
from utils.text_comparer import compare_texts


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Document Comparison Tool",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f0f2f6;
            border-radius: 5px 5px 0 0;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea;
            color: white;
        }
        
        .file-info {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        
        .comparison-stats {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📄 Document Comparison Tool</h1>
        <p>Compare documents and highlight differences with advanced color coding</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        comparison_type = st.selectbox(
            "Comparison View",
            ["unified", "side_by_side", "context"],
            format_func=lambda x: {
                "unified": "📝 Unified Diff",
                "side_by_side": "↔️ Side-by-Side",
                "context": "📋 Context Diff"
            }[x]
        )
        
        st.markdown("---")
        
        st.markdown("""
        ### 🎨 Color Legend
        - 🟢 **Green**: Added content
        - 🔴 **Red**: Removed content  
        - 🟡 **Yellow**: Modified content
        - 🔵 **Blue**: Context lines
        """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 📁 Supported Formats
        - **Text files** (.txt)
        - **Word documents** (.docx)
        - **PDF files** (.pdf)
        """)
    
    # Main content tabs
    tab1, tab2 = st.tabs(["📁 File Comparison", "✏️ Text Comparison"])
    
    with tab1:
        st.header("Compare Documents")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Document 1")
            file1 = st.file_uploader(
                "Upload first document",
                type=["txt", "pdf", "docx"],
                key="file1",
                help="Select a text file, PDF, or Word document"
            )
            
            if file1:
                file_info1 = get_file_info(file1)
                st.markdown(f"""
                <div class="file-info">
                    <strong>📋 File Info:</strong><br>
                    📝 Name: {file_info1['name']}<br>
                    📏 Size: {file_info1['size']:,} bytes<br>
                    🏷️ Type: {file_info1['extension'].upper()}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("📄 Document 2")
            file2 = st.file_uploader(
                "Upload second document",
                type=["txt", "pdf", "docx"],
                key="file2",
                help="Select a text file, PDF, or Word document"
            )
            
            if file2:
                file_info2 = get_file_info(file2)
                st.markdown(f"""
                <div class="file-info">
                    <strong>📋 File Info:</strong><br>
                    📝 Name: {file_info2['name']}<br>
                    📏 Size: {file_info2['size']:,} bytes<br>
                    🏷️ Type: {file_info2['extension'].upper()}
                </div>
                """, unsafe_allow_html=True)
        
        if file1 and file2:
            if st.button("🔍 Compare Documents", type="primary", use_container_width=True):
                with st.spinner("Extracting text and comparing documents..."):
                    try:
                        # Extract text from files
                        text1 = extract_text_from_file(file1)
                        text2 = extract_text_from_file(file2)
                        
                        # Normalize texts
                        text1_normalized = normalize_text(text1)
                        text2_normalized = normalize_text(text2)
                        
                        # Display comparison statistics
                        lines1 = len(text1_normalized.splitlines())
                        lines2 = len(text2_normalized.splitlines())
                        chars1 = len(text1_normalized)
                        chars2 = len(text2_normalized)
                        
                        st.markdown(f"""
                        <div class="comparison-stats">
                            <h4>📊 Comparison Statistics</h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                                <div>
                                    <strong>Document 1:</strong><br>
                                    📏 Lines: {lines1:,}<br>
                                    🔤 Characters: {chars1:,}
                                </div>
                                <div>
                                    <strong>Document 2:</strong><br>
                                    📏 Lines: {lines2:,}<br>
                                    🔤 Characters: {chars2:,}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Perform comparison
                        diff_html = compare_texts(text1_normalized, text2_normalized, comparison_type)
                        
                        # Display results
                        st.markdown("### 🔍 Comparison Results")
                        st.markdown(diff_html, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"❌ Error during comparison: {str(e)}")
                        st.info("💡 Please ensure both files are valid and readable.")
    
    with tab2:
        st.header("Compare Text Content")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Text 1")
            text1 = st.text_area(
                "Enter or paste first text",
                height=300,
                key="text1",
                placeholder="Paste your first text here..."
            )
            
            if text1:
                lines1 = len(text1.splitlines())
                chars1 = len(text1)
                st.info(f"📏 Lines: {lines1:,} | 🔤 Characters: {chars1:,}")
        
        with col2:
            st.subheader("📝 Text 2")
            text2 = st.text_area(
                "Enter or paste second text",
                height=300,
                key="text2",
                placeholder="Paste your second text here..."
            )
            
            if text2:
                lines2 = len(text2.splitlines())
                chars2 = len(text2)
                st.info(f"📏 Lines: {lines2:,} | 🔤 Characters: {chars2:,}")
        
        if text1 and text2:
            if st.button("🔍 Compare Texts", type="primary", use_container_width=True):
                with st.spinner("Comparing texts..."):
                    try:
                        # Normalize texts
                        text1_normalized = normalize_text(text1)
                        text2_normalized = normalize_text(text2)
                        
                        # Perform comparison
                        diff_html = compare_texts(text1_normalized, text2_normalized, comparison_type)
                        
                        # Display results
                        st.markdown("### 🔍 Comparison Results")
                        st.markdown(diff_html, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"❌ Error during comparison: {str(e)}")
        
        elif not text1 and not text2:
            st.info("💡 Enter text in both fields above to start comparing.")
        elif not text1:
            st.warning("⚠️ Please enter text in the first field.")
        elif not text2:
            st.warning("⚠️ Please enter text in the second field.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>📄 Document Comparison Tool | Built with Streamlit & Python</p>
        <p>💡 Tip: Use the sidebar to change comparison view modes</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
