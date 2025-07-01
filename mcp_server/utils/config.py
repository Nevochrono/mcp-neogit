"""Configuration utilities for MCP server."""

import os
import json
from pathlib import Path
from typing import Dict, Any


def get_server_config() -> Dict[str, Any]:
    """Get server configuration from environment or config file."""
    config = {
        "auth_token": os.getenv("MCP_AUTH_TOKEN", "your-token-here"),
        "ai_providers": ["openai", "anthropic", "google", "huggingface", "ollama"],
        "default_provider": "openai",
        "host": os.getenv("MCP_HOST", "localhost"),
        "port": int(os.getenv("MCP_PORT", "8000")),
        "log_level": os.getenv("MCP_LOG_LEVEL", "info"),
    }
    
    # Try to load from config file
    config_file = Path("mcp_server_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception:
            pass
    
    return config


def save_server_config(config: Dict[str, Any]) -> bool:
    """Save server configuration to file."""
    try:
        config_file = Path("mcp_server_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False 