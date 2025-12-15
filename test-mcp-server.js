#!/usr/bin/env node

/**
 * Простой тест для проверки работы MCP сервера
 * Использование: node test-mcp-server.js
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const serverPath = join(__dirname, 'dist', 'index.js');

console.log('🧪 Тестирование MCP сервера...\n');

// Запускаем сервер
const server = spawn('node', [serverPath], {
  stdio: ['pipe', 'pipe', 'pipe']
});

let output = '';
let errorOutput = '';

server.stdout.on('data', (data) => {
  output += data.toString();
});

server.stderr.on('data', (data) => {
  errorOutput += data.toString();
});

server.on('error', (error) => {
  console.error('❌ Ошибка запуска сервера:', error.message);
  console.error('\nУбедитесь, что:');
  console.error('1. Проект собран: npm run build');
  console.error('2. Node.js установлен и доступен');
  process.exit(1);
});

// Отправляем тестовый запрос на список инструментов
setTimeout(() => {
  const testRequest = {
    jsonrpc: '2.0',
    id: 1,
    method: 'tools/list',
    params: {}
  };

  console.log('📤 Отправка запроса: tools/list');
  server.stdin.write(JSON.stringify(testRequest) + '\n');
  
  setTimeout(() => {
    if (errorOutput.includes('запущен')) {
      console.log('✅ Сервер успешно запущен!');
    }
    
    console.log('\n📋 Вывод сервера:');
    if (output) {
      console.log(output);
    }
    if (errorOutput) {
      console.log('stderr:', errorOutput);
    }
    
    server.kill();
    console.log('\n✨ Тест завершен');
    process.exit(0);
  }, 1000);
}, 500);

