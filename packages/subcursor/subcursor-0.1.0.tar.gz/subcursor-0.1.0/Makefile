.PHONY: all build clean test

all: build

build:
	@echo "🔨 Building subcursor..."
	@echo "📦 Building dylib with clang (arm64e)..."
	clang -arch arm64e -dynamiclib -o libcursor_redirect.dylib src/redirect_interpose.c
	codesign -s - -f libcursor_redirect.dylib
	@echo "🐍 Installing Python dependencies..."
	uv sync
	@echo "✅ Build complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Add the MCP server to your .cursor/mcp.json"
	@echo "2. Restart Cursor"
	@echo "3. Use the spawn-subagent MCP tool!"

clean:
	rm -f libcursor_redirect.dylib
	rm -f libcursor_redirect_interpose.dylib
	rm -f libcursor_redirect_arm64e.dylib
	rm -rf .venv
	rm -rf zig-cache zig-out .zig-cache

test: build
	@./test_redirect.sh

