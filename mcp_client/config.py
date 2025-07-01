"""Configuration for MCP client."""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class MCPClientConfig:
    """Configuration for MCP client."""
    host: str = "localhost"
    port: int = 8000
    token: str = "your-token-here"
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> "MCPClientConfig":
        """Create config from environment variables."""
        return cls(
            host=os.getenv("MCP_HOST", "localhost"),
            port=int(os.getenv("MCP_PORT", "8000")),
            token=os.getenv("MCP_TOKEN", "your-token-here"),
            timeout=int(os.getenv("MCP_TIMEOUT", "30"))
        )
    
    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> "MCPClientConfig":
        """Create config from file."""
        if config_path is None:
            config_path = "mcp_client_config.json"
        
        config_file = Path(config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                    return cls(**data)
            except Exception:
                pass
        
        return cls()
    
    def save_to_file(self, config_path: Optional[str] = None) -> bool:
        """Save config to file."""
        if config_path is None:
            config_path = "mcp_client_config.json"
        
        try:
            config_file = Path(config_path)
            with open(config_file, 'w') as f:
                json.dump(self.__dict__, f, indent=2)
            return True
        except Exception:
            return False 