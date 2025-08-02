# ClaudeProjects
Claude Projects Enhanced CLI is a powerful command-line tool that brings the Claude.ai website experience to your terminal. It provides project-based file management, comprehensive AI responses, and automatic code artifact generation.

Claude Projects Enhanced CLI
User Guide & Instructions

Table of Contents

Introduction
Installation & Setup
Getting Started
Working with Artifacts
Command Reference


Introduction
Claude Projects Enhanced CLI is a powerful command-line tool that brings the Claude.ai website experience to your terminal. It provides project-based file management, comprehensive AI responses, and automatic code artifact generation.
Key Features

🌐 Website-Parity Responses: Get the same detailed, comprehensive responses as Claude.ai
📦 Automatic Artifacts: Code improvements are automatically saved as separate files
📁 Project Isolation: Each project maintains its own files and conversation history
💾 Persistent Storage: All conversations and artifacts are saved for future reference

System Requirements

Python 3.7 or higher
Internet connection for API calls
Anthropic API key


Installation & Setup
Step 1: Download the Script
Save claude_projects_enhanced.py to your desired directory.
Step 2: Install Dependencies
bashpip install anthropic python-dotenv
Step 3: Configure API Key
Create a .env file in the same directory:
ANTHROPIC_API_KEY=your_api_key_here
Step 4: Run the CLI
bashpython claude_projects_enhanced.py
You should see:
🚀 Starting Enhanced Claude Projects CLI...
   This version aims for parity with Claude.ai website responses

╔═══════════════════════════════════════════════════════════════╗
║                Claude Projects CLI - Enhanced Edition           ║
║          Website-Parity Mode for Consistent Responses          ║
╚═══════════════════════════════════════════════════════════════╝

Getting Started
Creating Your First Project

Create a new project:
(claude) > create my_project
✅ Created enhanced project: my_project

Add files to analyze:
(my_project) > add /path/to/your/code.py
✅ Added: code.py

Chat with Claude about your files:
(my_project) > chat What does this code do and how can I improve it?


Understanding the Response
When you chat with Claude, you'll see:
📎 Including 1 files from 'my_project' project
🌐 Using website-parity mode for comprehensive response...
🤔 Thinking deeply (website-style response)...

══════════════════════════════════════════════════════════
🤖 Claude (opus) - Enhanced Response:
══════════════════════════════════════════════════════════

[Detailed analysis with code improvements...]

══════════════════════════════════════════════════════════

📦 Created 5 code artifacts:
   ✓ ImprovedClass (python) → improvedclass_20250802_161611.python
   ✓ OptimizedFunction (python) → optimizedfunction_20250802_161611.python
   ...

💾 Enhanced conversation saved: conversation_20250802_161611.json

📊 Response Metrics:
   • Length: 15,234 characters
   • Words: 2,456 words
   • Code artifacts: 5

Working with Artifacts
What are Artifacts?
Artifacts are complete, production-ready code files that Claude automatically generates when providing improvements or solutions. They're extracted from the response and saved as separate files you can immediately use.
Viewing Artifacts

List all artifacts:
(my_project) > artifacts

📦 Artifacts in my_project:
Name                                    Size     Modified
─────────────────────────────────────────────────────────
improvedclass_20250802_161611.python    2.5 KB   2025-08-02 16:16
optimizedfunction_20250802_161611.python 1.8 KB   2025-08-02 16:16

View a specific artifact:
(my_project) > view improvedclass_20250802_161611.python

View all files and artifacts together:
(my_project) > list


Exporting Artifacts

Export to a specific directory:
(my_project) > export artifacts ~/Desktop/my_improvements
✅ Exported 5 artifacts to: /Users/you/Desktop/my_improvements

Open project folder in file manager:
(my_project) > open_project_folder
✅ Opened project folder


Artifact File Structure
Your artifacts are stored in:
Claude_Projects/
└── my_project/
    ├── files/          # Your original files
    ├── artifacts/      # Generated improvements
    │   ├── improvedclass_20250802_161611.python
    │   ├── optimizedfunction_20250802_161611.python
    │   └── ...
    └── conversations/  # Chat history
Managing Artifacts

Clear all artifacts (with confirmation):
(my_project) > clear_artifacts

Get a project summary:
(my_project) > summary

📊 Project Summary: my_project
══════════════════════════════════════════════
📄 Files: 3 (45.2 KB)
📦 Artifacts: 12 (156.8 KB)
💬 Conversations: 8



Command Reference
Project Management
CommandDescriptionExamplecreate <name>Create a new projectcreate web_appopen <name>Open existing projectopen web_appprojectsList all projectsprojectssummaryShow project statisticssummary
File Management
CommandDescriptionExampleadd <path>Add file to projectadd ~/code/app.pyfilesList project filesfilesremove <name>Remove fileremove old_code.pyupdateSync files from directoryupdate
Artifact Management
CommandDescriptionExampleartifactsList all artifactsartifactsview <name>View file or artifactview improved_code.pythonlistShow files AND artifactslistexport artifacts <path>Export artifactsexport artifacts ~/Desktopclear_artifactsRemove all artifactsclear_artifacts
Conversation
CommandDescriptionExamplechat <message>Talk to Claudechat explain this algorithmconversationsList chat historyconversationsmodel <name>Switch modelmodel opusmodelsList available modelsmodels
Utilities
CommandDescriptionopen_project_folderOpen in file managerhelpShow all commandshelp_artifactsArtifact helpclearClear screenexit or quitExit CLI
Pro Tips

Auto-completion: Use TAB to complete commands
Quick artifact access: view works for both files and artifacts
Batch operations: Export all artifacts at once with export artifacts
Model selection: Use opus for best quality, sonnet for balance, haiku for speed

Common Workflows
Code Review Workflow:
bash> create code_review
> add src/main.py src/utils.py src/models.py
> chat Review this code for potential issues and improvements
> export artifacts ~/Desktop/improvements
Learning Workflow:
bash> create learning_python
> add confusing_code.py
> chat Explain this code in detail with examples
> view explanation_examples_*.python
Refactoring Workflow:
bash> create refactor_project
> add legacy_code.py
> chat Refactor this code using modern best practices
> list  # See all original files and new artifacts
> export artifacts ./refactored_code/

Troubleshooting
No API Key Error:

Ensure .env file exists with ANTHROPIC_API_KEY=your_key

File Not Found:

Use full paths or paths relative to current directory
Check with files or list command

No Artifacts Created:

Artifacts are only created for substantial code (100+ chars)
Small snippets remain in the conversation

Can't Find Artifacts:

Use artifacts to list all
Use open_project_folder to browse manually
Check Claude_Projects/project_name/artifacts/
