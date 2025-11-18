# subcursor CLI Reference

## Installation

```bash
# Install/run with uvx (no installation needed)
uvx subcursor

# Or install globally with uv
uv tool install subcursor
```

## Commands

### Run MCP Server (Default)

```bash
uvx subcursor
```

Starts the MCP server with automatic dylib compilation on first run.

### Force Recompile Dylib

```bash
uvx subcursor --compile
```

Forces recompilation of the arm64e dylib. Useful if:
- You modified the C source
- The dylib is corrupted
- You want to ensure you have the latest version

### Check Dylib Status

```bash
uvx subcursor --check
```

Verifies if the dylib is compiled and ready to use.

### Show Version

```bash
uvx subcursor --version
```

## Environment Variables

### `SUBCURSOR_DYLIB_PATH`

Overrides the default dylib location. Automatically set when running via CLI.

```bash
export SUBCURSOR_DYLIB_PATH=/custom/path/libcursor_redirect.dylib
uvx subcursor
```

## Usage with Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "subcursor": {
      "command": "uvx",
      "args": ["subcursor"]
    }
  }
}
```

Restart Cursor, and the MCP server will start automatically.

## Troubleshooting

### Compilation Errors

```bash
# Ensure clang is installed
xcode-select --install

# Try forcing recompilation
uvx subcursor --compile
```

### Dylib Not Found

```bash
# Check status
uvx subcursor --check

# Recompile if needed
uvx subcursor --compile
```

### Permission Errors

The dylib is automatically code-signed. If you see permission errors:

```bash
# Manually sign the dylib
codesign -s - -f ~/.local/share/subcursor/libcursor_redirect.dylib
```

## How It Works

When you run `uvx subcursor`:

1. **uvx** installs subcursor in an isolated environment
2. **subcursor CLI** checks if dylib exists at `~/.local/share/subcursor/`
3. If not, **compiles** `redirect_interpose.c` with clang
4. **Code signs** the dylib
5. **Starts** the MCP server with the compiled dylib

The dylib is cached at `~/.local/share/subcursor/libcursor_redirect.dylib`, so compilation only happens once (or when you use `--compile`).

## Advanced: Local Development

```bash
# Clone repository
git clone <repository-url>
cd subcursor

# Build manually
./build.sh

# Run locally
uv run subcursor/cli.py
```

## Examples

### Check if Everything is Ready

```bash
uvx subcursor --check
```

### Recompile After Modifications

```bash
# Edit src/redirect_interpose.c
vim src/redirect_interpose.c

# Force recompile
uvx subcursor --compile

# Test with Cursor
# (restart Cursor to reload MCP server)
```

### Run from Specific Version

```bash
# Run specific version
uvx subcursor@0.1.0

# Run from git
uvx --from git+https://github.com/user/subcursor subcursor
```

## See Also

- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Quick setup
- [USAGE.md](USAGE.md) - Detailed usage guide
- [AGENTS.md](AGENTS.md) - For AI assistants

