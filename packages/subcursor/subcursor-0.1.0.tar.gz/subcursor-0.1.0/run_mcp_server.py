#!/usr/bin/env python3
"""Standalone entry point for the subcursor MCP server."""

import asyncio
from subcursor import main

if __name__ == "__main__":
    asyncio.run(main())

