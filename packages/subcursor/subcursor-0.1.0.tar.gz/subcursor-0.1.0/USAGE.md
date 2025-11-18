# subcursor Usage Guide

## Quick Start

### 1. Build the Project

```bash
./build.sh
```

This will:
- Build the Zig dylib for system call interception
- Install Python dependencies via uv
- Set up the project structure

### 2. Configure MCP Server

Add the subcursor MCP server to your main `.cursor/mcp.json` (or in Cursor Settings):

```json
{
  "mcpServers": {
    "subcursor": {
      "command": "uv",
      "args": [
        "run",
        "/Users/yoav/Documents/Personal/subcursor/run_mcp_server.py"
      ]
    }
  }
}
```

**Important**: Update the path to match your actual installation path.

### 3. Restart Cursor

Restart Cursor to load the new MCP server configuration.

### 4. Use Subagents

In Cursor, you can now use these MCP tools:

#### List Available Subagents

Use the `list-subagents` tool to see all configured subagents:
- `designer` - UI/UX design specialist
- `backend` - Backend API and database specialist
- `frontend` - React and modern frontend specialist

#### Create a New Subagent

Use the `create-subagent` tool:
```
name: "devops"
description: "DevOps and infrastructure automation specialist"
```

#### Spawn a Subagent

Use the `spawn-subagent` tool:
```
name: "designer"
prompt: "Create a modern app icon with a purple gradient"
workspace_path: (optional, defaults to project root)
```

This will launch a new Cursor window with:
- The subagent's custom `.cursorrules`
- The subagent's MCP server configuration
- All file reads redirected to the subagent's `.cursor` directory

## How Subagents Work

### Directory Structure

Each subagent has its own isolated configuration:

```
.cursor/subagents/designer/
├── description.txt          # Subagent description
└── .cursor/
    ├── rules/
    │   └── .cursorrules    # Custom rules for this subagent
    └── mcp.json            # MCP server config for this subagent
```

### System Call Redirection

When you spawn a subagent, the system:

1. Sets `DYLD_INSERT_LIBRARIES` to load our dylib
2. Sets `CURSOR_REDIRECT_SOURCE` to your main `.cursor` directory
3. Sets `CURSOR_REDIRECT_TARGET` to the subagent's `.cursor` directory
4. Launches `cursor-cli` with these environment variables

The dylib intercepts file system calls (open, stat, access, etc.) and redirects:
- Reads from `~/.cursor` → `.cursor/subagents/designer/.cursor`
- This makes Cursor load the subagent's configuration seamlessly

## Example Workflows

### UI Design Task

```bash
# Spawn the designer subagent
spawn-subagent "designer" "Create a beautiful landing page hero section"
```

The designer subagent will:
- Focus on visual design and UX
- Suggest modern CSS and animations
- Create accessible, responsive layouts
- Provide design system recommendations

### Backend API Task

```bash
# Spawn the backend subagent
spawn-subagent "backend" "Create a REST API for user authentication"
```

The backend subagent will:
- Design secure API endpoints
- Implement proper authentication
- Set up database schemas
- Add comprehensive error handling

### Frontend Component Task

```bash
# Spawn the frontend subagent
spawn-subagent "frontend" "Build a reusable modal component in React"
```

The frontend subagent will:
- Create TypeScript React components
- Implement proper state management
- Add accessibility features
- Include unit tests

## Customizing Subagents

### Editing Rules

Edit a subagent's rules:

```bash
code .cursor/subagents/designer/.cursor/rules/.cursorrules
```

Update the rules to customize the subagent's behavior, expertise, and communication style.

### Adding MCP Servers

Each subagent can have its own MCP servers. Edit the subagent's MCP config:

```bash
code .cursor/subagents/designer/.cursor/mcp.json
```

Example - add a design-specific MCP server:

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

## Troubleshooting

### "Dylib could not be loaded" Error

**Issue**: macOS may block the dylib due to architecture or security restrictions.

**Solutions**:

1. **Check Architecture**: The dylib is built for arm64. Ensure you're on Apple Silicon.

2. **Disable SIP (not recommended for production)**:
   ```bash
   # Reboot into Recovery Mode (hold Command+R during startup)
   csrutil disable
   # Reboot normally
   ```

3. **Code Sign the Dylib**:
   ```bash
   codesign -s - -f zig-out/lib/libcursor_redirect.dylib
   ```

4. **Use without SIP restrictions**: The dylib works best with user-space applications like cursor-cli.

### MCP Server Not Showing Up

1. Check that the MCP server is configured correctly in `.cursor/mcp.json`
2. Verify the path is absolute and correct
3. Check Cursor's logs: `~/Library/Logs/Cursor/`
4. Test the server directly: `uv run run_mcp_server.py`

### Subagent Not Using Custom Rules

1. Verify the environment variables are set correctly
2. Check that `DYLD_INSERT_LIBRARIES` points to the dylib
3. Ensure the subagent's `.cursor` directory exists and has the correct structure
4. Try running cursor-cli manually with the environment variables

### Testing the Dylib Manually

```bash
# Set up environment
export DYLD_INSERT_LIBRARIES="$PWD/zig-out/lib/libcursor_redirect.dylib"
export CURSOR_REDIRECT_SOURCE="$PWD/.cursor"
export CURSOR_REDIRECT_TARGET="$PWD/.cursor/subagents/designer/.cursor"

# Test with a simple command
ls -la .cursor/
# Should show the contents of .cursor/subagents/designer/.cursor/
```

## Advanced Usage

### Multiple Subagents in Parallel

You can spawn multiple subagents simultaneously, each in their own Cursor window:

```bash
spawn-subagent "frontend" "Build the user dashboard"
spawn-subagent "backend" "Create the API endpoints"
spawn-subagent "designer" "Design the color scheme"
```

### Subagent Templates

Create template subagents for common roles:

```bash
# Data scientist subagent
create-subagent "data-scientist" "Python data analysis and machine learning specialist"

# DevOps subagent
create-subagent "devops" "Infrastructure, CI/CD, and deployment automation specialist"

# Security subagent
create-subagent "security" "Security auditing and vulnerability assessment specialist"
```

### Workspace-Specific Subagents

Spawn a subagent for a specific project:

```bash
spawn-subagent "frontend" "Optimize the checkout flow" "/Users/yoav/projects/ecommerce"
```

## Best Practices

1. **Focused Roles**: Keep subagent roles specific and focused
2. **Clear Descriptions**: Write clear descriptions to help team members understand each subagent's purpose
3. **Custom MCP Servers**: Add specialized MCP servers to enhance subagent capabilities
4. **Rule Updates**: Regularly update subagent rules based on your team's evolving needs
5. **Documentation**: Document your custom subagents in your project's README

## Limitations

- **macOS Only**: Currently only supports macOS (DYLD_INSERT_LIBRARIES)
- **Cursor CLI Required**: Requires the `cursor` command-line tool
- **SIP Restrictions**: May require SIP adjustments for some use cases
- **No Cross-Subagent Communication**: Subagents don't automatically share context

## Future Enhancements

Planned features:
- [ ] Linux support (LD_PRELOAD)
- [ ] Windows support (DLL injection)
- [ ] Cross-subagent communication protocol
- [ ] Web UI for managing subagents
- [ ] Subagent activity logging
- [ ] Shared context between subagents
- [ ] Subagent marketplace/templates

