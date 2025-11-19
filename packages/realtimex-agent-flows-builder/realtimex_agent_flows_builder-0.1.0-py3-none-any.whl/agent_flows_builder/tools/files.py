"""Hybrid filesystem tools for Agent Flows Builder.

Intelligently routes between state (for flow.json and session files)
and real filesystem (for documentation access).
"""

from pathlib import Path
from typing import Annotated

from deepagents.prompts import LIST_FILES_TOOL_DESCRIPTION
from deepagents.state import DeepAgentState
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from agent_flows_builder.prompts.tools import (
    EDIT_FILE_TOOL_DESCRIPTION,
    READ_FILE_TOOL_DESCRIPTION,
    WRITE_FILE_TOOL_DESCRIPTION,
)
from agent_flows_builder.utils.file_operations import (
    format_file_lines_with_numbers,
    validate_and_replace_string,
)
from agent_flows_builder.utils.workspace import get_workspace


def _normalize_path(file_path: str) -> str:
    """Removes common leading prefixes from a file path."""
    # Strip leading './'
    if file_path.startswith("./"):
        file_path = file_path[2:]

    # Note: We don't strip leading '/' to allow absolute paths
    # Strip leading '/' (uncomment if absolute paths should be relative to workspace)
    # elif file_path.startswith('/'):
    #     file_path = file_path[1:]

    return file_path


def _should_use_state(file_path: str) -> bool:
    """Determine if file operations should use state vs real filesystem.

    State Usage (for streaming and session persistence):
    - flow.json: Critical for State Seeding approach
    - user_request.md: Session working file
    - Default: Other session files use state

    Real Filesystem Usage:
    - docs/*: Documentation access (relative or absolute paths)
    """
    # Critical state files for State Seeding
    if file_path in {"flow.json", "user_request.md"}:
        return True

    # Documentation always uses real filesystem
    # Handle both relative (docs/...) and absolute (/path/to/docs/...) paths
    if file_path.startswith("docs/") or "/docs/" in file_path:
        return False

    # Default to state for session isolation
    return True


@tool(description=READ_FILE_TOOL_DESCRIPTION)
def read_file(
    file_path: str,
    state: Annotated[DeepAgentState, InjectedState],
    offset: int = 0,
    limit: int = 2000,
) -> str:
    """Read file with intelligent routing between state and filesystem."""
    file_path = _normalize_path(file_path)
    if _should_use_state(file_path):
        return _read_from_state(file_path, state, offset, limit)
    else:
        # Use global workspace
        workspace = get_workspace()
        return _read_from_filesystem(file_path, offset, limit, workspace)


def _read_from_state(
    file_path: str, state: DeepAgentState, offset: int, limit: int
) -> str:
    """Read file from state (virtual filesystem)."""
    mock_filesystem = state.get("files", {})
    if file_path not in mock_filesystem:
        return f"Error: File '{file_path}' not found"

    content = mock_filesystem[file_path]
    return format_file_lines_with_numbers(content, offset, limit)


def _read_from_filesystem(
    file_path: str, offset: int, limit: int, workspace: Path
) -> str:
    """Read file from real filesystem."""
    try:
        # Use workspace as base if file_path is relative
        if not Path(file_path).is_absolute():
            path = (workspace / file_path).resolve()
        else:
            path = Path(file_path).resolve()

        # Check if file exists and is actually a file
        if not path.exists():
            return f"Error: File '{file_path}' not found"
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"

        # Read and format file content (handles UnicodeDecodeError internally)
        content = path.read_text(encoding="utf-8")
        return format_file_lines_with_numbers(content, offset, limit)

    except UnicodeDecodeError:
        return f"Error: File '{file_path}' contains binary data or invalid encoding"
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"


@tool(description=WRITE_FILE_TOOL_DESCRIPTION)
def write_file(
    file_path: str,
    content: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write file with intelligent routing between state and filesystem."""
    file_path = _normalize_path(file_path)
    if _should_use_state(file_path):
        files = state.get("files", {})
        files[file_path] = content
        return Command(
            update={
                "files": files,
                "messages": [
                    ToolMessage(f"Updated file {file_path}", tool_call_id=tool_call_id)
                ],
            }
        )
    else:
        try:
            # Use global workspace
            workspace = get_workspace()

            # Use workspace as base if file_path is relative
            if not Path(file_path).is_absolute():
                path = (workspace / file_path).resolve()
            else:
                path = Path(file_path).resolve()

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            path.write_text(content, encoding="utf-8")

            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"Successfully wrote to file {file_path}",
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )
        except Exception as e:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"Error writing file '{file_path}': {str(e)}",
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )


@tool(description=EDIT_FILE_TOOL_DESCRIPTION)
def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    replace_all: bool = False,
) -> Command | str:
    """Edit file with intelligent routing between state and filesystem."""
    file_path = _normalize_path(file_path)
    try:
        if _should_use_state(file_path):
            # Get content from state
            mock_filesystem = state.get("files", {})
            if file_path not in mock_filesystem:
                return f"Error: File '{file_path}' not found"
            content = mock_filesystem[file_path]

            # Perform replacement using shared utility
            new_content, result_msg = validate_and_replace_string(
                content, old_string, new_string, replace_all
            )
            result_msg += f" in '{file_path}'"

            # Update state
            mock_filesystem[file_path] = new_content
            return Command(
                update={
                    "files": mock_filesystem,
                    "messages": [ToolMessage(result_msg, tool_call_id=tool_call_id)],
                }
            )
        else:
            # Use global workspace
            workspace = get_workspace()

            # Use workspace as base if file_path is relative
            if not Path(file_path).is_absolute():
                path = (workspace / file_path).resolve()
            else:
                path = Path(file_path).resolve()

            if not path.exists():
                return f"Error: File '{file_path}' not found"
            if not path.is_file():
                return f"Error: '{file_path}' is not a file"

            content = path.read_text(encoding="utf-8")

            # Perform replacement using shared utility
            new_content, result_msg = validate_and_replace_string(
                content, old_string, new_string, replace_all
            )
            result_msg += f" in '{file_path}'"

            # Write back to filesystem
            path.write_text(new_content, encoding="utf-8")

            return Command(
                update={
                    "messages": [ToolMessage(result_msg, tool_call_id=tool_call_id)],
                }
            )

    except ValueError as e:
        # Handle validation errors from shared utility (formatted as strings already)
        return str(e)
    except UnicodeDecodeError:
        return f"Error: File '{file_path}' contains binary data or invalid encoding"
    except Exception as e:
        return f"Error editing file '{file_path}': {str(e)}"


@tool(description=LIST_FILES_TOOL_DESCRIPTION)
def ls(state: Annotated[DeepAgentState, InjectedState]) -> list[str]:
    """List files from both state and workspace directory."""
    files = []

    # Add files from state (session files)
    state_files = list(state.get("files", {}).keys())
    files.extend(state_files)

    # Add files from workspace directory
    try:
        # Use global workspace
        workspace = get_workspace()
        for item in workspace.iterdir():
            item_name = item.name if item.is_file() else f"{item.name}/"
            if item_name not in files:  # Avoid duplicates
                files.append(item_name)
    except Exception as e:
        files.append(f"Error listing directory: {str(e)}")  # Inform the agent

    return sorted(files)
