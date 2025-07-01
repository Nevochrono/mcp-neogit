"""Data models for MCP server requests and responses."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path
from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    """Project information model."""
    name: str
    description: str
    language: str
    framework: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)
    structure: Dict[str, Any] = Field(default_factory=dict)
    has_tests: bool = False
    has_docs: bool = False
    has_license: bool = False
    has_requirements: bool = False


class AnalyzeProjectRequest(BaseModel):
    """Request model for project analysis."""
    project_path: str
    include_files: bool = True
    include_dependencies: bool = True


class AnalyzeProjectResponse(BaseModel):
    """Response model for project analysis."""
    success: bool
    project_info: Optional[ProjectInfo] = None
    error: Optional[str] = None


class GenerateReadmeRequest(BaseModel):
    """Request model for README generation."""
    project_path: str
    readme_type: str = "advanced"  # simple, advanced, installation
    ai_provider: str = "openai"
    config: Dict[str, Any] = Field(default_factory=dict)


class GenerateReadmeResponse(BaseModel):
    """Response model for README generation."""
    success: bool
    readme_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class CreateGitignoreRequest(BaseModel):
    """Request model for .gitignore creation."""
    project_path: str
    technologies: Optional[str] = None
    include_defaults: bool = True


class CreateGitignoreResponse(BaseModel):
    """Response model for .gitignore creation."""
    success: bool
    gitignore_content: Optional[str] = None
    file_path: Optional[str] = None
    error: Optional[str] = None


class DeployGitHubRequest(BaseModel):
    """Request model for GitHub deployment."""
    project_path: str
    github_username: str
    github_token: str
    branch: str = "main"
    private: bool = False
    readme_content: Optional[str] = None


class DeployGitHubResponse(BaseModel):
    """Response model for GitHub deployment."""
    success: bool
    repository_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    uptime: float
    ai_providers: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None 