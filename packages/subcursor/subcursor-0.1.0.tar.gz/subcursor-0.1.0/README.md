# subcursor

**Specialized AI subagents for Cursor with isolated configurations**

subcursor enables running multiple Cursor instances, each with their own custom rules, MCP servers, and configurations. Perfect for teams that need specialized AI assistants for different domains (design, backend, frontend, etc.) or for solo developers who want focused AI assistance for specific tasks.

## Features

- **Isolated Configurations**: Each subagent has its own `.cursor` directory with custom rules and MCP servers
- **Transparent Redirection**: System-level file interception makes Cursor load subagent configurations seamlessly
- **Pre-configured Subagents**: Designer, Backend, and Frontend specialists ready to use
- **Easy Extension**: Create new subagents with custom expertise via MCP tools
- **Zero Cursor Modifications**: Works with standard Cursor installation

## How It Works

subcursor uses a dynamic library (dylib) to intercept file system calls, redirecting Cursor's reads from the main `.cursor` directory to a subagent's isolated `.cursor` directory. This allows each Cursor instance to load completely different configurations without modifying Cursor itself.

```
User spawns "designer" subagent
        ↓
MCP server launches cursor-agent with environment:
  DYLD_INSERT_LIBRARIES → libcursor_redirect.dylib
  CURSOR_REDIRECT_SOURCE → .cursor/
  CURSOR_REDIRECT_TARGET → .cursor/subagents/designer/.cursor/
        ↓
File system calls intercepted via DYLD_INTERPOSE
        ↓
Cursor loads designer's .cursorrules and mcp.json
```

## Requirements

- **macOS** (uses DYLD_INSERT_LIBRARIES)
- **Cursor** with cursor-agent installed
- **Xcode Command Line Tools** (for clang - install with `xcode-select --install`)
- **Python 3.11+**
- **uv** (install with `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Installation

### Option 1: Using uvx (Recommended)

The easiest way to use subcursor is with `uvx`, which automatically handles compilation:

```bash
# Add to your .cursor/mcp.json:
{
  "mcpServers": {
    "subcursor": {
      "command": "uvx",
      "args": ["subcursor"]
    }
  }
}
```

On first run, uvx will automatically:
- Install subcursor and dependencies
- Compile the arm64e dylib with clang
- Start the MCP server

**That's it!** No git clone or manual builds needed.

### Option 2: From Source

For development or customization:

```bash
git clone <repository-url>
cd subcursor
./build.sh

# Add to your .cursor/mcp.json:
{
  "mcpServers": {
    "subcursor": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/subcursor/run_mcp_server.py"]
    }
  }
}
```

### Restart Cursor

Restart Cursor to load the MCP server.

## Usage

### List Available Subagents

Use the `list-subagents` MCP tool in Cursor to see all configured subagents.

### Spawn a Subagent

Use the `spawn-subagent` MCP tool:

```
Tool: spawn-subagent
Arguments:
  name: "designer"
  prompt: "Create a modern app icon with purple gradient"
```

This launches a new Cursor instance with the designer's configuration.

### Create a Custom Subagent

Use the `create-subagent` MCP tool:

```
Tool: create-subagent
Arguments:
  name: "devops"
  description: "DevOps and infrastructure automation specialist"
```

Then customize the subagent's `.cursorrules` and `mcp.json` files.

## Pre-configured Subagents

### Designer
**Specialization**: UI/UX design, visual assets, modern interfaces

**Expertise**: Design systems, CSS, accessibility, Tailwind, SVG

### Backend
**Specialization**: Server-side APIs, databases, authentication

**Expertise**: REST/GraphQL, PostgreSQL, Redis, microservices, security

### Frontend
**Specialization**: Modern web applications with React/Next.js

**Expertise**: React, TypeScript, state management, performance optimization

## Architecture

### Project Structure

```
subcursor/
├── src/
│   └── redirect_interpose.c   # System call interception dylib
├── subcursor/
│   ├── __init__.py            # MCP server implementation
│   └── __main__.py            # Entry point
├── .cursor/
│   └── subagents/             # Subagent configurations
│       ├── designer/
│       ├── backend/
│       └── frontend/
├── libcursor_redirect.dylib   # Compiled dylib
├── Makefile                   # Build automation
├── build.sh                   # Build script
└── pyproject.toml             # Python dependencies
```

### Technical Details

**Interception Method**: Uses `DYLD_INTERPOSE` macro to hook file system calls
**Target Binary**: cursor-agent's Node.js runtime
**Architecture**: arm64e (required for cursor-agent compatibility)
**Interposed Functions**: `open`, `openat`, `stat`, `lstat`, `access`, `readlink`, `realpath`

## Customization

### Editing Subagent Rules

```bash
# Edit designer's rules
code .cursor/subagents/designer/.cursor/rules/.cursorrules
```

Customize the AI's behavior, expertise, and communication style.

### Adding MCP Servers

```bash
# Edit designer's MCP configuration
code .cursor/subagents/designer/.cursor/mcp.json
```

Add specialized MCP servers for each subagent:

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-figma"]
    }
  }
}
```

## Development

### Building from Source

```bash
# Using Makefile
make

# Or using build script
./build.sh
```

### Testing the Dylib

```bash
# Create test files
mkdir -p .cursor/test .cursor/subagents/designer/.cursor/test
echo "designer" > .cursor/subagents/designer/.cursor/test/file.txt
echo "main" > .cursor/test/file.txt

# Test redirection
DYLD_INSERT_LIBRARIES="$PWD/libcursor_redirect.dylib" \
CURSOR_REDIRECT_SOURCE="$PWD/.cursor" \
CURSOR_REDIRECT_TARGET="$PWD/.cursor/subagents/designer/.cursor" \
~/.local/share/cursor-agent/versions/*/node -e \
  "console.log(require('fs').readFileSync('.cursor/test/file.txt', 'utf8'))"

# Should output: designer
```

## Troubleshooting

### MCP Server Not Loading

- Verify the path in `mcp.json` is absolute
- Check Cursor's logs: `~/Library/Logs/Cursor/`
- Test manually: `uv run run_mcp_server.py`

### Dylib Not Working

- Ensure cursor-agent is installed: `ls ~/.local/bin/cursor-agent`
- Verify dylib is signed: `codesign -d -vvv libcursor_redirect.dylib`
- Check environment variables are set correctly

### Subagent Not Using Custom Rules

- Verify the subagent directory exists
- Check that `.cursor/rules/.cursorrules` is present
- Ensure environment variables point to correct paths

## Limitations

- **macOS Only**: Uses DYLD_INSERT_LIBRARIES (macOS-specific)
- **cursor-agent Required**: Needs cursor-agent with library validation disabled
- **No Cross-Communication**: Subagents don't share context automatically

## Security Considerations

subcursor uses dylib injection, which requires the target binary (cursor-agent) to have library validation disabled. This is a legitimate technique for development tools but should be understood:

- The dylib only redirects file paths within your project
- No network access or system modifications
- Open source - audit the code yourself

## Credits

- **Inspiration**: [Yair Chuchem's system call interception](https://yairchu.github.io/posts/intercept-to-fix)
- **Technique**: [BallisKit's macOS dylib injection research](https://blog.balliskit.com/macos-dylib-injection-at-scale-designing-a-self-sufficient-loader-da8799a56ada)

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR for:

- New subagent templates
- Linux/Windows support
- Bug fixes and improvements
- Documentation enhancements

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [USAGE.md](USAGE.md) - Detailed usage instructions
- [AGENTS.md](AGENTS.md) - For LLMs: How to use subcursor effectively

---

**Note**: subcursor is an independent project and is not affiliated with or endorsed by Cursor or Anysphere, Inc.
