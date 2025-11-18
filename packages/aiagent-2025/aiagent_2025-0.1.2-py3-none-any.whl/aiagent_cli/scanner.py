"""
Project file scanner with .gitignore support.

Scans project directories and identifies relevant source files while
respecting .gitignore patterns.
"""

import pathspec
from pathlib import Path
from typing import List, Set, Dict, Any


# File extensions to include in scanning
SUPPORTED_EXTENSIONS = {
    # Programming languages
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".kt", ".scala",
    ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
    ".rb", ".php", ".swift",
    ".cs", ".vb",
    # Web
    ".html", ".css", ".scss", ".sass", ".less",
    ".vue", ".svelte",
    # Configuration & Data
    ".json", ".yaml", ".yml", ".toml", ".xml", ".ini", ".cfg",
    # Documentation
    ".md", ".rst", ".txt",
    # Database & Query
    ".sql",
    # Shell
    ".sh", ".bash", ".zsh",
    # Other
    ".env.example", ".env.template",
}

# Directories to always exclude
EXCLUDED_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "bower_components",
    "venv", "env", ".env", "virtualenv", ".venv",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "build", "dist", "target", "out", "bin",
    ".idea", ".vscode", ".vs",
    "coverage", ".coverage", "htmlcov",
    ".next", ".nuxt", ".cache",
    "vendor", "packages",
}

# File patterns to always exclude
EXCLUDED_PATTERNS = {
    "*.pyc", "*.pyo", "*.pyd",
    "*.so", "*.dylib", "*.dll",
    "*.class", "*.jar", "*.war",
    "*.o", "*.a",
    "*.exe", "*.bin",
    "*.log",
    "*.lock", "package-lock.json", "yarn.lock", "poetry.lock",
    ".DS_Store", "Thumbs.db",
}

# Test file patterns to deprioritize
TEST_PATTERNS = {
    "test_", "_test.", "test.", ".test.",
    "spec_", "_spec.", ".spec.",
    "tests/", "test/", "__tests__/", "spec/", "specs/",
}

# Generated code patterns to skip
GENERATED_PATTERNS = {
    ".generated.", "_generated.", "generated/",
    ".pb.", "_pb2.", ".proto.",  # Protocol buffers
    "migrations/", "migration/",  # Database migrations
    "snapshots/", "__snapshots__/",  # Test snapshots
}

# Entry point file names (high priority)
ENTRY_POINT_NAMES = {
    "main.py", "app.py", "__main__.py", "cli.py",
    "index.js", "index.ts", "main.js", "main.ts",
    "server.py", "server.js", "server.ts",
    "app.js", "app.ts", "application.py",
    "manage.py", "wsgi.py", "asgi.py",
}

# Configuration file names (medium priority)
CONFIG_FILE_NAMES = {
    "setup.py", "pyproject.toml", "requirements.txt",
    "package.json", "tsconfig.json", "webpack.config.js",
    "Dockerfile", "docker-compose.yml",
    "Makefile", "Rakefile", "Gemfile",
    ".env.example", "config.py", "settings.py",
}

# Maximum file size to process (1MB)
MAX_FILE_SIZE = 1024 * 1024


def load_gitignore(project_path: Path) -> pathspec.PathSpec:
    """
    Load and parse .gitignore file if it exists.

    Args:
        project_path: Root directory of the project

    Returns:
        PathSpec object for matching .gitignore patterns
    """
    gitignore_file = project_path / ".gitignore"
    patterns = []

    if gitignore_file.exists():
        try:
            patterns = gitignore_file.read_text().splitlines()
        except Exception:
            pass  # If we can't read .gitignore, continue without it

    # Add our default exclusions
    patterns.extend([f"/{d}/" for d in EXCLUDED_DIRS])
    patterns.extend(EXCLUDED_PATTERNS)

    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


def is_test_file(file_path: Path) -> bool:
    """
    Check if a file is a test file.

    Args:
        file_path: Path to the file

    Returns:
        True if file appears to be a test file
    """
    path_str = str(file_path).lower()
    filename = file_path.name.lower()

    for pattern in TEST_PATTERNS:
        if pattern.endswith('/'):
            if f"/{pattern}" in f"/{path_str}/":
                return True
        elif filename.startswith(pattern) or pattern in filename:
            return True

    return False


def is_generated_file(file_path: Path) -> bool:
    """
    Check if a file is generated code.

    Args:
        file_path: Path to the file

    Returns:
        True if file appears to be generated
    """
    path_str = str(file_path).lower()
    filename = file_path.name.lower()

    for pattern in GENERATED_PATTERNS:
        if pattern.endswith('/'):
            if f"/{pattern}" in f"/{path_str}/":
                return True
        elif pattern in filename or pattern in path_str:
            return True

    return False


def get_file_priority(file_path: Path) -> int:
    """
    Determine file priority for analysis.

    Priority levels:
    - 0: Entry points (main.py, app.py, index.js, etc.)
    - 1: Configuration files (setup.py, package.json, etc.)
    - 2: Regular source files
    - 3: Test files (lower priority)
    - 4: Documentation files (lowest priority)

    Args:
        file_path: Path to the file

    Returns:
        Priority level (lower number = higher priority)
    """
    filename = file_path.name.lower()

    # Entry points - highest priority
    if filename in ENTRY_POINT_NAMES or file_path.name in ENTRY_POINT_NAMES:
        return 0

    # Configuration files - high priority
    if filename in CONFIG_FILE_NAMES or file_path.name in CONFIG_FILE_NAMES:
        return 1

    # Test files - lower priority
    if is_test_file(file_path):
        return 3

    # Documentation files - lowest priority
    if file_path.suffix.lower() in {".md", ".rst", ".txt"}:
        return 4

    # Regular source files - normal priority
    return 2


def should_include_file(file_path: Path, project_path: Path) -> bool:
    """
    Determine if a file should be included in the scan.

    Args:
        file_path: Path to the file
        project_path: Root directory of the project

    Returns:
        True if file should be included, False otherwise
    """
    # Skip generated files
    if is_generated_file(file_path):
        return False

    # Check file extension
    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        # Special case for files without extensions that might be important
        if file_path.name not in ["Dockerfile", "Makefile", "Rakefile", "Gemfile"]:
            return False

    # Check file size
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return False
    except Exception:
        return False

    return True


def scan_project(project_path: Path) -> List[Dict[str, Any]]:
    """
    Scan project directory and collect relevant files.

    Args:
        project_path: Root directory of the project to scan

    Returns:
        List of dictionaries containing file information:
        - path: Relative path from project root
        - absolute_path: Absolute path to the file
        - size: File size in bytes
        - extension: File extension
    """
    gitignore_spec = load_gitignore(project_path)
    files = []
    scanned_dirs: Set[Path] = set()

    for item in project_path.rglob("*"):
        # Skip if not a file
        if not item.is_file():
            continue

        # Check if any parent directory is in excluded list
        skip = False
        for parent in item.parents:
            if parent == project_path:
                break
            if parent.name in EXCLUDED_DIRS:
                skip = True
                break

        if skip:
            continue

        # Check against gitignore patterns
        try:
            relative_path = item.relative_to(project_path)
            if gitignore_spec.match_file(str(relative_path)):
                continue
        except Exception:
            continue

        # Check if file should be included
        if not should_include_file(item, project_path):
            continue

        # Add file to results
        try:
            files.append({
                "path": str(relative_path),
                "absolute_path": str(item),
                "size": item.stat().st_size,
                "extension": item.suffix.lower(),
                "priority": get_file_priority(item),
                "is_test": is_test_file(item),
            })
        except Exception:
            # Skip files we can't access
            continue

    # Sort by priority first, then by path for consistent ordering
    files.sort(key=lambda f: (f["priority"], f["path"]))

    return files


def get_prioritized_files(
    files: List[Dict[str, Any]],
    max_entry_points: int = 10,
    max_config: int = 20,
    max_source: int = 100,
    include_tests: bool = False,
) -> List[Dict[str, Any]]:
    """
    Get prioritized subset of files for analysis.

    Args:
        files: List of all scanned files
        max_entry_points: Max number of entry point files to include
        max_config: Max number of configuration files to include
        max_source: Max number of regular source files to include
        include_tests: Whether to include test files

    Returns:
        Prioritized list of files for analysis
    """
    prioritized = []

    # Separate files by priority
    entry_points = [f for f in files if f["priority"] == 0]
    configs = [f for f in files if f["priority"] == 1]
    source_files = [f for f in files if f["priority"] == 2]
    tests = [f for f in files if f["priority"] == 3]

    # Add in order of priority
    prioritized.extend(entry_points[:max_entry_points])
    prioritized.extend(configs[:max_config])
    prioritized.extend(source_files[:max_source])

    if include_tests:
        # Include some tests for context, but limit them
        prioritized.extend(tests[:20])

    return prioritized


def get_file_tree(project_path: Path, max_depth: int = 3) -> str:
    """
    Generate a tree representation of the project structure.

    Args:
        project_path: Root directory of the project
        max_depth: Maximum depth to traverse

    Returns:
        String representation of the file tree
    """
    gitignore_spec = load_gitignore(project_path)
    tree_lines = [f"{project_path.name}/"]

    def build_tree(current_path: Path, prefix: str = "", depth: int = 0) -> None:
        if depth >= max_depth:
            return

        try:
            items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return

        # Filter out ignored items
        filtered_items = []
        for item in items:
            if item.name in EXCLUDED_DIRS:
                continue

            try:
                relative_path = item.relative_to(project_path)
                if gitignore_spec.match_file(str(relative_path)):
                    continue
            except Exception:
                continue

            filtered_items.append(item)

        for i, item in enumerate(filtered_items):
            is_last = i == len(filtered_items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = "    " if is_last else "│   "

            tree_lines.append(f"{prefix}{current_prefix}{item.name}{'/' if item.is_dir() else ''}")

            if item.is_dir():
                build_tree(item, prefix + next_prefix, depth + 1)

    build_tree(project_path)
    return "\n".join(tree_lines)
