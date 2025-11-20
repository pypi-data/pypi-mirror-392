# Cognautic CLI

**A Python-based CLI AI coding agent that provides agentic development capabilities with multi-provider AI support and real-time interaction.**

⚠️ **Under Development** - Some features may be unavailable

## Voice Input (NEW)

Cognautic CLI supports one-shot speech-to-text to quickly prefill your prompt.

### Installation

- Recommended (extras):
  - `pip install -e .[voice]`
- Or install dependencies directly:
  - `pip install SpeechRecognition PyAudio`
- Linux note: PyAudio often requires PortAudio headers first:
  - Debian/Ubuntu: `sudo apt install portaudio19-dev`

### Usage

- Press `Ctrl+G` in the chat prompt to start a one-shot capture. After you speak, the recognized text is prefilled as the next prompt so you can edit or send.
- Use the slash command `/voice` to capture once and prefill the next prompt.

### Troubleshooting

- ALSA warnings: The CLI suppresses common ALSA/libportaudio stderr noise while accessing the microphone.
- "No default microphone": Ensure a working input device is selected and not in use by another app.
- Network required: The default recognizer uses Google's Web Speech API.
- Prefer offline STT (e.g., Vosk or faster-whisper)? Open an issue to request integration.

---

## Vim Editor Integration (NEW)

Cognautic CLI now includes built-in vim editor integration, allowing you to edit files directly from the chat interface without leaving the terminal.

### Installation

Vim must be installed on your system:

```bash
# On Arch Linux
sudo pacman -S vim

# On Debian/Ubuntu
sudo apt install vim

# On macOS
brew install vim
```

### Usage

#### Open vim without a file
```bash
/editor
```
Opens vim in an empty buffer. Perfect for quick notes or scratch work.

#### Open vim with a specific file
```bash
/editor myfile.txt
/editor src/main.py
/editor /absolute/path/to/file.js
```
Opens vim with the specified file. Supports both relative (to current workspace) and absolute paths.

#### Editing and returning to chat

1. Make your changes in vim
2. Press **Ctrl+E** to save and exit back to chat
3. Or use `:wq` to save and quit, or `:q!` to quit without saving

**Key Features:**
- ✅ Seamless integration - edit files without leaving Cognautic
- ✅ Ctrl+E shortcut - quick save and return to chat
- ✅ Path support - works with relative and absolute paths
- ✅ Workspace aware - relative paths are resolved from current workspace

**Example workflow:**
```bash
You: /editor config.json
# Vim opens, you make changes, press Ctrl+E
INFO: Returned to chat mode

You: I've updated the configuration file
AI: Great! Let me review those changes...
```

---

## Overview

Cognautic CLI is a Python-based command-line interface that brings AI-powered development capabilities directly to your terminal. It provides agentic tools for file operations, command execution, web search, and code analysis with support for multiple AI providers. The tool is accessed through a single `cognautic` command with various subcommands.

> **⚠️ Development Notice:** Cognautic CLI is currently under development. Some features may be unavailable or subject to change.

### Project Information

| Property | Value |
|----------|-------|
| **Developer** | Cognautic |
| **Written in** | Python |
| **Operating system** | Cross-platform |
| **Type** | AI Development Tool |
| **Status** | Under Development |
| **Repository** | [github.com/cognautic/cli](https://github.com/cognautic/cli) |

---

## Features

- **Multi-Provider AI Support**: Integrate with OpenAI, Anthropic, Google, Together AI, OpenRouter, and 15+ other AI providers
- **Local Model Support**: Run free open-source Hugging Face models locally without API keys (NEW! 🎉)
- **Agentic Tools**: File operations, command execution, web search, and code analysis
- **Intelligent Web Search**: Automatically searches the web when implementing features requiring current/external information (NEW! 🔍)
- **Rules Management**: Define global and workspace rules to guide AI behavior
- **Real-time Communication**: WebSocket server for live AI responses and tool execution
- **Secure Configuration**: Encrypted API key storage and permission management
- **Interactive CLI**: Rich terminal interface with progress indicators, colored output, and command history
- **Terminal Mode**: Toggle between Chat and Terminal modes with `Shift+Tab` for seamless workflows
- **Live Streaming with Tool Execution**: True real-time AI streaming and immediate tool execution during responses
- **Smart Auto-Continuation**: Continues work automatically until `end_response` is called, reducing manual "continue" steps
- **Background Commands**: Run long tasks in the background and manage them with `/ps` and `/ct <process_id>`
- **Command Auto-Completion**: Tab-completion for slash commands with inline descriptions
- **Safety Modes**: Confirmation prompts by default (Safe Mode) with quick toggle to YOLO mode via `/yolo` or `Ctrl+Y`
- **Directory Context & Code Navigation**: Built-in tools for project structure awareness and symbol search/navigation
- **Better Input & Exit Controls**: Multi-line input with `Alt+Enter` and safe exit with double `Ctrl+C`
- **Multi-Model Testing**: Compare models side-by-side with `/mml ...`

---

## Installation

### Prerequisites

Ensure you have Python 3.8 or higher installed:

```bash
python --version
```

### Download the Wheel File

Download the latest `.whl` file from the official repository:

```bash
# Visit https://github.com/cognautic/cli/releases
# Download the latest cognautic_cli-z.z.z-py3-none-any.whl file
```

### Installation with pip

Install the downloaded wheel file using pip:

```bash
# Navigate to your downloads folder
cd ~/Downloads

# Install the wheel file
pip install cognautic_cli-z.z.z-py3-none-any.whl

#or (Now Available On PyPi)
pip install cognautic-cli
```

### Installation with pipx (Recommended)

For isolated installation, use pipx:

```bash
# Install pipx if you don't have it
pip install pipx
pipx ensurepath

# Install Cognautic CLI with pipx
pipx install cognautic_cli-z.z.z-py3-none-any.whl

#or (Now Available On PyPi)
pip install cognautic-cli
```

### Verify Installation

Check that Cognautic CLI is installed correctly:

```bash
cognautic --version
```

### Updating Cognautic CLI

To update to a newer version, download the new wheel file and:

```bash
# With pip (force reinstall)
pip install cognautic_cli-y.y.y-py3-none-any.whl --force-reinstall

#or
pip install --upgrade cognautic-cli

# With pipx
pipx upgrade cognautic-cli
# Or force reinstall with pipx
pipx install cognautic_cli-y.y.y-py3-none-any.whl --force
```

_**Note:** Replace `y.y.y` and `z.z.z` with actual version numbers (e.g., 1.0.0, 1.1.0)._

### Uninstallation

To remove Cognautic CLI:

```bash
# With pip
pip uninstall cognautic-cli

# With pipx
pipx uninstall cognautic-cli
```

---

## Quick Start

### Step 1: Install Cognautic CLI

```bash
pip install cognautic_cli-x.x.x-py3-none-any.whl
```

### Step 2: Run Setup

```bash
cognautic setup --interactive
```

This will guide you through:
- Configuring API keys for your preferred AI providers
- Setting default provider and model
- Basic preferences

### Step 3: Start Chatting

```bash
cognautic chat
```

Now you can chat with AI and use slash commands like:
- `/help` - Show available commands
- `/provider openai` - Switch AI provider
- `/model gpt-4` - Change model
- `/workspace ~/myproject` - Set working directory
- `/lmodel microsoft/phi-2` - Load local model

**That's it!** Start chatting and let the AI help you code.

---

## Available Slash Commands

Once you're in chat mode (`cognautic chat`), use these commands:

### Workspace & Configuration

```bash
/workspace <path>    # Change working directory (alias: /ws)
/setup               # Run interactive setup wizard
/config list         # Show current configuration
/config set <key> <value>  # Set configuration value
/config get <key>    # Get configuration value
/config delete <key> # Delete configuration key
/config reset        # Reset to defaults
/help                # Show all available commands
```

### AI Provider & Model Management

```bash
/provider [name]           # Switch AI provider (openai, anthropic, google, openrouter, together, ollama, etc.)
/model [model_id]          # Switch AI model
/model list                # Fetch available models from provider's API (supports Ollama via /api/tags)
/lmodel <path>             # Load local Hugging Face model
/lmodel unload             # Unload current local model
/endpoint <prov> <url>     # Override provider base URL (e.g., ollama http://localhost:11434/api)
```

### Session Management

```bash
/session             # Show current session info
/session list        # List all sessions
/session new         # Create new session
/session load <id>   # Load existing session
/session delete <id> # Delete session
/session title <text> # Update session title
```
Note: You can also load sessions by numeric index from `/session list` using `/session load <index>`.

### Display & Interface

```bash
/speed [instant|fast|normal|slow]  # Set typing speed
/editor [filepath]   # Open vim editor (Ctrl+E to save and exit)
/clear               # Clear chat screen
/exit or /quit       # Exit chat session
```

### Safety & Confirmation

```bash
/yolo                 # Toggle between Safe (confirm) and YOLO (no confirm) modes
```

### Background Processes

```bash
/ps                   # List running background processes
/ct <process_id>      # Terminate a background process by its ID
```

### Multi-Model Testing

```bash
/mml <prov1> <model1> [prov2] <model2> ...   # Run models side-by-side with live streaming
# Example: /mml google gemini-2.5-flash openrouter gpt-4
```

### Rules Management

```bash
/rules                               # Display all rules (global + workspace)
/rules add global <text> [desc]      # Add a global rule
/rules add workspace <text> [desc]   # Add a workspace rule
/rules remove global <index>         # Remove a global rule by index
/rules remove workspace <index>      # Remove a workspace rule by index
/rules clear global                  # Clear all global rules
/rules clear workspace               # Clear all workspace rules
```

---

## Command-Line Usage

Cognautic CLI provides these main commands:

### Setup Command

```bash
cognautic setup --interactive           # Interactive setup wizard
cognautic setup --provider openai       # Quick provider setup
```

### Chat Command

```bash
cognautic chat                          # Start interactive chat
cognautic chat --provider anthropic     # Chat with specific provider
cognautic chat --model claude-3-sonnet  # Chat with specific model
cognautic chat --project-path ./my_project  # Set workspace
cognautic chat --session <id>           # Continue existing session
```

### Config Command

```bash
cognautic config list                   # Show all configuration
cognautic config set <key> <value>      # Set configuration value
cognautic config get <key>              # Get configuration value
cognautic config delete <key>           # Delete configuration key
cognautic config reset                  # Reset to defaults
```

### Providers Command

```bash
cognautic providers                     # List all AI providers and endpoints
```

### Key Bindings

- **Enter**: Send message
- **Alt+Enter**: New line (multi-line input)
- **Shift+Tab**: Toggle Chat/Terminal mode
- **Ctrl+C** (twice within 2s): Exit CLI
- **Ctrl+Y**: Toggle YOLO/Safe mode
- **Ctrl+G**: One-shot voice capture to prefill the next prompt
- **Tab**: Auto-complete slash commands and `@` file paths (accept selection)

---

## Supported AI Providers

| Provider | Models | API Key Required |
|----------|--------|------------------|
| **OpenAI** | GPT models (GPT-4, GPT-3.5) | `OPENAI_API_KEY` |
| **Anthropic** | Claude models (Claude-3 Sonnet, Haiku) | `ANTHROPIC_API_KEY` |
| **Google** | Gemini models | `GOOGLE_API_KEY` |
| **Together AI** | Various open-source models | `TOGETHER_API_KEY` |
| **OpenRouter** | Access to multiple providers | `OPENROUTER_API_KEY` |
| **Ollama** | Local models via Ollama daemon | ❌ No API key needed! |
| **Local Models** | Hugging Face models (Llama, Mistral, Phi, etc.) | ❌ No API key needed! |

### Using Local Models (NEW! 🎉)

Run free open-source AI models locally without any API keys:

```bash
# Install dependencies
pip install transformers torch accelerate

# Start chat and load a local model
cognautic chat
/lmodel microsoft/phi-2
/provider local

# Now chat with your local model!
```

**Popular local models:**
- `microsoft/phi-2` - Small and fast (2.7B)
- `TinyLlama/TinyLlama-1.1B-Chat-v1.0` - Ultra lightweight (1.1B)
- `meta-llama/Llama-2-7b-chat-hf` - High quality (7B)
- `mistralai/Mistral-7B-Instruct-v0.2` - Excellent performance (7B)

**Benefits:**
- ✅ Complete privacy - no data sent externally
- ✅ No API costs
- ✅ Works offline
- ✅ Full control over model behavior

📖 **[Read the full Local Models Guide →](LOCAL_MODELS.md)**

---

## Intelligent Web Search (NEW! 🔍)

Cognautic CLI now features **intelligent web search** that automatically researches information when needed. The AI will search the web when:

- **Implementing APIs**: "Implement Stripe payment integration"
- **Using Latest Libraries**: "Create a React app with TailwindCSS"
- **Research Requests**: "What's the best way to implement real-time chat?"
- **Current Best Practices**: "Build a modern authentication system"

### Example Usage

```bash
You: Implement OpenAI API in my Python project

AI: 🔍 Searching for latest OpenAI API documentation...
    ✅ Found: OpenAI API Reference
    📝 Creating implementation with current best practices...
    
    [Creates files with up-to-date API usage]
```

### When Web Search is Used

✅ **Automatically triggered for:**
- Latest API documentation
- Current framework/library versions
- Modern best practices
- Technologies requiring external information

❌ **Not used for:**
- Basic programming concepts
- Simple file operations
- General coding tasks

📖 **[Read the full Web Search Guide →](docs/WEB_SEARCH_TOOL.md)** | **[Quick Reference →](docs/WEB_SEARCH_QUICK_REFERENCE.md)**

---

## Configuration

Configuration files are stored in `~/.cognautic/`:

- `config.json`: General settings and preferences
- `api_keys.json`: Encrypted API keys for AI providers
- `sessions/`: Chat session history and context
- `cache/`: Temporary files and model cache

---

## Command Usage

All Cognautic CLI functionality is accessed through the single `cognautic` command. The general syntax is:

```bash
cognautic <subcommand> [options] [arguments]
```

### Getting Help

```bash
# Show general help
cognautic --help

# Show help for specific command
cognautic chat --help
```

### Version Information

```bash
cognautic --version
```

---

## WebSocket Server & Real-time Streaming

Cognautic CLI includes a powerful WebSocket server that enables **real-time, streaming AI responses**. Instead of waiting for the complete response, you receive AI-generated content as it's being produced, providing a much more interactive experience.

### Starting the WebSocket Server

The WebSocket server starts automatically when you run chat mode:

```bash
# Start with default settings (port 8765)
cognautic chat

# Specify custom port
cognautic chat --websocket-port 9000

# With specific provider and model
cognautic chat --provider openai --model gpt-4o-mini --websocket-port 8765
```

### Key Features

- ✨ **Real-time Streaming**: AI responses stream chunk-by-chunk as they're generated
- 🔄 **Bi-directional**: Full duplex WebSocket communication
- 🔐 **Session Management**: Automatic session creation and context preservation
- 🤖 **Multi-provider**: Works with all supported AI providers
- 🛠️ **Tool Execution**: Execute tools and file operations via WebSocket

### Client Examples

**Python Client:**
```bash
python examples/websocket_client_example.py

# Interactive mode
python examples/websocket_client_example.py interactive
```

**Web Browser:**
```bash
# Open in your browser
open examples/websocket_client.html
```

### Basic Usage Example

```python
import asyncio
import json
import websockets

async def chat():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        # Receive welcome message
        welcome = json.loads(await ws.recv())
        print(f"Connected! Session: {welcome['session_id']}")
        
        # Send chat message with streaming enabled
        await ws.send(json.dumps({
            "type": "chat",
            "message": "Explain Python async/await",
            "stream": true
        }))
        
        # Receive streaming response in real-time
        while True:
            response = json.loads(await ws.recv())
            
            if response['type'] == 'stream_chunk':
                print(response['chunk'], end='', flush=True)
            elif response['type'] == 'stream_end':
                break

asyncio.run(chat())
```

### API Documentation

For complete WebSocket API documentation, see **[WEBSOCKET_API.md](WEBSOCKET_API.md)**.

---

## Examples

### Simple Chat Session

Start chatting with AI:

```bash
$ cognautic chat
 ██████╗ ██████╗  ██████╗ ███╗   ██╗ █████╗ ██╗   ██╗████████╗██╗ ██████╗
██╔════╝██╔═══██╗██╔════╝ ████╗  ██║██╔══██╗██║   ██║╚══██╔══╝██║██╔════╝
██║     ██║   ██║██║  ███╗██╔██╗ ██║███████║██║   ██║   ██║   ██║██║     
██║     ██║   ██║██║   ██║██║╚██╗██║██╔══██║██║   ██║   ██║   ██║██║     
╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║██║  ██║╚██████╔╝   ██║   ██║╚██████╗
 ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝

💡 Type '/help' for commands, 'exit' to quit
🌐 WebSocket server: ws://localhost:8765
📁 Workspace: /home/user/projects
--------------------------------------------------

You [projects]: Can you help me create a Python function?
AI: Of course! I'd be happy to help you create a Python function...

You [projects]: /workspace ~/myproject
✅ Workspace changed to: /home/user/myproject

You [myproject]: Create a file called utils.py with helper functions
AI: I'll create that file for you...
```

### First-Time Setup

```bash
$ cognautic
🎉 Welcome to Cognautic! Let's get you set up.
🔑 No API keys found. Let's configure them.

Which AI provider would you like to use?
1. OpenAI (GPT-4, GPT-3.5)
2. Anthropic (Claude)
3. Google (Gemini)
4. Other providers...

Choice [1-4]: 2
🔐 Please enter your Anthropic API key: sk-ant-...
✅ API key saved securely!

🚀 Setup complete! You're ready to go.
```

### Using Local Models

Run AI models locally without API keys:

```bash
$ cognautic chat
You: /lmodel microsoft/phi-2
🔄 Loading local model from: microsoft/phi-2
⏳ This may take a few minutes depending on model size...
Loading local model from microsoft/phi-2 on cuda...
✅ Model loaded successfully on cuda
✅ Local model loaded successfully!
💡 Use: /provider local - to switch to the local model

You: /provider local
✅ Switched to provider: local

You: Hello! Can you help me code?
AI: Hello! Yes, I'd be happy to help you with coding...
```

### Working with Multiple Providers

Switch between different AI providers:

```bash
You: /provider openai
✅ Switched to provider: openai

You: /model gpt-4o
✅ Switched to model: gpt-4o

You: Write a Python function to sort a list
AI: Here's a Python function...

You: /provider anthropic
✅ Switched to provider: anthropic

You: /model claude-3-sonnet-20240229
✅ Switched to model: claude-3-sonnet-20240229
```

### Using @ Path Suggestions

Type `@` followed by a path fragment to get filesystem suggestions relative to the current workspace. Use Up/Down to navigate; press Tab to accept. Enter sends the message.

```bash
You [myproject]: Please review @README
You [myproject]: Please review @README.md

You [myproject]: Refactor @src/
You [myproject]: Refactor @src/utils/
```

---

## License

MIT
