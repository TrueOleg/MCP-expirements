# Использование DeepSeek с MCP Mac Apps Server

Есть несколько способов использовать DeepSeek с вашим MCP сервером для управления приложениями Mac:

## Способ 1: DeepSeek Desktop App (рекомендуется)

Если у DeepSeek есть официальное desktop-приложение с поддержкой MCP:

1. **Установите DeepSeek Desktop App** из App Store или с официального сайта

2. **Найдите файл конфигурации MCP**. Обычно он находится в:
   - `~/Library/Application Support/DeepSeek/mcp.json` или
   - `~/.deepseek/mcp.json` или
   - В настройках приложения DeepSeek

3. **Добавьте конфигурацию MCP сервера**:

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

4. **Перезапустите DeepSeek** для применения изменений

## Способ 2: Через Claude Desktop с DeepSeek API

Если DeepSeek поддерживает API, совместимый с OpenAI, можно использовать Claude Desktop:

1. **Установите Claude Desktop** (если еще не установлен)

2. **Найдите файл конфигурации Claude Desktop**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

3. **Добавьте конфигурацию**:

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

4. **Настройте использование DeepSeek API** в Claude Desktop (если поддерживается)

## Способ 3: Использование универсального MCP клиента

Можно использовать любой MCP-совместимый клиент с DeepSeek:

### Вариант 3.1: MCP Inspector / Playground

Если есть инструменты для тестирования MCP серверов, можно использовать их для проверки работы сервера.

### Вариант 3.2: Создание собственного клиента

Можно создать простой клиент на Node.js/TypeScript, который будет использовать DeepSeek API и наш MCP сервер.

## Проверка работы сервера

Перед подключением к DeepSeek убедитесь, что сервер работает:

```bash
cd /Users/olegzaichkin/Documents/MCP
npm run build
node dist/index.js
```

Сервер должен запуститься и вывести сообщение "MCP Mac Apps Server запущен" в stderr.

## Тестирование через командную строку

Вы можете протестировать MCP сервер напрямую, отправляя JSON-RPC сообщения:

```bash
# Тест списка инструментов
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node dist/index.js

# Тест вызова инструмента
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_running_applications","arguments":{}}}' | node dist/index.js
```

## Типичные проблемы и решения

### Проблема: Сервер не запускается
**Решение**: Убедитесь, что:
- Node.js версии 18+ установлен
- Все зависимости установлены (`npm install`)
- Проект собран (`npm run build`)

### Проблема: DeepSeek не видит инструменты
**Решение**: 
- Проверьте, что путь к серверу в конфигурации правильный
- Убедитесь, что DeepSeek перезапущен после изменения конфигурации
- Проверьте логи DeepSeek на наличие ошибок

### Проблема: Ошибки доступа к приложениям
**Решение**: 
- macOS может требовать разрешения в "Системные настройки → Конфиденциальность и безопасность → Управление компьютером"
- Разрешите доступ для Terminal/Node.js

## Альтернативный вариант: Интеграция через API

Если DeepSeek имеет REST API, можно создать простой HTTP-обертку для MCP сервера, но это требует дополнительной разработки.

## Где найти актуальную информацию

- Официальная документация DeepSeek
- [MCP Specification](https://modelcontextprotocol.io/)
- Документация по вашему MCP клиенту

---

**Примечание**: Структура конфигурации может отличаться в зависимости от версии DeepSeek и типа клиента. Сверьтесь с официальной документацией DeepSeek для актуальной информации.

