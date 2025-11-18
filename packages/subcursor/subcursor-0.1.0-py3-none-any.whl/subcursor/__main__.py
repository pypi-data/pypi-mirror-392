#!/usr/bin/env python3
"""Entry point for running the subcursor MCP server."""

import asyncio
from . import main

if __name__ == "__main__":
    asyncio.run(main())

