"""CLI entry point for lokalise-mcp.

This module allows the package to be run as:
- lokalise-mcp (via console_scripts entry point)
- python -m lokalise_mcp
- uvx lokalise-mcp
"""

from .server import main

if __name__ == "__main__":
    main()
