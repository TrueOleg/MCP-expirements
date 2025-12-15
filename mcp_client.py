#!/usr/bin/env python3
"""
Простой MCP клиент, который использует Ollama для понимания запросов
и вызывает MCP инструменты для управления приложениями Mac
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
    """Вызывает MCP инструмент через JSON-RPC"""
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
        # Запускаем MCP сервер и отправляем запрос
        process = subprocess.Popen(
            ["python3", MCP_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Отправляем запрос
        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        # Парсим ответ
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if "result" in response:
                        content = response["result"].get("content", [])
                        if content:
                            return content[0].get("text", "")
                    if "error" in response:
                        return f"Ошибка: {response['error'].get('message', 'Неизвестная ошибка')}"
                except json.JSONDecodeError:
                    continue
        
        return "Нет ответа от MCP сервера"
        
    except subprocess.TimeoutExpired:
        process.kill()
        return "Тайм-аут при вызове MCP инструмента"
    except Exception as e:
        return f"Ошибка вызова MCP инструмента: {str(e)}"


def list_mcp_tools():
    """Получает список доступных MCP инструментов"""
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
        print(f"Ошибка получения списка инструментов: {e}", file=sys.stderr)
        return []


def ask_ollama_with_tools(user_query):
    """Использует Ollama для понимания запроса и вызова соответствующих MCP инструментов"""
    
    # Получаем список доступных инструментов
    tools = list_mcp_tools()
    tools_description = "\n".join([
        f"- {tool['name']}: {tool['description']}"
        for tool in tools
    ])
    
    # Создаем системный промпт с описанием инструментов
    system_prompt = f"""Ты помощник, который может управлять приложениями на Mac через MCP инструменты.

Доступные инструменты:
{tools_description}

Когда пользователь просит открыть приложение, выполнить действие или получить информацию, определи какой инструмент нужно использовать и верни JSON в формате:
{{
    "tool": "имя_инструмента",
    "arguments": {{"параметр": "значение"}}
}}

Если запрос не требует использования инструментов, просто ответь обычным текстом.

Примеры:
- "Открой Calculator" -> {{"tool": "open_application", "arguments": {{"appName": "Calculator"}}}}
- "Какие приложения запущены?" -> {{"tool": "get_running_applications", "arguments": {{}}}}
- "Закрой Safari" -> {{"tool": "quit_application", "arguments": {{"appName": "Safari"}}}}
- "Открой MongoDB Compass" -> {{"tool": "open_application", "arguments": {{"appName": "MongoDB Compass"}}}}
- "Создай базу данных test" -> {{"tool": "mongodb_create_database", "arguments": {{"databaseName": "test"}}}}
- "Создай коллекцию users в базе test" -> {{"tool": "mongodb_create_collection", "arguments": {{"databaseName": "test", "collectionName": "users"}}}}

Отвечай только JSON или обычным текстом, без дополнительных объяснений."""

    # Запрашиваем у Ollama
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"{system_prompt}\n\nПользователь: {user_query}\nПомощник:",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"Ошибка Ollama: {response.status_code}"
        
        result = response.json()
        answer = result.get("response", "").strip()
        
        # Пытаемся распарсить JSON ответ
        try:
            # Ищем JSON в ответе (может быть на нескольких строках)
            import re
            # Более точный поиск JSON объекта
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, answer, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    tool_call = json.loads(json_str)
                    
                    if "tool" in tool_call:
                        tool_name = tool_call["tool"]
                        tool_args = tool_call.get("arguments", {})
                        
                        print(f"🔧 Вызываю инструмент: {tool_name}")
                        print(f"📝 Аргументы: {tool_args}")
                        
                        # Вызываем MCP инструмент
                        result = call_mcp_tool(tool_name, tool_args)
                        return result
                except json.JSONDecodeError:
                    continue
            
            # Если не нашли JSON, пытаемся распарсить весь ответ как JSON
            tool_call = json.loads(answer)
            if "tool" in tool_call:
                tool_name = tool_call["tool"]
                tool_args = tool_call.get("arguments", {})
                
                print(f"🔧 Вызываю инструмент: {tool_name}")
                print(f"📝 Аргументы: {tool_args}")
                
                result = call_mcp_tool(tool_name, tool_args)
                return result
                    
        except (json.JSONDecodeError, KeyError):
            # Если не JSON, возвращаем обычный ответ
            pass
        
        return answer
        
    except requests.exceptions.ConnectionError:
        return "❌ Не удалось подключиться к Ollama. Запустите: ollama serve"
    except Exception as e:
        return f"Ошибка: {str(e)}"


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Введите запрос: ")
    
    print(f"\n💬 Запрос: {query}")
    print("-" * 50)
    
    result = ask_ollama_with_tools(query)
    
    print("\n📋 Результат:")
    print(result)
    print()


if __name__ == "__main__":
    main()

