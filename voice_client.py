#!/usr/bin/env python3
"""
Голосовой клиент для управления приложениями Mac через MCP
Использует Ollama для понимания команд и MCP инструменты для управления
"""

import requests
import json
import subprocess
import sys
import os
import time

MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "src", "server.py")
OLLAMA_API_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️  speech_recognition не установлен. Установите: pip install SpeechRecognition")
    print("   Для голосового ввода также нужен pyaudio: pip install pyaudio")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️  pyttsx3 не установлен. Установите: pip install pyttsx3")
    print("   Или используйте macOS встроенный say (уже доступен)")


def speak(text, use_system=True):
    """Преобразует текст в речь"""
    if use_system:
        # Используем встроенную macOS команду say
        subprocess.run(["say", text], check=False)
    elif TTS_AVAILABLE:
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Ошибка TTS: {e}")
            subprocess.run(["say", text], check=False)
    else:
        subprocess.run(["say", text], check=False)


def listen(use_microphone=True):
    """Слушает голосовой ввод и преобразует в текст"""
    if not use_microphone or not SPEECH_RECOGNITION_AVAILABLE:
        # Альтернатива: используем системную команду macOS (требует разрешения)
        print("🎤 Говорите... (нажмите Enter когда закончите)")
        # Для macOS можно использовать встроенное распознавание речи
        # Но проще использовать библиотеку speech_recognition
        return input("Вы: ")
    
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Слушаю... (говорите после сигнала)")
        # Адаптация к окружающему шуму
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("✓ Готово, говорите!")
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("🔄 Распознаю речь...")
            
            # Используем Google Speech Recognition (требует интернет)
            # Для офлайн можно использовать Whisper или другие
            text = r.recognize_google(audio, language="ru-RU")
            print(f"📝 Распознано: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏱️  Тайм-аут. Не услышал команду.")
            return None
        except sr.UnknownValueError:
            print("❌ Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            print(f"❌ Ошибка сервиса распознавания речи: {e}")
            print("💡 Используйте текстовый ввод или установите офлайн распознавание")
            return None


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
        print(f"Ошибка получения списка инструментов: {e}", file=sys.stderr)
        return []


def ask_ollama_with_tools(user_query, verbose=False):
    """Использует Ollama для понимания запроса и вызова соответствующих MCP инструментов"""
    
    tools = list_mcp_tools()
    tools_description = "\n".join([
        f"- {tool['name']}: {tool['description']}"
        for tool in tools
    ])
    
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
- "Закрой Safari" -> {{"tool": "quit_application", "arguments": {{"appName": "Safari"}}}}
- "Какие приложения запущены?" -> {{"tool": "get_running_applications", "arguments": {{}}}}
- "Открой MongoDB Compass" -> {{"tool": "open_application", "arguments": {{"appName": "MongoDB Compass"}}}}
- "Создай базу данных test" -> {{"tool": "mongodb_create_database", "arguments": {{"databaseName": "test"}}}}
- "Создай коллекцию users в базе test" -> {{"tool": "mongodb_create_collection", "arguments": {{"databaseName": "test", "collectionName": "users"}}}}
- "Добавь документ {{\"name\": \"John\"}} в коллекцию users базы test" -> {{"tool": "mongodb_insert_document", "arguments": {{"databaseName": "test", "collectionName": "users", "document": "{{\\\"name\\\": \\\"John\\\"}}"}}}}

Отвечай только JSON или обычным текстом, без дополнительных объяснений."""

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
            return f"Ошибка Ollama: {response.status_code}", False
        
        result = response.json()
        answer = result.get("response", "").strip()
        
        if verbose:
            print(f"🤖 Ответ Ollama: {answer}")
        
        # Пытаемся распарсить JSON
        try:
            import re
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_matches = re.findall(json_pattern, answer, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    tool_call = json.loads(json_str)
                    
                    if "tool" in tool_call:
                        tool_name = tool_call["tool"]
                        tool_args = tool_call.get("arguments", {})
                        
                        if verbose:
                            print(f"🔧 Вызываю инструмент: {tool_name}")
                            print(f"📝 Аргументы: {tool_args}")
                        
                        result = call_mcp_tool(tool_name, tool_args)
                        return result, True
                except json.JSONDecodeError:
                    continue
            
            # Пытаемся распарсить весь ответ как JSON
            tool_call = json.loads(answer)
            if "tool" in tool_call:
                tool_name = tool_call["tool"]
                tool_args = tool_call.get("arguments", {})
                
                if verbose:
                    print(f"🔧 Вызываю инструмент: {tool_name}")
                
                result = call_mcp_tool(tool_name, tool_args)
                return result, True
                    
        except (json.JSONDecodeError, KeyError):
            pass
        
        return answer, False
        
    except requests.exceptions.ConnectionError:
        return "❌ Не удалось подключиться к Ollama. Запустите: ollama serve", False
    except Exception as e:
        return f"Ошибка: {str(e)}", False


def main():
    print("🎤 Голосовой помощник для управления приложениями Mac")
    print("=" * 60)
    print(f"📦 Модель: {OLLAMA_MODEL}")
    print(f"🌐 Ollama: {OLLAMA_API_URL}")
    print("=" * 60)
    print()
    
    # Проверка доступности
    if not SPEECH_RECOGNITION_AVAILABLE:
        print("💡 Для голосового ввода установите:")
        print("   pip install SpeechRecognition pyaudio")
        print()
        print("📝 Сейчас будет использован текстовый ввод")
        print()
        use_voice_input = False
    else:
        use_voice_input = True
        print("✅ Голосовой ввод доступен")
        print("✅ Голосовой вывод доступен (через macOS say)")
        print()
    
    while True:
        try:
            # Голосовой или текстовый ввод
            if use_voice_input:
                query = listen()
                if query is None:
                    continue
            else:
                query = input("Вы (или 'выход' для завершения): ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['выход', 'exit', 'quit', 'стоп']:
                speak("До свидания!")
                print("👋 До свидания!")
                break
            
            print(f"\n💬 Запрос: {query}")
            print("-" * 60)
            
            # Обработка запроса
            result, is_action = ask_ollama_with_tools(query, verbose=True)
            
            print(f"\n📋 Результат: {result}")
            
            # Голосовой вывод результата
            if is_action:
                # Для действий говорим краткий ответ
                speak(result.split('\n')[0] if '\n' in result else result)
            else:
                # Для обычных ответов говорим весь текст (если короткий)
                if len(result) < 200:
                    speak(result)
                else:
                    speak("Результат показан на экране")
            
            print()
            time.sleep(0.5)  # Небольшая пауза между командами
            
        except KeyboardInterrupt:
            print("\n\n👋 Прервано пользователем")
            speak("До свидания!")
            break
        except Exception as e:
            error_msg = f"Ошибка: {str(e)}"
            print(f"\n❌ {error_msg}")
            speak("Произошла ошибка")
            time.sleep(1)


if __name__ == "__main__":
    main()

