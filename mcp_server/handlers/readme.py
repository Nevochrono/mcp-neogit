"""README generation handler for MCP server."""

import json
import openai
import anthropic
import google.generativeai as genai
import requests
from typing import Dict, Any, Optional
from ..models import ProjectInfo, GenerateReadmeRequest, GenerateReadmeResponse


class READMEGenerator:
    """README generation functionality copied from neogit."""
    
    SYSTEM_PROMPT = (
        "You are an expert technical writer and open source documentation specialist. "
        "Your job is to create clear, comprehensive, and engaging README.md files for software projects. "
        "You follow best practices for open source documentation, ensuring the README is well-structured, easy to navigate, and provides all essential information for users and contributors. "
        "You highlight the project's unique features, architecture, setup instructions, usage examples, contribution guidelines, and licensing. "
        "Always use professional Markdown formatting, include badges if relevant, and tailor the content to the project's language and framework. "
        "If the project is a library or API, include usage examples and API reference. "
        "If the project is an application, include screenshots or demo instructions if possible. "
        "Be concise but thorough, and make the README welcoming for both new users and contributors."
    )

    def __init__(self, ai_providers: Optional[Dict[str, Any]] = None, selected_provider: str = "openai"):
        self.ai_providers = ai_providers or {}
        self.selected_provider = selected_provider
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        self.hf_client = None
        self.ollama_client = None
        
        # Setup clients based on config
        prov = self.selected_provider
        if prov == "openai" and self.ai_providers.get("openai"):
            self.openai_client = openai.OpenAI(api_key=self.ai_providers["openai"].get("api_key"))
        elif prov == "anthropic" and self.ai_providers.get("anthropic"):
            self.anthropic_client = anthropic.Anthropic(api_key=self.ai_providers["anthropic"].get("api_key"))
        elif prov == "google" and self.ai_providers.get("google"):
            genai.configure(api_key=self.ai_providers["google"].get("api_key"))
            self.google_client = genai.GenerativeModel('gemini-pro')
        elif prov == "huggingface" and self.ai_providers.get("huggingface"):
            self.hf_client = requests.Session()
            self.hf_api_key = self.ai_providers["huggingface"].api_key
            self.hf_model = self.ai_providers["huggingface"].default_model
        elif prov == "ollama" and self.ai_providers.get("ollama"):
            self.ollama_client = requests.Session()
            self.ollama_endpoint = self.ai_providers["ollama"].get("endpoint")

    def generate_readme(self, project_info: ProjectInfo, readme_type: str = "advanced") -> str:
        """Generate README content using the selected AI provider."""
        prov = self.selected_provider
        if prov == "openai" and self.openai_client:
            return self._generate_openai_readme(project_info, readme_type)
        elif prov == "anthropic" and self.anthropic_client:
            return self._generate_anthropic_readme(project_info, readme_type)
        elif prov == "google" and self.google_client:
            return self._generate_google_readme(project_info, readme_type)
        elif prov == "huggingface" and self.hf_client:
            return self._generate_huggingface_readme(project_info, readme_type)
        elif prov == "ollama" and self.ollama_client:
            return self._generate_ollama_readme(project_info, readme_type)
        else:
            return self._generate_template_readme(project_info, readme_type)

    def _generate_openai_readme(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Generate README using OpenAI."""
        try:
            prompt = self._create_ai_prompt(project_info, readme_type)
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return self._generate_template_readme(project_info, readme_type)

    def _generate_anthropic_readme(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Generate README using Anthropic."""
        try:
            prompt = self._create_ai_prompt(project_info, readme_type)
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return self._generate_template_readme(project_info, readme_type)

    def _generate_google_readme(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Generate README using Google Gemini."""
        try:
            prompt = self._create_ai_prompt(project_info, readme_type)
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
            response = self.google_client.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return self._generate_template_readme(project_info, readme_type)

    def _generate_huggingface_readme(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Generate README using HuggingFace."""
        try:
            api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
            headers = {
                "Authorization": f"Bearer {self.hf_api_key}",
                "Content-Type": "application/json"
            }
            prompt = self._create_ai_prompt(project_info, readme_type)
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.95
                }
            }
            response = self.hf_client.post(api_url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', '')
                else:
                    return str(result)
            else:
                return self._generate_template_readme(project_info, readme_type)
        except Exception as e:
            return self._generate_template_readme(project_info, readme_type)

    def _generate_ollama_readme(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Generate README using Ollama."""
        try:
            prompt = self._create_ai_prompt(project_info, readme_type)
            full_prompt = f"{self.SYSTEM_PROMPT}\n\n{prompt}"
            api_url = f"{self.ollama_endpoint}/api/generate"
            payload = {
                "model": "codellama:7b-instruct",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "num_predict": 2000
                }
            }
            response = self.ollama_client.post(api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return self._generate_template_readme(project_info, readme_type)
        except Exception as e:
            return self._generate_template_readme(project_info, readme_type)

    def _create_ai_prompt(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Create the AI prompt for README generation."""
        prompt = f"""Create a professional README.md for the following project:

Project Name: {project_info.name}
Description: {project_info.description}
Language: {project_info.language}
Framework: {project_info.framework or 'None'}
Dependencies: {', '.join(project_info.dependencies[:10])}
Has Tests: {project_info.has_tests}
Has Documentation: {project_info.has_docs}
Has License: {project_info.has_license}
Has Requirements: {project_info.has_requirements}

Project Structure:
{json.dumps(project_info.structure, indent=2)}

README Type: {readme_type}

Please create a comprehensive README that includes:
1. Project title and description
2. Features and capabilities
3. Installation instructions
4. Usage examples
5. Configuration options
6. Contributing guidelines
7. License information

Make it engaging, professional, and tailored to the project's specific language and framework."""

        if readme_type == "simple":
            prompt += "\n\nKeep it simple and concise, focusing on essential information only."
        elif readme_type == "installation":
            prompt += "\n\nFocus heavily on installation and setup instructions, with detailed steps for different environments."
        else:  # advanced
            prompt += "\n\nMake it comprehensive with detailed sections, examples, and advanced usage patterns."

        return prompt

    def _generate_template_readme(self, project_info: ProjectInfo, readme_type: str) -> str:
        """Generate a template-based README as fallback."""
        if readme_type == "simple":
            return self._simple_template(project_info)
        elif readme_type == "installation":
            return self._installation_template(project_info)
        else:
            return self._advanced_template(project_info)

    def _simple_template(self, project_info: ProjectInfo) -> str:
        """Generate a simple README template."""
        return f"""# {project_info.name}

{project_info.description}

## Features

- Built with {project_info.language}
- {f'Uses {project_info.framework} framework' if project_info.framework else 'Modern architecture'}
- {f'Includes {len(project_info.dependencies)} dependencies' if project_info.dependencies else 'Lightweight'}

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_info.name}

# Install dependencies
{self._get_install_command(project_info)}
```

## Usage

```bash
{self._get_run_command(project_info)}
```

## License

This project is licensed under the MIT License.
"""

    def _installation_template(self, project_info: ProjectInfo) -> str:
        """Generate an installation-focused README template."""
        return f"""# {project_info.name}

{project_info.description}

## Prerequisites

- {self._get_prerequisites(project_info)}

## Installation

### Option 1: Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd {project_info.name}

# Install dependencies
{self._get_install_command(project_info)}
```

### Option 2: Development Install

```bash
# Clone the repository
git clone <repository-url>
cd {project_info.name}

# Install in development mode
{self._get_dev_install_command(project_info)}
```

### Option 3: Using Package Manager

```bash
# If available via package manager
{self._get_package_manager_install(project_info)}
```

## Configuration

{self._get_configuration_section(project_info)}

## Verification

```bash
{self._get_verify_command(project_info)}
```

## Testing

```bash
{self._get_test_command(project_info)}
```

## Troubleshooting

### Common Issues

1. **Dependency conflicts**: Try using a virtual environment
2. **Permission errors**: Check file permissions
3. **Network issues**: Verify internet connection

## License

This project is licensed under the MIT License.
"""

    def _advanced_template(self, project_info: ProjectInfo) -> str:
        """Generate an advanced README template."""
        language_icons = {
            "Python": "🐍",
            "JavaScript/TypeScript": "🟨",
            "Java": "☕",
            "C/C++": "⚡",
            "Go": "🐹",
            "Rust": "🦀",
            "Ruby": "💎",
            "PHP": "🐘"
        }
        
        icon = language_icons.get(project_info.language, "📦")
        
        return f"""# {icon} {project_info.name}

{project_info.description}

![License](https://img.shields.io/badge/license-MIT-green.svg)
![Language](https://img.shields.io/badge/language-{project_info.language.replace('/', '%2F')}-blue.svg)
{f'![Framework](https://img.shields.io/badge/framework-{project_info.framework}-orange.svg)' if project_info.framework else ''}

## 🚀 Features

- **Modern {project_info.language}** implementation
- {f'**{project_info.framework}** framework integration' if project_info.framework else '**Clean architecture**'}
- **Comprehensive testing** {f'✅' if project_info.has_tests else '❌'}
- **Documentation** {f'✅' if project_info.has_docs else '❌'}
- **License** {f'✅' if project_info.has_license else '❌'}

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

{self._get_prerequisites(project_info)}

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd {project_info.name}

# Install dependencies
{self._get_install_command(project_info)}
```

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd {project_info.name}

# Install in development mode
{self._get_dev_install_command(project_info)}

# Run tests
{self._get_test_command(project_info)}
```

## 🎯 Usage

### Basic Usage

{self._get_basic_usage(project_info)}

### Advanced Usage

```python
# Example advanced usage
import {project_info.name.lower().replace('-', '_')}

# Initialize the component
component = {project_info.name.lower().replace('-', '_')}.Component()

# Use advanced features
result = component.advanced_feature()
```

## ⚙️ Configuration

{self._get_configuration_section(project_info)}

## 📚 API Reference

{self._get_api_reference(project_info)}

## 🧪 Testing

```bash
# Run all tests
{self._get_test_command(project_info)}

# Run with coverage
pytest --cov={project_info.name.lower().replace('-', '_')}

# Run specific test
pytest tests/test_specific.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors
- Inspired by the {project_info.language} community
- Built with modern development practices
"""

    def _get_prerequisites(self, project_info: ProjectInfo) -> str:
        """Get prerequisites based on project info."""
        if project_info.language == "Python":
            return "- Python 3.8+\n- pip or uv\n- virtual environment (recommended)"
        elif project_info.language == "JavaScript/TypeScript":
            return "- Node.js 16+\n- npm or yarn\n- Git"
        elif project_info.language == "Java":
            return "- Java 11+\n- Maven or Gradle\n- Git"
        else:
            return "- Git\n- Appropriate language runtime\n- Package manager"

    def _get_install_command(self, project_info: ProjectInfo) -> str:
        """Get installation command based on project info."""
        if project_info.language == "Python":
            return "pip install -r requirements.txt"
        elif project_info.language == "JavaScript/TypeScript":
            return "npm install"
        elif project_info.language == "Java":
            return "mvn install"
        else:
            return "# Check project documentation for installation steps"

    def _get_run_command(self, project_info: ProjectInfo) -> str:
        """Get run command based on project info."""
        if project_info.language == "Python":
            return "python main.py"
        elif project_info.language == "JavaScript/TypeScript":
            return "npm start"
        elif project_info.language == "Java":
            return "java -jar target/app.jar"
        else:
            return "# Check project documentation for run commands"

    def _get_configuration_section(self, project_info: ProjectInfo) -> str:
        """Get configuration section based on project info."""
        if project_info.language == "Python":
            return """### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_KEY=your_api_key_here
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Configuration Files

The application can be configured via:
- Environment variables
- Configuration files
- Command-line arguments"""
        else:
            return """### Configuration

Please refer to the project documentation for configuration options."""

    def _get_verify_command(self, project_info: ProjectInfo) -> str:
        """Get verification command based on project info."""
        if project_info.language == "Python":
            return "python -c \"import sys; print('Python version:', sys.version)\""
        elif project_info.language == "JavaScript/TypeScript":
            return "node --version && npm --version"
        else:
            return "# Check if the application runs correctly"

    def _get_test_command(self, project_info: ProjectInfo) -> str:
        """Get test command based on project info."""
        if project_info.language == "Python":
            return "pytest"
        elif project_info.language == "JavaScript/TypeScript":
            return "npm test"
        elif project_info.language == "Java":
            return "mvn test"
        else:
            return "# Check project documentation for test commands"

    def _get_dev_install_command(self, project_info: ProjectInfo) -> str:
        """Get development install command based on project info."""
        if project_info.language == "Python":
            return "pip install -e .[dev]"
        elif project_info.language == "JavaScript/TypeScript":
            return "npm install --include=dev"
        else:
            return self._get_install_command(project_info)

    def _get_basic_usage(self, project_info: ProjectInfo) -> str:
        """Get basic usage examples based on project info."""
        if project_info.language == "Python":
            return """```python
# Basic usage example
from {project_info.name.lower().replace('-', '_')} import main

# Run the application
main()
```"""
        elif project_info.language == "JavaScript/TypeScript":
            return """```javascript
// Basic usage example
const app = require('{project_info.name.lower()}');

// Run the application
app.start();
```"""
        else:
            return """```bash
# Basic usage
./run.sh
```"""

    def _get_api_reference(self, project_info: ProjectInfo) -> str:
        """Get API reference section based on project info."""
        return """### Core Functions

#### `main()`
The main entry point for the application.

#### `configure(options)`
Configure the application with custom options.

### Classes

#### `Component`
Main component class for the application.

For detailed API documentation, please refer to the source code or generated documentation."""

    def _get_package_manager_install(self, project_info: ProjectInfo) -> str:
        """Get package manager install command based on project info."""
        if project_info.language == "Python":
            return "pip install {project_info.name.lower()}"
        elif project_info.language == "JavaScript/TypeScript":
            return "npm install {project_info.name.lower()}"
        else:
            return "# Check if available in your package manager"


async def generate_readme(request: GenerateReadmeRequest) -> GenerateReadmeResponse:
    """Handle README generation request."""
    try:
        from .analysis import ProjectAnalyzer
        
        # Analyze the project first
        project_path = request.project_path
        analyzer = ProjectAnalyzer(project_path)
        project_info = analyzer.analyze()
        
        # Get AI provider configuration from request
        ai_providers = request.config.get("ai_providers", {})
        selected_provider = request.ai_provider
        
        # Create README generator
        generator = READMEGenerator(ai_providers, selected_provider)
        
        # Generate README
        readme_content = generator.generate_readme(project_info, request.readme_type)
        
        # Create metadata
        metadata = {
            "provider_used": selected_provider,
            "readme_type": request.readme_type,
            "project_language": project_info.language,
            "project_framework": project_info.framework,
            "dependencies_count": len(project_info.dependencies)
        }
        
        return GenerateReadmeResponse(
            success=True,
            readme_content=readme_content,
            metadata=metadata
        )
        
    except Exception as e:
        return GenerateReadmeResponse(
            success=False,
            error=f"README generation failed: {str(e)}"
        ) 