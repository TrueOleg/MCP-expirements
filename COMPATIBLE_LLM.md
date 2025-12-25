# Compatible LLMs and Clients for MCP Mac Apps Server

Your MCP server works with **any LLM** that uses an MCP-compatible client. MCP (Model Context Protocol) is a standardized protocol, so the main thing is to use a client that supports it.

## 🔌 MCP-Compatible Clients

### 1. Claude Desktop (Anthropic) ⭐ Recommended

**Status**: Full MCP support, official client

**Installation**:
- Download from the official Anthropic website
- Install and create an account

**Configuration**:
1. Find the file: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add configuration:

```json
{
  "mcpServers": {
    "mac-apps": {
      "command": "node",
      "args": ["/Users/olegzaichkin/Documents/MCP/dist/index.js"]
    }
  }
}
```

**Available LLMs**: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku

---

### 2. Ollama (Local Models) 🏠 ✅ INSTALLED

**Status**: Local models via MCP clients

**Current models**: 
- ✅ `llama3.2` (2.0 GB) - installed
- ✅ `deepseek-r1:8b` (5.2 GB) - installed

📖 **Detailed instructions**: [OLLAMA_SETUP.md](./OLLAMA_SETUP.md)

**Installation**:
```bash
# Install Ollama
brew install ollama
# Or download from https://ollama.ai

# Start Ollama
ollama serve
```

**Available models** (loaded on demand):
```bash
# Popular models:
ollama pull llama3.2          # 3B parameters, very fast
ollama pull llama3.1:8b       # 8B parameters
ollama pull qwen2.5:7b        # Alibaba Qwen
ollama pull mistral:7b        # Mistral AI
ollama pull codellama:7b      # For programming
ollama pull phi3              # Microsoft Phi-3
```

**Usage with MCP**:
- Via Claude Desktop: install MCP server for Ollama
- Or use other MCP clients with Ollama support

---

### 3. LM Studio (Local Models) 🎨

**Status**: Graphical interface for local LLMs

**Installation**:
- Download from https://lmstudio.ai
- Install and load models through the interface

**MCP Support**:
- Official MCP server for LM Studio available
- Integrates with Claude Desktop

**Available models**: Supports GGUF format (Llama, Mistral, Phi, etc.)

---

### 4. DeepSeek

**Status**: Depends on MCP support in DeepSeek client

**Options**:
- If DeepSeek Desktop supports MCP (see DEEPSEEK_SETUP.md)
- Via API through other clients

---

### 5. OpenAI (GPT-4, GPT-3.5)

**Status**: Via Claude Desktop or other MCP clients

**Usage**:
- Claude Desktop can use OpenAI API (if supported)
- Or through other MCP-compatible clients

---

### 6. Other Local LLMs

Through Ollama or LM Studio you can use:
- **Llama 3** (Meta) - various sizes
- **Mistral** (Mistral AI)
- **Qwen** (Alibaba)
- **Phi-3** (Microsoft)
- **Code Llama** (Meta) - for code
- **StarCoder** - for programming
- And many others...

---

## 🎯 Selection Recommendations

### For Quick Start
**Claude Desktop** - the simplest option:
- ✅ Installation in 2 minutes
- ✅ Full MCP support out of the box
- ✅ Excellent response quality
- ❌ Requires internet (cloud model)

### For Privacy and Offline Work
**Ollama + Claude Desktop**:
- ✅ Works completely locally
- ✅ No internet required
- ✅ Free
- ❌ Requires sufficient RAM (8GB+ for large models)
- ❌ May be slower than cloud models

### For Convenient Model Management
**LM Studio**:
- ✅ Beautiful graphical interface
- ✅ Easy to switch between models
- ✅ Detailed model information
- ✅ MCP support through integration

---

## 🔧 Local Model Configuration

### Option 1: Ollama via MCP

1. Install Ollama and start the server
2. Install MCP server for Ollama in Claude Desktop:

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

### Option 2: LM Studio MCP

1. Install LM Studio
2. Start local server in LM Studio
3. Add to Claude Desktop configuration:

```json
{
  "mcpServers": {
    "lmstudio": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-lmstudio"]
    },
    "mac-apps": {
      "command": "node",
      "args": ["/Users/olegzaichkin/Documents/MCP/dist/index.js"]
    }
  }
}
```

---

## 📊 Option Comparison

| Option | Speed | Privacy | Quality | Cost | Internet |
|--------|-------|---------|---------|------|----------|
| Claude Desktop | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 💰💰💰 | Required |
| Ollama (llama3.2) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Free | Not needed |
| Ollama (llama3.1:8b) | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free | Not needed |
| LM Studio | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free | Not needed |

---

## 🚀 Quick Start

### Simplest Path (recommended for beginners):

1. **Install Claude Desktop**
   ```bash
   # Download from https://claude.ai/download
   ```

2. **Configure MCP server** (see README.md)

3. **Start using** - just ask Claude:
   - "Open Safari"
   - "What applications are running?"
   - "Open file ~/Documents/test.txt in TextEdit"

### For Local Models:

1. **Install Ollama**
   ```bash
   brew install ollama
   ollama serve
   ```

2. **Load a model**
   ```bash
   ollama pull llama3.2
   ```

3. **Configure MCP in Claude Desktop** (see above)

4. **Use local model** through Claude Desktop

---

## 📝 Usage Examples

After configuring any of these options, you'll be able to use LLM to manage applications:

```
User: "Open Safari and go to google.com"
LLM: [uses open_application and run_applescript]

User: "Show me all running applications"
LLM: [uses get_running_applications]

User: "Create a new document in TextEdit and write 'Hello World'"
LLM: [uses open_application and run_applescript]
```

---

## 🔍 Finding Other MCP Clients

If you want to find other options:
- [MCP Servers List](https://github.com/modelcontextprotocol/servers)
- [MCP Market](https://mcplist.ru)
- Official MCP documentation

---

## ⚠️ Important Notes

1. **Compatibility**: Your MCP server works with any MCP-compatible client
2. **Multiple Servers**: You can use multiple MCP servers simultaneously
3. **Privacy**: Local models (Ollama, LM Studio) provide complete privacy
4. **Performance**: Local models require sufficient RAM (16GB+ recommended)

---

**Main point**: Choose the client that suits you. The MCP server will work the same with all of them! 🎉
