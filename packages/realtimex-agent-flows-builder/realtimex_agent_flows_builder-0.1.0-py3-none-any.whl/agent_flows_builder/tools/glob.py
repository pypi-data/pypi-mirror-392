"""Glob tool for file pattern matching."""

import glob as python_glob
import os

from langchain_core.tools import tool


@tool
def glob(pattern: str, path: str | None = None) -> list[str]:
    """Fast file pattern matching tool that works with any codebase size.

    Args:
        pattern: The glob pattern to match files against (e.g., "**/*.js", "src/**/*.ts")
        path: The directory to search in. If not specified, uses current working directory.

    Returns:
        List of matching file paths sorted by modification time

    Usage:
        - Supports glob patterns like "**/*.js" or "src/**/*.ts"
        - Returns matching file paths sorted by modification time
        - Use this tool when you need to find files by name patterns
        - When you are doing an open ended search that may require multiple rounds of
          globbing and grepping, use the Agent tool instead
        - You have the capability to call multiple tools in a single response. It is
          always better to speculatively perform multiple searches as a batch that are
          potentially useful.
    """
    # Set search directory
    search_dir = path if path else os.getcwd()

    # Ensure the directory exists
    if not os.path.exists(search_dir):
        return [f"Error: Directory '{search_dir}' not found"]

    # Change to search directory for glob operation
    original_dir = os.getcwd()
    try:
        os.chdir(search_dir)

        # Use glob to find matching files
        matches = python_glob.glob(pattern, recursive=True)

        # Convert to absolute paths and filter out directories
        absolute_matches = []
        for match in matches:
            abs_path = os.path.abspath(match)
            if os.path.isfile(abs_path):
                absolute_matches.append(abs_path)

        # Sort by modification time (most recent first)
        try:
            absolute_matches.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        except OSError:
            # If we can't get modification time, just sort alphabetically
            absolute_matches.sort()

        return absolute_matches

    except Exception as e:
        return [f"Error: {str(e)}"]
    finally:
        # Always restore original directory
        os.chdir(original_dir)
