# Using MCP Client with Ollama

## 🎉 What is This?

`mcp_client.py` - a simple Python client that combines Ollama (local LLMs) with MCP tools for managing Mac applications.

**How it works:**
1. You ask a question in natural language
2. Ollama determines which MCP tool to use
3. Client calls the appropriate tool
4. Result is returned to you

## 🚀 Quick Start

### 1. Make Sure Everything is Running

```bash
# Ollama should be running
ollama serve

# MCP server should be built
npm run build
```

### 2. Use the Client

```bash
# Simple request
python3 mcp_client.py "Open Calculator"

# Or interactive mode
python3 mcp_client.py
# Then enter request
```

## 📝 Usage Examples

### Application Management

```bash
# Open application
python3 mcp_client.py "Open Safari"

# Close application
python3 mcp_client.py "Close Calculator"

# List running applications
python3 mcp_client.py "What applications are currently running?"

# Open file in application
python3 mcp_client.py "Open file ~/Documents/test.txt in TextEdit"
```

### Using Ollama Tools

```bash
# Generate via Ollama
python3 mcp_client.py "Use Ollama to explain this code"

# List models
python3 mcp_client.py "Show list of Ollama models"
```

### Combined Requests

You can combine requests, though the client currently processes one tool at a time.

## ⚙️ Configuration

### Changing Ollama Model

In `mcp_client.py` file, change:

```python
OLLAMA_MODEL = "llama3.2"  # Change to your model
```

### Changing Ollama URL

```python
OLLAMA_API_URL = "http://localhost:11434"  # Or other address
```

## 🔧 How It Works Technically

1. **Getting Tool List**: Client first requests list of available tools from MCP server

2. **Creating Prompt**: System prompt is formed for Ollama with description of all available tools

3. **Querying Ollama**: Request is sent with tool descriptions and user question

4. **Parsing Response**: Response from Ollama is parsed to find JSON with tool name and arguments

5. **Calling Tool**: If JSON with tool is found, client calls the appropriate MCP tool via JSON-RPC

6. **Returning Result**: Tool execution result is returned to user

## 🐛 Troubleshooting

### Error: "Failed to Connect to Ollama"

**Solution:**
```bash
# Start Ollama server
ollama serve
```

### Error: "No Response from MCP Server"

**Solution:**
```bash
# Make sure server is built
npm run build

# Check that file exists
ls -la dist/index.js
```

### Model Doesn't Understand Request

Try a more explicit request:
- Instead of "Open calculator" → "Open application Calculator"
- Instead of "Close browser" → "Close application Safari"

### Ollama Returns Text Instead of JSON

This is normal for some requests. Client will return text response from Ollama if it couldn't determine a tool.

## 💡 Recommendations

1. **Use Exact Application Names**: "Calculator", "Safari", "TextEdit" (with capital letter)

2. **For Complex Tasks Use Claude Desktop**: This client is a simplified version. For more complex tasks, it's better to use a full MCP client (Claude Desktop)

3. **Check Tool List**: Client automatically gets list of available tools on each startup

## 🆚 Comparison with Claude Desktop

| Feature | mcp_client.py | Claude Desktop |
|---------|---------------|----------------|
| Ease of Use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Understanding Accuracy | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Complex Request Support | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Local Operation | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Multiple Tools at Once | ❌ | ✅ |
| Graphical Interface | ❌ | ✅ |

## 📚 Next Steps

For more advanced usage, it's recommended to:
1. Configure Claude Desktop with MCP servers (see README.md)
2. Use multiple MCP servers simultaneously
3. Create your own more complex client with support for tool chains
