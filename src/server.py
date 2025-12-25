#!/usr/bin/env python3
"""
MCP server for managing Mac applications
Python rewritten version
Uses JSON-RPC protocol via stdio
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests
from pymongo import MongoClient


# Константы
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def exec_command(command: str) -> tuple[str, str]:
    """Executes shell command and returns stdout and stderr"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Command execution timeout"
    except Exception as e:
        return "", str(e)


def get_tools() -> List[Dict[str, Any]]:
    """Returns list of all available tools"""
    return [
        {
            "name": "open_application",
            "description": "Opens an application on Mac by name. Examples: 'Safari', 'Finder', 'TextEdit', 'Calculator'",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "appName": {
                        "type": "string",
                        "description": "Application name to launch (e.g., 'Safari', 'Calculator')",
                    },
                },
                "required": ["appName"],
            },
        },
        {
            "name": "get_running_applications",
            "description": "Gets list of all running applications on Mac",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "run_applescript",
            "description": "Executes AppleScript command in specified application. Useful for automating actions in applications",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "appName": {
                        "type": "string",
                        "description": "Application name (e.g., 'Safari', 'Finder')",
                    },
                    "script": {
                        "type": "string",
                        "description": "AppleScript command to execute",
                    },
                },
                "required": ["appName", "script"],
            },
        },
        {
            "name": "quit_application",
            "description": "Closes specified application",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "appName": {
                        "type": "string",
                        "description": "Application name to close",
                    },
                },
                "required": ["appName"],
            },
        },
        {
            "name": "open_file_with_app",
            "description": "Opens file or URL in specified application",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file or URL",
                    },
                    "appName": {
                        "type": "string",
                        "description": "Application name to open file with",
                    },
                },
                "required": ["path", "appName"],
            },
        },
        {
            "name": "ollama_generate",
            "description": "Generates response using local Ollama model. Use for tasks requiring AI text processing",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Ollama model name (e.g., 'llama3.2', 'deepseek-r1:8b'). Default 'llama3.2'",
                        "default": "llama3.2",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt for the model",
                    },
                },
                "required": ["prompt"],
            },
        },
        {
            "name": "ollama_list_models",
            "description": "Gets list of available Ollama models",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "mongodb_create_database",
            "description": "Creates new database in MongoDB",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                },
                "required": ["databaseName"],
            },
        },
        {
            "name": "mongodb_list_databases",
            "description": "Gets list of all databases in MongoDB",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "mongodb_create_collection",
            "description": "Creates new collection in specified database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Collection name",
                    },
                },
                "required": ["databaseName", "collectionName"],
            },
        },
        {
            "name": "mongodb_list_collections",
            "description": "Gets list of collections in specified database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                },
                "required": ["databaseName"],
            },
        },
        {
            "name": "mongodb_delete_collection",
            "description": "Deletes collection from database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Collection name to delete",
                    },
                },
                "required": ["databaseName", "collectionName"],
            },
        },
        {
            "name": "mongodb_insert_document",
            "description": "Inserts document into collection",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Collection name",
                    },
                    "document": {
                        "type": "string",
                        "description": "JSON string with document to insert",
                    },
                },
                "required": ["databaseName", "collectionName", "document"],
            },
        },
        {
            "name": "mongodb_find_documents",
            "description": "Finds documents in collection",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Collection name",
                    },
                    "filter": {
                        "type": "string",
                        "description": "JSON string with search filter (optional)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of documents (default 100)",
                    },
                },
                "required": ["databaseName", "collectionName"],
            },
        },
        {
            "name": "mongodb_delete_document",
            "description": "Deletes document(s) from collection by filter",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Database name",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Collection name",
                    },
                    "filter": {
                        "type": "string",
                        "description": "JSON string with deletion filter",
                    },
                },
                "required": ["databaseName", "collectionName", "filter"],
            },
        },
        {
            "name": "search_google_in_safari",
            "description": "Performs Google search through Safari browser",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Google",
                    },
                },
                "required": ["query"],
            },
        },
    ]


# Implementation of tools for working with Mac applications
def open_application(app_name: str) -> str:
    """Opens application by name"""
    stdout, stderr = exec_command(f'open -a "{app_name}"')
    if stderr:
        raise Exception(f'Failed to launch application "{app_name}": {stderr}')
    return f'Application "{app_name}" successfully launched'


def search_google_in_safari(query: str) -> str:
    """Performs Google search through Safari"""
    if not query:
        raise Exception("Search query cannot be empty")
    
    # Convert to string and encode search query for URL
    query_str = str(query)
    encoded_query = quote_plus(query_str)
    google_url = f"https://www.google.com/search?q={encoded_query}"
    
    stdout, stderr = exec_command(f'open -a Safari "{google_url}"')
    if stderr:
        raise Exception(f'Failed to open search in Safari: {stderr}')
    return f'Search "{query_str}" opened in Safari'


def get_running_applications() -> str:
    """Gets list of running applications"""
    apple_script = 'tell application "System Events" to get name of every application process whose background only is false'
    stdout, stderr = exec_command(f'osascript -e \'{apple_script}\'')
    if stderr:
        raise Exception(f"Failed to get list of applications: {stderr}")

    apps = [app.strip() for app in stdout.strip().split(", ") if app.strip()]
    return "Running applications:\n" + "\n".join(apps)


def run_applescript(app_name: str, script: str) -> str:
    """Executes AppleScript command"""
    apple_script = f'tell application "{app_name}"\n{script}\nend tell'
    # Escape single quotes
    apple_script_escaped = apple_script.replace("'", "'\\''")
    stdout, stderr = exec_command(f"osascript -e '{apple_script_escaped}'")
    return stdout or stderr or "Command executed successfully"


def quit_application(app_name: str) -> str:
    """Closes application"""
    apple_script = f'tell application "{app_name}"\nquit\nend tell'
    apple_script_escaped = apple_script.replace("'", "'\\''")
    stdout, stderr = exec_command(f"osascript -e '{apple_script_escaped}'")
    if stderr:
        raise Exception(f'Failed to close application "{app_name}": {stderr}')
    return f'Application "{app_name}" closed'


def open_file_with_app(path: str, app_name: str) -> str:
    """Opens file in specified application"""
    stdout, stderr = exec_command(f'open -a "{app_name}" "{path}"')
    if stderr:
        raise Exception(f"Failed to open file: {stderr}")
    return f'File "{path}" opened in application "{app_name}"'


# Implementation of tools for working with Ollama
def ollama_generate(prompt: str, model: str = "llama3.2") -> str:
    """Generates response via Ollama API"""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response from model")
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Failed to connect to Ollama server ({OLLAMA_API_URL}). "
            "Make sure Ollama is running: ollama serve"
        )
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")


def ollama_list_models() -> str:
    """Gets list of Ollama models"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])

        if not models:
            return "No available models. Load a model: ollama pull llama3.2"

        model_list = "\n".join(
            [
                f"- {model['name']} ({(model.get('size', 0) / 1024 / 1024 / 1024):.2f} GB)"
                for model in models
            ]
        )
        return f"Available Ollama models:\n{model_list}"
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Failed to connect to Ollama server ({OLLAMA_API_URL}). "
            "Make sure Ollama is running: ollama serve"
        )
    except Exception as e:
        raise Exception(f"Error getting list of models: {str(e)}")


# Implementation of tools for working with MongoDB
def mongodb_create_database(database_name: str) -> str:
    """Creates database in MongoDB"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        # Create temporary collection so database is actually created
        db.create_collection("_temp")
        db["_temp"].drop()
        return f'Database "{database_name}" successfully created'
    except Exception as e:
        raise Exception(f"Error creating database: {str(e)}")
    finally:
        client.close()


def mongodb_list_databases() -> str:
    """Gets list of databases"""
    client = MongoClient(MONGODB_URI)
    try:
        admin_db = client.admin
        databases = admin_db.command("listDatabases")
        db_names = [
            db["name"]
            for db in databases["databases"]
            if db["name"] not in ["admin", "config", "local"]
        ]
        result = "Databases:\n" + (
            "\n".join(db_names) if db_names else "No databases found"
        )
        return result
    except Exception as e:
        raise Exception(f"Error getting list of databases: {str(e)}")
    finally:
        client.close()


def mongodb_create_collection(database_name: str, collection_name: str) -> str:
    """Creates collection in database"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        db.create_collection(collection_name)
        return (
            f'Collection "{collection_name}" successfully created '
            f'in database "{database_name}"'
        )
    except Exception as e:
        raise Exception(f"Error creating collection: {str(e)}")
    finally:
        client.close()


def mongodb_list_collections(database_name: str) -> str:
    """Gets list of collections"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collections = list(db.list_collection_names())
        result = f'Collections in database "{database_name}":\n' + (
            "\n".join(collections) if collections else "No collections found"
        )
        return result
    except Exception as e:
        raise Exception(f"Error getting list of collections: {str(e)}")
    finally:
        client.close()


def mongodb_delete_collection(database_name: str, collection_name: str) -> str:
    """Deletes collection"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        db[collection_name].drop()
        return (
            f'Collection "{collection_name}" successfully deleted '
            f'from database "{database_name}"'
        )
    except Exception as e:
        raise Exception(f"Error deleting collection: {str(e)}")
    finally:
        client.close()


def mongodb_insert_document(
    database_name: str, collection_name: str, document_json: str
) -> str:
    """Inserts document into collection"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collection = db[collection_name]
        document = json.loads(document_json)
        result = collection.insert_one(document)
        return f'Document successfully inserted into collection "{collection_name}". ID: {result.inserted_id}'
    except Exception as e:
        raise Exception(f"Error inserting document: {str(e)}")
    finally:
        client.close()


def mongodb_find_documents(
    database_name: str,
    collection_name: str,
    filter_json: Optional[str] = None,
    limit: int = 100,
) -> str:
    """Finds documents in collection"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collection = db[collection_name]
        filter_dict = json.loads(filter_json) if filter_json else {}
        documents = list(collection.find(filter_dict).limit(limit))
        # Convert ObjectId to strings
        for doc in documents:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        documents_str = json.dumps(documents, ensure_ascii=False, indent=2)
        return f"Found documents: {len(documents)}\n\n{documents_str}"
    except Exception as e:
        raise Exception(f"Error finding documents: {str(e)}")
    finally:
        client.close()


def mongodb_delete_document(
    database_name: str, collection_name: str, filter_json: str
) -> str:
    """Deletes document(s) by filter"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collection = db[collection_name]
        filter_dict = json.loads(filter_json)
        result = collection.delete_many(filter_dict)
        return f"Deleted documents: {result.deleted_count}"
    except Exception as e:
        raise Exception(f"Error deleting document: {str(e)}")
    finally:
        client.close()


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handles MCP JSON-RPC request"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                    },
                    "serverInfo": {
                        "name": "mac-apps-mcp-server",
                        "version": "1.0.0",
                    },
                },
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": get_tools(),
                },
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            # Call corresponding tool
            if tool_name == "open_application":
                result_text = open_application(arguments.get("appName"))
            elif tool_name == "get_running_applications":
                result_text = get_running_applications()
            elif tool_name == "run_applescript":
                result_text = run_applescript(
                    arguments.get("appName"), arguments.get("script")
                )
            elif tool_name == "quit_application":
                result_text = quit_application(arguments.get("appName"))
            elif tool_name == "open_file_with_app":
                result_text = open_file_with_app(
                    arguments.get("path"), arguments.get("appName")
                )
            elif tool_name == "search_google_in_safari":
                result_text = search_google_in_safari(arguments.get("query"))
            elif tool_name == "ollama_generate":
                result_text = ollama_generate(
                    arguments.get("prompt"), arguments.get("model", "llama3.2")
                )
            elif tool_name == "ollama_list_models":
                result_text = ollama_list_models()
            # elif tool_name == "mongodb_create_database":
            #     result_text = mongodb_create_database(arguments.get("databaseName"))
            # elif tool_name == "mongodb_list_databases":
            #     result_text = mongodb_list_databases()
            # elif tool_name == "mongodb_create_collection":
            #     result_text = mongodb_create_collection(
            #         arguments.get("databaseName"), arguments.get("collectionName")
            #     )
            # elif tool_name == "mongodb_list_collections":
            #     result_text = mongodb_list_collections(arguments.get("databaseName"))
            # elif tool_name == "mongodb_delete_collection":
            #     result_text = mongodb_delete_collection(
            #         arguments.get("databaseName"), arguments.get("collectionName")
            #     )
            # elif tool_name == "mongodb_insert_document":
            #     result_text = mongodb_insert_document(
            #         arguments.get("databaseName"),
            #         arguments.get("collectionName"),
            #         arguments.get("document"),
            #     )
            # elif tool_name == "mongodb_find_documents":
            #     result_text = mongodb_find_documents(
            #         arguments.get("databaseName"),
            #         arguments.get("collectionName"),
            #         arguments.get("filter"),
            #         arguments.get("limit", 100),
            #     )
            # elif tool_name == "mongodb_delete_document":
            #     result_text = mongodb_delete_document(
            #         arguments.get("databaseName"),
            #         arguments.get("collectionName"),
            #         arguments.get("filter"),
            #     )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {"type": "text", "text": result_text}
                    ],
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

    except Exception as e:
        error_msg = str(e)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {"type": "text", "text": f"Error: {error_msg}", "isError": True}
                ],
            },
        }


def main():
    """Main function - processes JSON-RPC requests via stdio"""
    print("MCP Mac Apps Server (Python) started", file=sys.stderr)

    # Читаем запросы из stdin и отправляем ответы в stdout
    for line in sys.stdin:
        if not line.strip():
            continue

        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}",
                },
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
