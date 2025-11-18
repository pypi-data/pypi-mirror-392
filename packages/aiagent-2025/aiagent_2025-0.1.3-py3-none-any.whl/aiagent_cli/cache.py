"""
Analysis caching using SQLite for incremental analysis.

Stores file analysis results and metadata to avoid re-analyzing unchanged files.
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class AnalysisCache:
    """SQLite-based cache for file analysis results."""

    def __init__(self, project_path: Path):
        """
        Initialize the analysis cache.

        Args:
            project_path: Root directory of the project
        """
        self.project_path = project_path
        self.cache_dir = project_path / ".aiagent"
        self.cache_dir.mkdir(exist_ok=True)
        self.db_path = self.cache_dir / "analysis_cache.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_analysis (
                file_path TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                last_modified REAL NOT NULL,
                analysis_data TEXT NOT NULL,
                analyzed_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def _get_file_hash(self, file_path: str) -> str:
        """
        Calculate hash of file content.

        Args:
            file_path: Path to the file

        Returns:
            SHA256 hash of file content
        """
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def get_cached_analysis(self, file_info: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve cached analysis for a file if it exists and is up-to-date.

        Args:
            file_info: File information dictionary with 'absolute_path' and 'size'

        Returns:
            Cached analysis text or None if cache miss
        """
        file_path = file_info["absolute_path"]

        try:
            # Check file modification time
            current_mtime = Path(file_path).stat().st_mtime
        except Exception:
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT content_hash, last_modified, analysis_data FROM file_analysis WHERE file_path = ?",
            (file_path,)
        )

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        cached_hash, cached_mtime, analysis_data = result

        # Check if file has been modified
        if current_mtime > cached_mtime:
            # File modified, verify with content hash
            current_hash = self._get_file_hash(file_path)
            if current_hash != cached_hash:
                return None  # Content changed

        return analysis_data

    def store_analysis(self, file_info: Dict[str, Any], analysis: str) -> None:
        """
        Store analysis result in cache.

        Args:
            file_info: File information dictionary
            analysis: Analysis text to cache
        """
        file_path = file_info["absolute_path"]

        try:
            mtime = Path(file_path).stat().st_mtime
            content_hash = self._get_file_hash(file_path)
        except Exception:
            return  # Skip caching if we can't access file

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO file_analysis
            (file_path, content_hash, last_modified, analysis_data, analyzed_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            file_path,
            content_hash,
            mtime,
            analysis,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM file_analysis")
        total_files = cursor.fetchone()[0]

        cursor.execute("""
            SELECT SUM(LENGTH(analysis_data)) FROM file_analysis
        """)
        total_size = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "cached_files": total_files,
            "total_size_bytes": total_size,
            "database_path": str(self.db_path),
        }

    def clear_cache(self) -> None:
        """Clear all cached analysis data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM file_analysis")
        conn.commit()
        conn.close()

    def get_metadata(self, key: str) -> Optional[str]:
        """
        Retrieve metadata value.

        Args:
            key: Metadata key

        Returns:
            Metadata value or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT value FROM project_metadata WHERE key = ?",
            (key,)
        )

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    def set_metadata(self, key: str, value: str) -> None:
        """
        Store metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO project_metadata (key, value)
            VALUES (?, ?)
        """, (key, value))

        conn.commit()
        conn.close()
