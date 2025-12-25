# Ollama Setup with MCP Mac Apps Server

## ✅ Current Status

- ✅ Ollama installed
- ✅ Ollama server running
- ✅ Model `llama3.2` loaded (2.0 GB)
- ✅ Model `deepseek-r1:8b` available (5.2 GB)

## 🚀 Quick Start

### Option 1: Usage via Claude Desktop

1. **Install Claude Desktop** (if not already installed):
   - Download from https://claude.ai/download

2. **Install MCP Server for Ollama**:
   ```bash
   npx -y @modelcontextprotocol/create-server ollama-mcp
   ```
   
   Or add to Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "ollama": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-ollama"]
       },
       "mac-apps": {
         "command": "node",
         "args": ["/Users/olegzaichkin/Documents/MCP/dist/index.js"]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Now Claude can**:
   - Use local models via Ollama
   - Manage Mac applications through your MCP server

### Option 2: Direct API Usage

Ollama provides REST API at `http://localhost:11434`. You can use it directly with any client that supports OpenAI-compatible API.

**Testing API:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello! How are you?",
  "stream": false
}'
```

## 📝 Available Models

Check model list:
```bash
ollama list
```

Load other models:
```bash
# Popular models
ollama pull llama3.1:8b       # More powerful version
ollama pull mistral:7b        # Mistral AI
ollama pull qwen2.5:7b        # Alibaba Qwen
ollama pull codellama:7b      # For programming
ollama pull phi3              # Lightweight Microsoft model
```

## 🔧 Ollama Management

**Start Server:**
```bash
ollama serve
```

**Stop Server:**
```bash
# Press Ctrl+C or find process and kill it
ps aux | grep ollama
kill <PID>
```

**Auto-start (macOS):**
Ollama usually starts automatically via LaunchAgent. If you need to add to autostart:
```bash
# Create LaunchAgent
cat > ~/Library/LaunchAgents/com.ollama.server.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load agent
launchctl load ~/Library/LaunchAgents/com.ollama.server.plist
```

## 🎯 Usage Examples

### Test Model Directly:
```bash
ollama run llama3.2 "Tell me about MCP protocol"
```

### Usage via API with curl:
```bash
# Simple request
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "What is Model Context Protocol?",
  "stream": false
}'

# With streaming
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Hello!",
  "stream": true
}'
```

### Usage with Python:
```python
import requests
import json

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'llama3.2',
        'prompt': 'Open Safari',
        'stream': False
    }
)

print(response.json()['response'])
```

## 🔍 Verification

Check that server is running:
```bash
curl http://localhost:11434/api/tags
```

Should return list of models in JSON format.

## 💡 Tips

1. **Performance**: Model `llama3.2` (2GB) works fast but is less powerful. For better quality, use `llama3.1:8b` or `deepseek-r1:8b`.

2. **Memory**: Make sure you have enough RAM. Models require:
   - `llama3.2`: ~2-4 GB RAM
   - `llama3.1:8b`: ~8-10 GB RAM
   - `deepseek-r1:8b`: ~10-12 GB RAM

3. **Speed**: On Mac with Apple Silicon (M1/M2/M3), models work significantly faster thanks to the neural processor.

4. **Privacy**: All processing happens locally, data is not sent anywhere.

## 📚 Useful Links

- [Ollama Documentation](https://ollama.ai/docs)
- [Available Models](https://ollama.ai/library)
- [Ollama GitHub](https://github.com/ollama/ollama)
