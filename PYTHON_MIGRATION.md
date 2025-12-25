# MCP Server Migration to Python

## ✅ Completed

MCP server successfully rewritten from TypeScript/JavaScript to Python!

## 📁 New Files

- **`src/server.py`** - Python version of MCP server
- **`requirements.txt`** - Python dependencies

## 🚀 Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install pymongo requests
```

### 2. Run Server

```bash
python3 src/server.py
```

Or make the file executable:
```bash
chmod +x src/server.py
./src/server.py
```

### 3. Use with Clients

All clients are already updated to use the Python version:
- `mcp_client.py` - text client
- `voice_client.py` - voice client

## ⚙️ Claude Desktop Configuration

Update Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

## 🔄 What Changed

### Python Version Advantages:

1. ✅ Easier to use - no compilation required (npm run build)
2. ✅ Fewer dependencies - only pymongo and requests
3. ✅ Direct JSON-RPC implementation via stdio
4. ✅ All features preserved - all tools work identically

### Functionality:

All tools work the same as in the TypeScript version:
- ✅ Mac application management
- ✅ Ollama integration
- ✅ MongoDB integration
- ✅ AppleScript automation

## 📋 Version Comparison

| Feature | TypeScript | Python |
|---------|-----------|--------|
| Compilation | Required (npm run build) | Not required |
| Dependencies | @modelcontextprotocol/sdk, mongodb | pymongo, requests |
| Size | Larger (node_modules) | Smaller |
| Speed | Fast | Fast |
| Compatibility | ✅ | ✅ |

## 🔧 Environment Variables

Both versions use the same environment variables:

```bash
export OLLAMA_API_URL="http://localhost:11434"
export MONGODB_URI="mongodb://localhost:27017"
```

## 📚 Documentation

- Main documentation: [README.md](./README.md)
- Voice control: [VOICE_SETUP.md](./VOICE_SETUP.md)
- MongoDB: [MONGODB_USAGE.md](./MONGODB_USAGE.md)

## 🐛 Troubleshooting

### Error: "No module named 'pymongo'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Error: "No module named 'requests'"

**Solution:**
```bash
pip install requests
```

### Server Won't Start

Check that Python 3 is installed:
```bash
python3 --version
```

Should be Python 3.7 or higher.

## ⚠️ Note

The old TypeScript version (`src/index.ts` and `dist/index.js`) is still available, but clients now use the Python version by default.

If you need to revert to the TypeScript version, update paths in clients back to `dist/index.js` and `node`.
