"""
Semantic code chunking using AST parsing and heuristics.

Chunks code by function/class boundaries instead of arbitrary line counts.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


def chunk_python_file(content: str, max_chunk_size: int = 100) -> List[Dict[str, str]]:
    """
    Chunk Python file by function and class boundaries using AST.

    Args:
        content: Python source code content
        max_chunk_size: Maximum number of lines per chunk

    Returns:
        List of chunks with metadata
    """
    chunks = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        # If we can't parse, fall back to line-based chunking
        return chunk_generic_file(content, max_chunk_size)

    lines = content.split('\n')

    # Extract top-level definitions
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                start_line = node.lineno - 1  # AST is 1-indexed
                end_line = node.end_lineno

                chunk_lines = lines[start_line:end_line]
                chunk_content = '\n'.join(chunk_lines)

                chunk_type = "class" if isinstance(node, ast.ClassDef) else "function"
                chunks.append({
                    "type": chunk_type,
                    "name": node.name,
                    "start_line": start_line + 1,
                    "end_line": end_line,
                    "content": chunk_content,
                    "line_count": len(chunk_lines),
                })

    # If no chunks found or very few, fall back to generic chunking
    if len(chunks) < 3:
        return chunk_generic_file(content, max_chunk_size)

    # Merge small consecutive chunks to reach optimal size
    merged_chunks = []
    current_chunk = None

    for chunk in chunks:
        if current_chunk is None:
            current_chunk = chunk
        elif current_chunk["line_count"] + chunk["line_count"] <= max_chunk_size:
            # Merge with current chunk
            current_chunk["content"] += "\n\n" + chunk["content"]
            current_chunk["end_line"] = chunk["end_line"]
            current_chunk["line_count"] += chunk["line_count"]
            current_chunk["name"] += f", {chunk['name']}"
        else:
            # Save current chunk and start new one
            merged_chunks.append(current_chunk)
            current_chunk = chunk

    if current_chunk:
        merged_chunks.append(current_chunk)

    return merged_chunks


def chunk_javascript_file(content: str, max_chunk_size: int = 100) -> List[Dict[str, str]]:
    """
    Chunk JavaScript/TypeScript file by function boundaries using regex.

    Args:
        content: JavaScript/TypeScript source code
        max_chunk_size: Maximum number of lines per chunk

    Returns:
        List of chunks with metadata
    """
    chunks = []
    lines = content.split('\n')

    # Regex patterns for function/class definitions
    function_patterns = [
        r'^(export\s+)?(async\s+)?function\s+(\w+)',  # function declarations
        r'^(export\s+)?class\s+(\w+)',  # class declarations
        r'^const\s+(\w+)\s*=\s*(async\s+)?\([^)]*\)\s*=>',  # arrow functions
        r'^(export\s+)?const\s+(\w+)\s*=\s*function',  # function expressions
    ]

    combined_pattern = '|'.join(function_patterns)
    compiled_pattern = re.compile(combined_pattern, re.MULTILINE)

    current_chunk = {"start": 0, "lines": [], "name": "module-start"}

    for i, line in enumerate(lines):
        match = compiled_pattern.match(line.strip())

        if match and i > 0:
            # Found a new function/class, save current chunk
            if current_chunk["lines"]:
                chunks.append({
                    "type": "block",
                    "name": current_chunk["name"],
                    "start_line": current_chunk["start"] + 1,
                    "end_line": i,
                    "content": '\n'.join(current_chunk["lines"]),
                    "line_count": len(current_chunk["lines"]),
                })

            # Start new chunk
            current_chunk = {
                "start": i,
                "lines": [line],
                "name": line.strip()[:50]  # First 50 chars as name
            }
        else:
            current_chunk["lines"].append(line)

    # Add final chunk
    if current_chunk["lines"]:
        chunks.append({
            "type": "block",
            "name": current_chunk["name"],
            "start_line": current_chunk["start"] + 1,
            "end_line": len(lines),
            "content": '\n'.join(current_chunk["lines"]),
            "line_count": len(current_chunk["lines"]),
        })

    # If chunking didn't work well, fall back to generic
    if len(chunks) < 2:
        return chunk_generic_file(content, max_chunk_size)

    return chunks


def chunk_generic_file(content: str, max_chunk_size: int = 100) -> List[Dict[str, str]]:
    """
    Chunk file by line count (fallback for unsupported languages).

    Args:
        content: File content
        max_chunk_size: Maximum number of lines per chunk

    Returns:
        List of chunks
    """
    lines = content.split('\n')
    chunks = []

    for i in range(0, len(lines), max_chunk_size):
        chunk_lines = lines[i:i + max_chunk_size]
        chunks.append({
            "type": "lines",
            "name": f"lines-{i+1}-{i+len(chunk_lines)}",
            "start_line": i + 1,
            "end_line": i + len(chunk_lines),
            "content": '\n'.join(chunk_lines),
            "line_count": len(chunk_lines),
        })

    return chunks


def chunk_file_content(
    file_path: str,
    content: str,
    max_chunk_size: int = 100
) -> List[Dict[str, str]]:
    """
    Chunk file content using appropriate strategy based on file type.

    Args:
        file_path: Path to the file (used to determine language)
        content: File content to chunk
        max_chunk_size: Maximum lines per chunk

    Returns:
        List of semantic chunks
    """
    extension = Path(file_path).suffix.lower()

    # Python files - use AST
    if extension == ".py":
        return chunk_python_file(content, max_chunk_size)

    # JavaScript/TypeScript files - use regex
    elif extension in {".js", ".ts", ".jsx", ".tsx"}:
        return chunk_javascript_file(content, max_chunk_size)

    # Other files - generic line-based chunking
    else:
        return chunk_generic_file(content, max_chunk_size)


def get_file_summary(chunks: List[Dict[str, str]]) -> str:
    """
    Generate a summary of file chunks.

    Args:
        chunks: List of file chunks

    Returns:
        Summary string
    """
    if not chunks:
        return "Empty file"

    summary_parts = []
    for chunk in chunks:
        chunk_type = chunk.get("type", "block")
        name = chunk.get("name", "unnamed")
        line_count = chunk.get("line_count", 0)

        summary_parts.append(f"  - {chunk_type}: {name} ({line_count} lines)")

    return '\n'.join(summary_parts)
