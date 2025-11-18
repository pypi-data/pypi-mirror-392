"""
Entry point for running bookmark-lens as a module.

Usage:
    python -m bookmark_lens                    # Runs in stdio mode (default)
    python -m bookmark_lens --transport http   # Runs in HTTP mode
    python -m bookmark_lens --transport http --port 8080  # Custom port
"""

from .server import run

if __name__ == "__main__":
    run()
