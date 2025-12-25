# Ollama Integration in MCP Mac Apps Server

## ✅ What's Added

Ollama API integration has been added to the MCP server, allowing you to use local LLM models directly from MCP tools.

### New Tools:

1. **`ollama_generate`** - Generate responses using local Ollama models
2. **`ollama_list_models`** - Get list of available Ollama models

## 🚀 Usage

### 1. Make Sure Ollama is Running

```bash
# Check that Ollama server is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve
```

### 2. Rebuild MCP Server

```bash
npm run build
```

### 3. Usage via LLM Client

After configuring in Claude Desktop or another MCP client, you can use the new tools:

**Example Requests:**
- "Use Ollama to explain this code"
- "Show list of available Ollama models"
- "Generate response using llama3.2 model"

## 📋 Tool Parameters

### `ollama_generate`

**Parameters:**
- `prompt` (required) - Prompt for the model
- `model` (optional) - Model name (default: "llama3.2")

**Usage Example:**
```json
{
  "name": "ollama_generate",
  "arguments": {
    "prompt": "Explain what MCP protocol is",
    "model": "llama3.2"
  }
}
```

### `ollama_list_models`

**Parameters:** none

**Returns:** List of available models with sizes

## ⚙️ Configuration

### Changing Ollama Server URL

By default, `http://localhost:11434` is used.

To change URL, set environment variable:
```bash
export OLLAMA_API_URL=http://your-ollama-server:11434
```

Or change in code:
```typescript
const OLLAMA_API_URL = "http://your-custom-url:11434";
```

## 🔧 Usage Examples

### Via Claude Desktop

After configuring MCP server, simply ask Claude:

```
"Use Ollama to generate response to question: what is artificial intelligence?"
```

Claude will automatically use the `ollama_generate` tool.

### Combining with Other Tools

You can combine Ollama with application management tools:

```
"Use Ollama to analyze contents of file ~/Documents/report.txt, 
then open TextEdit to show results"
```

## 📊 Available Models

Check list of models via `ollama_list_models` tool or manually:

```bash
ollama list
```

Popular models:
- `llama3.2` - fast, lightweight model (2GB)
- `llama3.1:8b` - more powerful version (4.7GB)
- `deepseek-r1:8b` - for reasoning (5.2GB)
- `mistral:7b` - Mistral AI model
- `qwen2.5:7b` - Alibaba Qwen

## 🛠️ Troubleshooting

### Error: "Failed to Connect to Ollama Server"

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Check that port 11434 is accessible: `curl http://localhost:11434/api/tags`
3. Check `OLLAMA_API_URL` environment variable

### Error: "Model Not Found"

**Solution:**
1. Load model: `ollama pull llama3.2`
2. Check model list: `ollama list`

### Slow Generation

**Causes:**
- Model too large for your hardware
- Insufficient RAM
- CPU instead of GPU

**Solutions:**
- Use smaller model (e.g., `llama3.2` instead of `llama3.1:8b`)
- Close other applications to free memory
- On Mac with Apple Silicon, use Metal for acceleration

## 🔐 Security

- Ollama API works locally and doesn't send data to internet
- All requests are processed on your computer
- Make sure Ollama server is not accessible externally (localhost only by default)

## 📚 Additional Information

- [Ollama Documentation](https://ollama.ai/docs)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Ollama Model List](https://ollama.ai/library)
