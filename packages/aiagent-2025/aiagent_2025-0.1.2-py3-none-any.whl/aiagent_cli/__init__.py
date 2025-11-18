"""
AI Agent CLI - An AI-powered CLI tool for codebase analysis and documentation generation.

Inspired by GitHub spec-kit, this tool integrates with Databricks AI models to understand
projects and generate comprehensive technical and business documentation.
"""

__version__ = "0.1.2"
__author__ = "AI Agent CLI Team"

from .main import cli

__all__ = ["cli"]
