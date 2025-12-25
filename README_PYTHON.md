# MCP Server - Python Version ✅

## ✅ Status

MCP server successfully rewritten in Python! All features work identically to the TypeScript version.

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python3 src/server.py
```

## 📋 What Works

✅ All tools preserved:
- Mac application management
- Ollama integration
- MongoDB integration
- AppleScript automation

## 🔄 Usage

### With Clients

All clients updated:
- `mcp_client.py` - text client
- `voice_client.py` - voice client

### With Claude Desktop

Update configuration:
```json
{
  "mcpServers": {
    "mac-apps": {
      "command": "python3",
      "args": ["/path/to/MCP/src/server.py"]
    }
  }
}
```

## 📚 Documentation

- Main: [README.md](./README.md)
- Migration: [PYTHON_MIGRATION.md](./PYTHON_MIGRATION.md)
