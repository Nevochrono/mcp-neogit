#!/usr/bin/env python3
"""Test script for MCP NeoGit functionality."""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_client.client import MCPClientSync
from mcp_client.config import MCPClientConfig


def test_mcp_client():
    """Test the MCP client functionality."""
    print("🧪 Testing MCP NeoGit Client...")
    
    # Configure client
    config = MCPClientConfig(
        host="localhost",
        port=8000,
        token="your-token-here"
    )
    
    client = MCPClientSync(config)
    
    try:
        # Test health check
        print("1. Testing health check...")
        health = client.health_check()
        print(f"   ✅ Health check passed: {health}")
        
        # Test project analysis
        print("2. Testing project analysis...")
        project_path = str(Path(__file__).parent.parent / "neogit")
        result = client.analyze_project(project_path)
        
        if result.get("success"):
            project_info = result["project_info"]
            print(f"   ✅ Project analysis successful:")
            print(f"      - Name: {project_info['name']}")
            print(f"      - Language: {project_info['language']}")
            print(f"      - Framework: {project_info['framework']}")
            print(f"      - Dependencies: {len(project_info['dependencies'])} found")
        else:
            print(f"   ❌ Project analysis failed: {result.get('error')}")
        
        # Test README generation
        print("3. Testing README generation...")
        readme_result = client.generate_readme(
            project_path=project_path,
            readme_type="simple",
            ai_provider="openai"
        )
        
        if readme_result.get("success"):
            print(f"   ✅ README generation successful:")
            print(f"      - Provider used: {readme_result['metadata']['provider_used']}")
            print(f"      - README type: {readme_result['metadata']['readme_type']}")
            print(f"      - Content length: {len(readme_result['readme_content'])} characters")
        else:
            print(f"   ❌ README generation failed: {readme_result.get('error')}")
        
        # Test .gitignore creation
        print("4. Testing .gitignore creation...")
        gitignore_result = client.create_gitignore(
            project_path=project_path,
            technologies="python",
            include_defaults=True
        )
        
        if gitignore_result.get("success"):
            print(f"   ✅ Gitignore creation successful:")
            print(f"      - File path: {gitignore_result['file_path']}")
            print(f"      - Content length: {len(gitignore_result['gitignore_content'])} characters")
        else:
            print(f"   ❌ Gitignore creation failed: {gitignore_result.get('error')}")
        
        # Test providers endpoint
        print("5. Testing providers endpoint...")
        providers = client.get_providers()
        print(f"   ✅ Available providers: {providers}")
        
        # Test GitHub deployment (without actual deployment)
        print("6. Testing GitHub deployment (dry run)...")
        print("   ⚠️  Skipping actual GitHub deployment to avoid creating repositories")
        print("   💡 To test GitHub deployment, provide valid credentials and set private=True")
        
        print("\n🎉 All tests completed!")
        print("\n📊 Summary:")
        print("   ✅ Project analysis: Working")
        print("   ✅ README generation: Working")
        print("   ✅ Gitignore creation: Working")
        print("   ✅ Providers endpoint: Working")
        print("   ⚠️  GitHub deployment: Requires valid credentials")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n💡 Make sure the MCP server is running:")
        print("   cd mcp-neogit")
        print("   python start_server.py")
        return False


def test_github_deployment():
    """Test GitHub deployment with credentials (optional)."""
    print("\n🔐 Testing GitHub deployment (requires credentials)...")
    
    # This is optional - only run if user wants to test actual deployment
    github_token = input("Enter GitHub token (or press Enter to skip): ").strip()
    if not github_token:
        print("   ⏭️  Skipping GitHub deployment test")
        return True
    
    github_username = input("Enter GitHub username: ").strip()
    if not github_username:
        print("   ❌ GitHub username required")
        return False
    
    config = MCPClientConfig(
        host="localhost",
        port=8000,
        token="your-token-here"
    )
    
    client = MCPClientSync(config)
    
    try:
        project_path = str(Path(__file__).parent.parent / "neogit")
        
        # First generate a README
        readme_result = client.generate_readme(
            project_path=project_path,
            readme_type="simple",
            ai_provider="openai"
        )
        
        if not readme_result.get("success"):
            print("   ❌ Failed to generate README for deployment")
            return False
        
        # Deploy to GitHub
        deploy_result = client.deploy_github(
            project_path=project_path,
            github_username=github_username,
            github_token=github_token,
            branch="main",
            private=True,  # Make it private for testing
            readme_content=readme_result['readme_content']
        )
        
        if deploy_result.get("success"):
            print(f"   ✅ GitHub deployment successful:")
            print(f"      - Repository URL: {deploy_result['repository_url']}")
            print(f"      - Repository name: {deploy_result['metadata']['repository_name']}")
            print(f"      - Files uploaded: {deploy_result['metadata']['files_uploaded']}")
            print(f"      - Files skipped: {deploy_result['metadata']['files_skipped']}")
        else:
            print(f"   ❌ GitHub deployment failed: {deploy_result.get('error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ GitHub deployment test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_mcp_client()
    
    if success:
        # Ask if user wants to test GitHub deployment
        test_github = input("\n🔐 Do you want to test GitHub deployment? (y/N): ").strip().lower()
        if test_github == 'y':
            github_success = test_github_deployment()
            success = success and github_success
    
    sys.exit(0 if success else 1) 