#!/usr/bin/env python3
"""
subcursor CLI - Entry point for uvx subcursor
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_package_root() -> Path:
    """Get the package root directory."""
    # When installed via uvx, __file__ will be in site-packages
    # Try to find the package directory
    package_dir = Path(__file__).parent.absolute()
    return package_dir


def get_project_root() -> Path:
    """Get the actual project root (where user runs from)."""
    return Path.cwd()


def get_dylib_path() -> Path:
    """Get the path to the dylib (in cache or local)."""
    # Default location: ~/.local/share/subcursor
    default_dir = Path.home() / ".local" / "share" / "subcursor"
    default_dylib = default_dir / "libcursor_redirect.dylib"

    # First check default location
    if default_dylib.exists():
        return default_dylib

    # Check local directory (for development)
    local_dylib = Path.cwd() / "libcursor_redirect.dylib"
    if local_dylib.exists():
        return local_dylib

    # Check in package directory (for uvx)
    package_dylib = get_package_root() / "libcursor_redirect.dylib"
    if package_dylib.exists():
        return package_dylib

    # Default to ~/.local/share/subcursor for new compilation
    return default_dylib


def compile_dylib(force: bool = False) -> Path:
    """Compile the dylib if needed."""
    dylib_path = get_dylib_path()
    package_root = get_package_root()
    c_source = package_root / "redirect_interpose.c"

    # Check if we need to compile
    if dylib_path.exists() and not force:
        return dylib_path

    print("🔨 Compiling dylib for cursor-agent interception...")

    # Verify clang is available
    try:
        subprocess.run(["clang", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: clang not found. Please install Xcode Command Line Tools:")
        print("   xcode-select --install")
        sys.exit(1)

    # Verify source file exists
    if not c_source.exists():
        print(f"❌ Error: Source file not found: {c_source}")
        sys.exit(1)

    # Create directory if needed
    dylib_path.parent.mkdir(parents=True, exist_ok=True)

    # Compile
    try:
        cmd = [
            "clang",
            "-arch", "arm64e",
            "-dynamiclib",
            "-o", str(dylib_path),
            str(c_source)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        # Code sign
        subprocess.run(
            ["codesign", "-s", "-", "-f", str(dylib_path)],
            check=True,
            capture_output=True
        )

        print(f"✅ Dylib compiled: {dylib_path}")
        return dylib_path

    except subprocess.CalledProcessError as e:
        print(f"❌ Error compiling dylib: {e}")
        if e.stderr:
            print(e.stderr.decode())
        sys.exit(1)


def run_mcp_server():
    """Run the MCP server."""
    dylib_path = compile_dylib()

    # Set environment variable so the MCP server knows where the dylib is
    os.environ["SUBCURSOR_DYLIB_PATH"] = str(dylib_path)

    # Import and run the server
    from . import main as server_main
    import asyncio

    print(f"🚀 Starting subcursor MCP server...")
    print(f"   Dylib: {dylib_path}")
    print(f"   Project: {get_project_root()}")
    print()

    asyncio.run(server_main())


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="subcursor - Specialized AI subagents for Cursor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uvx subcursor              # Run MCP server
  uvx subcursor --compile    # Force recompile dylib
  uvx subcursor --version    # Show version

For more information: https://github.com/yourusername/subcursor
"""
    )

    parser.add_argument(
        "--compile",
        action="store_true",
        help="Force recompile the dylib"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="subcursor 0.1.0"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if dylib is compiled and ready"
    )

    args = parser.parse_args()

    if args.check:
        dylib_path = get_dylib_path()
        if dylib_path.exists():
            print(f"✅ Dylib ready: {dylib_path}")
            sys.exit(0)
        else:
            print(f"❌ Dylib not found: {dylib_path}")
            print("   Run 'uvx subcursor --compile' to build it")
            sys.exit(1)

    if args.compile:
        compile_dylib(force=True)
        print("✅ Compilation complete!")
        sys.exit(0)

    # Default: run MCP server
    run_mcp_server()


if __name__ == "__main__":
    main()

