#!/usr/bin/env python3
"""
Voice client for managing Mac applications through MCP
Uses Ollama for understanding commands and MCP tools for management
"""

import requests
import json
import subprocess
import sys
import os
import time
import select

MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "src", "server.py")
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  speech_recognition is not installed. Install: pip install SpeechRecognition")
    print("   For voice input, pyaudio is also needed: pip install pyaudio")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 is not installed. Install: pip install pyttsx3")
    print("   Or use macOS built-in say (already available)")


def speak(text, use_system=True):
    """Converts text to speech"""
    if use_system:
        # Use built-in macOS say command
        subprocess.run(["say", text], check=False)
    elif TTS_AVAILABLE:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
            subprocess.run(["say", text], check=False)
    else:
        subprocess.run(["say", text], check=False)


def listen(use_microphone=True, activation_key='space'):
    """
    Listens to voice input and converts it to text
    Activated by pressing a key (default is space)
    """
    if not use_microphone or not SPEECH_RECOGNITION_AVAILABLE:
        # Alternative: use text input
        return input("You: ")
    
    # Wait for activation key press
    if activation_key == 'space':
        print("⌨️  Press SPACE to start voice recording (or Enter for text input)")
    elif activation_key == 'enter':
        print("⌨️  Press ENTER to start voice recording")
    else:
        print(f"⌨️  Press {activation_key.upper()} to start voice recording")
    
    # Use threading for non-blocking key reading
    import select
    import termios
    import tty
    
    # Configure terminal for single character reading
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        
        while True:
            # Check if there's input
            if select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                
                # Space or Enter activates recording
                if key in [' ', '\n', '\r']:
                    print("\n🎤 Recording... (speak, press Enter when finished)")
                    break
                # 'q' to exit
                elif key == 'q':
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    return None
                # Any other key - text mode
                elif key == '\x1b':  # ESC
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    return input("\nYou: ")
    except (ImportError, AttributeError):
        # Fallback for systems without termios (e.g., Windows)
        key = input("Press Enter to record voice: ")
        if key.lower() == 'q':
            return None
    
    finally:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except:
            pass
    
    # Start recording
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        # Adapt to ambient noise (faster for button activation)
        r.adjust_for_ambient_noise(source, duration=0.3)
        
        try:
            # Listen with increased time limit since user already pressed button
            audio = r.listen(source, timeout=30, phrase_time_limit=30)
            print("🔄 Recognizing speech...")
            
            # Use Google Speech Recognition (requires internet)
            text = r.recognize_google(audio, language="en-US")
            print(f"📝 Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️  Timeout. Didn't hear command.")
            return None
        except sr.UnknownValueError:
            print("❌ Could not recognize speech")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            print("💡 Use text input or install offline recognition")
            return None


def call_mcp_tool(tool_name, arguments):
    """Calls MCP tool via JSON-RPC"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        process = subprocess.Popen(
            ["python3", MCP_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if "result" in response:
                        content = response["result"].get("content", [])
                        if content:
                            return content[0].get("text", "")
                    if "error" in response:
                        return f"Error: {response['error'].get('message', 'Unknown error')}"
                except json.JSONDecodeError:
                    continue
        
        return "No response from MCP server"
        
    except subprocess.TimeoutExpired:
        process.kill()
        return "Timeout when calling MCP tool"
    except Exception as e:
        return f"Error calling MCP tool: {str(e)}"


def extract_search_query(user_query):
    print(f"🔍 Extracting query from: '{user_query}'")
    """Extracts search query from user text"""
    import re
    if not user_query:
        return None
    
    # Patterns for finding query (more precise, using greedy quantifier)
    patterns = [
        r'find\s+(.+?)\s+in\s+google',
        r'search\s+(.+?)\s+in\s+google',
        r'search\s+for\s+(.+?)\s+in\s+google',
        r'look\s+up\s+(.+?)\s+in\s+google',
        r'google\s+(.+?)$',
    ]
    
    query_lower = user_query.lower()
    for pattern in patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            # Remove extra words at the end (in case pattern captured extra)
            query = re.sub(r'\s+in\s+google.*$', '', query, flags=re.IGNORECASE)
            if query:
                return query.strip()
    
    # If pattern with "in google" not found, try just "find X" or "search X"
    simple_patterns = [
        r'^find\s+(.+)$',
        r'^search\s+(.+)$',
        r'^search\s+for\s+(.+)$',
        r'^look\s+up\s+(.+)$',
    ]
    
    for pattern in simple_patterns:
        match = re.search(pattern, query_lower, re.IGNORECASE)
        if match:
            query = match.group(1).strip()
            # Remove "in google" if present
            query = re.sub(r'\s+in\s+google.*$', '', query, flags=re.IGNORECASE)
            if query:
                return query.strip()
    
    # If no pattern found, return entire query, removing words "find", "search", "in google"
    query = user_query
    query = re.sub(r'^find\s+', '', query, flags=re.IGNORECASE)
    query = re.sub(r'^search\s+', '', query, flags=re.IGNORECASE)
    query = re.sub(r'^search\s+for\s+', '', query, flags=re.IGNORECASE)
    query = re.sub(r'^look\s+up\s+', '', query, flags=re.IGNORECASE)
    query = re.sub(r'\s+in\s+google.*$', '', query, flags=re.IGNORECASE)
    result = query.strip() if query.strip() else None
    return result


def list_mcp_tools():
    """Gets list of available MCP tools"""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        process = subprocess.Popen(
            ["python3", MCP_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if "result" in response and "tools" in response["result"]:
                        return response["result"]["tools"]
                except json.JSONDecodeError:
                    continue
        
        return []
        
    except Exception as e:
        print(f"Error getting list of tools: {e}", file=sys.stderr)
        return []


def ask_ollama_with_tools(user_query, verbose=False):
    """Uses Ollama to understand the request and call appropriate MCP tools"""
    
    tools = list_mcp_tools()
    tools_description = "\n".join([
        f"- {tool['name']}: {tool['description']}"
        for tool in tools
    ])
    
    system_prompt = f"""You are an assistant that can manage Mac applications through MCP tools.

Available tools:
{tools_description}

When the user asks to open an application, perform an action, or get information, determine which tool to use and return JSON in the format:
{{
    "tool": "tool_name",
    "arguments": {{"parameter": "value"}}
}}

If the request doesn't require using tools, just respond with regular text.

Examples:
- "Open Calculator" -> {{"tool": "open_application", "arguments": {{"appName": "Calculator"}}}}
- "Close Safari" -> {{"tool": "quit_application", "arguments": {{"appName": "Safari"}}}}
- "What applications are running?" -> {{"tool": "get_running_applications", "arguments": {{}}}}
- "Open MongoDB Compass" -> {{"tool": "open_application", "arguments": {{"appName": "MongoDB Compass"}}}}
- "Create database test" -> {{"tool": "mongodb_create_database", "arguments": {{"databaseName": "test"}}}}
- "Create collection users in database test" -> {{"tool": "mongodb_create_collection", "arguments": {{"databaseName": "test", "collectionName": "users"}}}}
- "Add document {{\"name\": \"John\"}} to collection users in database test" -> {{"tool": "mongodb_insert_document", "arguments": {{"databaseName": "test", "collectionName": "users", "document": "{{\\\"name\\\": \\\"John\\\"}}"}}}}
- "Find apple image in Google" -> {{"tool": "search_google_in_safari", "arguments": {{"query": "apple image"}}}}
- "Search Google for Python" -> {{"tool": "search_google_in_safari", "arguments": {{"query": "Python"}}}}
- "Find information about MCP in Google" -> {{"tool": "search_google_in_safari", "arguments": {{"query": "MCP"}}}}

IMPORTANT: 
- For search_google_in_safari always extract the search query from the user's text and pass it in the "query" parameter. If the user says "find X in Google" or "search Y", then query should be "X" or "Y".
- ALWAYS return ONLY a valid JSON object in the format {{"tool": "...", "arguments": {{...}}}}. DO NOT return just text or tool name without JSON. DO NOT return empty arguments.

Respond ONLY with JSON, without additional explanations or text."""

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\nUser: {user_query}\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"Ollama error: {response.status_code}", False
        
        result = response.json()
        answer = result.get("response", "").strip()
        
        if verbose:
            print(f"🤖 Ollama response: {answer}")
        
        # Try to parse JSON
        try:
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, answer, re.DOTALL)
            print(f"🔍 JSON matches: {json_matches}")
            
            for json_str in json_matches:
                try:
                    tool_call = json.loads(json_str)
                    if "tool" in tool_call:
                        tool_name = tool_call["tool"]
                        tool_args = tool_call.get("arguments", {})
                        
                        print(f"🔧 tool_call: {tool_call}")
                        print(f"🔧 tool_name: {tool_name}")
                        
                        # Fallback: if arguments are empty for search_google_in_safari, extract query from user_query
                        if tool_name == "search_google_in_safari":
                            print(f"🔍 ==========tool_name: {tool_name}")
                            # Check if query is in arguments
                            current_query = None
                            if tool_args and isinstance(tool_args, dict):
                                current_query = tool_args.get("query")
                            
                            print(f"🔍 Check: tool_args={tool_args}, current_query={current_query}")
                            
                            if not current_query:
                                # Try to extract search query from original request
                                print(f"🔍 Extracting query from: '{user_query}'")
                                query = extract_search_query(user_query)
                                print(f"🔍 Extraction result: '{query}'")
                                
                                if query:
                                    # Make sure tool_args is a dictionary
                                    if not tool_args or not isinstance(tool_args, dict):
                                        tool_args = {}
                                    tool_args["query"] = query
                                    print(f"✅ Set query: '{query}'")
                                else:
                                    print(f"⚠️ Failed to extract query from: '{user_query}'")
                                    # As last resort, use entire query, removing service words
                                    fallback_query = user_query.replace("find", "").replace("search", "").replace("in google", "").replace("for", "").strip()
                                    if fallback_query:
                                        if not tool_args or not isinstance(tool_args, dict):
                                            tool_args = {}
                                        tool_args["query"] = fallback_query
                                        print(f"✅ Used fallback query: '{fallback_query}'")
                        
                        if verbose:
                            print(f"🔧 Calling tool: {tool_name}")
                            print(f"📝 Arguments: {tool_args}")
                        
                        result = call_mcp_tool(tool_name, tool_args)
                        return result, True
                except json.JSONDecodeError:
                    continue
            
            # Try to parse entire response as JSON
            tool_call = json.loads(answer)
            print(f"🔧 tool_call: {tool_call}")
            if "tool" in tool_call:
                tool_name = tool_call["tool"]
                tool_args = tool_call.get("arguments", {})
                
                # Fallback: if arguments are empty for search_google_in_safari, extract query from user_query
                if tool_name == "search_google_in_safari" and (not tool_args or not tool_args.get("query")):
                    query = extract_search_query(user_query)
                    if query:
                        if not tool_args:
                            tool_args = {}
                        tool_args["query"] = query
                        print(f"🔍 Extracted search query from text: '{query}'")
                    else:
                        print(f"⚠️ Failed to extract search query from: '{user_query}'")
                
                if verbose:
                    print(f"🔧 Calling tool: {tool_name}")
                    print(f"📝 Arguments: {tool_args}")
                
                result = call_mcp_tool(tool_name, tool_args)
                return result, True
                    
        except (json.JSONDecodeError, KeyError):
            print(f"🔧 Failed to parse JSON: {answer}")
            # If not JSON, check if it's just a tool name
            answer_lower = answer.lower().strip()
            if "search_google" in answer_lower or answer_lower == "search_google_in_safari":
                # Try to extract search query from original request
                query = extract_search_query(user_query)
                if query:
                    if verbose:
                        print(f"🔧 Calling tool: search_google_in_safari")
                        print(f"📝 Arguments: {{'query': '{query}'}}")
                    result = call_mcp_tool("search_google_in_safari", {"query": query})
                    return result, True
            pass
        
        return answer, False
        
    except requests.exceptions.ConnectionError:
        return "❌ Failed to connect to Ollama. Start: ollama serve", False
    except Exception as e:
        return f"Error: {str(e)}", False


def main():
    print("🎤 Voice assistant for managing Mac applications")
    print("=" * 60)
    print(f"📦 Model: {OLLAMA_MODEL}")
    print(f"🌐 Ollama: {OLLAMA_API_URL}")
    print("=" * 60)
    print()
    
    # Check availability
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("💡 For voice input, install:")
        print("   pip install SpeechRecognition pyaudio")
        print()
        print("📝 Text input will be used now")
        print()
        use_voice_input = False
    else:
        use_voice_input = True
        print("✅ Voice input available")
        print("✅ Voice output available (via macOS say)")
        print()
    
    while True:
        try:
            # Voice or text input
            if use_voice_input:
                query = listen()
                if query is None:
                    continue
            else:
                query = input("You (or 'exit' to quit): ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'stop']:
                speak("Goodbye!")
                print("👋 Goodbye!")
                break
            
            print(f"\n💬 Request: {query}")
            print("-" * 60)
            
            # Process request
            result, is_action = ask_ollama_with_tools(query, verbose=True)
            
            print(f"\n📋 Result: {result}")
            
            # Voice output of result
            if is_action:
                # For actions, speak brief answer
                speak(result.split('\n')[0] if '\n' in result else result)
            else:
                # For regular answers, speak entire text (if short)
                if len(result) < 200:
                    speak(result)
                else:
                    speak("Result shown on screen")
            
            print()
            time.sleep(0.5)  # Small pause between commands
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            speak("Goodbye!")
            break
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\n❌ {error_msg}")
            speak("An error occurred")
            time.sleep(1)


if __name__ == "__main__":
    main()

