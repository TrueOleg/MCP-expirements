"""
Тест работы Ollama API

Этот скрипт проверяет, что Ollama работает и отвечает на запросы.
Однако для управления приложениями Mac через MCP нужно использовать
MCP-совместимый клиент (например, Claude Desktop).

Для реального использования MCP сервера:
1. Настройте Claude Desktop с MCP серверами (см. README.md)
2. Или используйте mcp_client.py - простой клиент, который объединяет Ollama и MCP инструменты
"""

import requests
import json

print("🧪 Тестирование Ollama API...")
print("-" * 50)

try:
    # Проверка доступности Ollama
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ Ollama сервер работает")
        print(f"📦 Доступные модели: {', '.join([m['name'] for m in models])}")
    else:
        print(f"❌ Ollama сервер недоступен (код: {response.status_code})")
        exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Не удалось подключиться к Ollama серверу")
    print("💡 Запустите Ollama: ollama serve")
    exit(1)

print("\n🤖 Тестовый запрос к модели llama3.2...")
print("-" * 50)

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'llama3.2',
        'prompt': 'Запусти приложение Calculator.',
        'stream': False
    },
    timeout=30
)

if response.status_code == 200:
    result = response.json()
    print(result.get('response', 'Нет ответа'))
    print("\n" + "-" * 50)
    print("✅ Тест успешен! Ollama работает корректно.")
    print("\n💡 Важно:")
    print("   Этот тест проверяет только работу Ollama.")
    print("   Для управления приложениями Mac нужен MCP клиент")
    print("   (например, Claude Desktop с настроенным MCP сервером).")
    print("   См. README.md для инструкций по настройке.")
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(response.text)