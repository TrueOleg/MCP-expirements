#!/usr/bin/env python3
"""
MCP сервер для управления приложениями Mac
Переписанная версия на Python
Использует JSON-RPC протокол через stdio
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import requests
from pymongo import MongoClient


# Константы
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")


def exec_command(command: str) -> tuple[str, str]:
    """Выполняет shell команду и возвращает stdout и stderr"""
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
        return "", "Тайм-аут выполнения команды"
    except Exception as e:
        return "", str(e)


def get_tools() -> List[Dict[str, Any]]:
    """Возвращает список всех доступных инструментов"""
    return [
        {
            "name": "open_application",
            "description": "Открывает приложение на Mac по имени. Примеры: 'Safari', 'Finder', 'TextEdit', 'Calculator'",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "appName": {
                        "type": "string",
                        "description": "Имя приложения для запуска (например, 'Safari', 'Calculator')",
                    },
                },
                "required": ["appName"],
            },
        },
        {
            "name": "get_running_applications",
            "description": "Получает список всех запущенных приложений на Mac",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "run_applescript",
            "description": "Выполняет AppleScript команду в указанном приложении. Полезно для автоматизации действий в приложениях",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "appName": {
                        "type": "string",
                        "description": "Имя приложения (например, 'Safari', 'Finder')",
                    },
                    "script": {
                        "type": "string",
                        "description": "AppleScript команда для выполнения",
                    },
                },
                "required": ["appName", "script"],
            },
        },
        {
            "name": "quit_application",
            "description": "Закрывает указанное приложение",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "appName": {
                        "type": "string",
                        "description": "Имя приложения для закрытия",
                    },
                },
                "required": ["appName"],
            },
        },
        {
            "name": "open_file_with_app",
            "description": "Открывает файл или URL в указанном приложении",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Путь к файлу или URL",
                    },
                    "appName": {
                        "type": "string",
                        "description": "Имя приложения для открытия файла",
                    },
                },
                "required": ["path", "appName"],
            },
        },
        {
            "name": "ollama_generate",
            "description": "Генерирует ответ используя локальную модель Ollama. Используйте для задач, требующих AI обработки текста",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Название модели Ollama (например, 'llama3.2', 'deepseek-r1:8b'). По умолчанию 'llama3.2'",
                        "default": "llama3.2",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Запрос для модели",
                    },
                },
                "required": ["prompt"],
            },
        },
        {
            "name": "ollama_list_models",
            "description": "Получает список доступных моделей Ollama",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "mongodb_create_database",
            "description": "Создает новую базу данных в MongoDB",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                },
                "required": ["databaseName"],
            },
        },
        {
            "name": "mongodb_list_databases",
            "description": "Получает список всех баз данных в MongoDB",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "mongodb_create_collection",
            "description": "Создает новую коллекцию в указанной базе данных",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Имя коллекции",
                    },
                },
                "required": ["databaseName", "collectionName"],
            },
        },
        {
            "name": "mongodb_list_collections",
            "description": "Получает список коллекций в указанной базе данных",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                },
                "required": ["databaseName"],
            },
        },
        {
            "name": "mongodb_delete_collection",
            "description": "Удаляет коллекцию из базы данных",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Имя коллекции для удаления",
                    },
                },
                "required": ["databaseName", "collectionName"],
            },
        },
        {
            "name": "mongodb_insert_document",
            "description": "Вставляет документ в коллекцию",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Имя коллекции",
                    },
                    "document": {
                        "type": "string",
                        "description": "JSON строка с документом для вставки",
                    },
                },
                "required": ["databaseName", "collectionName", "document"],
            },
        },
        {
            "name": "mongodb_find_documents",
            "description": "Находит документы в коллекции",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Имя коллекции",
                    },
                    "filter": {
                        "type": "string",
                        "description": "JSON строка с фильтром для поиска (необязательно)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Максимальное количество документов (по умолчанию 100)",
                    },
                },
                "required": ["databaseName", "collectionName"],
            },
        },
        {
            "name": "mongodb_delete_document",
            "description": "Удаляет документ(ы) из коллекции по фильтру",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "databaseName": {
                        "type": "string",
                        "description": "Имя базы данных",
                    },
                    "collectionName": {
                        "type": "string",
                        "description": "Имя коллекции",
                    },
                    "filter": {
                        "type": "string",
                        "description": "JSON строка с фильтром для удаления",
                    },
                },
                "required": ["databaseName", "collectionName", "filter"],
            },
        },
    ]


# Реализация инструментов для работы с приложениями Mac
def open_application(app_name: str) -> str:
    """Открывает приложение по имени"""
    stdout, stderr = exec_command(f'open -a "{app_name}"')
    if stderr:
        raise Exception(f'Не удалось запустить приложение "{app_name}": {stderr}')
    return f'Приложение "{app_name}" успешно запущено'


def get_running_applications() -> str:
    """Получает список запущенных приложений"""
    apple_script = 'tell application "System Events" to get name of every application process whose background only is false'
    stdout, stderr = exec_command(f'osascript -e \'{apple_script}\'')
    if stderr:
        raise Exception(f"Не удалось получить список приложений: {stderr}")

    apps = [app.strip() for app in stdout.strip().split(", ") if app.strip()]
    return "Запущенные приложения:\n" + "\n".join(apps)


def run_applescript(app_name: str, script: str) -> str:
    """Выполняет AppleScript команду"""
    apple_script = f'tell application "{app_name}"\n{script}\nend tell'
    # Экранируем одинарные кавычки
    apple_script_escaped = apple_script.replace("'", "'\\''")
    stdout, stderr = exec_command(f"osascript -e '{apple_script_escaped}'")
    return stdout or stderr or "Команда выполнена успешно"


def quit_application(app_name: str) -> str:
    """Закрывает приложение"""
    apple_script = f'tell application "{app_name}"\nquit\nend tell'
    apple_script_escaped = apple_script.replace("'", "'\\''")
    stdout, stderr = exec_command(f"osascript -e '{apple_script_escaped}'")
    if stderr:
        raise Exception(f'Не удалось закрыть приложение "{app_name}": {stderr}')
    return f'Приложение "{app_name}" закрыто'


def open_file_with_app(path: str, app_name: str) -> str:
    """Открывает файл в указанном приложении"""
    stdout, stderr = exec_command(f'open -a "{app_name}" "{path}"')
    if stderr:
        raise Exception(f"Не удалось открыть файл: {stderr}")
    return f'Файл "{path}" открыт в приложении "{app_name}"'


# Реализация инструментов для работы с Ollama
def ollama_generate(prompt: str, model: str = "llama3.2") -> str:
    """Генерирует ответ через Ollama API"""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Нет ответа от модели")
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Не удалось подключиться к Ollama серверу ({OLLAMA_API_URL}). "
            "Убедитесь, что Ollama запущен: ollama serve"
        )
    except Exception as e:
        raise Exception(f"Ошибка Ollama: {str(e)}")


def ollama_list_models() -> str:
    """Получает список моделей Ollama"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])

        if not models:
            return "Нет доступных моделей. Загрузите модель: ollama pull llama3.2"

        model_list = "\n".join(
            [
                f"- {model['name']} ({(model.get('size', 0) / 1024 / 1024 / 1024):.2f} GB)"
                for model in models
            ]
        )
        return f"Доступные модели Ollama:\n{model_list}"
    except requests.exceptions.ConnectionError:
        raise Exception(
            f"Не удалось подключиться к Ollama серверу ({OLLAMA_API_URL}). "
            "Убедитесь, что Ollama запущен: ollama serve"
        )
    except Exception as e:
        raise Exception(f"Ошибка получения списка моделей: {str(e)}")


# Реализация инструментов для работы с MongoDB
def mongodb_create_database(database_name: str) -> str:
    """Создает базу данных в MongoDB"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        # Создаем временную коллекцию, чтобы база данных реально создалась
        db.create_collection("_temp")
        db["_temp"].drop()
        return f'База данных "{database_name}" успешно создана'
    except Exception as e:
        raise Exception(f"Ошибка создания базы данных: {str(e)}")
    finally:
        client.close()


def mongodb_list_databases() -> str:
    """Получает список баз данных"""
    client = MongoClient(MONGODB_URI)
    try:
        admin_db = client.admin
        databases = admin_db.command("listDatabases")
        db_names = [
            db["name"]
            for db in databases["databases"]
            if db["name"] not in ["admin", "config", "local"]
        ]
        result = "Базы данных:\n" + (
            "\n".join(db_names) if db_names else "Базы данных не найдены"
        )
        return result
    except Exception as e:
        raise Exception(f"Ошибка получения списка баз данных: {str(e)}")
    finally:
        client.close()


def mongodb_create_collection(database_name: str, collection_name: str) -> str:
    """Создает коллекцию в базе данных"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        db.create_collection(collection_name)
        return (
            f'Коллекция "{collection_name}" успешно создана '
            f'в базе данных "{database_name}"'
        )
    except Exception as e:
        raise Exception(f"Ошибка создания коллекции: {str(e)}")
    finally:
        client.close()


def mongodb_list_collections(database_name: str) -> str:
    """Получает список коллекций"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collections = list(db.list_collection_names())
        result = f'Коллекции в базе данных "{database_name}":\n' + (
            "\n".join(collections) if collections else "Коллекции не найдены"
        )
        return result
    except Exception as e:
        raise Exception(f"Ошибка получения списка коллекций: {str(e)}")
    finally:
        client.close()


def mongodb_delete_collection(database_name: str, collection_name: str) -> str:
    """Удаляет коллекцию"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        db[collection_name].drop()
        return (
            f'Коллекция "{collection_name}" успешно удалена '
            f'из базы данных "{database_name}"'
        )
    except Exception as e:
        raise Exception(f"Ошибка удаления коллекции: {str(e)}")
    finally:
        client.close()


def mongodb_insert_document(
    database_name: str, collection_name: str, document_json: str
) -> str:
    """Вставляет документ в коллекцию"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collection = db[collection_name]
        document = json.loads(document_json)
        result = collection.insert_one(document)
        return f'Документ успешно вставлен в коллекцию "{collection_name}". ID: {result.inserted_id}'
    except Exception as e:
        raise Exception(f"Ошибка вставки документа: {str(e)}")
    finally:
        client.close()


def mongodb_find_documents(
    database_name: str,
    collection_name: str,
    filter_json: Optional[str] = None,
    limit: int = 100,
) -> str:
    """Находит документы в коллекции"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collection = db[collection_name]
        filter_dict = json.loads(filter_json) if filter_json else {}
        documents = list(collection.find(filter_dict).limit(limit))
        # Преобразуем ObjectId в строки
        for doc in documents:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        documents_str = json.dumps(documents, ensure_ascii=False, indent=2)
        return f"Найдено документов: {len(documents)}\n\n{documents_str}"
    except Exception as e:
        raise Exception(f"Ошибка поиска документов: {str(e)}")
    finally:
        client.close()


def mongodb_delete_document(
    database_name: str, collection_name: str, filter_json: str
) -> str:
    """Удаляет документ(ы) по фильтру"""
    client = MongoClient(MONGODB_URI)
    try:
        db = client[database_name]
        collection = db[collection_name]
        filter_dict = json.loads(filter_json)
        result = collection.delete_many(filter_dict)
        return f"Удалено документов: {result.deleted_count}"
    except Exception as e:
        raise Exception(f"Ошибка удаления документа: {str(e)}")
    finally:
        client.close()


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Обрабатывает MCP JSON-RPC запрос"""
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

            # Вызываем соответствующий инструмент
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
            elif tool_name == "ollama_generate":
                result_text = ollama_generate(
                    arguments.get("prompt"), arguments.get("model", "llama3.2")
                )
            elif tool_name == "ollama_list_models":
                result_text = ollama_list_models()
            elif tool_name == "mongodb_create_database":
                result_text = mongodb_create_database(arguments.get("databaseName"))
            elif tool_name == "mongodb_list_databases":
                result_text = mongodb_list_databases()
            elif tool_name == "mongodb_create_collection":
                result_text = mongodb_create_collection(
                    arguments.get("databaseName"), arguments.get("collectionName")
                )
            elif tool_name == "mongodb_list_collections":
                result_text = mongodb_list_collections(arguments.get("databaseName"))
            elif tool_name == "mongodb_delete_collection":
                result_text = mongodb_delete_collection(
                    arguments.get("databaseName"), arguments.get("collectionName")
                )
            elif tool_name == "mongodb_insert_document":
                result_text = mongodb_insert_document(
                    arguments.get("databaseName"),
                    arguments.get("collectionName"),
                    arguments.get("document"),
                )
            elif tool_name == "mongodb_find_documents":
                result_text = mongodb_find_documents(
                    arguments.get("databaseName"),
                    arguments.get("collectionName"),
                    arguments.get("filter"),
                    arguments.get("limit", 100),
                )
            elif tool_name == "mongodb_delete_document":
                result_text = mongodb_delete_document(
                    arguments.get("databaseName"),
                    arguments.get("collectionName"),
                    arguments.get("filter"),
                )
            else:
                raise ValueError(f"Неизвестный инструмент: {tool_name}")

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
                    {"type": "text", "text": f"Ошибка: {error_msg}", "isError": True}
                ],
            },
        }


def main():
    """Главная функция - обрабатывает JSON-RPC запросы через stdio"""
    print("MCP Mac Apps Server (Python) запущен", file=sys.stderr)

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
