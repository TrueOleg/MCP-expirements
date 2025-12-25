# Voice Control Setup for Applications via MCP

## 🎤 What is This?

`voice_client.py` - a voice client that allows you to control Mac applications with voice commands, using Ollama for understanding and MCP tools for executing actions.

## 🚀 Quick Installation

### 1. Install Required Libraries

```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Install libraries for voice input
pip install SpeechRecognition pyaudio

# For better TTS quality (optional)
pip install pyttsx3
```

**Note for macOS:**
- `pyaudio` may require installing PortAudio via Homebrew:
  ```bash
  brew install portaudio
  pip install pyaudio
  ```

### 2. Configure Permissions

macOS may require microphone permissions:
- System Settings → Privacy & Security → Microphone
- Allow access for Terminal/Python

### 3. Make Sure Everything is Running

```bash
# Ollama should be running
ollama serve

# MCP server should be built
npm run build
```

## 📝 Usage

### Starting Voice Client

```bash
python3 voice_client.py
```

### Voice Command Examples

**Opening Applications:**
- "Open Calculator"
- "Open Safari"
- "Launch TextEdit"

**Closing Applications:**
- "Close Calculator"
- "Close Safari"
- "Quit Telegram application"

**Information:**
- "What applications are running?"
- "Show list of applications"

**Exit:**
- "Exit"
- "Stop"

## ⚙️ Configuration

### Changing Ollama Model

In `voice_client.py` file:

```python
OLLAMA_MODEL = "llama3.2"  # Change to your model
```

### Disabling Voice Input (Text Only)

If you don't want to use a microphone, simply don't install `SpeechRecognition` and `pyaudio`. The client will automatically switch to text input.

### Using Different TTS

By default, the built-in macOS `say` command is used. You can use `pyttsx3` for more control:

```python
# In speak() function change use_system=False
speak(text, use_system=False)
```

## 🔧 How It Works

1. **Voice Input**: Microphone records your speech
2. **Speech Recognition**: Google Speech Recognition converts speech to text (requires internet)
3. **Command Understanding**: Ollama analyzes text and determines the needed MCP tool
4. **Action Execution**: MCP tool executes action (opens/closes application)
5. **Voice Response**: Result is spoken via macOS `say`

## 🌐 Offline Speech Recognition

By default, Google Speech Recognition is used (requires internet). For offline work, you can use:

### Option 1: Whisper (OpenAI)

```bash
pip install openai-whisper
```

Then in `voice_client.py` modify the `listen()` function:

```python
import whisper

def listen():
    model = whisper.load_model("base")
    # ... code for recording audio ...
    result = model.transcribe(audio_file)
    return result["text"]
```

### Option 2: Built-in macOS Recognition (via AppleScript)

You can use built-in macOS recognition via AppleScript, but this is more complex.

## 🐛 Troubleshooting

### Error: "No module named 'speech_recognition'"

**Solution:**
```bash
pip install SpeechRecognition
```

### Error Installing pyaudio

**Solution (macOS):**
```bash
brew install portaudio
pip install pyaudio
```

### Microphone Not Working

**Solution:**
1. Check permissions: System Settings → Privacy → Microphone
2. Check that microphone is connected and working
3. Try running through Terminal (not through IDE)

### "Could Not Recognize Speech"

**Causes:**
- Speech too quiet
- Background noise
- No internet (for Google Speech Recognition)

**Solutions:**
- Speak clearer and louder
- Reduce background noise
- Use offline recognition (Whisper)

### Voice Output Not Working

**Solution:**
Check that macOS `say` command works:
```bash
say "Test"
```

If it doesn't work, install `pyttsx3`:
```bash
pip install pyttsx3
```

## 💡 Usage Tips

1. **Speak Clearly**: Pronounce commands clearly and loud enough
2. **Use Exact Names**: "Calculator", "Safari" (with capital letter)
3. **Short Commands**: Short, direct commands work better
4. **Silence Between Commands**: Give the system time to process a command before the next one

## 📊 Comparison with Text Client

| Feature | voice_client.py | mcp_client.py |
|---------|-----------------|---------------|
| Voice Input | ✅ | ❌ |
| Voice Output | ✅ | ❌ |
| Text Input | ✅ | ✅ |
| Simplicity | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Requires Internet | Yes (for STT) | No |
| Microphone | Required | Not required |

## 🔐 Privacy

**Important:**
- Google Speech Recognition sends audio to Google servers for processing
- If this is a concern, use offline recognition (Whisper)
- Everything else (Ollama, MCP) works locally

## 🎯 Usage Examples

### Basic Usage

```bash
python3 voice_client.py
# Say: "Open Calculator"
# Calculator opens
# System responds: "Application Calculator successfully launched"
```

### Continuous Operation

The client works in a loop, allowing you to give multiple commands in a row:
- "Open Safari"
- "Open Calculator"
- "What applications are running?"
- "Close Calculator"
- "Exit"

## 🚀 Advanced Usage

### Custom Commands

You can extend the command list by adding handling in `ask_ollama_with_tools()`.

### Integration with Other Services

You can add integration with:
- Calendar (creating events)
- Reminders
- Music (playback control)
- And more

## 📚 Additional Resources

- [SpeechRecognition documentation](https://github.com/Uberi/speech_recognition)
- [Whisper (offline STT)](https://github.com/openai/whisper)
- [pyttsx3 (TTS)](https://pyttsx3.readthedocs.io/)
