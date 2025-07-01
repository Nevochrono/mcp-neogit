"""GitHub deployment handler for MCP server."""

import base64
import os
import mimetypes
from pathlib import Path
from typing import List, Tuple
from github import Github, InputGitTreeElement
from ..models import DeployGitHubRequest, DeployGitHubResponse


class GitHubManager:
    """GitHub deployment functionality copied from neogit."""
    
    EXCLUDE_PATTERNS = ['.git', 'node_modules', '__pycache__', 'venv', '.DS_Store', '.mypy_cache']
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    
    def __init__(self, token: str, username: str):
        self.token = token
        self.username = username
        self.client = Github(token)
    
    def deploy_project(self, project_path: str, readme_content: str = None, branch: str = 'main', private: bool = False) -> dict:
        """Deploy project to GitHub."""
        project_path = Path(project_path)
        
        # Analyze project to get info
        from .analysis import ProjectAnalyzer
        analyzer = ProjectAnalyzer(project_path)
        project_info = analyzer.analyze()
        
        repo_name = project_info.name.replace(' ', '-').replace('_', '-')
        repo_name = ''.join(c for c in repo_name if c.isalnum() or c in '-_')
        
        # Get or create repository
        repo = self._get_or_create_repo(repo_name, project_info.description, private=private)
        if not repo:
            return {
                "success": False,
                "error": f"Failed to get or create repository: {repo_name}"
            }
        
        # Upload files
        result = self._upload_files(repo, project_path, readme_content, branch=branch)
        
        return {
            "success": True,
            "repository_url": repo.html_url,
            "repository_name": repo_name,
            "branch": branch,
            "private": private,
            "files_uploaded": result.get("files_uploaded", 0),
            "files_skipped": result.get("files_skipped", 0)
        }
    
    def _get_or_create_repo(self, repo_name: str, description: str, private: bool = False):
        """Get existing repository or create a new one."""
        user = self.client.get_user()
        try:
            repo = user.get_repo(repo_name)
            return repo
        except Exception:
            try:
                repo = user.create_repo(
                    name=repo_name,
                    description=description,
                    private=private
                )
                return repo
            except Exception as e:
                return None
    
    def _upload_files(self, repo, project_path: Path, readme_content: str = None, branch: str = 'main') -> dict:
        """Upload project files to GitHub."""
        # Gather all files to upload
        files_to_upload = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_PATTERNS and not d.startswith('.')]
            for file in files:
                if file.startswith('.') or file in self.EXCLUDE_PATTERNS:
                    continue
                file_path = Path(root) / file
                rel_path = file_path.relative_to(project_path)
                if file_path.stat().st_size > self.MAX_FILE_SIZE:
                    continue
                files_to_upload.append((file_path, str(rel_path)))
        
        # Ensure branch exists
        try:
            ref = repo.get_git_ref(f'heads/{branch}')
            latest_commit = repo.get_git_commit(ref.object.sha)
            base_tree = repo.get_git_tree(latest_commit.tree.sha)
        except Exception as e:
            # Handle empty repository
            if hasattr(e, 'status') and e.status == 409 or 'Git Repository is empty' in str(e):
                # Create initial commit with README
                if readme_content:
                    repo.create_file('README.md', "Initial commit: README.md", readme_content, branch=branch)
                else:
                    # Find existing README file
                    readme_tuple = next(((fp, rp) for fp, rp in files_to_upload if str(rp).lower() == 'readme.md'), None)
                    if readme_tuple:
                        file_path, rel_path = readme_tuple
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            repo.create_file(rel_path, f"Initial commit: {rel_path}", content.decode('utf-8'), branch=branch)
                        files_to_upload = [t for t in files_to_upload if t != readme_tuple]
                    else:
                        # Create empty README
                        repo.create_file('README.md', "Initial commit: README.md", "# " + project_path.name, branch=branch)
                
                # Re-fetch refs after initial commit
                ref = repo.get_git_ref(f'heads/{branch}')
                latest_commit = repo.get_git_commit(ref.object.sha)
                base_tree = repo.get_git_tree(latest_commit.tree.sha)
            else:
                # Branch does not exist, create it
                try:
                    master_ref = repo.get_git_ref('heads/main')
                except Exception:
                    master_ref = repo.get_git_ref(f'heads/{repo.default_branch}')
                ref = repo.create_git_ref(ref=f'refs/heads/{branch}', sha=master_ref.object.sha)
                latest_commit = repo.get_git_commit(master_ref.object.sha)
                base_tree = repo.get_git_tree(latest_commit.tree.sha)
        
        # Upload files
        files_uploaded = 0
        files_skipped = 0
        tree_elements = []
        
        for file_path, rel_path in files_to_upload:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    mime, _ = mimetypes.guess_type(file_path)
                    is_bin = self._is_binary(content)
                    
                    if is_bin:
                        # Handle binary files
                        blob = repo.create_git_blob(base64.b64encode(content).decode('utf-8'), 'base64')
                        tree_elements.append(InputGitTreeElement(rel_path, '100644', 'blob', sha=blob.sha))
                    else:
                        # Handle text files
                        try:
                            contents = repo.get_contents(rel_path, ref=branch)
                            # File exists, update
                            repo.update_file(rel_path, f"Update {rel_path}", content.decode('utf-8'), contents.sha, branch=branch)
                        except Exception as e:
                            if '404' in str(e) or 'Not Found' in str(e):
                                # File does not exist, create
                                repo.create_file(rel_path, f"Add {rel_path}", content.decode('utf-8'), branch=branch)
                            else:
                                raise e
                    
                    files_uploaded += 1
                    
            except Exception as e:
                files_skipped += 1
                continue
        
        # Commit binary files if any
        if tree_elements:
            try:
                # Re-fetch latest commit/tree for branch after text file updates
                ref = repo.get_git_ref(f'heads/{branch}')
                latest_commit = repo.get_git_commit(ref.object.sha)
                base_tree = repo.get_git_tree(latest_commit.tree.sha)
                new_tree = repo.create_git_tree(tree_elements, base_tree)
                commit_message = "Add/update binary files"
                new_commit = repo.create_git_commit(commit_message, new_tree, [latest_commit])
                ref.edit(new_commit.sha)
            except Exception as e:
                pass
        
        return {
            "files_uploaded": files_uploaded,
            "files_skipped": files_skipped
        }
    
    def _is_binary(self, content: bytes) -> bool:
        """Check if content is binary."""
        # Check for null bytes
        if b'\x00' in content:
            return True
        
        # Check for common text encodings
        try:
            content.decode('utf-8')
            return False
        except UnicodeDecodeError:
            return True


async def deploy_github(request: DeployGitHubRequest) -> DeployGitHubResponse:
    """Handle GitHub deployment request."""
    try:
        # Create GitHub manager
        github_manager = GitHubManager(
            token=request.github_token,
            username=request.github_username
        )
        
        # Deploy project
        result = github_manager.deploy_project(
            project_path=request.project_path,
            readme_content=request.readme_content,
            branch=request.branch,
            private=request.private
        )
        
        if result["success"]:
            return DeployGitHubResponse(
                success=True,
                repository_url=result["repository_url"],
                metadata={
                    "repository_name": result["repository_name"],
                    "branch": result["branch"],
                    "private": result["private"],
                    "files_uploaded": result["files_uploaded"],
                    "files_skipped": result["files_skipped"]
                }
            )
        else:
            return DeployGitHubResponse(
                success=False,
                error=result["error"]
            )
        
    except Exception as e:
        return DeployGitHubResponse(
            success=False,
            error=f"GitHub deployment failed: {str(e)}"
        ) 