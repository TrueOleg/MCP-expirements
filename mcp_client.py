#!/usr/bin/env python3
"""
Simple MCP client that uses Ollama to understand requests
and calls MCP tools to manage Mac applications
"""

import requests
import json
import subprocess
import sys
import os

MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "src", "server.py")
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

def call_mcp_tool(tool_name, arguments):
    """
    Calls MCP tool via JSON-RPC protocol.
    
    This method implements the client side of the MCP (Model Context Protocol) protocol.
    It launches the MCP server as a separate process and communicates with it via stdin/stdout,
    using JSON-RPC format for message exchange.
    
    Process:
    1. Forms JSON-RPC request with tool name and its arguments
    2. Launches MCP server as a child process
    3. Sends request to server's stdin
    4. Receives response from server's stdout
    5. Parses JSON-RPC response and extracts tool execution result
    
    Args:
        tool_name (str): Name of MCP tool to call (e.g., "open_application")
        arguments (dict): Dictionary with tool arguments
                         (e.g., {"appName": "Calculator"})
    
    Returns:
        str: Text result of tool execution or error message
    
    Usage example:
        result = call_mcp_tool("open_application", {"appName": "Safari"})
        # Returns: "Application 'Safari' successfully launched"
    """
    # Step 1: Form JSON-RPC request
    # JSON-RPC 2.0 is a standard protocol for remote procedure calls
    # All MCP servers communicate in this format
    request = {
        "jsonrpc": "2.0",          # JSON-RPC protocol version
        "id": 1,                   # Unique request identifier (for request-response matching)
        "method": "tools/call",    # MCP protocol method - tool call
        "params": {                # Call parameters
            "name": tool_name,     # Name of tool to call
            "arguments": arguments # Arguments to pass to tool
        }
    }
    
    try:
        # Step 2: Launch MCP server as separate process
        # subprocess.Popen creates new process and sets up communication channels
        process = subprocess.Popen(
            ["python3", MCP_SERVER_PATH],  # Command to run: python3 path/to/server.py
            stdin=subprocess.PIPE,          # Channel for sending data to server (server's stdin)
            stdout=subprocess.PIPE,         # Channel for reading response from server (server's stdout)
            stderr=subprocess.PIPE,         # Channel for errors (server's stderr)
            text=True                       # Indicate we're working with text input/output
        )
        
        # Step 3: Prepare and send JSON-RPC request
        # Convert request dictionary to JSON string
        request_json = json.dumps(request) + "\n"  # Add newline (MCP requires \n)
        
        # Send request to process stdin and wait for completion
        # communicate() sends data to stdin, waits for process completion
        # and returns (stdout, stderr). timeout=10 means if process
        # doesn't respond within 10 seconds, TimeoutExpired exception will be raised
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        # Step 4: Parse response from MCP server
        # MCP server sends response in JSON-RPC format, one line = one response
        # Go through all lines in stdout, look for valid JSON
        for line in stdout.split('\n'):
            if line.strip():  # Skip empty lines
                try:
                    # Try to parse line as JSON
                    response = json.loads(line)
                    
                    # Check if response has "result" field (successful response)
                    if "result" in response:
                        # In MCP protocol, result contains "content" array
                        # Each element has type (usually "text") and the text itself
                        content = response["result"].get("content", [])
                        if content:
                            # Extract text from first content element
                            # Usually content contains one element with type "text"
                            return content[0].get("text", "")
                    
                    # Check if response has "error" field (error)
                    if "error" in response:
                        # Extract error message from JSON-RPC response
                        error_message = response["error"].get("message", "Unknown error")
                        return f"Error: {error_message}"
                
                except json.JSONDecodeError:
                    # If line is not valid JSON, skip it
                    # (these could be service messages or stderr output)
                    continue
        
        # If we got here, didn't find valid JSON-RPC response
        return "No response from MCP server"
        
    except subprocess.TimeoutExpired:
        # If server didn't respond within 10 seconds
        process.kill()  # Force kill process
        return "Timeout when calling MCP tool"
    
    except Exception as e:
        # Any other error (e.g., server file not found, launch error, etc.)
        return f"Error calling MCP tool: {str(e)}"


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
            ["node", MCP_SERVER_PATH],
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


def ask_ollama_with_tools(user_query):
    """Uses Ollama to understand the request and call appropriate MCP tools"""
    
    # Get list of available tools
    tools = list_mcp_tools()
    tools_description = "\n".join([
        f"- {tool['name']}: {tool['description']}"
        for tool in tools
    ])
    
    # Create system prompt with tool descriptions
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
- "What applications are running?" -> {{"tool": "get_running_applications", "arguments": {{}}}}
- "Close Safari" -> {{"tool": "quit_application", "arguments": {{"appName": "Safari"}}}}
- "Open MongoDB Compass" -> {{"tool": "open_application", "arguments": {{"appName": "MongoDB Compass"}}}}
- "Create database test" -> {{"tool": "mongodb_create_database", "arguments": {{"databaseName": "test"}}}}
- "Create collection users in database test" -> {{"tool": "mongodb_create_collection", "arguments": {{"databaseName": "test", "collectionName": "users"}}}}
- "Find apple image in Google" -> {{"tool": "search_google_in_safari", "arguments": {{"query": "apple image"}}}}
- "Search Google for Python" -> {{"tool": "search_google_in_safari", "arguments": {{"query": "Python"}}}}
- "Find information about MCP in Google" -> {{"tool": "search_google_in_safari", "arguments": {{"query": "MCP"}}}}

IMPORTANT: 
- For search_google_in_safari always extract the search query from the user's text and pass it in the "query" parameter. If the user says "find X in Google" or "search Y", then query should be "X" or "Y".
- ALWAYS return ONLY a valid JSON object in the format {{"tool": "...", "arguments": {{...}}}}. DO NOT return just text or tool name without JSON. DO NOT return empty arguments.

Respond ONLY with JSON, without additional explanations or text."""

    # Query Ollama
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
            return f"Ollama error: {response.status_code}"
        
        result = response.json()
        answer = result.get("response", "").strip()
        
        print(f"🤖 Ollama response: {answer}")
        
        # Try to parse JSON response
        try:
            # Look for JSON in response (may be on multiple lines)
            import re
            # More precise JSON object search
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
                        
                        print(f"🔧 Calling tool: {tool_name}")
                        print(f"📝 Arguments: {tool_args}")
                        
                        # Call MCP tool
                        result = call_mcp_tool(tool_name, tool_args)
                        return result
                except json.JSONDecodeError:
                    continue
            
            # If JSON not found, try to parse entire response as JSON
            tool_call = json.loads(answer)
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
                
                print(f"🔧 Calling tool: {tool_name}")
                print(f"📝 Arguments: {tool_args}")
                
                result = call_mcp_tool(tool_name, tool_args)
                return result
                    
        except (json.JSONDecodeError, KeyError):
            print(f"🔧 Failed to parse JSON: {answer}")
            # If not JSON, check if it's just a tool name
            answer_lower = answer.lower().strip()
            if "search_google" in answer_lower or answer_lower == "search_google_in_safari":
                # Try to extract search query from original request
                query = extract_search_query(user_query)
                if query:
                    print(f"🔧 Calling tool: search_google_in_safari")
                    print(f"📝 Arguments: {{'query': '{query}'}}")
                    result = call_mcp_tool("search_google_in_safari", {"query": query})
                    return result
            # If not JSON, return regular response
            pass
        
        return answer
        
    except requests.exceptions.ConnectionError:
        return "❌ Failed to connect to Ollama. Start: ollama serve"
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter request: ")
    
    print(f"\n💬 Request: {query}")
    print("-" * 50)
    
    result = ask_ollama_with_tools(query)
    
    print("\n📋 Result:")
    print(result)
    print()


if __name__ == "__main__":
    main()

