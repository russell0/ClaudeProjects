🧠 Claude Projects Enhanced CLI
✨ Bring the Claude.ai Website Experience to Your Terminal
GitHub Repo →

📖 Overview
Claude Projects Enhanced CLI is a developer-first command-line interface that mirrors the Claude.ai website experience — giving you persistent project memory, artifact generation, and deep Opus-4 model interactions — all locally, with no throttling.

🔑 Key Features
🌐 Website-Parity Responses — Same deep reasoning as Claude.ai

📦 Automatic Artifacts — Claude saves generated code as files

📁 Project Isolation — Each project has separate files and chat history

💾 Persistent Storage — Files, conversations, and artifacts saved locally

⚙️ System Requirements
Python 3.7+

Internet connection

Anthropic API key (ANTHROPIC_API_KEY)

🚀 Installation & Setup
bash
Copy
Edit
# Step 1: Clone the repo or save the script
git clone https://github.com/russell0/ClaudeProjects.git

# Step 2: Install dependencies
pip install anthropic python-dotenv

# Step 3: Configure your API key
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Step 4: Run the CLI
python claude_projects_enhanced.py
🛠 Getting Started
Create a new project
bash
Copy
Edit
(claude) > create my_project
✅ Created enhanced project: my_project
Add files
bash
Copy
Edit
(my_project) > add /path/to/your/code.py
✅ Added: code.py
Chat with Claude
bash
Copy
Edit
(my_project) > chat What does this code do and how can I improve it?
🧠 Sample Response Output
yaml
Copy
Edit
📎 Including 1 file from 'my_project' project
🌐 Using website-parity mode for comprehensive response...
🤔 Thinking deeply...

══════════════════════════════════════════════════
🤖 Claude (opus) - Enhanced Response:
══════════════════════════════════════════════════

[Detailed analysis and improvements...]

📦 Created 5 code artifacts:
✓ ImprovedClass → improvedclass_20250802_161611.python
✓ OptimizedFunction → optimizedfunction_20250802_161611.python

💾 Saved: conversation_20250802_161611.json
📊 Tokens: 15,234 characters | 2,456 words | 5 artifacts
🧩 Working with Artifacts
View artifacts
bash
Copy
Edit
(my_project) > artifacts
(my_project) > view improvedclass_20250802_161611.python
(my_project) > list
Export artifacts
bash
Copy
Edit
(my_project) > export artifacts ~/Desktop/my_improvements
✅ Exported artifacts to ~/Desktop/my_improvements
Open in file explorer
bash
Copy
Edit
(my_project) > open_project_folder
📂 Artifact Directory Structure
bash
Copy
Edit
Claude_Projects/
└── my_project/
    ├── files/           # Your input files
    ├── artifacts/       # Generated code improvements
    └── conversations/   # Saved chat history
📚 Command Reference
🔧 Project Management
Command	Description	Example
create	Create new project	create web_app
open	Open existing project	open web_app
projects	List all projects	projects
summary	Show project stats	summary

📁 File Management
Command	Description	Example
add	Add file to project	add ~/app.py
files	List project files	files
remove	Remove file	remove old.py
update	Sync project folder	update

🧠 Conversation
Command	Description	Example
chat	Talk to Claude	chat explain this
model	Switch Claude model	model opus
models	List available models	models
conversations	View chat history	conversations

📦 Artifact Management
Command	Description	Example
artifacts	List generated artifacts	artifacts
view <file>	View file or artifact	view improved_code.py
list	Show all files + artifacts	list
export artifacts <path>	Export artifacts	export artifacts ~/Desktop
clear_artifacts	Remove all artifacts	clear_artifacts

🧰 Utilities
Command	Description
open_project_folder	Open project folder in Finder
help	Show help for all commands
exit or quit	Exit CLI

💡 Pro Tips
Press TAB for autocompletion

Artifacts are saved automatically per Claude’s output

Use opus model for best response quality

Export all your artifacts in one go with export artifacts

✅ Example Workflows
🔍 Code Review
bash
Copy
Edit
> create code_review
> add main.py utils.py
> chat Review this code for issues and improvements
> export artifacts ~/Desktop/reviewed
🧪 Learning
bash
Copy
Edit
> create learning
> add tricky_function.py
> chat Explain this line by line
🔧 Refactoring
bash
Copy
Edit
> create legacy_upgrade
> add legacy_code.py
> chat Refactor using modern best practices
❗️Troubleshooting
No API Key?
→ Make sure .env file has ANTHROPIC_API_KEY=your_key

File Not Found?
→ Use relative/full paths or run files to check

No Artifacts Created?
→ Only large responses (~100+ characters) generate files

Can’t Find Artifacts?
→ Use artifacts, or browse Claude_Projects/my_project/artifacts

Let me know if you want this as a README.md or downloadable PDF.
