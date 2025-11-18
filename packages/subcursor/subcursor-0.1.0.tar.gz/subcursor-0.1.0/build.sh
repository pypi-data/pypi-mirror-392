#!/bin/bash
set -e

echo "🔨 Building subcursor..."

# Build the dylib with clang (arm64e for cursor-agent compatibility)
echo "📦 Building dylib with clang (arm64e)..."
clang -arch arm64e -dynamiclib -o libcursor_redirect.dylib src/redirect_interpose.c
codesign -s - -f libcursor_redirect.dylib

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
uv sync

echo "✅ Build complete!"
echo ""
echo "Next steps:"
echo "1. Add the MCP server to your .cursor/mcp.json:"
echo ""
echo '   "subcursor": {'
echo '     "command": "uv",'
echo "     \"args\": [\"run\", \"$PWD/run_mcp_server.py\"]"
echo '   }'
echo ""
echo "2. Restart Cursor to load the MCP server"
echo "3. Use the MCP tools to manage subagents!"

