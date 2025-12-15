# Настройка Ollama с MCP Mac Apps Server

## ✅ Текущий статус

- ✅ Ollama установлен
- ✅ Сервер Ollama запущен
- ✅ Модель `llama3.2` загружена (2.0 GB)
- ✅ Модель `deepseek-r1:8b` доступна (5.2 GB)

## 🚀 Быстрый старт

### Вариант 1: Использование через Claude Desktop

1. **Установите Claude Desktop** (если еще не установлен):
   - Скачайте с https://claude.ai/download

2. **Установите MCP сервер для Ollama**:
   ```bash
   npx -y @modelcontextprotocol/create-server ollama-mcp
   ```
   
   Или добавьте в конфигурацию Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):
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

3. **Перезапустите Claude Desktop**

4. **Теперь Claude сможет**:
   - Использовать локальные модели через Ollama
   - Управлять приложениями на Mac через ваш MCP сервер

### Вариант 2: Использование через API напрямую

Ollama предоставляет REST API на `http://localhost:11434`. Вы можете использовать его напрямую с любым клиентом, поддерживающим OpenAI-совместимый API.

**Тестирование API:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Привет! Как дела?",
  "stream": false
}'
```

## 📝 Доступные модели

Проверить список моделей:
```bash
ollama list
```

Загрузить другие модели:
```bash
# Популярные модели
ollama pull llama3.1:8b       # Более мощная версия
ollama pull mistral:7b        # Mistral AI
ollama pull qwen2.5:7b        # Alibaba Qwen
ollama pull codellama:7b      # Для программирования
ollama pull phi3              # Легкая модель Microsoft
```

## 🔧 Управление Ollama

**Запуск сервера:**
```bash
ollama serve
```

**Остановка сервера:**
```bash
# Нажмите Ctrl+C или найдите процесс и завершите его
ps aux | grep ollama
kill <PID>
```

**Автозапуск (macOS):**
Ollama обычно запускается автоматически через LaunchAgent. Если нужно добавить в автозагрузку:
```bash
# Создать LaunchAgent
cat > ~/Library/LaunchAgents/com.ollama.server.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Загрузить агент
launchctl load ~/Library/LaunchAgents/com.ollama.server.plist
```

## 🎯 Примеры использования

### Тест модели напрямую:
```bash
ollama run llama3.2 "Расскажи про MCP протокол"
```

### Использование через API с curl:
```bash
# Простой запрос
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Что такое Model Context Protocol?",
  "stream": false
}'

# С стримингом
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Привет!",
  "stream": true
}'
```

### Использование с Python:
```python
import requests
import json

response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'llama3.2',
        'prompt': 'Открой Safari',
        'stream': False
    }
)

print(response.json()['response'])
```

## 🔍 Проверка работы

Проверить, что сервер работает:
```bash
curl http://localhost:11434/api/tags
```

Должен вернуть список моделей в формате JSON.

## 💡 Советы

1. **Производительность**: Модель `llama3.2` (2GB) работает быстро, но менее мощная. Для лучшего качества используйте `llama3.1:8b` или `deepseek-r1:8b`.

2. **Память**: Убедитесь, что у вас достаточно RAM. Модели требуют:
   - `llama3.2`: ~2-4 GB RAM
   - `llama3.1:8b`: ~8-10 GB RAM
   - `deepseek-r1:8b`: ~10-12 GB RAM

3. **Скорость**: На Mac с Apple Silicon (M1/M2/M3) модели работают значительно быстрее благодаря нейропроцессору.

4. **Приватность**: Все обработка происходит локально, данные никуда не отправляются.

## 📚 Полезные ссылки

- [Ollama документация](https://ollama.ai/docs)
- [Доступные модели](https://ollama.ai/library)
- [Ollama GitHub](https://github.com/ollama/ollama)

