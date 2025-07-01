"""MCP Server for NeoGit - FastAPI implementation."""

import time
import os
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from .models import (
    AnalyzeProjectRequest, AnalyzeProjectResponse,
    GenerateReadmeRequest, GenerateReadmeResponse,
    CreateGitignoreRequest, CreateGitignoreResponse,
    DeployGitHubRequest, DeployGitHubResponse,
    HealthResponse, ErrorResponse
)
from .handlers.analysis import analyze_project
from .handlers.readme import generate_readme
from .handlers.gitignore import create_gitignore
from .handlers.github import deploy_github
from .utils.config import get_server_config

# Security
security = HTTPBearer()

# Server startup time
STARTUP_TIME = time.time()

# Create FastAPI app
app = FastAPI(
    title="NeoGit MCP Server",
    description="Model Context Protocol server for NeoGit functionality",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify the authentication token."""
    config = get_server_config()
    expected_token = config.get("auth_token", "your-token-here")
    
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return True


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    config = get_server_config()
    ai_providers = config.get("ai_providers", [])
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        uptime=time.time() - STARTUP_TIME,
        ai_providers=ai_providers
    )


@app.post("/mcp/analyze-project", response_model=AnalyzeProjectResponse)
async def handle_analyze_project(
    request: AnalyzeProjectRequest,
    _: bool = Depends(verify_token)
):
    """Handle project analysis request."""
    return await analyze_project(request)


@app.post("/mcp/generate-readme", response_model=GenerateReadmeResponse)
async def handle_generate_readme(
    request: GenerateReadmeRequest,
    _: bool = Depends(verify_token)
):
    """Handle README generation request."""
    return await generate_readme(request)


@app.post("/mcp/create-gitignore", response_model=CreateGitignoreResponse)
async def handle_create_gitignore(
    request: CreateGitignoreRequest,
    _: bool = Depends(verify_token)
):
    """Handle .gitignore creation request."""
    return await create_gitignore(request)


@app.post("/mcp/deploy-github", response_model=DeployGitHubResponse)
async def handle_deploy_github(
    request: DeployGitHubRequest,
    _: bool = Depends(verify_token)
):
    """Handle GitHub deployment request."""
    return await deploy_github(request)


@app.get("/mcp/providers")
async def get_available_providers(_: bool = Depends(verify_token)):
    """Get available AI providers."""
    config = get_server_config()
    return {
        "providers": config.get("ai_providers", []),
        "default": config.get("default_provider", "openai")
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return ErrorResponse(
        error=str(exc),
        error_code="INTERNAL_ERROR",
        details={"path": str(request.url)}
    )


def run_server(host: str = "localhost", port: int = 8000, reload: bool = False):
    """Run the MCP server."""
    uvicorn.run(
        "mcp_server.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_server() 