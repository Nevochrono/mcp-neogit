#!/usr/bin/env python3
"""
Complete MCP NeoGit Workflow Example

This script demonstrates the full workflow:
1. Analyze a project
2. Generate a README
3. Create a .gitignore
4. Deploy to GitHub

Usage:
    python example_workflow.py /path/to/your/project
"""

import sys
import os
from pathlib import Path
from mcp_client.client import MCPClientSync
from mcp_client.config import MCPClientConfig


def main():
    """Run the complete MCP workflow."""
    if len(sys.argv) != 2:
        print("Usage: python example_workflow.py /path/to/your/project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    if not Path(project_path).exists():
        print(f"Error: Project path '{project_path}' does not exist")
        sys.exit(1)
    
    print("🚀 Starting MCP NeoGit Workflow...")
    print(f"📁 Project: {project_path}")
    print()
    
    # Configure MCP client
    config = MCPClientConfig(
        host="localhost",
        port=8000,
        token="your-token-here"
    )
    
    client = MCPClientSync(config)
    
    try:
        # Step 1: Analyze the project
        print("1️⃣  Analyzing project structure...")
        analysis_result = client.analyze_project(project_path)
        
        if not analysis_result.get("success"):
            print(f"❌ Analysis failed: {analysis_result.get('error')}")
            sys.exit(1)
        
        project_info = analysis_result["project_info"]
        print(f"   ✅ Project: {project_info['name']}")
        print(f"   ✅ Language: {project_info['language']}")
        print(f"   ✅ Framework: {project_info['framework'] or 'None'}")
        print(f"   ✅ Dependencies: {len(project_info['dependencies'])} found")
        print()
        
        # Step 2: Generate README
        print("2️⃣  Generating README...")
        readme_result = client.generate_readme(
            project_path=project_path,
            readme_type="advanced",
            ai_provider="openai"
        )
        
        if not readme_result.get("success"):
            print(f"❌ README generation failed: {readme_result.get('error')}")
            print("   💡 This might be due to missing AI provider configuration")
            print("   💡 The server will use template-based generation as fallback")
            # Continue with template generation
            readme_result = client.generate_readme(
                project_path=project_path,
                readme_type="simple",
                ai_provider="template"
            )
        
        if readme_result.get("success"):
            print(f"   ✅ README generated successfully")
            print(f"   ✅ Provider: {readme_result['metadata']['provider_used']}")
            print(f"   ✅ Type: {readme_result['metadata']['readme_type']}")
            print(f"   ✅ Length: {len(readme_result['readme_content'])} characters")
        else:
            print(f"❌ README generation failed: {readme_result.get('error')}")
            sys.exit(1)
        
        print()
        
        # Step 3: Create .gitignore
        print("3️⃣  Creating .gitignore...")
        gitignore_result = client.create_gitignore(
            project_path=project_path,
            technologies=project_info['language'].lower(),
            include_defaults=True
        )
        
        if gitignore_result.get("success"):
            print(f"   ✅ .gitignore created successfully")
            print(f"   ✅ File: {gitignore_result['file_path']}")
            print(f"   ✅ Length: {len(gitignore_result['gitignore_content'])} characters")
        else:
            print(f"❌ .gitignore creation failed: {gitignore_result.get('error')}")
            sys.exit(1)
        
        print()
        
        # Step 4: Deploy to GitHub (optional)
        print("4️⃣  GitHub Deployment")
        deploy_to_github = input("   Deploy to GitHub? (y/N): ").strip().lower()
        
        if deploy_to_github == 'y':
            github_username = input("   GitHub username: ").strip()
            github_token = input("   GitHub token: ").strip()
            make_private = input("   Make repository private? (y/N): ").strip().lower() == 'y'
            
            if not github_username or not github_token:
                print("   ❌ GitHub credentials required for deployment")
                print("   💡 Skipping GitHub deployment")
            else:
                print("   🚀 Deploying to GitHub...")
                deploy_result = client.deploy_github(
                    project_path=project_path,
                    github_username=github_username,
                    github_token=github_token,
                    branch="main",
                    private=make_private,
                    readme_content=readme_result['readme_content']
                )
                
                if deploy_result.get("success"):
                    print(f"   ✅ Deployment successful!")
                    print(f"   ✅ Repository: {deploy_result['repository_url']}")
                    print(f"   ✅ Files uploaded: {deploy_result['metadata']['files_uploaded']}")
                    print(f"   ✅ Files skipped: {deploy_result['metadata']['files_skipped']}")
                else:
                    print(f"   ❌ Deployment failed: {deploy_result.get('error')}")
        else:
            print("   ⏭️  Skipping GitHub deployment")
        
        print()
        print("🎉 Workflow completed successfully!")
        print()
        print("📊 Summary:")
        print(f"   📁 Project: {project_info['name']}")
        print(f"   🐍 Language: {project_info['language']}")
        print(f"   📝 README: Generated ({readme_result['metadata']['readme_type']} type)")
        print(f"   🚫 .gitignore: Created")
        if deploy_to_github == 'y':
            print(f"   🚀 GitHub: Deployed")
        else:
            print(f"   🚀 GitHub: Skipped")
        
        # Save README to file
        readme_path = Path(project_path) / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_result['readme_content'])
        print(f"   💾 README saved to: {readme_path}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        print("\n💡 Make sure the MCP server is running:")
        print("   cd mcp-neogit")
        print("   python start_server.py")
        sys.exit(1)


if __name__ == "__main__":
    main() 