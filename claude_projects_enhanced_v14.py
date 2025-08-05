#!/usr/bin/env python3
"""
Enhanced Claude Projects CLI - Achieves parity with Claude.ai website responses
Complete standalone version with all required classes
"""

import os
import json
import cmd
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import mimetypes
import re

# Load environment variables
load_dotenv()


class Project:
    """Manages project files and conversations"""
    
    def __init__(self, name: str, base_path: Optional[Path] = None):
        self.name = name
        self.base_path = base_path or Path.cwd() / "Claude_Projects"
        self.project_path = self.base_path / name
        self.files_path = self.project_path / "files"
        self.conversations_path = self.project_path / "conversations"
        self.metadata_path = self.project_path / "metadata.json"
        
        # Create directory structure
        self.files_path.mkdir(parents=True, exist_ok=True)
        self.conversations_path.mkdir(exist_ok=True)
        
        self.metadata = self._load_metadata()
    
    def add_file(self, filepath: Path) -> str:
        """Add a file to the project"""
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Copy file to project
        dest = self.files_path / filepath.name
        if dest.exists():
            # Add timestamp to avoid overwriting
            stem = filepath.stem
            suffix = filepath.suffix
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = self.files_path / f"{stem}_{timestamp}{suffix}"
        
        shutil.copy2(filepath, dest)
        
        # Update metadata
        self.metadata['files'][dest.name] = {
            'added': datetime.now().isoformat(),
            'original_path': str(filepath),
            'size': dest.stat().st_size
        }
        self._save_metadata()
        
        return dest.name
    
    def remove_file(self, filename: str) -> bool:
        """Remove a file from the project"""
        filepath = self.files_path / filename
        if filepath.exists():
            filepath.unlink()
            if filename in self.metadata['files']:
                del self.metadata['files'][filename]
                self._save_metadata()
            return True
        return False
    
    def list_files(self) -> List[Tuple[str, int, str]]:
        """List all project files with details"""
        files = []
        for filepath in sorted(self.files_path.iterdir()):
            if filepath.is_file():
                size = filepath.stat().st_size
                modified = datetime.fromtimestamp(filepath.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                files.append((filepath.name, size, modified))
        return files
    
    def get_file_content(self, filename: str) -> str:
        """Get content of a text file"""
        filepath = self.files_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        # Determine if file is text
        mime_type, _ = mimetypes.guess_type(str(filepath))
        
        if mime_type and mime_type.startswith('text'):
            return filepath.read_text()
        elif filepath.suffix in ['.txt', '.md', '.tex', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml']:
            return filepath.read_text()
        else:
            return f"[Binary file: {filename} ({mime_type or 'unknown type'})]"
    
    def save_conversation(self, messages: List[Dict], response: str) -> str:
        """Save a conversation to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'messages': messages,
            'response': response
        }
        
        filepath = self.conversations_path / filename
        with open(filepath, 'w') as f:
            json.dump(conversation, f, indent=2)
        
        return filename
    
    def list_conversations(self) -> List[Tuple[str, str]]:
        """List all conversations"""
        conversations = []
        for filepath in sorted(self.conversations_path.iterdir(), reverse=True):
            if filepath.suffix == '.json':
                with open(filepath, 'r') as f:
                    data = json.load(f)
                timestamp = data.get('timestamp', 'Unknown')
                conversations.append((filepath.name, timestamp))
        return conversations
    
    def get_project_context(self) -> str:
        """Generate context from all project files - ONLY from current project"""
        context_parts = [f"Project: {self.name}\n{'='*60}\n"]
        context_parts.append("Files in this project:\n")
        
        # ONLY read files from THIS project's files directory
        for filepath in sorted(self.files_path.iterdir()):
            if filepath.is_file():
                context_parts.append(f"\n--- File: {filepath.name} ---\n")
                try:
                    content = self.get_file_content(filepath.name)
                    context_parts.append(content)
                except Exception as e:
                    context_parts.append(f"[Error reading file: {e}]")
                context_parts.append("\n")
        
        if len(list(self.files_path.iterdir())) == 0:
            context_parts.append("(No files in project yet)\n")
        
        return "".join(context_parts)
    
    def sync_files(self) -> List[str]:
        """Sync metadata with actual files in the files directory"""
        synced = []
        
        # Remove metadata for files that no longer exist
        files_to_remove = []
        for filename in self.metadata['files']:
            if not (self.files_path / filename).exists():
                files_to_remove.append(filename)
        
        for filename in files_to_remove:
            del self.metadata['files'][filename]
        
        # Add metadata for new files
        for filepath in self.files_path.iterdir():
            if filepath.is_file() and filepath.name not in self.metadata['files']:
                self.metadata['files'][filepath.name] = {
                    'added': datetime.now().isoformat(),
                    'original_path': 'manually_added',
                    'size': filepath.stat().st_size
                }
                synced.append(filepath.name)
        
        if files_to_remove or synced:
            self._save_metadata()
        
        return synced
    
    def _load_metadata(self) -> Dict:
        """Load project metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {
            'created': datetime.now().isoformat(),
            'files': {},
            'settings': {}
        }
    
    def _save_metadata(self):
        """Save project metadata"""
        self.metadata['updated'] = datetime.now().isoformat()
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)


class ClaudeCLI(cmd.Cmd):
    """Interactive CLI for Claude Projects"""
    
    intro = """
╔═══════════════════════════════════════════════════════════════╗
║                     Claude Projects CLI                        ║
║  Manage your project files and have conversations with Claude  ║
╠═══════════════════════════════════════════════════════════════╣
║  📁 Projects are isolated - Claude sees ONLY current project   ║
╚═══════════════════════════════════════════════════════════════╝

Type 'help' for commands or 'help <command>' for details.
    """
    
    prompt = '(claude) > '
    
    # Available Claude models
    MODELS = {
        'opus': 'claude-opus-4-20250514',
        'sonnet': 'claude-3-5-sonnet-20241022',
        'haiku': 'claude-3-haiku-20240307'
    }
    
    def __init__(self):
        super().__init__()
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment")
            print("   Create a .env file with: ANTHROPIC_API_KEY=your_key_here")
            self.client = None
        else:
            self.client = Anthropic(api_key=api_key)
        
        self.current_project: Optional[Project] = None
        self.projects_base = Path.cwd() / "Claude_Projects"
        self.projects_base.mkdir(exist_ok=True)
        
        # Load or set default model
        self.settings_file = self.projects_base / ".settings.json"
        self.current_model = self._load_settings().get('model', 'opus')
    
    def _load_settings(self) -> Dict:
        """Load CLI settings"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {'model': 'opus'}
    
    def _save_settings(self):
        """Save CLI settings"""
        settings = {
            'model': self.current_model,
            'updated': datetime.now().isoformat()
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def do_create(self, name: str):
        """Create a new project: create <project_name>"""
        if not name:
            print("❌ Please provide a project name")
            return
        
        self.current_project = Project(name)
        self.prompt = f'({name}) > '
        print(f"✅ Created project: {name}")
        
        # Check if files already exist in the directory
        synced = self.current_project.sync_files()
        if synced:
            print(f"📂 Found and loaded {len(synced)} existing files in project directory")
    
    def do_open(self, name: str):
        """Open an existing project: open <project_name>"""
        if not name:
            print("❌ Please provide a project name")
            return
        
        project_path = self.projects_base / name
        if not project_path.exists():
            print(f"❌ Project '{name}' not found")
            return
        
        self.current_project = Project(name)
        self.prompt = f'({name}) > '
        print(f"✅ Opened project: {name}")
        
        # Auto-sync files
        synced = self.current_project.sync_files()
        if synced:
            print(f"📂 Auto-loaded {len(synced)} files from project directory")
    
    def do_projects(self, _):
        """List all projects"""
        projects = [p.name for p in self.projects_base.iterdir() if p.is_dir() and not p.name.startswith('.')]
        if projects:
            print("\n📁 Available projects:")
            for project in sorted(projects):
                marker = "→" if self.current_project and self.current_project.name == project else " "
                print(f" {marker} {project}")
        else:
            print("No projects found. Create one with: create <name>")
    
    def do_add(self, filepath: str):
        """Add a file to the current project: add <filepath>"""
        if not self.current_project:
            print("❌ No project open. Use: open <project_name>")
            return
        
        if not filepath:
            print("❌ Please provide a file path")
            return
        
        try:
            path = Path(filepath).expanduser()
            filename = self.current_project.add_file(path)
            print(f"✅ Added: {filename}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_files(self, _):
        """List all files in the current project"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        files = self.current_project.list_files()
        if files:
            print(f"\n📄 Files in {self.current_project.name}:")
            print(f"{'Name':<40} {'Size':>10} {'Modified'}")
            print("-" * 65)
            for name, size, modified in files:
                size_str = self._format_size(size)
                print(f"{name:<40} {size_str:>10} {modified}")
        else:
            print("No files in project. Add with: add <filepath>")
    
    def do_model(self, model_name: str):
        """Change the Claude model: model <opus|sonnet|haiku>"""
        if not model_name:
            print(f"Current model: {self.current_model}")
            print("Available models: " + ", ".join(self.MODELS.keys()))
            return
        
        model_name = model_name.lower()
        if model_name not in self.MODELS:
            print(f"❌ Unknown model: {model_name}")
            print("Available models: " + ", ".join(self.MODELS.keys()))
            return
        
        self.current_model = model_name
        self._save_settings()
        print(f"✅ Switched to {model_name} ({self.MODELS[model_name]})")
    
    def do_chat(self, message: str):
        """Chat with Claude about your project: chat <your message>"""
        if not self.client:
            print("❌ No API key configured")
            return
        
        if not message:
            print("❌ Please provide a message")
            return
        
        # Get ONLY current project context
        context = ""
        if self.current_project:
            context = self.current_project.get_project_context()
            print(f"📎 Including {len(self.current_project.list_files())} files from '{self.current_project.name}' project only")
        else:
            print("⚠️  No project open - chatting without file context")
        
        # Prepare messages
        full_message = message
        if context:
            full_message = f"I'm sharing files from my project with you. These are ALL and ONLY the files in my current project:\n\n{context}\n\nMy question/request: {message}"
        
        print("🤔 Thinking...")
        
        try:
            model_id = self.MODELS[self.current_model]
            response = self.client.messages.create(
                model=model_id,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_message}]
            )
            
            response_text = response.content[0].text
            print(f"\n🤖 Claude ({self.current_model}):\n{response_text}\n")
            
            # Save conversation if in a project
            if self.current_project:
                conv_file = self.current_project.save_conversation(
                    [{"role": "user", "content": message}],
                    response_text
                )
                print(f"💾 Conversation saved: {conv_file}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def do_exit(self, _):
        """Exit the CLI"""
        print("👋 Goodbye!")
        return True
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def do_open_project_folder(self, _):
        """Open the current project folder in your file manager"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        project_path = self.current_project.project_path
        
        import platform
        import subprocess
        
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["open", str(project_path)])
            elif system == "Windows":
                subprocess.run(["explorer", str(project_path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(project_path)])
            print(f"✅ Opened project folder: {project_path}")
        except Exception as e:
            print(f"❌ Could not open folder: {e}")
            print(f"📁 Project path: {project_path.absolute()}")
    
    def do_quit(self, arg):
        """Exit the CLI"""
        return self.do_exit(arg)
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass


class EnhancedAnthropicClient:
    """Enhanced client that mimics Claude.ai website behavior"""
    
    # System instructions that approximate website behavior
    WEBSITE_SYSTEM_PROMPT = """You are Claude, an AI assistant created by Anthropic. When helping with code:

1. **Always provide comprehensive, detailed responses** that match the depth and quality expected on the Claude.ai website.

2. **When analyzing code files**:
   - First explain what the code does in detail
   - Identify key components and features
   - Explain the workflow
   - Then provide specific, actionable improvements

3. **When suggesting improvements**:
   - Create complete, enhanced versions of the code
   - Use proper code blocks with syntax highlighting
   - Include detailed explanations for each improvement
   - Structure improvements with clear categories

4. **Use rich formatting**:
   - Use **bold** for emphasis
   - Use bullet points and numbered lists
   - Create clear section headers
   - Use code blocks with language specification

5. **Be thorough and comprehensive**:
   - Provide multiple improvement suggestions
   - Include code examples for each suggestion
   - Explain the benefits of each improvement
   - Consider architecture, performance, and maintainability

6. **Match website response style**:
   - Start with a clear explanation of what you're analyzing
   - Break down functionality into digestible sections
   - Provide both high-level overview and detailed analysis
   - End with actionable next steps

Remember: Your responses should be as comprehensive and helpful as those on the Claude.ai website, with the same level of detail and formatting."""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        
    def create_message_with_context(self, message: str, context: str, model: str) -> Dict[str, Any]:
        """Create a message that mimics website behavior"""
        
        # Format the context similar to how the website might present it
        formatted_context = self._format_file_context(context)
        
        # Combine system prompt with user message
        full_message = f"""{self.WEBSITE_SYSTEM_PROMPT}

User has shared the following project files:

{formatted_context}

User's question: {message}

Please provide a comprehensive response that matches the quality and detail level of responses on the Claude.ai website. Include code improvements if applicable."""

        # Use parameters that likely match the website
        response = self.client.messages.create(
            model=model,
            max_tokens=8192,  # Larger token limit for comprehensive responses
            temperature=0.7,   # Balanced temperature for detailed but coherent responses
            messages=[
                {
                    "role": "user",
                    "content": full_message
                }
            ]
        )
        
        return response
    
    def _format_file_context(self, context: str) -> str:
        """Format file context to match website presentation"""
        # Parse the context to extract file information
        lines = context.split('\n')
        formatted = []
        current_file = None
        file_content = []
        
        for line in lines:
            if line.startswith('--- File:') and line.endswith('---'):
                # Save previous file if exists
                if current_file and file_content:
                    formatted.append(f"**File: {current_file}**")
                    formatted.append("```python")
                    formatted.extend(file_content)
                    formatted.append("```")
                    formatted.append("")
                
                # Extract new file name
                current_file = line.replace('--- File:', '').replace('---', '').strip()
                file_content = []
            elif current_file and line.strip():
                file_content.append(line)
        
        # Don't forget the last file
        if current_file and file_content:
            formatted.append(f"**File: {current_file}**")
            formatted.append("```python")
            formatted.extend(file_content)
            formatted.append("```")
        
        return '\n'.join(formatted)


class ArtifactManager:
    """Manages code artifacts similar to Claude.ai website"""
    
    def __init__(self, project_path: Path):
        self.artifacts_path = project_path / "artifacts"
        self.artifacts_path.mkdir(exist_ok=True)
        
    def create_artifact(self, content: str, language: str, title: str) -> Dict[str, Any]:
        """Create an artifact similar to website behavior"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title.lower().replace(' ', '_')}_{timestamp}.{language}"
        
        filepath = self.artifacts_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {
            'filename': filename,
            'path': str(filepath),
            'language': language,
            'title': title,
            'created': datetime.now().isoformat()
        }
    
    def extract_code_blocks(self, response_text: str) -> List[Dict[str, Any]]:
        """Extract code blocks from response to create artifacts"""
        artifacts = []
        
        # Pattern to match code blocks with language specification
        code_pattern = r'```(\w+)\n(.*?)```'
        matches = re.finditer(code_pattern, response_text, re.DOTALL)
        
        for i, match in enumerate(matches):
            language = match.group(1)
            code = match.group(2)
            
            # Skip small code snippets
            if len(code.strip()) < 100:
                continue
                
            # Try to extract a title from the code or context
            title = self._extract_title(code, language, i)
            
            artifact = self.create_artifact(code, language, title)
            artifacts.append(artifact)
            
        return artifacts
    
    def _extract_title(self, code: str, language: str, index: int) -> str:
        """Extract a meaningful title from code"""
        # Look for class or function definitions
        if language == 'python':
            class_match = re.search(r'class\s+(\w+)', code)
            if class_match:
                return class_match.group(1)
            func_match = re.search(r'def\s+(\w+)', code)
            if func_match:
                return func_match.group(1)
                
        # Look for a comment at the top
        lines = code.strip().split('\n')
        if lines and lines[0].startswith('#'):
            return lines[0].strip('# ').replace('_', ' ').title()
            
        return f"Code_Artifact_{index + 1}"


class EnhancedProject(Project):
    """Enhanced project with artifact support"""
    
    def __init__(self, name: str, base_path: Optional[Path] = None):
        super().__init__(name, base_path)
        self.artifact_manager = ArtifactManager(self.project_path)
        
    def save_enhanced_conversation(self, message: str, response: str, artifacts: List[Dict]) -> str:
        """Save conversation with artifacts information"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.json"
        
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': response,
            'artifacts': artifacts,
            'metadata': {
                'response_length': len(response),
                'has_code_artifacts': len(artifacts) > 0,
                'word_count': len(response.split())
            }
        }
        
        filepath = self.conversations_path / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        return filename


class EnhancedClaudeCLI(ClaudeCLI):
    """Enhanced CLI that better mimics Claude.ai website behavior"""
    
    intro = """
╔═══════════════════════════════════════════════════════════════╗
║                Claude Projects CLI - Enhanced Edition           ║
║          Website-Parity Mode for Consistent Responses          ║
╠═══════════════════════════════════════════════════════════════╣
║  🌐 Mimics Claude.ai website response style and quality        ║
║  📄 Creates code artifacts automatically                       ║
║  🎯 Uses enhanced prompting for comprehensive responses        ║
╚═══════════════════════════════════════════════════════════════╝

Type 'help' for commands or 'help <command>' for details.
    """
    
    def __init__(self):
        super().__init__()
        
        # Use enhanced client if API key is available
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.enhanced_client = EnhancedAnthropicClient(api_key)
        else:
            self.enhanced_client = None
    
    def do_create(self, name: str):
        """Create a new enhanced project: create <project_name>"""
        if not name:
            print("❌ Please provide a project name")
            return
        
        self.current_project = EnhancedProject(name)
        self.prompt = f'({name}) > '
        print(f"✅ Created enhanced project: {name}")
        
        # Check if files already exist in the directory
        synced = self.current_project.sync_files()
        if synced:
            print(f"📂 Found and loaded {len(synced)} existing files in project directory")
    
    def do_open(self, name: str):
        """Open an existing project with enhanced features: open <project_name>"""
        if not name:
            print("❌ Please provide a project name")
            return
        
        project_path = self.projects_base / name
        if not project_path.exists():
            print(f"❌ Project '{name}' not found")
            return
        
        self.current_project = EnhancedProject(name)
        self.prompt = f'({name}) > '
        print(f"✅ Opened enhanced project: {name}")
        
        # Auto-sync files
        synced = self.current_project.sync_files()
        if synced:
            print(f"📂 Auto-loaded {len(synced)} files from project directory")
    
    def do_chat(self, message: str):
        """Enhanced chat with Claude - token-aware with selective file inclusion
        
        Usage:
          chat <message>                    - Include all files (if under limit)
          chat -n <message>                 - No file context
          chat -s file1,file2 -- <message>  - Include specific files only
          chat -f <filename>                - Read message from file
          chat -m                           - Multi-line mode
        """
        if not self.enhanced_client:
            print("❌ No API key configured")
            return
        
        # Parse command options
        include_context = True
        selected_files = None
        
        # Handle -n (no context) option
        if message.startswith("-n "):
            include_context = False
            message = message[3:]
            print("📄 Running without file context")
        
        # Handle -s (selective files) option
        elif message.startswith("-s "):
            parts = message[3:].split(" -- ", 1)
            if len(parts) != 2:
                print("❌ Usage: chat -s file1,file2 -- Your message")
                return
            selected_files = [f.strip() for f in parts[0].split(",")]
            message = parts[1]
            print(f"📎 Including only: {', '.join(selected_files)}")
        
        # Handle -f (file input) option
        elif message.startswith("-f "):
            filename = message[3:].strip()
            if not self.current_project:
                print("❌ No project open")
                return
            try:
                message = self.current_project.get_file_content(filename)
                print(f"📄 Read message from: {filename}")
            except Exception as e:
                print(f"❌ Error: {e}")
                return
        
        # Handle -m (multi-line mode)
        elif message.strip() == "-m":
            print("📝 Entering multi-line mode. Type 'EOF' on a line by itself to send.")
            print("   (or press Ctrl+C to cancel)")
            lines = []
            try:
                while True:
                    line = input("... ")
                    if line.strip() == "EOF":
                        break
                    lines.append(line)
                message = "\n".join(lines)
                if not message.strip():
                    print("❌ No message provided")
                    return
            except KeyboardInterrupt:
                print("\n❌ Cancelled")
                return
        
        if not message:
            print("❌ Please provide a message")
            print("   Usage: chat <message> | chat -n <message> | chat -s files -- <message>")
            return
        
        # Get project context with token counting
        context = ""
        context_tokens = 0
        
        if include_context and self.current_project:
            if selected_files:
                # Build context from selected files only
                context_parts = [f"Project: {self.current_project.name} (Selected Files)\n{'='*60}\n"]
                included_files = []
                
                for filename in selected_files:
                    try:
                        content = self.current_project.get_file_content(filename)
                        file_section = f"\n--- File: {filename} ---\n{content}\n"
                        file_tokens = self.estimate_tokens(file_section)
                        
                        # Check if adding this file would exceed limit
                        if context_tokens + file_tokens + self.estimate_tokens(message) > 190000:
                            print(f"⚠️  Skipping {filename} (would exceed token limit)")
                            continue
                        
                        context_parts.append(file_section)
                        context_tokens += file_tokens
                        included_files.append(filename)
                        
                    except Exception as e:
                        print(f"⚠️  Could not include {filename}: {e}")
                
                context = "".join(context_parts)
                print(f"📎 Included {len(included_files)} files (~{context_tokens:,} tokens)")
                
            else:
                # Try to include all files with token limit checking
                context = self.current_project.get_project_context()
                context_tokens = self.estimate_tokens(context)
                
                # Check if we're over the limit
                if context_tokens + self.estimate_tokens(message) > 190000:
                    print(f"⚠️  Project files exceed token limit (~{context_tokens:,} tokens)")
                    print("   Options:")
                    print("   • Use 'chat -n <message>' for no file context")
                    print("   • Use 'chat -s file1,file2 -- <message>' to select specific files")
                    print("   • Use 'tokens' command to see file sizes")
                    return
                
                print(f"📎 Including {len(self.current_project.list_files())} files (~{context_tokens:,} tokens)")
        
        else:
            if not include_context:
                print("📄 No file context included")
            else:
                print("⚠️  No project open - chatting without file context")
        
        # Check total tokens
        message_tokens = self.estimate_tokens(message)
        total_tokens = context_tokens + message_tokens + 2000  # Buffer for system prompt
        
        print(f"📊 Estimated tokens: {total_tokens:,} / 200,000")
        
        if total_tokens > 195000:
            print("❌ Request too large")
            return
        
        print("🤔 Thinking deeply (website-style response)...")
        
        try:
            model_id = self.MODELS[self.current_model]
            
            # Use enhanced client for website-like responses
            response = self.enhanced_client.create_message_with_context(
                message=message,
                context=context,
                model=model_id
            )
            
            response_text = response.content[0].text
            
            # Format response with better spacing
            print(f"\n{'='*70}")
            print(f"🤖 Claude ({self.current_model}) - Enhanced Response:")
            print(f"{'='*70}\n")
            print(response_text)
            print(f"\n{'='*70}\n")
            
            # Extract and create artifacts if in a project
            artifacts = []
            if self.current_project and isinstance(self.current_project, EnhancedProject):
                artifacts = self.current_project.artifact_manager.extract_code_blocks(response_text)
                
                if artifacts:
                    print(f"📦 Created {len(artifacts)} code artifacts:")
                    for artifact in artifacts:
                        print(f"   ✓ {artifact['title']} ({artifact['language']}) → {artifact['filename']}")
                
                # Save enhanced conversation
                conv_file = self.current_project.save_enhanced_conversation(
                    message=message,
                    response=response_text,
                    artifacts=artifacts
                )
                print(f"💾 Enhanced conversation saved: {conv_file}")
                
            # Show response metrics
            print(f"\n📊 Response Metrics:")
            print(f"   • Length: {len(response_text)} characters")
            print(f"   • Words: {len(response_text.split())} words")
            print(f"   • Code artifacts: {len(artifacts)}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def do_artifacts(self, _):
        """List all artifacts in the current project"""
        if not self.current_project:
            print("❌ No project open")
            return
            
        if not isinstance(self.current_project, EnhancedProject):
            print("❌ Current project doesn't support artifacts")
            return
        
        artifacts_path = self.current_project.project_path / "artifacts"
        if not artifacts_path.exists():
            print("No artifacts created yet")
            return
            
        artifacts = list(artifacts_path.iterdir())
        if artifacts:
            print(f"\n📦 Artifacts in {self.current_project.name}:")
            print(f"{'Name':<50} {'Size':>10} {'Modified'}")
            print("-" * 75)
            for artifact in sorted(artifacts):
                if artifact.is_file():
                    size = self._format_size(artifact.stat().st_size)
                    modified = datetime.fromtimestamp(artifact.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"{artifact.name:<50} {size:>10} {modified}")
            print(f"\nTotal: {len(artifacts)} artifacts")
            print("Tip: Use 'view <filename>' to see artifact content")
        else:
            print("No artifacts created yet")
    
    def do_list(self, _):
        """List all files and artifacts in the current project"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        # List regular files
        files = self.current_project.list_files()
        if files:
            print(f"\n📄 Project Files:")
            print(f"{'Name':<40} {'Size':>10} {'Modified'}")
            print("-" * 65)
            for name, size, modified in files:
                size_str = self._format_size(size)
                print(f"{name:<40} {size_str:>10} {modified}")
        else:
            print("\n📄 No project files")
        
        # List artifacts if using enhanced project
        if isinstance(self.current_project, EnhancedProject):
            artifacts_path = self.current_project.project_path / "artifacts"
            if artifacts_path.exists():
                artifacts = list(artifacts_path.iterdir())
                if artifacts:
                    print(f"\n📦 Artifacts:")
                    print(f"{'Name':<50} {'Size':>10} {'Modified'}")
                    print("-" * 75)
                    for artifact in sorted(artifacts):
                        if artifact.is_file():
                            size = self._format_size(artifact.stat().st_size)
                            modified = datetime.fromtimestamp(artifact.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                            print(f"{artifact.name:<50} {size:>10} {modified}")
                else:
                    print("\n📦 No artifacts")
        
        print("\nTip: Use 'view <filename>' to see any file or artifact content")
    
    def do_export(self, args: str):
        """Export artifacts or files: export artifacts <path> | export files <path>"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        parts = args.split(maxsplit=1)
        if len(parts) < 1:
            print("❌ Usage: export artifacts [path] | export files [path]")
            return
        
        export_type = parts[0]
        destination = parts[1] if len(parts) > 1 else f"exported_{export_type}"
        
        if export_type == "artifacts":
            if not isinstance(self.current_project, EnhancedProject):
                print("❌ Current project doesn't support artifacts")
                return
            
            artifacts_path = self.current_project.project_path / "artifacts"
            if not artifacts_path.exists() or not list(artifacts_path.iterdir()):
                print("No artifacts to export")
                return
            
            source_path = artifacts_path
            file_type = "artifacts"
        elif export_type == "files":
            source_path = self.current_project.files_path
            if not list(source_path.iterdir()):
                print("No files to export")
                return
            file_type = "files"
        else:
            print("❌ Usage: export artifacts [path] | export files [path]")
            return
        
        # Create destination directory
        dest_path = Path(destination).expanduser()
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Copy all items
        copied = 0
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, dest_path)
                copied += 1
        
        print(f"✅ Exported {copied} {file_type} to: {dest_path.absolute()}")
    
    def do_clear_artifacts(self, _):
        """Clear all artifacts from the current project (with confirmation)"""
        if not self.current_project:
            print("❌ No project open")
            return
            
        if not isinstance(self.current_project, EnhancedProject):
            print("❌ Current project doesn't support artifacts")
            return
        
        artifacts_path = self.current_project.project_path / "artifacts"
        if not artifacts_path.exists():
            print("No artifacts to clear")
            return
        
        artifacts = list(artifacts_path.iterdir())
        if not artifacts:
            print("No artifacts to clear")
            return
        
        print(f"⚠️  This will delete {len(artifacts)} artifacts from {self.current_project.name}")
        confirm = input("Are you sure? (yes/no): ").lower()
        
        if confirm == "yes":
            removed = 0
            for artifact in artifacts:
                if artifact.is_file():
                    artifact.unlink()
                    removed += 1
            print(f"✅ Removed {removed} artifacts")
        else:
            print("❌ Cancelled")
    
    def do_help_chat(self, _):
        """Show detailed help for chat command options"""
        print("""
💬 Chat Command Options:
========================

BASIC USAGE:
  chat <message>                    - Chat with all project files included

TOKEN-AWARE OPTIONS:
  chat -n <message>                 - No file context (fastest, no token limit issues)
  chat -s file1,file2 -- <message>  - Include only specific files
  
INPUT OPTIONS:
  chat -f <filename>                - Read message from a file in your project
  chat -m                           - Multi-line mode (end with 'EOF')

EXAMPLES:
  chat Tell me about this code
  chat -n What are TBI assessment best practices?
  chat -s main.py,utils.py -- Analyze these two files
  chat -f long_prompt.txt
  chat -m
  ... Type your multi-line
  ... message here
  EOF

TOKEN MANAGEMENT:
  Use 'tokens' command to see which files use the most tokens
  Token limit: 200,000 (including ~2,000 for system prompts)

💡 TIP: If you hit token limits, use -n or -s options to control context
""")
    
    def do_help_artifacts(self, _):
        """Show help for artifact commands"""
        print("""
📦 Artifact Management Commands:
================================

VIEW & LIST:
  view <filename>         - View any file or artifact content
  list                    - List all files AND artifacts
  artifacts              - List only artifacts with details
  files                  - List only project files

EXPORT & MANAGE:
  export artifacts <path> - Export all artifacts to a directory
  export files <path>    - Export all project files to a directory
  clear_artifacts        - Remove all artifacts (with confirmation)

QUICK ACCESS:
  open_project_folder    - Open project folder in file manager

EXAMPLES:
  view llmprovider_20250802_161611.python    # View an artifact
  export artifacts ~/Desktop/my_code         # Export to Desktop
  list                                       # See everything

💡 TIP: Artifacts are stored in: Claude_Projects/<project_name>/artifacts/
""")
    
    def do_help(self, arg):
        """Show help for commands"""
        if arg:
            # Call parent help for specific command
            super().do_help(arg)
        else:
            # Show custom organized help
            print("""
🎯 Claude Projects Enhanced CLI - Command Reference
================================================

PROJECT MANAGEMENT:
  create <name>         - Create a new project
  open <name>           - Open existing project
  projects              - List all projects
  summary               - Show project statistics

FILE MANAGEMENT:
  add <path>            - Add file to project
  files                 - List project files
  remove <filename>     - Remove file from project
  update                - Sync files from directory
  view <filename>       - View file or artifact content

TOKEN MANAGEMENT:
  tokens                - Show token analysis for all files
  
CHAT & AI:
  chat <message>        - Chat with Claude about your project
  chat -n <message>     - Chat without file context
  chat -s files -- msg  - Chat with specific files only
  model <name>          - Switch model (opus/sonnet/haiku)
  models                - List available models

ARTIFACTS:
  artifacts             - List all artifacts
  export artifacts <p>  - Export artifacts to directory
  clear_artifacts       - Remove all artifacts
  
UTILITIES:
  conversations         - List chat history
  open_project_folder   - Open in file manager
  clear                 - Clear screen
  exit/quit            - Exit CLI

HELP:
  help                  - Show this message
  help <command>        - Detailed help for command
  help_chat            - Chat command options
  help_artifacts       - Artifact management help

💡 Quick Start:
  1. create my_project
  2. add file1.py file2.py
  3. tokens  (check token usage)
  4. chat Analyze this code
""")
💬 Chat Command Options:
========================

BASIC USAGE:
  chat <message>                    - Chat with all project files included

TOKEN-AWARE OPTIONS:
  chat -n <message>                 - No file context (fastest, no token limit issues)
  chat -s file1,file2 -- <message>  - Include only specific files
  
INPUT OPTIONS:
  chat -f <filename>                - Read message from a file in your project
  chat -m                           - Multi-line mode (end with 'EOF')

EXAMPLES:
  chat Tell me about this code
  chat -n What are TBI assessment best practices?
  chat -s main.py,utils.py -- Analyze these two files
  chat -f long_prompt.txt
  chat -m
  ... Type your multi-line
  ... message here
  EOF

TOKEN MANAGEMENT:
  Use 'tokens' command to see which files use the most tokens
  Token limit: 200,000 (including ~2,000 for system prompts)

💡 TIP: If you hit token limits, use -n or -s options to control context
""")
    
    def do_help_artifacts(self, _):
        """Show help for artifact commands"""
        print("""
📦 Artifact Management Commands:
================================

VIEW & LIST:
  view <filename>         - View any file or artifact content
  list                    - List all files AND artifacts
  artifacts              - List only artifacts with details
  files                  - List only project files

EXPORT & MANAGE:
  export artifacts <path> - Export all artifacts to a directory
  export files <path>    - Export all project files to a directory
  clear_artifacts        - Remove all artifacts (with confirmation)

QUICK ACCESS:
  open_project_folder    - Open project folder in file manager

EXAMPLES:
  view llmprovider_20250802_161611.python    # View an artifact
  export artifacts ~/Desktop/my_code         # Export to Desktop
  list                                       # See everything

💡 TIP: Artifacts are stored in: Claude_Projects/<project_name>/artifacts/
""")
    
    def do_help(self, arg):
        """Show help for commands"""
        if arg:
            # Call parent help for specific command
            super().do_help(arg)
        else:
            # Show custom organized help
            print("""
🎯 Claude Projects Enhanced CLI - Command Reference
================================================

PROJECT MANAGEMENT:
  create <name>          - Create a new project
  open <name>           - Open existing project
  projects              - List all projects
  summary               - Show project statistics

FILE MANAGEMENT:
  add <path>            - Add file to project
  files                 - List project files
  remove <filename>     - Remove file from project
  update                - Sync files from directory
  view <filename>       - View file or artifact content

TOKEN MANAGEMENT:
  tokens                - Show token analysis for all files
  
CHAT & AI:
  chat <message>        - Chat with Claude about your project
  chat -n <message>     - Chat without file context
  chat -s files -- msg  - Chat with specific files only
  model <name>          - Switch model (opus/sonnet/haiku)
  models                - List available models

ARTIFACTS:
  artifacts             - List all artifacts
  export artifacts <p>  - Export artifacts to directory
  clear_artifacts       - Remove all artifacts
  
UTILITIES:
  conversations         - List chat history
  open_project_folder   - Open in file manager
  clear                 - Clear screen
  exit/quit            - Exit CLI

HELP:
  help                  - Show this message
  help <command>        - Detailed help for command
  help_chat            - Chat command options
  help_artifacts       - Artifact management help

💡 Quick Start:
  1. create my_project
  2. add file1.py file2.py
  3. tokens  (check token usage)
  4. chat Analyze this code
""")
    
    def do_summary(self, _):
        """Show project summary including files, artifacts, and conversations"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        print(f"\n📊 Project Summary: {self.current_project.name}")
        print("=" * 60)
        
        # Count files
        files = self.current_project.list_files()
        total_file_size = sum(f[1] for f in files)
        print(f"📄 Files: {len(files)} ({self._format_size(total_file_size)})")
        
        # Count artifacts if enhanced project
        artifact_count = 0
        artifact_size = 0
        if isinstance(self.current_project, EnhancedProject):
            artifacts_path = self.current_project.project_path / "artifacts"
            if artifacts_path.exists():
                artifacts = list(artifacts_path.iterdir())
                artifact_count = len([a for a in artifacts if a.is_file()])
                artifact_size = sum(a.stat().st_size for a in artifacts if a.is_file())
        
        print(f"📦 Artifacts: {artifact_count} ({self._format_size(artifact_size)})")
        
        # Count conversations
        conversations = self.current_project.list_conversations()
        print(f"💬 Conversations: {len(conversations)}")
        
        # Project location
        print(f"\n📁 Location: {self.current_project.project_path.absolute()}")
        
        # Quick tips based on content
        print("\n💡 Quick actions:")
        if artifact_count > 0:
            print("   • view <artifact_name>  - View an artifact")
            print("   • export artifacts ~/Desktop/code  - Export all artifacts")
        if len(files) > 0:
            print("   • chat <your question>  - Ask about your files")
        print("   • open_project_folder  - Open in file manager")
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation without tiktoken)"""
        # Rough estimation: ~4 characters per token on average
        # This is a simplified approach, actual tokenization is more complex
        word_count = len(text.split())
        char_count = len(text)
        
        # Use a weighted average of word and character counts
        # Most tokens are ~0.75 words or ~4 characters
        estimated_tokens = int((word_count / 0.75 + char_count / 4) / 2)
        
        return estimated_tokens
    
    def do_tokens(self, _):
        """Show token count analysis for current project"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        print(f"\n📊 Token Analysis: {self.current_project.name}")
        print("=" * 70)
        print("Note: Token counts are estimates. Actual usage may vary.")
        print("=" * 70)
        
        total_tokens = 0
        file_data = []
        
        # Analyze each file
        for filepath in sorted(self.current_project.files_path.iterdir()):
            if filepath.is_file():
                try:
                    content = self.current_project.get_file_content(filepath.name)
                    tokens = self.estimate_tokens(content)
                    total_tokens += tokens
                    file_data.append((filepath.name, tokens, len(content)))
                except Exception as e:
                    file_data.append((filepath.name, 0, 0))
                    print(f"⚠️  Error reading {filepath.name}: {e}")
        
        # Sort by token count (highest first)
        file_data.sort(key=lambda x: x[1], reverse=True)
        
        # Display results
        print(f"\n{'File':<40} {'Tokens':>12} {'Size':>10}")
        print("-" * 65)
        
        for filename, tokens, size in file_data:
            size_str = self._format_size(size)
            # Color code based on token count
            if tokens > 50000:
                prefix = "🔴"  # Red - very large
            elif tokens > 20000:
                prefix = "🟡"  # Yellow - large
            else:
                prefix = "🟢"  # Green - ok
            
            print(f"{prefix} {filename:<38} {tokens:>11,} {size_str:>10}")
        
        print("-" * 65)
        print(f"{'TOTAL':<40} {total_tokens:>11,}")
        
        # Add context overhead estimate
        context_overhead = 2000  # System prompts, formatting, etc.
        total_with_overhead = total_tokens + context_overhead
        
        print(f"\n📝 Context overhead (prompts, formatting): ~{context_overhead:,} tokens")
        print(f"📊 Estimated total with overhead: ~{total_with_overhead:,} tokens")
        print(f"📏 Token limit: 200,000")
        
        # Status indicator
        percentage = (total_with_overhead / 200000) * 100
        if percentage < 50:
            status = "✅ Well within limits"
            color = "green"
        elif percentage < 80:
            status = "⚠️  Approaching limits"
            color = "yellow"
        elif percentage < 95:
            status = "⚠️  Close to limit - consider removing files"
            color = "orange"
        else:
            status = "🔴 Over/at limit - remove files or use selective chat"
            color = "red"
        
        print(f"\n🚦 Status: {status} ({percentage:.1f}% of limit)")
        
        if total_with_overhead > 150000:
            print("\n💡 Recommendations:")
            print("   • Use 'chat -n <message>' to chat without file context")
            print("   • Use 'chat -s file1,file2 -- <message>' to include only specific files")
            print("   • Remove large files with 'remove <filename>'")
            print("   • Create a new project with only essential files")
            
            # Show largest files
            print("\n📍 Largest files (consider removing or excluding):")
            for filename, tokens, _ in file_data[:3]:
                if tokens > 10000:
                    print(f"   - {filename} ({tokens:,} tokens)")
    
    def do_view(self, filename: str):
        """View contents of a file or artifact: view <filename>"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        if not filename:
            print("❌ Please provide a filename")
            return
        
        # First try to find in regular files
        try:
            content = self.current_project.get_file_content(filename)
            print(f"\n{'='*70}")
            print(f"📄 File: {filename}")
            print(f"{'='*70}\n")
            print(content)
            print(f"\n{'='*70}")
            
            # Show token estimate
            tokens = self.estimate_tokens(content)
            print(f"📊 Estimated tokens: {tokens:,}")
            return
        except FileNotFoundError:
            pass  # Try artifacts next
        
        # If not found in files, try artifacts
        if isinstance(self.current_project, EnhancedProject):
            artifact_path = self.current_project.project_path / "artifacts" / filename
            if artifact_path.exists():
                try:
                    content = artifact_path.read_text(encoding='utf-8')
                    print(f"\n{'='*70}")
                    print(f"📦 Artifact: {filename}")
                    print(f"{'='*70}\n")
                    print(content)
                    print(f"\n{'='*70}")
                    
                    # Show token estimate
                    tokens = self.estimate_tokens(content)
                    print(f"📊 Estimated tokens: {tokens:,}")
                    return
                except Exception as e:
                    print(f"❌ Error reading artifact: {e}")
                    return
        
        # Not found anywhere
        print(f"❌ File not found: {filename}")
        
        # Show suggestions
        suggestions = []
        
        # Check files directory
        files = self.current_project.list_files()
        if files:
            file_names = [f[0] for f in files]
            for fname in file_names:
                if filename.lower() in fname.lower():
                    suggestions.append(('file', fname))
        
        # Check artifacts directory
        if isinstance(self.current_project, EnhancedProject):
            artifacts_path = self.current_project.project_path / "artifacts"
            if artifacts_path.exists():
                for artifact in artifacts_path.iterdir():
                    if artifact.is_file() and filename.lower() in artifact.name.lower():
                        suggestions.append(('artifact', artifact.name))
        
        if suggestions:
            print("\nDid you mean:")
            for typ, name in suggestions[:5]:
                icon = "📄" if typ == 'file' else "📦"
                print(f"  {icon} {name}")
            print("\nTip: Use 'files' to list project files or 'artifacts' to list artifacts")
    
    def do_remove(self, filename: str):
        """Remove a file from the project: remove <filename>"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        if not filename:
            print("❌ Please provide a filename")
            return
        
        if self.current_project.remove_file(filename):
            print(f"✅ Removed: {filename}")
            
            # Show updated token count
            total_tokens = 0
            for filepath in self.current_project.files_path.iterdir():
                if filepath.is_file():
                    try:
                        content = self.current_project.get_file_content(filepath.name)
                        total_tokens += self.estimate_tokens(content)
                    except:
                        pass
            
            print(f"📊 Project now has ~{total_tokens:,} tokens")
        else:
            print(f"❌ File not found: {filename}")
    
    def do_update(self, _):
        """Update/reload all files from the project's files directory"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        synced = self.current_project.sync_files()
        if synced:
            print(f"✅ Loaded {len(synced)} new files:")
            for filename in synced:
                print(f"   + {filename}")
        else:
            print("✅ All files are up to date")
        
        # Show current files
        files = self.current_project.list_files()
        print(f"\n📄 Total files in project: {len(files)}")
    
    def do_conversations(self, _):
        """List all conversations in the current project"""
        if not self.current_project:
            print("❌ No project open")
            return
        
        conversations = self.current_project.list_conversations()
        if conversations:
            print(f"\n💬 Conversations in {self.current_project.name}:")
            for filename, timestamp in conversations[:10]:  # Show last 10
                print(f"  {filename} - {timestamp}")
            if len(conversations) > 10:
                print(f"  ... and {len(conversations) - 10} more")
        else:
            print("No conversations yet. Start with: chat <message>")
    
    def do_models(self, _):
        """List all available Claude models"""
        print("\n🤖 Available Claude models:")
        print(f"{'Name':<10} {'Model ID':<35} {'Status'}")
        print("-" * 60)
        for name, model_id in self.MODELS.items():
            status = "✓ Current" if name == self.current_model else ""
            print(f"{name:<10} {model_id:<35} {status}")
        print(f"\nCurrently using: {self.current_model}")
        print("Change with: model <name>")
    
    def do_clear(self, _):
        """Clear the screen"""
        os.system('clear' if os.name == 'posix' else 'cls')


def main():
    """Run the enhanced CLI"""
    print("\n🚀 Starting Enhanced Claude Projects CLI...")
    print("   This version aims for parity with Claude.ai website responses\n")
    
    cli = EnhancedClaudeCLI()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    main()
