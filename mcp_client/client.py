"""MCP Client for NeoGit."""

import httpx
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

from .config import MCPClientConfig
from .exceptions import MCPClientError, MCPConnectionError


class MCPClient:
    """Client for communicating with NeoGit MCP server."""
    
    def __init__(self, config: Optional[MCPClientConfig] = None):
        self.config = config or MCPClientConfig()
        self.base_url = f"http://{self.config.host}:{self.config.port}"
        self.headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
            except httpx.HTTPStatusError as e:
                raise MCPClientError(f"Health check failed: {e}")
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze a project via MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "project_path": project_path,
                    "include_files": True,
                    "include_dependencies": True
                }
                response = await client.post(
                    f"{self.base_url}/mcp/analyze-project",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
            except httpx.HTTPStatusError as e:
                raise MCPClientError(f"Project analysis failed: {e}")
    
    async def generate_readme(
        self, 
        project_path: str, 
        readme_type: str = "advanced",
        ai_provider: str = "openai",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate README via MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "project_path": project_path,
                    "readme_type": readme_type,
                    "ai_provider": ai_provider,
                    "config": config or {}
                }
                response = await client.post(
                    f"{self.base_url}/mcp/generate-readme",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
            except httpx.HTTPStatusError as e:
                raise MCPClientError(f"README generation failed: {e}")
    
    async def create_gitignore(
        self, 
        project_path: str, 
        technologies: Optional[str] = None,
        include_defaults: bool = True
    ) -> Dict[str, Any]:
        """Create .gitignore via MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "project_path": project_path,
                    "technologies": technologies,
                    "include_defaults": include_defaults
                }
                response = await client.post(
                    f"{self.base_url}/mcp/create-gitignore",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
            except httpx.HTTPStatusError as e:
                raise MCPClientError(f"Gitignore creation failed: {e}")
    
    async def deploy_github(
        self,
        project_path: str,
        github_username: str,
        github_token: str,
        branch: str = "main",
        private: bool = False,
        readme_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deploy to GitHub via MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "project_path": project_path,
                    "github_username": github_username,
                    "github_token": github_token,
                    "branch": branch,
                    "private": private,
                    "readme_content": readme_content
                }
                response = await client.post(
                    f"{self.base_url}/mcp/deploy-github",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
            except httpx.HTTPStatusError as e:
                raise MCPClientError(f"GitHub deployment failed: {e}")
    
    async def get_providers(self) -> Dict[str, Any]:
        """Get available AI providers from MCP server."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/mcp/providers",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise MCPConnectionError(f"Failed to connect to MCP server: {e}")
            except httpx.HTTPStatusError as e:
                raise MCPClientError(f"Failed to get providers: {e}")


# Synchronous wrapper for easier use
class MCPClientSync:
    """Synchronous wrapper for MCP client."""
    
    def __init__(self, config: Optional[MCPClientConfig] = None):
        self.client = MCPClient(config)
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        return asyncio.run(self.client.health_check())
    
    def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze a project via MCP server."""
        return asyncio.run(self.client.analyze_project(project_path))
    
    def generate_readme(
        self, 
        project_path: str, 
        readme_type: str = "advanced",
        ai_provider: str = "openai",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate README via MCP server."""
        return asyncio.run(self.client.generate_readme(project_path, readme_type, ai_provider, config))
    
    def create_gitignore(
        self, 
        project_path: str, 
        technologies: Optional[str] = None,
        include_defaults: bool = True
    ) -> Dict[str, Any]:
        """Create .gitignore via MCP server."""
        return asyncio.run(self.client.create_gitignore(project_path, technologies, include_defaults))
    
    def deploy_github(
        self,
        project_path: str,
        github_username: str,
        github_token: str,
        branch: str = "main",
        private: bool = False,
        readme_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deploy to GitHub via MCP server."""
        return asyncio.run(self.client.deploy_github(project_path, github_username, github_token, branch, private, readme_content))
    
    def get_providers(self) -> Dict[str, Any]:
        """Get available AI providers from MCP server."""
        return asyncio.run(self.client.get_providers()) 