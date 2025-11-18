#!/usr/bin/env python3
"""
subcursor MCP Server

Manages Cursor subagents with isolated .cursor directories using system call interception.
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Get paths
# Default dylib location: ~/.local/share/subcursor/
# Can be overridden with SUBCURSOR_DYLIB_PATH env var
default_dylib = Path.home() / ".local" / "share" / "subcursor" / "libcursor_redirect.dylib"
DYLIB_PATH = Path(os.environ.get("SUBCURSOR_DYLIB_PATH", default_dylib))
PROJECT_ROOT = Path.cwd()
SUBAGENTS_DIR = PROJECT_ROOT / ".cursor" / "subagents"


def get_available_subagents() -> list[str]:
    """List all available subagents."""
    if not SUBAGENTS_DIR.exists():
        return []

    return [
        d.name for d in SUBAGENTS_DIR.iterdir()
        if d.is_dir() and (d / ".cursor").exists()
    ]


def get_subagent_info(name: str) -> Optional[dict]:
    """Get information about a specific subagent."""
    subagent_path = SUBAGENTS_DIR / name
    if not subagent_path.exists():
        return None

    cursor_dir = subagent_path / ".cursor"
    info = {
        "name": name,
        "path": str(subagent_path),
        "cursor_dir": str(cursor_dir),
        "has_rules": (cursor_dir / "rules" / ".cursorrules").exists(),
        "has_mcp_config": (cursor_dir / "mcp.json").exists(),
    }

    # Read description if available
    desc_file = subagent_path / "description.txt"
    if desc_file.exists():
        info["description"] = desc_file.read_text().strip()

    return info


def spawn_subagent(name: str, prompt: str, workspace_path: Optional[str] = None) -> dict:
    """
    Spawn a cursor-cli instance with the subagent's .cursor directory.

    Uses DYLD_INSERT_LIBRARIES to redirect file system calls to the subagent's
    .cursor directory.
    """
    subagent_path = SUBAGENTS_DIR / name
    if not subagent_path.exists():
        return {
            "success": False,
            "error": f"Subagent '{name}' does not exist"
        }

    if not DYLIB_PATH.exists():
        return {
            "success": False,
            "error": f"Dylib not found at {DYLIB_PATH}. Build it first with: zig build"
        }

    # Determine workspace path
    if workspace_path is None:
        workspace_path = str(PROJECT_ROOT)

    # Set up environment variables for the dylib
    env = os.environ.copy()
    env["DYLD_INSERT_LIBRARIES"] = str(DYLIB_PATH)
    env["CURSOR_REDIRECT_TARGET"] = str(subagent_path / ".cursor")
    env["CURSOR_REDIRECT_SOURCE"] = str(PROJECT_ROOT / ".cursor")

    # Build cursor-agent command
    # Note: cursor-agent is actually a Node.js process with library validation disabled
    cursor_agent_path = os.path.expanduser("~/.local/bin/cursor-agent")
    cursor_cmd = [cursor_agent_path]

    try:
        # Launch cursor-cli in the background
        process = subprocess.Popen(
            cursor_cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        return {
            "success": True,
            "subagent": name,
            "pid": process.pid,
            "workspace": workspace_path,
            "cursor_dir": str(subagent_path / ".cursor"),
            "message": f"Spawned subagent '{name}' with prompt: {prompt}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to spawn subagent: {str(e)}"
        }


# Create the MCP server
app = Server("subcursor")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="list-subagents",
            description="List all available Cursor subagents with their configurations",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="spawn-subagent",
            description="Spawn a Cursor instance with a specific subagent's configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the subagent to spawn (e.g., 'designer', 'backend')"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Initial prompt/task for the subagent"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "Optional: Custom workspace path (defaults to project root)"
                    }
                },
                "required": ["name", "prompt"]
            }
        ),
        Tool(
            name="create-subagent",
            description="Create a new subagent with a basic .cursor directory structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the new subagent"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the subagent's purpose"
                    }
                },
                "required": ["name", "description"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "list-subagents":
        subagents = get_available_subagents()

        if not subagents:
            return [TextContent(
                type="text",
                text="No subagents found. Create one using the create-subagent tool."
            )]

        result = ["Available subagents:\n"]
        for subagent_name in subagents:
            info = get_subagent_info(subagent_name)
            if info:
                result.append(f"\n**{info['name']}**")
                if "description" in info:
                    result.append(f"  Description: {info['description']}")
                result.append(f"  Path: {info['path']}")
                result.append(f"  Has rules: {info['has_rules']}")
                result.append(f"  Has MCP config: {info['has_mcp_config']}")

        return [TextContent(type="text", text="\n".join(result))]

    elif name == "spawn-subagent":
        subagent_name = arguments["name"]
        prompt = arguments["prompt"]
        workspace_path = arguments.get("workspace_path")

        result = spawn_subagent(subagent_name, prompt, workspace_path)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    elif name == "create-subagent":
        subagent_name = arguments["name"]
        description = arguments["description"]

        subagent_path = SUBAGENTS_DIR / subagent_name
        cursor_dir = subagent_path / ".cursor"

        if subagent_path.exists():
            return [TextContent(
                type="text",
                text=f"Error: Subagent '{subagent_name}' already exists"
            )]

        # Create directory structure
        (cursor_dir / "rules").mkdir(parents=True, exist_ok=True)

        # Create description file
        (subagent_path / "description.txt").write_text(description)

        # Create a basic .cursorrules file
        cursorrules = f"""# {subagent_name} Subagent

{description}

## Role
You are a specialized subagent focused on: {description.lower()}

## Guidelines
- Stay focused on your specialized role
- Collaborate with other subagents when needed
- Follow best practices in your domain
"""
        (cursor_dir / "rules" / ".cursorrules").write_text(cursorrules)

        # Create empty MCP config
        mcp_config = {
            "mcpServers": {}
        }
        (cursor_dir / "mcp.json").write_text(json.dumps(mcp_config, indent=2))

        return [TextContent(
            type="text",
            text=f"Created subagent '{subagent_name}' at {subagent_path}"
        )]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

