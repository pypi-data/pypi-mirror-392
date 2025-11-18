# subcursor Quick Start

## 🚀 Installation (1 minute)

```bash
# 1. Add to your .cursor/mcp.json:
{
  "mcpServers": {
    "subcursor": {
      "command": "uvx",
      "args": ["subcursor"]
    }
  }
}

# 2. Restart Cursor
```

**That's it!** uvx automatically handles everything:
- Installing subcursor
- Compiling the dylib
- Starting the MCP server

No git clone or manual builds needed!

## 🎯 Basic Usage

In Cursor, use these MCP tools:

### List Subagents
```
Tool: list-subagents
```

### Spawn a Subagent
```
Tool: spawn-subagent
name: designer
prompt: Create a modern app icon
```

### Create New Subagent
```
Tool: create-subagent
name: ml-engineer
description: Machine learning and data science specialist
```

## 📋 Pre-configured Subagents

- **designer** - UI/UX design, icons, visual assets
- **backend** - APIs, databases, server-side logic
- **frontend** - React, Next.js, modern web apps

## 🔧 How It Works

```
You spawn "designer" subagent
        ↓
MCP server launches cursor-cli with:
  DYLD_INSERT_LIBRARIES=libcursor_redirect.dylib
  CURSOR_REDIRECT_SOURCE=.cursor/
  CURSOR_REDIRECT_TARGET=.cursor/subagents/designer/.cursor/
        ↓
Dylib intercepts file system calls
        ↓
Cursor loads designer's custom:
  - .cursorrules
  - mcp.json
  - Any other .cursor configs
```

## 📚 Documentation

- **README.md** - Full project documentation
- **USAGE.md** - Detailed usage guide and troubleshooting
- **QUICKSTART.md** - This file

## ⚠️ macOS Security Note

If you see "dylib could not be loaded", this is normal with SIP enabled.
The dylib works with user-space apps like cursor-cli.

See USAGE.md for troubleshooting options.

## 🎨 Example Workflow

```bash
# Day 1: Design phase
spawn-subagent "designer" "Create landing page design"

# Day 2: Backend implementation
spawn-subagent "backend" "Build user authentication API"

# Day 3: Frontend implementation
spawn-subagent "frontend" "Implement login form component"
```

Each subagent works in its own Cursor window with specialized rules and context!

