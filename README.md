# MCP Mac Apps Server

MCP server for managing macOS applications through LLM. Allows launching applications, managing them via AppleScript, and getting information about running applications.

🎤 **Voice Control**: Use [voice_client.py](./voice_client.py) to control applications by voice! See [VOICE_SETUP.md](./VOICE_SETUP.md)

## Features

- 🚀 **Launch Applications** - open any applications on Mac
- 📋 **List Running Applications** - get list of active applications
- 🤖 **AppleScript Automation** - execute commands in applications
- ❌ **Close Applications** - quit applications
- 📂 **Open Files** - open files in specific applications

## Installation

### Python Version (Recommended)

1. Make sure you have Python 3.7+ installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Server is ready to use! No compilation required.

### TypeScript Version (Alternative)

1. Make sure you have Node.js (v18+) and npm installed

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

## Configuration for Use with MCP Clients

### Claude Desktop

Add configuration to the MCP client settings file. For Claude Desktop this is usually the MCP configuration file:

`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mac-apps": {
      "command": "python3",
      "args": ["/Users/olegzaichkin/Documents/MCP/src/server.py"]
    }
  }
}
```

Or for development using tsx:

```json
{
  "mcpServers": {
    "mac-apps": {
      "command": "npm",
      "args": ["run", "dev"],
      "cwd": "/Users/olegzaichkin/Documents/MCP"
    }
  }
}
```

### Other LLMs and Clients

**Available options**:
- **Claude Desktop** (recommended) - full MCP support
- **Ollama** ✅ - local models (installed, models loaded) - see [OLLAMA_SETUP.md](./OLLAMA_SETUP.md)
- **LM Studio** - graphical interface for local LLMs
- **DeepSeek** - see [DEEPSEEK_SETUP.md](./DEEPSEEK_SETUP.md)

📖 **Detailed list of compatible LLMs and instructions**: [COMPATIBLE_LLM.md](./COMPATIBLE_LLM.md)

## Usage

After configuration, the LLM will be able to use the following tools:

### 1. Open Application
```
Open Safari
```

### 2. Get List of Applications
```
What applications are currently running?
```

### 3. Execute AppleScript
```
In Safari, open a new tab
```

### 4. Close Application
```
Close Calculator
```

### 5. Open File
```
Open file ~/Documents/example.txt in TextEdit
```

## Available Tools

### `open_application`
Opens an application by name.

**Parameters:**
- `appName` (string) - application name (e.g., "Safari", "Calculator")

### `get_running_applications`
Returns a list of all running applications.

### `run_applescript`
Executes an AppleScript command in the specified application.

**Parameters:**
- `appName` (string) - application name
- `script` (string) - AppleScript command

**AppleScript Examples:**
- Safari: `make new document` - create a new tab
- Finder: `open folder "Documents"` - open a folder
- TextEdit: `make new document` - create a new document

### `quit_application`
Closes the specified application.

**Parameters:**
- `appName` (string) - application name to close

### `open_file_with_app`
Opens a file or URL in the specified application.

**Parameters:**
- `path` (string) - path to file or URL
- `appName` (string) - application name

## Testing

To test the server:

```bash
node test-mcp-server.js
```

Or test manually:

```bash
npm run build
npm start
```

## Development

For development with auto-reload:

```bash
npm run dev
```

## Security

⚠️ **Warning:** This server allows executing commands on your system. Use it only with trusted LLM clients and in a secure environment.

For macOS, you may need permission to control other applications:
- System Settings → Privacy & Security → Automation
- Allow access for Terminal/Node.js

## License

MIT
