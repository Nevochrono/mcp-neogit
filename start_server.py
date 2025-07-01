#!/usr/bin/env python3
"""Start the MCP NeoGit server."""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.server import run_server


def main():
    """Start the MCP server."""
    print("🚀 Starting MCP NeoGit Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔑 Default token: your-token-here")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Set default environment variables if not set
    if not os.getenv("MCP_HOST"):
        os.environ["MCP_HOST"] = "localhost"
    if not os.getenv("MCP_PORT"):
        os.environ["MCP_PORT"] = "8000"
    if not os.getenv("MCP_AUTH_TOKEN"):
        os.environ["MCP_AUTH_TOKEN"] = "your-token-here"
    
    try:
        run_server(
            host=os.getenv("MCP_HOST", "localhost"),
            port=int(os.getenv("MCP_PORT", "8000")),
            reload=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 