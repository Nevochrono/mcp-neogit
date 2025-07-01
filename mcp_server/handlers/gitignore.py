"""Gitignore creation handler for MCP server."""

import requests
from pathlib import Path
from typing import List
from ..models import CreateGitignoreRequest, CreateGitignoreResponse


class GitignoreGenerator:
    """Gitignore generation functionality copied from neogit."""
    
    def __init__(self):
        self.required_patterns = ['mcp_client.config', '.env', '*.secret', '.venv', 'node_modules']
    
    def create_gitignore(self, project_path: str, technologies: str = None, include_defaults: bool = True) -> str:
        """Create a .gitignore file for the project."""
        project_path = Path(project_path)
        
        # Try to detect language if not provided
        if not technologies:
            try:
                from .analysis import ProjectAnalyzer
                analyzer = ProjectAnalyzer(project_path)
                project_info = analyzer.analyze()
                detected = project_info.language.lower() if project_info.language else "python"
            except Exception:
                detected = "python"
            technologies = detected
        
        # Fetch .gitignore from gitignore.io
        url = f"https://www.toptal.com/developers/gitignore/api/{technologies}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text.rstrip()
                
                # Always append required patterns if not present
                if include_defaults:
                    for pattern in self.required_patterns:
                        if pattern not in content:
                            content += f"\n{pattern}"
                
                content += '\n'
                return content
            else:
                # Fallback to basic .gitignore
                return self._create_basic_gitignore(technologies, include_defaults)
                
        except Exception:
            # Fallback to basic .gitignore
            return self._create_basic_gitignore(technologies, include_defaults)
    
    def _create_basic_gitignore(self, technologies: str, include_defaults: bool) -> str:
        """Create a basic .gitignore when gitignore.io is unavailable."""
        content = "# Basic .gitignore file\n\n"
        
        # Add technology-specific patterns
        tech_list = [tech.strip().lower() for tech in technologies.split(',')]
        
        for tech in tech_list:
            if tech in ['python', 'py']:
                content += self._get_python_patterns()
            elif tech in ['javascript', 'js', 'typescript', 'ts', 'node']:
                content += self._get_javascript_patterns()
            elif tech in ['java']:
                content += self._get_java_patterns()
            elif tech in ['go']:
                content += self._get_go_patterns()
            elif tech in ['rust']:
                content += self._get_rust_patterns()
            elif tech in ['php']:
                content += self._get_php_patterns()
            elif tech in ['ruby']:
                content += self._get_ruby_patterns()
            elif tech in ['c', 'cpp', 'c++']:
                content += self._get_cpp_patterns()
        
        # Add default patterns
        if include_defaults:
            content += self._get_default_patterns()
        
        return content
    
    def _get_python_patterns(self) -> str:
        """Get Python-specific .gitignore patterns."""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

"""
    
    def _get_javascript_patterns(self) -> str:
        """Get JavaScript/Node.js-specific .gitignore patterns."""
        return """# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
jspm_packages/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test

# parcel-bundler cache
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

"""
    
    def _get_java_patterns(self) -> str:
        """Get Java-specific .gitignore patterns."""
        return """# Java
*.class

# Log file
*.log

# BlueJ files
*.ctxt

# Mobile Tools for Java (J2ME)
.mtj.tmp/

# Package Files #
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# virtual machine crash logs
hs_err_pid*
replay_pid*

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/timing.properties
.mvn/wrapper/maven-wrapper.jar

# Gradle
.gradle
build/

# IntelliJ IDEA
.idea/
*.iws
*.iml
*.ipr

# Eclipse
.apt_generated
.classpath
.factorypath
.project
.settings
.springBeans
.sts4-cache

"""
    
    def _get_go_patterns(self) -> str:
        """Get Go-specific .gitignore patterns."""
        return """# Go
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Output of the go coverage tool
*.out

# Dependency directories
vendor/

# Go workspace file
go.work

# Build output
bin/
dist/

"""
    
    def _get_rust_patterns(self) -> str:
        """Get Rust-specific .gitignore patterns."""
        return """# Rust
target/
Cargo.lock

# Remove Cargo.lock from gitignore if creating an executable
# Cargo.lock

# These are backup files generated by rustfmt
**/*.rs.bk

# MSVC Windows builds of rustc generate these, which store debugging information
*.pdb

"""
    
    def _get_php_patterns(self) -> str:
        """Get PHP-specific .gitignore patterns."""
        return """# PHP
/vendor/
composer.phar
composer.lock

# Environment files
.env
.env.local
.env.production

# IDE files
.idea/
.vscode/

# Logs
*.log

# Cache
cache/
tmp/

"""
    
    def _get_ruby_patterns(self) -> str:
        """Get Ruby-specific .gitignore patterns."""
        return """# Ruby
*.gem
*.rbc
/.config
/coverage/
/InstalledFiles
/pkg/
/spec/reports/
/spec/examples.txt
/test/tmp/
/test/version_tmp/
/tmp/

# Ignore all logfiles and tempfiles.
/log/*
/tmp/*
!/log/.keep
!/tmp/.keep

# Ignore pidfiles, but keep the directory.
/tmp/pids/*
!/tmp/pids/
!/tmp/pids/.keep

# Ignore uploaded files in development.
/storage/*
!/storage/.keep
/tmp/storage/*
!/tmp/storage/
!/tmp/storage/.keep

# Ignore master key for decrypting credentials and more.
/config/master.key

# Ignore application configuration
/config/application.yml

"""
    
    def _get_cpp_patterns(self) -> str:
        """Get C/C++-specific .gitignore patterns."""
        return """# C/C++
# Prerequisites
*.d

# Compiled Object files
*.slo
*.lo
*.o
*.obj

# Precompiled Headers
*.gch
*.pch

# Compiled Dynamic libraries
*.so
*.dylib
*.dll

# Fortran module files
*.mod
*.smod

# Compiled Static libraries
*.lai
*.la
*.a
*.lib

# Executables
*.exe
*.out
*.app

# Build directories
build/
dist/
out/

# IDE files
.vscode/
.idea/
*.swp
*.swo

"""
    
    def _get_default_patterns(self) -> str:
        """Get default .gitignore patterns."""
        return """# Default patterns
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor directories and files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log

# Secrets and config files
.env
*.secret
mcp_client.config

# Virtual environments
.venv
venv/
env/

# Dependencies
node_modules/

"""
    
    def save_gitignore(self, project_path: str, content: str) -> str:
        """Save the .gitignore file to the project directory."""
        project_path = Path(project_path)
        gitignore_path = project_path / '.gitignore'
        
        with open(gitignore_path, 'w') as f:
            f.write(content)
        
        return str(gitignore_path)


async def create_gitignore(request: CreateGitignoreRequest) -> CreateGitignoreResponse:
    """Handle .gitignore creation request."""
    try:
        generator = GitignoreGenerator()
        
        # Create .gitignore content
        gitignore_content = generator.create_gitignore(
            project_path=request.project_path,
            technologies=request.technologies,
            include_defaults=request.include_defaults
        )
        
        # Save the file
        file_path = generator.save_gitignore(request.project_path, gitignore_content)
        
        return CreateGitignoreResponse(
            success=True,
            gitignore_content=gitignore_content,
            file_path=file_path
        )
        
    except Exception as e:
        return CreateGitignoreResponse(
            success=False,
            error=f"Gitignore creation failed: {str(e)}"
        ) 