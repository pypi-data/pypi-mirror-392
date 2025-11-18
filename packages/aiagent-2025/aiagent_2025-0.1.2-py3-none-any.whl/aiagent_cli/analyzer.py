"""
Codebase analysis using Databricks AI.

Analyzes project structure and code to build a comprehensive understanding
of the codebase with parallel processing, caching, and smart prioritization.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console

from .databricks import DatabricksClient
from .scanner import get_file_tree, get_prioritized_files
from .cache import AnalysisCache
from .chunking import chunk_file_content, get_file_summary
from .project_brief import load_project_brief, format_brief_for_ai

console = Console()

# Anti-hallucination grounding instructions
GROUNDING_INSTRUCTIONS = """
CRITICAL ANTI-HALLUCINATION INSTRUCTIONS:
- ONLY mention technologies, frameworks, and tools that are explicitly present in the provided code or files
- DO NOT assume orchestration tools (Apache Airflow, Databricks Workflows, schedulers, etc.) unless they explicitly appear in imports, code, or configuration files
- DO NOT invent implementation details, deployment strategies, or infrastructure components not visible in the source code
- If a technical aspect is not evident from the provided information, state "Not visible in the provided codebase" rather than making assumptions
- Stick strictly to what can be directly observed and inferred from the actual code structure, imports, and dependencies
- When describing architecture, only include components that are actually implemented in the code
"""

# Document completion footer
COMPLETION_FOOTER = """
---

**Document completed by AI Agent CLI developed by Hossam. Thank you for using it!**
"""


def chunk_files(files: List[Dict[str, Any]], max_chunk_size: int = 50) -> List[List[Dict[str, Any]]]:
    """
    Split files into chunks for processing.

    Args:
        files: List of file dictionaries
        max_chunk_size: Maximum number of files per chunk

    Returns:
        List of file chunks
    """
    chunks = []
    for i in range(0, len(files), max_chunk_size):
        chunks.append(files[i:i + max_chunk_size])
    return chunks


def read_file_content(file_path: str, max_lines: int = 500) -> str:
    """
    Read file content with truncation for large files.

    Args:
        file_path: Path to the file
        max_lines: Maximum number of lines to read

    Returns:
        File content (potentially truncated)
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[:max_lines]
            content = "".join(lines)
            if len(lines) == max_lines:
                content += "\n... (file truncated) ..."
            return content
    except Exception as e:
        return f"[Error reading file: {str(e)}]"


def analyze_single_file(
    file_info: Dict[str, Any],
    client: DatabricksClient,
    cache: Optional[AnalysisCache] = None,
    use_semantic_chunking: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Analyze a single file with optional caching and semantic chunking.

    Args:
        file_info: File information dictionary
        client: Databricks AI client
        cache: Optional analysis cache
        use_semantic_chunking: Whether to use AST-based chunking

    Returns:
        Analysis result or None if analysis fails
    """
    file_path = file_info["absolute_path"]

    # Check cache first
    if cache:
        cached_result = cache.get_cached_analysis(file_info)
        if cached_result:
            return {
                "file": file_info["path"],
                "analysis": cached_result,
                "from_cache": True,
            }

    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return None

    # Use semantic chunking if enabled
    if use_semantic_chunking:
        chunks = chunk_file_content(file_path, content, max_chunk_size=150)

        # Create summary of file structure
        summary = get_file_summary(chunks)

        # Analyze top chunks (focus on important parts)
        top_chunks = chunks[:5]  # Analyze first 5 chunks in detail
        chunk_contents = "\n\n---\n\n".join([
            f"### {chunk['name']} (lines {chunk['start_line']}-{chunk['end_line']})\n{chunk['content'][:1000]}"
            for chunk in top_chunks
        ])

        analysis_prompt = f"""Analyze this file briefly:

File: {file_info['path']}
Structure:
{summary}

Key sections:
{chunk_contents}

Provide a brief analysis covering:
1. Purpose of this file
2. Key functions/classes
3. Dependencies and imports
4. Role in the larger system
"""
    else:
        # Fallback to simple truncation
        truncated_content = content[:2000]
        analysis_prompt = f"""Analyze this file briefly:

File: {file_info['path']}

Content (first 2000 chars):
{truncated_content}

Provide a brief analysis of purpose and key components.
"""

    try:
        # Use 750 tokens for brief file analysis
        analysis = client.chat(
            system_prompt=f"You are a code analyst. Provide concise, insightful file analysis.\n\n{GROUNDING_INSTRUCTIONS}",
            user_message=analysis_prompt,
            max_tokens=750,
            temperature=0.3,
        )

        # Cache the result
        if cache and analysis:
            cache.store_analysis(file_info, analysis)

        return {
            "file": file_info["path"],
            "analysis": analysis,
            "from_cache": False,
        }
    except Exception:
        return None


def analyze_files_parallel(
    files: List[Dict[str, Any]],
    client: DatabricksClient,
    cache: Optional[AnalysisCache] = None,
    max_workers: int = 4,
) -> List[Dict[str, Any]]:
    """
    Analyze multiple files in parallel with progress tracking.

    Args:
        files: List of file information dictionaries
        client: Databricks AI client
        cache: Optional analysis cache
        max_workers: Maximum number of parallel workers

    Returns:
        List of analysis results
    """
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        transient=False,
    ) as progress:
        task = progress.add_task(
            f"Analyzing {len(files)} files in parallel...",
            total=len(files)
        )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(analyze_single_file, file_info, client, cache): file_info
                for file_info in files
            }

            # Collect results as they complete
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    results.append(result)
                progress.update(task, advance=1)

    # Show cache stats if available
    if cache:
        stats = cache.get_cache_stats()
        console.print(f"[dim]Cache: {stats['cached_files']} files cached[/dim]")

    return results


def analyze_codebase(
    files: List[Dict[str, Any]],
    project_path: Path,
    model: str,
    enable_caching: bool = True,
    enable_parallel: bool = True,
) -> str:
    """
    Analyze the codebase and generate a knowledge document.

    Uses smart prioritization, parallel processing, caching, and semantic chunking
    for efficient analysis of large codebases.

    Args:
        files: List of file dictionaries from scanner
        project_path: Root directory of the project
        model: Databricks model to use for analysis
        enable_caching: Enable SQLite caching for incremental analysis
        enable_parallel: Enable parallel file processing

    Returns:
        Markdown content for the knowledge file
    """
    client = DatabricksClient(model=model)

    # Initialize cache if enabled
    cache = AnalysisCache(project_path) if enable_caching else None

    # Load project brief if available
    project_brief = load_project_brief(project_path)
    brief_context = format_brief_for_ai(project_brief)

    # Show brief status
    if project_brief:
        console.print(f"[green]📋 Using project brief for context-aware analysis[/green]")
    else:
        console.print(f"[dim]💡 Tip: Run 'aiagent project-brief' to provide project context for better analysis[/dim]")

    # Get project tree
    file_tree = get_file_tree(project_path)

    # Use smart file prioritization
    prioritized_files = get_prioritized_files(
        files,
        max_entry_points=10,
        max_config=20,
        max_source=100,
        include_tests=False,  # Skip test files for main analysis
    )

    console.print(f"[cyan]📊 Smart prioritization:[/cyan]")
    console.print(f"  • Total files scanned: {len(files)}")
    console.print(f"  • Prioritized for analysis: {len(prioritized_files)}")

    entry_points = [f for f in prioritized_files if f["priority"] == 0]
    if entry_points:
        console.print(f"  • Entry points found: {len(entry_points)}")
        for ep in entry_points[:3]:
            console.print(f"    - {ep['path']}")

    # Prepare file list summary (showing priority levels)
    file_summary = "\n".join([
        f"- {f['path']} ({f['size']} bytes, priority: {f['priority']})"
        for f in prioritized_files[:50]  # Show top 50
    ])

    if len(prioritized_files) > 50:
        file_summary += f"\n... and {len(prioritized_files) - 50} more files"

    # Initial structural analysis
    system_prompt = f"""You are an expert software architect and code analyst. Your task is to analyze a codebase and create a comprehensive understanding document.

Focus on:
1. Overall project structure and organization
2. Key architectural patterns and design decisions
3. Main components, modules, and their responsibilities
4. Technology stack and frameworks used
5. Data flow and component interactions
6. Dependencies and integrations

Create a well-structured Markdown document that captures the essence of this codebase.

{GROUNDING_INSTRUCTIONS}"""

    user_message = f"""Analyze this codebase and create a comprehensive knowledge document.
{brief_context}
## Project Information
- Name: {project_path.name}
- Total Files: {len(files)}
- Analyzed Files: {len(prioritized_files)}
- Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## File Tree
```
{file_tree}
```

## Prioritized Files
{file_summary}

Please provide a comprehensive analysis covering:
1. **Project Overview**: What is this project? What does it do?
2. **Architecture**: Overall architectural pattern and design
3. **Technology Stack**: Languages, frameworks, tools used
4. **Key Components**: Main modules/components and their roles
5. **Data Models**: Important data structures and entities
6. **Dependencies**: External libraries and integrations
7. **File Organization**: How the code is organized

Generate a well-structured Markdown document."""

    # Get initial structural analysis with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("🔍 Performing structural analysis...", total=None)

        initial_analysis, init_continuations = client.chat_with_continuation(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.3,
            max_continuations=5,
        )

    if init_continuations > 0:
        console.print(f"[dim]Initial analysis generated with {init_continuations} continuation(s)[/dim]")

    # Deep dive with parallel file analysis
    if enable_parallel and len(prioritized_files) > 5:
        # Parallel analysis for larger codebases
        console.print(f"[cyan]🚀 Analyzing files in detail (parallel mode)...[/cyan]")
        file_analyses = analyze_files_parallel(
            prioritized_files[:50],  # Analyze top 50 files in detail
            client,
            cache,
            max_workers=4,
        )
    else:
        # Sequential analysis for smaller codebases
        console.print(f"[cyan]🚀 Analyzing {min(len(prioritized_files), 20)} files in detail...[/cyan]")
        file_analyses = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Processing {min(len(prioritized_files), 20)} files...",
                total=None
            )
            for file_info in prioritized_files[:20]:
                result = analyze_single_file(file_info, client, cache)
                if result:
                    file_analyses.append(result)

    # Combine file analyses
    detailed_insights = "\n\n".join([
        f"### {result['file']}\n{result['analysis']}"
        for result in file_analyses[:15]  # Include top 15 in synthesis
    ])

    # Synthesize final analysis with progress indicator
    synthesis_message = f"""Based on the initial analysis, here are detailed insights from key files:

{detailed_insights}

Please enhance the previous analysis with these specific insights. Focus on:
- Implementation patterns discovered in the code
- Specific architectural decisions visible in entry points
- Data flow between components
- Integration points and dependencies
- Any notable design patterns or practices

Maintain the same structure but enrich with concrete details."""

    # Synthesize with continuation support using a workaround
    # (multi_turn_chat_with_continuation would need separate implementation)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("🧠 Synthesizing comprehensive analysis...", total=None)

        # For synthesis, use regular multi_turn for now with increased tokens via model default
        final_analysis = client.multi_turn_chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": initial_analysis},
                {"role": "user", "content": synthesis_message},
            ],
            temperature=0.3,
        )

    # Format the final knowledge document
    knowledge_doc = f"""# Codebase Knowledge: {project_path.name}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Created by:** AI Agent CLI developed by Hossam
**Files Analyzed:** {len(files)}

---

{final_analysis}

---

## File Inventory

Total files: {len(files)}

### File Tree
```
{file_tree}
```

### Files by Type
"""

    # Group files by extension
    files_by_type: Dict[str, List[str]] = {}
    for f in files:
        ext = f["extension"] or "no-extension"
        if ext not in files_by_type:
            files_by_type[ext] = []
        files_by_type[ext].append(f["path"])

    for ext, paths in sorted(files_by_type.items()):
        knowledge_doc += f"\n#### {ext} ({len(paths)} files)\n"
        for path in sorted(paths)[:20]:  # Show first 20 of each type
            knowledge_doc += f"- {path}\n"
        if len(paths) > 20:
            knowledge_doc += f"- ... and {len(paths) - 20} more\n"

    # Add completion footer
    knowledge_doc += COMPLETION_FOOTER

    return knowledge_doc
