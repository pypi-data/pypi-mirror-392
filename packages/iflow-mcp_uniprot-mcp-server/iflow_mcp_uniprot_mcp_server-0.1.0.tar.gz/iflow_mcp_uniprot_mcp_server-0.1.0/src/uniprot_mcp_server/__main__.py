"""Main entry point for uniprot_mcp_server module."""

import asyncio
from . import server

if __name__ == "__main__":
    asyncio.run(server.main())
