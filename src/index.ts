#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { exec } from "child_process";
import { promisify } from "util";
import { MongoClient, ObjectId } from "mongodb";

const execAsync = promisify(exec);

// Константа для Ollama API
const OLLAMA_API_URL = process.env.OLLAMA_API_URL || "http://localhost:11434";

// Константа для MongoDB
const MONGODB_URI = process.env.MONGODB_URI || "mongodb://localhost:27017";

class MacAppsMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "mac-apps-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  private setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };

    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "open_application",
            description:
              "Открывает приложение на Mac по имени. Примеры: 'Safari', 'Finder', 'TextEdit', 'Calculator'",
            inputSchema: {
              type: "object",
              properties: {
                appName: {
                  type: "string",
                  description: "Имя приложения для запуска (например, 'Safari', 'Calculator')",
                },
              },
              required: ["appName"],
            },
          },
          {
            name: "get_running_applications",
            description: "Получает список всех запущенных приложений на Mac",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "run_applescript",
            description:
              "Выполняет AppleScript команду в указанном приложении. Полезно для автоматизации действий в приложениях",
            inputSchema: {
              type: "object",
              properties: {
                appName: {
                  type: "string",
                  description: "Имя приложения (например, 'Safari', 'Finder')",
                },
                script: {
                  type: "string",
                  description: "AppleScript команда для выполнения",
                },
              },
              required: ["appName", "script"],
            },
          },
          {
            name: "quit_application",
            description: "Закрывает указанное приложение",
            inputSchema: {
              type: "object",
              properties: {
                appName: {
                  type: "string",
                  description: "Имя приложения для закрытия",
                },
              },
              required: ["appName"],
            },
          },
          {
            name: "open_file_with_app",
            description: "Открывает файл или URL в указанном приложении",
            inputSchema: {
              type: "object",
              properties: {
                path: {
                  type: "string",
                  description: "Путь к файлу или URL",
                },
                appName: {
                  type: "string",
                  description: "Имя приложения для открытия файла",
                },
              },
              required: ["path", "appName"],
            },
          },
          {
            name: "ollama_generate",
            description: "Генерирует ответ используя локальную модель Ollama. Используйте для задач, требующих AI обработки текста",
            inputSchema: {
              type: "object",
              properties: {
                model: {
                  type: "string",
                  description: "Название модели Ollama (например, 'llama3.2', 'deepseek-r1:8b'). По умолчанию 'llama3.2'",
                  default: "llama3.2",
                },
                prompt: {
                  type: "string",
                  description: "Запрос для модели",
                },
              },
              required: ["prompt"],
            },
          },
          {
            name: "ollama_list_models",
            description: "Получает список доступных моделей Ollama",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "mongodb_create_database",
            description: "Создает новую базу данных в MongoDB",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
              },
              required: ["databaseName"],
            },
          },
          {
            name: "mongodb_list_databases",
            description: "Получает список всех баз данных в MongoDB",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "mongodb_create_collection",
            description: "Создает новую коллекцию в указанной базе данных",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
                collectionName: {
                  type: "string",
                  description: "Имя коллекции",
                },
              },
              required: ["databaseName", "collectionName"],
            },
          },
          {
            name: "mongodb_list_collections",
            description: "Получает список коллекций в указанной базе данных",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
              },
              required: ["databaseName"],
            },
          },
          {
            name: "mongodb_delete_collection",
            description: "Удаляет коллекцию из базы данных",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
                collectionName: {
                  type: "string",
                  description: "Имя коллекции для удаления",
                },
              },
              required: ["databaseName", "collectionName"],
            },
          },
          {
            name: "mongodb_insert_document",
            description: "Вставляет документ в коллекцию",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
                collectionName: {
                  type: "string",
                  description: "Имя коллекции",
                },
                document: {
                  type: "string",
                  description: "JSON строка с документом для вставки",
                },
              },
              required: ["databaseName", "collectionName", "document"],
            },
          },
          {
            name: "mongodb_find_documents",
            description: "Находит документы в коллекции",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
                collectionName: {
                  type: "string",
                  description: "Имя коллекции",
                },
                filter: {
                  type: "string",
                  description: "JSON строка с фильтром для поиска (необязательно)",
                },
                limit: {
                  type: "number",
                  description: "Максимальное количество документов (по умолчанию 100)",
                },
              },
              required: ["databaseName", "collectionName"],
            },
          },
          {
            name: "mongodb_delete_document",
            description: "Удаляет документ(ы) из коллекции по фильтру",
            inputSchema: {
              type: "object",
              properties: {
                databaseName: {
                  type: "string",
                  description: "Имя базы данных",
                },
                collectionName: {
                  type: "string",
                  description: "Имя коллекции",
                },
                filter: {
                  type: "string",
                  description: "JSON строка с фильтром для удаления",
                },
              },
              required: ["databaseName", "collectionName", "filter"],
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "open_application":
            return await this.openApplication(args?.appName as string);

          case "get_running_applications":
            return await this.getRunningApplications();

          case "run_applescript":
            return await this.runAppleScript(
              args?.appName as string,
              args?.script as string
            );

          case "quit_application":
            return await this.quitApplication(args?.appName as string);

          case "open_file_with_app":
            return await this.openFileWithApp(
              args?.path as string,
              args?.appName as string
            );

          case "ollama_generate":
            return await this.ollamaGenerate(
              args?.prompt as string,
              (args?.model as string) || "llama3.2"
            );

          case "ollama_list_models":
            return await this.ollamaListModels();

          case "mongodb_create_database":
            return await this.mongodbCreateDatabase(args?.databaseName as string);

          case "mongodb_list_databases":
            return await this.mongodbListDatabases();

          case "mongodb_create_collection":
            return await this.mongodbCreateCollection(
              args?.databaseName as string,
              args?.collectionName as string
            );

          case "mongodb_list_collections":
            return await this.mongodbListCollections(args?.databaseName as string);

          case "mongodb_delete_collection":
            return await this.mongodbDeleteCollection(
              args?.databaseName as string,
              args?.collectionName as string
            );

          case "mongodb_insert_document":
            return await this.mongodbInsertDocument(
              args?.databaseName as string,
              args?.collectionName as string,
              args?.document as string
            );

          case "mongodb_find_documents":
            return await this.mongodbFindDocuments(
              args?.databaseName as string,
              args?.collectionName as string,
              args?.filter as string | undefined,
              args?.limit as number | undefined
            );

          case "mongodb_delete_document":
            return await this.mongodbDeleteDocument(
              args?.databaseName as string,
              args?.collectionName as string,
              args?.filter as string
            );

          default:
            throw new Error(`Неизвестный инструмент: ${name}`);
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        return {
          content: [
            {
              type: "text",
              text: `Ошибка: ${errorMessage}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  private async openApplication(appName: string) {
    try {
      // Используем команду open для запуска приложения
      await execAsync(`open -a "${appName}"`);
      return {
        content: [
          {
            type: "text",
            text: `Приложение "${appName}" успешно запущено`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Не удалось запустить приложение "${appName}": ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async getRunningApplications() {
    try {
      // Получаем список запущенных приложений через AppleScript
      const { stdout } = await execAsync(
        `osascript -e 'tell application "System Events" to get name of every application process whose background only is false'`
      );
      
      const apps = stdout
        .trim()
        .split(", ")
        .map((app) => app.trim())
        .filter((app) => app.length > 0);

      return {
        content: [
          {
            type: "text",
            text: `Запущенные приложения:\n${apps.join("\n")}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Не удалось получить список приложений: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async runAppleScript(appName: string, script: string) {
    try {
      // Выполняем AppleScript в контексте указанного приложения
      const appleScript = `
        tell application "${appName}"
          ${script}
        end tell
      `;

      const { stdout, stderr } = await execAsync(
        `osascript -e '${appleScript.replace(/'/g, "'\\''")}'`
      );

      return {
        content: [
          {
            type: "text",
            text: stdout || stderr || "Команда выполнена успешно",
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка выполнения AppleScript: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async quitApplication(appName: string) {
    try {
      const appleScript = `
        tell application "${appName}"
          quit
        end tell
      `;

      await execAsync(`osascript -e '${appleScript.replace(/'/g, "'\\''")}'`);

      return {
        content: [
          {
            type: "text",
            text: `Приложение "${appName}" закрыто`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Не удалось закрыть приложение "${appName}": ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async openFileWithApp(path: string, appName: string) {
    try {
      await execAsync(`open -a "${appName}" "${path}"`);
      return {
        content: [
          {
            type: "text",
            text: `Файл "${path}" открыт в приложении "${appName}"`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Не удалось открыть файл: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async ollamaGenerate(prompt: string, model: string = "llama3.2") {
    try {
      const response = await fetch(`${OLLAMA_API_URL}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model,
          prompt,
          stream: false,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Ollama API error: ${response.status} ${errorText}`
        );
      }

      const data = (await response.json()) as { response?: string };
      return {
        content: [
          {
            type: "text",
            text: data.response || "Нет ответа от модели",
          },
        ],
      };
    } catch (error) {
      // Проверяем, доступен ли Ollama сервер
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          `Не удалось подключиться к Ollama серверу (${OLLAMA_API_URL}). Убедитесь, что Ollama запущен: ollama serve`
        );
      }
      throw new Error(
        `Ошибка Ollama: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async ollamaListModels() {
    try {
      const response = await fetch(`${OLLAMA_API_URL}/api/tags`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Ollama API error: ${response.status} ${errorText}`
        );
      }

      const data = (await response.json()) as { models?: Array<{ name: string; size: number }> };
      const models = data.models || [];
      
      if (models.length === 0) {
        return {
          content: [
            {
              type: "text",
              text: "Нет доступных моделей. Загрузите модель: ollama pull llama3.2",
            },
          ],
        };
      }

      const modelList = models
        .map((m) => `- ${m.name} (${(m.size / 1024 / 1024 / 1024).toFixed(2)} GB)`)
        .join("\n");

      return {
        content: [
          {
            type: "text",
            text: `Доступные модели Ollama:\n${modelList}`,
          },
        ],
      };
    } catch (error) {
      if (error instanceof TypeError && error.message.includes("fetch")) {
        throw new Error(
          `Не удалось подключиться к Ollama серверу (${OLLAMA_API_URL}). Убедитесь, что Ollama запущен: ollama serve`
        );
      }
      throw new Error(
        `Ошибка получения списка моделей: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  }

  private async getMongoClient(): Promise<MongoClient> {
    const client = new MongoClient(MONGODB_URI);
    await client.connect();
    return client;
  }

  private async mongodbCreateDatabase(databaseName: string) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      // Создаем коллекцию, чтобы база данных реально создалась
      await db.createCollection("_temp");
      await db.collection("_temp").drop();
      return {
        content: [
          {
            type: "text",
            text: `База данных "${databaseName}" успешно создана`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка создания базы данных: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbListDatabases() {
    const client = await this.getMongoClient();
    try {
      const adminDb = client.db().admin();
      const { databases } = await adminDb.listDatabases();
      const dbNames = databases
        .map((db) => db.name)
        .filter((name) => !["admin", "config", "local"].includes(name));
      
      return {
        content: [
          {
            type: "text",
            text: `Базы данных:\n${dbNames.length > 0 ? dbNames.join("\n") : "Базы данных не найдены"}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка получения списка баз данных: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbCreateCollection(
    databaseName: string,
    collectionName: string
  ) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      await db.createCollection(collectionName);
      return {
        content: [
          {
            type: "text",
            text: `Коллекция "${collectionName}" успешно создана в базе данных "${databaseName}"`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка создания коллекции: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbListCollections(databaseName: string) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      const collections = await db.listCollections().toArray();
      const collectionNames = collections.map((col) => col.name);
      
      return {
        content: [
          {
            type: "text",
            text: `Коллекции в базе данных "${databaseName}":\n${
              collectionNames.length > 0
                ? collectionNames.join("\n")
                : "Коллекции не найдены"
            }`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка получения списка коллекций: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbDeleteCollection(
    databaseName: string,
    collectionName: string
  ) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      await db.collection(collectionName).drop();
      return {
        content: [
          {
            type: "text",
            text: `Коллекция "${collectionName}" успешно удалена из базы данных "${databaseName}"`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка удаления коллекции: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbInsertDocument(
    databaseName: string,
    collectionName: string,
    documentJson: string
  ) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      const collection = db.collection(collectionName);
      const document = JSON.parse(documentJson);
      const result = await collection.insertOne(document);
      
      return {
        content: [
          {
            type: "text",
            text: `Документ успешно вставлен в коллекцию "${collectionName}". ID: ${result.insertedId}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка вставки документа: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbFindDocuments(
    databaseName: string,
    collectionName: string,
    filterJson?: string,
    limit: number = 100
  ) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      const collection = db.collection(collectionName);
      const filter = filterJson ? JSON.parse(filterJson) : {};
      const documents = await collection
        .find(filter)
        .limit(limit)
        .toArray();
      
      // Преобразуем ObjectId в строки для JSON
      const documentsStr = JSON.stringify(
        documents.map((doc) => ({
          ...doc,
          _id: doc._id.toString(),
        })),
        null,
        2
      );
      
      return {
        content: [
          {
            type: "text",
            text: `Найдено документов: ${documents.length}\n\n${documentsStr}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка поиска документов: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  private async mongodbDeleteDocument(
    databaseName: string,
    collectionName: string,
    filterJson: string
  ) {
    const client = await this.getMongoClient();
    try {
      const db = client.db(databaseName);
      const collection = db.collection(collectionName);
      const filter = JSON.parse(filterJson);
      const result = await collection.deleteMany(filter);
      
      return {
        content: [
          {
            type: "text",
            text: `Удалено документов: ${result.deletedCount}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(
        `Ошибка удаления документа: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      await client.close();
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("MCP Mac Apps Server запущен");
  }
}

const server = new MacAppsMCPServer();
server.run().catch(console.error);

