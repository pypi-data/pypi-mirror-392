"""LangChain tool definitions for flow manipulation."""

import json
from typing import Annotated, Literal

from deepagents.state import DeepAgentState
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from agent_flows_builder.tools.flow_operations.step_operations import (
    add_step,
    remove_step,
    update_step,
)
from agent_flows_builder.tools.flow_operations.variable_operations import (
    add_variables,
    remove_variables,
    update_variables,
)


@tool(parse_docstring=True)
def update_flow_steps(
    operation: Literal[
        "add_variables",
        "update_variables",
        "remove_variables",
        "add_step",
        "update_step",
        "remove_step",
    ],
    data: dict | list[dict],
    target_id: str | None = None,
    position: Literal["before", "after"] | None = None,
    path: str | None = None,
    state: Annotated[DeepAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Manipulates flow steps and variables using semantic operations.

    This tool handles all step-related and variable-related modifications to flow.json.
    Use `update_flow_metadata` tool for name/description changes.

    Operations:

    1. add_variables: Add variable definitions to `flow_variables`
       Required: data (list of variable defs)
       Example: data=[{"name": "x", "type": "string", ...}]

    2. update_variables: Update existing variable definitions
       Required: data (list of variable updates with "name" field)
       Example: data=[{"name": "x", "type": "number", "description": "Updated"}]

    3. remove_variables: Remove variables by name
       Required: data (list of variable names as strings OR dicts with "name")
       Example: data=["var1", "var2"] or data=[{"name": "var1"}, {"name": "var2"}]

    4. add_step: Insert step at specified location
       Required: data (step config dict)
       Optional: target_id + position (for relative positioning)
       Optional: path (for nested insertion via JSONPath)
       Example: data={"id": "fetch", "type": "apiCall", "config": {...}}

    5. update_step: Modify existing step (deep merge)
       Required: target_id, data (partial step config)
       Optional: path (to locate step in nested structure)
       Example: target_id="fetch", data={"config": {"url": "https://new.com"}}

    6. remove_step: Remove step by ID
       Required: target_id
       Optional: path (to locate step in nested structure)
       Example: target_id="old_step"

    Args:
        operation (str): Type of modification
        data (dict | list): Content to add/update (varies by operation)
        target_id (str, optional): Step ID to target (for update_step, remove_step, relative add_step)
        position (str, optional): "before" or "after" for relative add_step positioning
        path (str, optional): JSONPath for nested operations (e.g., "$.steps[?(@.id=='x')].config['truePath']")
    """
    # Get flow from state
    files = state.get("files", {})
    if "flow.json" not in files:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: flow.json not found in state",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    try:
        flow = json.loads(files["flow.json"])
    except json.JSONDecodeError as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Invalid JSON in flow.json: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # Route to operation handlers
    success = False
    message = ""

    if operation == "add_variables":
        if not isinstance(data, list):
            message = "Error: data must be a list for add_variables operation"
        else:
            flow, message, success = add_variables(flow, data)

    elif operation == "update_variables":
        if not isinstance(data, list):
            message = "Error: data must be a list for update_variables operation"
        else:
            flow, message, success = update_variables(flow, data)

    elif operation == "remove_variables":
        if not isinstance(data, list):
            message = "Error: data must be a list for remove_variables operation"
        else:
            flow, message, success = remove_variables(flow, data)

    elif operation == "add_step":
        if not isinstance(data, dict):
            message = "Error: data must be a dict for add_step operation"
        else:
            flow, message, success = add_step(flow, data, target_id, position, path)

    elif operation == "update_step":
        if not target_id:
            message = "Error: target_id required for update_step operation"
        elif not isinstance(data, dict):
            message = "Error: data must be a dict for update_step operation"
        else:
            flow, message, success = update_step(flow, target_id, data, path)

    elif operation == "remove_step":
        if not target_id:
            message = "Error: target_id required for remove_step operation"
        else:
            flow, message, success = remove_step(flow, target_id, path)

    else:
        message = f"Error: Unknown operation '{operation}'"

    # Update state if successful
    if success:
        files["flow.json"] = json.dumps(flow, ensure_ascii=False, indent=2)
        return Command(
            update={
                "files": files,
                "messages": [ToolMessage(content=message, tool_call_id=tool_call_id)],
            }
        )
    else:
        return Command(
            update={
                "messages": [ToolMessage(content=message, tool_call_id=tool_call_id)]
            }
        )


@tool(parse_docstring=True)
def update_flow_metadata(
    name: str | None = None,
    description: str | None = None,
    state: Annotated[DeepAgentState, InjectedState] = None,
    tool_call_id: Annotated[str, InjectedToolCallId] = None,
) -> Command:
    """Updates the name and description of the workflow.

    This tool modifies top-level metadata fields only. For all structural
    changes, such as adding or removing steps and variables, use the
    `update_flow_steps` tool.

    Args:
        name (str, optional): The new name for the workflow.
        description (str, optional): The new description for the workflow.

    Returns:
        Command: An object containing the updated flow state or a structured
            error message if neither parameter is provided.
    """
    # Get flow from state
    files = state.get("files", {})
    if "flow.json" not in files:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: flow.json not found in state",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # Validate at least one parameter provided
    if name is None and description is None:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Error: At least one of 'name' or 'description' must be provided",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    try:
        flow = json.loads(files["flow.json"])
    except json.JSONDecodeError as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error: Invalid JSON in flow.json: {str(e)}",
                        tool_call_id=tool_call_id,
                    )
                ]
            }
        )

    # Update metadata
    updated_fields = []

    if name is not None:
        flow["name"] = name
        updated_fields.append("name")

    if description is not None:
        flow["description"] = description
        updated_fields.append("description")

    # Save back to state
    files["flow.json"] = json.dumps(flow, ensure_ascii=False, indent=2)

    fields_str = " and ".join(updated_fields)
    message = f"Updated flow {fields_str}"

    return Command(
        update={
            "files": files,
            "messages": [ToolMessage(content=message, tool_call_id=tool_call_id)],
        }
    )
