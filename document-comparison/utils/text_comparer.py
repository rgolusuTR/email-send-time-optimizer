"""
Text comparison module with advanced highlighting functionality.
"""

import difflib
import html
import re
from typing import List, Tuple


def compare_texts(text1: str, text2: str, comparison_type: str = "unified") -> str:
    """
    Compare two texts and return HTML with highlighted differences.
    
    Args:
        text1 (str): First text to compare
        text2 (str): Second text to compare
        comparison_type (str): Type of comparison ('unified', 'side_by_side', 'context')
        
    Returns:
        str: HTML string with highlighted differences
    """
    if not text1 and not text2:
        return "<p>Both texts are empty.</p>"
    
    if text1 == text2:
        return "<div class='match-result'><h3>✅ Documents are identical!</h3></div>"
    
    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)
    
    if comparison_type == "side_by_side":
        return _generate_side_by_side_diff(lines1, lines2)
    elif comparison_type == "context":
        return _generate_context_diff(lines1, lines2)
    else:  # unified
        return _generate_unified_diff(lines1, lines2)


def _generate_unified_diff(lines1: List[str], lines2: List[str]) -> str:
    """Generate unified diff format with color highlighting."""
    diff = list(difflib.unified_diff(
        lines1, lines2,
        fromfile='Document 1',
        tofile='Document 2',
        lineterm='',
        n=3
    ))
    
    if not diff:
        return "<div class='match-result'><h3>✅ Documents are identical!</h3></div>"
    
    html_lines = []
    html_lines.append(_get_custom_css())
    html_lines.append("<div class='diff-container'>")
    html_lines.append("<h3>📄 Document Comparison Results</h3>")
    html_lines.append("<div class='diff-legend'>")
    html_lines.append("<span class='legend-item'><span class='legend-add'>+</span> Added lines</span>")
    html_lines.append("<span class='legend-item'><span class='legend-remove'>-</span> Removed lines</span>")
    html_lines.append("<span class='legend-item'><span class='legend-context'>@</span> Context</span>")
    html_lines.append("</div>")
    html_lines.append("<pre class='diff-content'>")
    
    for line in diff:
        escaped_line = html.escape(line)
        if line.startswith('+++') or line.startswith('---'):
            html_lines.append(f"<span class='diff-header'>{escaped_line}</span>")
        elif line.startswith('@@'):
            html_lines.append(f"<span class='diff-context'>{escaped_line}</span>")
        elif line.startswith('+'):
            html_lines.append(f"<span class='diff-add'>{escaped_line}</span>")
        elif line.startswith('-'):
            html_lines.append(f"<span class='diff-remove'>{escaped_line}</span>")
        else:
            html_lines.append(f"<span class='diff-normal'>{escaped_line}</span>")
    
    html_lines.append("</pre>")
    html_lines.append("</div>")
    
    return '\n'.join(html_lines)


def _generate_side_by_side_diff(lines1: List[str], lines2: List[str]) -> str:
    """Generate side-by-side diff with inline character highlighting."""
    html_lines = []
    html_lines.append(_get_custom_css())
    html_lines.append("<div class='diff-container'>")
    html_lines.append("<h3>📄 Side-by-Side Document Comparison</h3>")
    html_lines.append("<div class='side-by-side-container'>")
    html_lines.append("<div class='side-by-side-header'>")
    html_lines.append("<div class='left-header'>Document 1</div>")
    html_lines.append("<div class='right-header'>Document 2</div>")
    html_lines.append("</div>")
    
    # Use SequenceMatcher for more detailed comparison
    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    
    html_lines.append("<div class='side-by-side-content'>")
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for i in range(i1, i2):
                left_line = html.escape(lines1[i].rstrip('\n'))
                right_line = html.escape(lines2[j1 + (i - i1)].rstrip('\n'))
                html_lines.append(f"<div class='line-pair'>")
                html_lines.append(f"<div class='left-line normal'>{left_line}</div>")
                html_lines.append(f"<div class='right-line normal'>{right_line}</div>")
                html_lines.append(f"</div>")
        
        elif tag == 'delete':
            for i in range(i1, i2):
                left_line = html.escape(lines1[i].rstrip('\n'))
                html_lines.append(f"<div class='line-pair'>")
                html_lines.append(f"<div class='left-line removed'>{left_line}</div>")
                html_lines.append(f"<div class='right-line empty'></div>")
                html_lines.append(f"</div>")
        
        elif tag == 'insert':
            for j in range(j1, j2):
                right_line = html.escape(lines2[j].rstrip('\n'))
                html_lines.append(f"<div class='line-pair'>")
                html_lines.append(f"<div class='left-line empty'></div>")
                html_lines.append(f"<div class='right-line added'>{right_line}</div>")
                html_lines.append(f"</div>")
        
        elif tag == 'replace':
            max_lines = max(i2 - i1, j2 - j1)
            for k in range(max_lines):
                left_line = ""
                right_line = ""
                
                if k < (i2 - i1):
                    left_line = html.escape(lines1[i1 + k].rstrip('\n'))
                if k < (j2 - j1):
                    right_line = html.escape(lines2[j1 + k].rstrip('\n'))
                
                # Highlight character-level differences
                if left_line and right_line:
                    left_highlighted, right_highlighted = _highlight_char_differences(
                        lines1[i1 + k].rstrip('\n'), lines2[j1 + k].rstrip('\n')
                    )
                    html_lines.append(f"<div class='line-pair'>")
                    html_lines.append(f"<div class='left-line modified'>{left_highlighted}</div>")
                    html_lines.append(f"<div class='right-line modified'>{right_highlighted}</div>")
                    html_lines.append(f"</div>")
                else:
                    left_class = "removed" if left_line else "empty"
                    right_class = "added" if right_line else "empty"
                    html_lines.append(f"<div class='line-pair'>")
                    html_lines.append(f"<div class='left-line {left_class}'>{left_line}</div>")
                    html_lines.append(f"<div class='right-line {right_class}'>{right_line}</div>")
                    html_lines.append(f"</div>")
    
    html_lines.append("</div>")
    html_lines.append("</div>")
    html_lines.append("</div>")
    
    return '\n'.join(html_lines)


def _highlight_char_differences(text1: str, text2: str) -> Tuple[str, str]:
    """Highlight character-level differences between two strings, including whitespace."""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    
    left_result = []
    right_result = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            left_text = _make_whitespace_visible(text1[i1:i2])
            right_text = _make_whitespace_visible(text2[j1:j2])
            left_result.append(html.escape(left_text))
            right_result.append(html.escape(right_text))
        elif tag == 'delete':
            deleted_text = _make_whitespace_visible(text1[i1:i2])
            left_result.append(f"<span class='char-removed'>{html.escape(deleted_text)}</span>")
        elif tag == 'insert':
            inserted_text = _make_whitespace_visible(text2[j1:j2])
            right_result.append(f"<span class='char-added'>{html.escape(inserted_text)}</span>")
        elif tag == 'replace':
            left_text = _make_whitespace_visible(text1[i1:i2])
            right_text = _make_whitespace_visible(text2[j1:j2])
            left_result.append(f"<span class='char-modified'>{html.escape(left_text)}</span>")
            right_result.append(f"<span class='char-modified'>{html.escape(right_text)}</span>")
    
    return ''.join(left_result), ''.join(right_result)


def _make_whitespace_visible(text: str) -> str:
    """Make whitespace characters visible for better comparison."""
    # Replace different types of whitespace with visible symbols
    text = text.replace(' ', '·')  # Middle dot for spaces
    text = text.replace('\t', '→')  # Arrow for tabs
    text = text.replace('\n', '↵\n')  # Return symbol for newlines
    text = text.replace('\r', '←')  # Left arrow for carriage returns
    return text


def _generate_context_diff(lines1: List[str], lines2: List[str]) -> str:
    """Generate context diff format."""
    diff = list(difflib.context_diff(
        lines1, lines2,
        fromfile='Document 1',
        tofile='Document 2',
        lineterm='',
        n=3
    ))
    
    if not diff:
        return "<div class='match-result'><h3>✅ Documents are identical!</h3></div>"
    
    html_lines = []
    html_lines.append(_get_custom_css())
    html_lines.append("<div class='diff-container'>")
    html_lines.append("<h3>📄 Context Document Comparison</h3>")
    html_lines.append("<pre class='diff-content'>")
    
    for line in diff:
        escaped_line = html.escape(line)
        if line.startswith('***') or line.startswith('---'):
            html_lines.append(f"<span class='diff-header'>{escaped_line}</span>")
        elif line.startswith('***************'):
            html_lines.append(f"<span class='diff-separator'>{escaped_line}</span>")
        elif line.startswith('+ '):
            html_lines.append(f"<span class='diff-add'>{escaped_line}</span>")
        elif line.startswith('- '):
            html_lines.append(f"<span class='diff-remove'>{escaped_line}</span>")
        elif line.startswith('! '):
            html_lines.append(f"<span class='diff-change'>{escaped_line}</span>")
        else:
            html_lines.append(f"<span class='diff-normal'>{escaped_line}</span>")
    
    html_lines.append("</pre>")
    html_lines.append("</div>")
    
    return '\n'.join(html_lines)


def _get_custom_css() -> str:
    """Return custom CSS for diff highlighting."""
    return """
    <style>
        .diff-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 100%;
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }
        
        .diff-container h3 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 15px 20px;
            font-size: 18px;
        }
        
        .diff-legend {
            background: #f8f9fa;
            padding: 10px 20px;
            border-bottom: 1px solid #eee;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-add, .legend-remove, .legend-context {
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
            font-family: monospace;
        }
        
        .legend-add { background: #d4edda; color: #155724; }
        .legend-remove { background: #f8d7da; color: #721c24; }
        .legend-context { background: #e2e3e5; color: #383d41; }
        
        .diff-content {
            margin: 0;
            padding: 20px;
            background: #fafafa;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        
        .diff-header { color: #6f42c1; font-weight: bold; }
        .diff-context { color: #6c757d; background: #e9ecef; padding: 2px 4px; border-radius: 3px; }
        .diff-separator { color: #495057; font-weight: bold; }
        .diff-add { background: #d4edda; color: #155724; padding: 2px 0; }
        .diff-remove { background: #f8d7da; color: #721c24; padding: 2px 0; }
        .diff-change { background: #fff3cd; color: #856404; padding: 2px 0; }
        .diff-normal { color: #495057; }
        
        .match-result {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .match-result h3 {
            color: #155724;
            font-size: 24px;
            margin: 0;
        }
        
        /* Side-by-side styles */
        .side-by-side-container {
            background: white;
        }
        
        .side-by-side-header {
            display: grid;
            grid-template-columns: 1fr 1fr;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        }
        
        .left-header, .right-header {
            padding: 15px 20px;
            font-weight: bold;
            text-align: center;
            color: #495057;
        }
        
        .left-header {
            border-right: 1px solid #dee2e6;
            background: #e3f2fd;
        }
        
        .right-header {
            background: #f3e5f5;
        }
        
        .side-by-side-content {
            max-height: 600px;
            overflow-y: auto;
        }
        
        .line-pair {
            display: grid;
            grid-template-columns: 1fr 1fr;
            border-bottom: 1px solid #eee;
        }
        
        .left-line, .right-line {
            padding: 8px 15px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.4;
            white-space: pre-wrap;
            word-break: break-word;
        }
        
        .left-line {
            border-right: 1px solid #dee2e6;
        }
        
        .left-line.normal, .right-line.normal {
            background: #f8f9fa;
            color: #495057;
        }
        
        .left-line.added, .right-line.added {
            background: #d4edda;
            color: #155724;
        }
        
        .left-line.removed, .right-line.removed {
            background: #f8d7da;
            color: #721c24;
        }
        
        .left-line.modified, .right-line.modified {
            background: #fff3cd;
            color: #856404;
        }
        
        .left-line.empty, .right-line.empty {
            background: #e9ecef;
            color: #6c757d;
            font-style: italic;
        }
        
        .char-added {
            background: #28a745;
            color: white;
            padding: 1px 2px;
            border-radius: 2px;
        }
        
        .char-removed {
            background: #dc3545;
            color: white;
            padding: 1px 2px;
            border-radius: 2px;
        }
        
        .char-modified {
            background: #ffc107;
            color: #212529;
            padding: 1px 2px;
            border-radius: 2px;
        }
    </style>
    """
