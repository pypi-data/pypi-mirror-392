"""Grep tool for searching content in files using regex."""

import glob as python_glob
import os
import re
from typing import Literal

from langchain_core.tools import tool


@tool
def grep(
    pattern: str,
    path: str | None = None,
    glob: str | None = None,
    output_mode: Literal[
        "content", "files_with_matches", "count"
    ] = "files_with_matches",
    B: int | None = None,
    A: int | None = None,
    C: int | None = None,
    n: bool = False,
    i: bool = False,
    type: str | None = None,
    head_limit: int | None = None,
    multiline: bool = False,
) -> str:
    """A powerful search tool built on ripgrep-like functionality.

    Args:
        pattern: The regular expression pattern to search for in file contents
        path: File or directory to search in. Defaults to current working directory.
        glob: Glob pattern to filter files (e.g. "*.js", "*.{ts,tsx}")
        output_mode: Output mode - "content" shows matching lines, "files_with_matches" shows file paths (default), "count" shows match counts
        B: Number of lines to show before each match (requires output_mode: "content")
        A: Number of lines to show after each match (requires output_mode: "content")
        C: Number of lines to show before and after each match (requires output_mode: "content")
        n: Show line numbers in output (requires output_mode: "content")
        i: Case insensitive search
        type: File type to search (js, py, rust, go, java, etc.)
        head_limit: Limit output to first N lines/entries
        multiline: Enable multiline mode where . matches newlines and patterns can span lines

    Returns:
        Search results formatted according to output_mode

    Usage:
        - ALWAYS use Grep for search tasks. NEVER invoke `grep` or `rg` as a Bash command.
        - Supports full regex syntax (e.g., "log.*Error", "function\\s+\\w+")
        - Filter files with glob parameter or type parameter
        - Output modes: "content" shows matching lines, "files_with_matches" shows only file paths (default), "count" shows match counts
        - Use Task tool for open-ended searches requiring multiple rounds
        - Pattern syntax: Uses Python regex - literal braces need escaping
        - Multiline matching: By default patterns match within single lines only
    """
    # Set search directory
    search_dir = path if path else os.getcwd()

    # Ensure the directory exists
    if not os.path.exists(search_dir):
        return f"Error: Path '{search_dir}' not found"

    # Get files to search
    files_to_search = []

    if os.path.isfile(search_dir):
        # Single file
        files_to_search = [search_dir]
    # Directory - get all files
    elif glob:
        # Use glob pattern
        original_dir = os.getcwd()
        try:
            os.chdir(search_dir)
            files_to_search = [
                os.path.abspath(f)
                for f in python_glob.glob(glob, recursive=True)
                if os.path.isfile(f)
            ]
        finally:
            os.chdir(original_dir)
    else:
        # Get all files recursively
        for root, dirs, files in os.walk(search_dir):
            for file in files:
                files_to_search.append(os.path.join(root, file))

    # Filter by file type if specified
    if type:
        type_extensions = {
            "js": [".js", ".jsx"],
            "ts": [".ts", ".tsx"],
            "py": [".py"],
            "rust": [".rs"],
            "go": [".go"],
            "java": [".java"],
            "c": [".c", ".h"],
            "cpp": [".cpp", ".hpp", ".cc", ".cxx"],
            "md": [".md", ".markdown"],
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "xml": [".xml"],
            "html": [".html", ".htm"],
            "css": [".css"],
            "txt": [".txt"],
        }

        if type in type_extensions:
            extensions = type_extensions[type]
            files_to_search = [
                f for f in files_to_search if any(f.endswith(ext) for ext in extensions)
            ]

    # Compile regex pattern
    flags = 0
    if i:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE | re.DOTALL

    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return f"Error: Invalid regex pattern: {e}"

    # Search results
    results = []
    file_matches = []
    match_counts = {}

    for file_path in files_to_search:
        try:
            # Skip binary files and very large files
            if os.path.getsize(file_path) > 10 * 1024 * 1024:  # Skip files > 10MB
                continue

            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content:
                continue

            lines = content.splitlines()
            file_has_matches = False
            file_match_count = 0
            matched_lines = set()  # Track which lines we've already processed

            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    file_has_matches = True
                    file_match_count += 1

                    if output_mode == "content" and line_num not in matched_lines:
                        # Handle context lines (A, B, C parameters)
                        context_before = B or C or 0
                        context_after = A or C or 0

                        # Calculate line range
                        start_line = max(1, line_num - context_before)
                        end_line = min(len(lines), line_num + context_after)

                        # Add context lines
                        for ctx_line_num in range(start_line, end_line + 1):
                            if ctx_line_num in matched_lines:
                                continue

                            ctx_line = lines[
                                ctx_line_num - 1
                            ]  # Convert to 0-based index

                            # Format line number if requested
                            line_prefix = f"{ctx_line_num}:" if n else ""

                            # Mark the actual match line vs context
                            if ctx_line_num == line_num:
                                results.append(f"{file_path}:{line_prefix}{ctx_line}")
                            elif context_before > 0 or context_after > 0:
                                results.append(f"{file_path}-{line_prefix}{ctx_line}")

                            matched_lines.add(ctx_line_num)

            if file_has_matches:
                file_matches.append(file_path)
                match_counts[file_path] = file_match_count

        except (UnicodeDecodeError, PermissionError, OSError):
            # Skip files we can't read
            continue

    # Format output based on mode
    if output_mode == "files_with_matches":
        output_lines = file_matches
    elif output_mode == "count":
        output_lines = [
            f"{file_path}:{count}" for file_path, count in match_counts.items()
        ]
    else:  # content
        output_lines = results

    # Apply head limit if specified
    if head_limit and head_limit > 0:
        output_lines = output_lines[:head_limit]

    return "\n".join(output_lines) if output_lines else "No matches found"
