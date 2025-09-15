#!/usr/bin/env node

/**
 * Standards-MCP Server
 * 
 * JTBD: Я (MCP сервер) хочу предоставить интеллектуальное управление стандартами,
 * чтобы AI Assistant мог автоматически находить и применять релевантные стандарты.
 * 
 * Основан на: task-master-ai v0.13.2 архитектуре
 * Автор: AI Assistant
 * Дата: 26 May 2025
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import express from 'express';
import cors from 'cors';
import fs from 'fs/promises';
import { DuckDBCacheReader } from './duckdb_integration.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * JTBD: Я (сервер) хочу предоставить набор инструментов для работы со стандартами,
 * чтобы обеспечить контекстные подсказки и автоматическую валидацию.
 */
class StandardsMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: "standards-mcp-server",
        version: "1.0.0",
        description: "Intelligent standards management and recommendations"
      },
      {
        capabilities: {
          tools: {},
          resources: {},
          prompts: {}
        }
      }
    );
    
    // Инициализируем DuckDB кеш для чтения файлов
    this.cacheReader = new DuckDBCacheReader();
    
    // HTTP API для внешнего доступа
    this.app = express();
    this.app.use(cors());
    this.app.use(express.json());
    
    this.setupHandlers();
    this.setupHttpApi();
  }
  
  setupHttpApi() {
    // GET /health - проверка состояния сервера
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy',
        message: 'MCP Standards Server is running',
        timestamp: new Date().toISOString(),
        mcp_server: 'running',
        http_api: 'active'
      });
    });

    // GET /standards - получить все стандарты из DuckDB кеша
    this.app.get('/standards', async (req, res) => {
      try {
        // Читаем из DuckDB кеша вместо диска
        const standards = await this.cacheReader.getAllFilesFromCache();
        
        if (standards.length === 0) {
          // Fallback: если кеш пустой, читаем с диска
          console.warn('DuckDB cache is empty, falling back to filesystem');
          const standardsDir = path.join(__dirname, '../../../[standards .md]');
          const files = await this.getAllStandardFiles(standardsDir);
          
          const fileStandards = [];
          for (const file of files) {
            const content = await fs.readFile(file, 'utf-8');
            const metadata = this.extractMetadata(content);
            fileStandards.push({
              id: path.basename(file, '.md'),
              filename: path.basename(file),
              metadata,
              path: file,
              source: 'filesystem_fallback'
            });
          }
          
          res.json({ success: true, standards: fileStandards });
        } else {
          // Преобразуем формат кеша в ожидаемый формат
          const formattedStandards = standards.map(standard => ({
            id: standard.id,
            filename: path.basename(standard.path),
            metadata: {
              name: standard.name,
              category: standard.category,
              word_count: standard.word_count
            },
            path: standard.path,
            source: 'duckdb_cache'
          }));
          
          res.json({ success: true, standards: formattedStandards });
        }
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // GET /mcp/commands - получить список MCP команд
    this.app.get('/mcp/commands', (req, res) => {
      const commands = [
        { name: "standards-resolver", description: "Resolves abstract standard addresses to actual content" },
        { name: "suggest-standards", description: "Suggests relevant standards based on context/JTBD" },
        { name: "validate-compliance", description: "Validates content against relevant standards" },
        { name: "standards-navigator", description: "Advanced search and discovery of standards" },
        { name: "analyze-landing", description: "HeroesGPT landing analysis workflow" },
        { name: "extract-all-offers", description: "Извлечение всех оферов с лендинга" },
        { name: "create-jtbd-scenarios", description: "Создание JTBD сценариев" },
        { name: "generate-heroesgpt-report", description: "Генерация полного отчета" }
      ];
      
      res.json({
        success: true,
        commands: commands,
        total: commands.length
      });
    });

    // POST /standards - создать новый стандарт
    this.app.post('/standards', async (req, res) => {
      try {
        const { title, content, category, author = 'API User' } = req.body;
        
        if (!title || !content) {
          return res.status(400).json({ 
            success: false, 
            error: 'Title and content are required' 
          });
        }

        const timestamp = new Date().toLocaleString('en-GB', {
          day: '2-digit',
          month: 'short', 
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Europe/Berlin'
        }).replace(',', '').toLowerCase();

        const filename = `${title.toLowerCase().replace(/[^a-z0-9]/g, '_')}_${timestamp.replace(/[^a-z0-9]/g, '_')}_by_${author.toLowerCase().replace(/[^a-z0-9]/g, '_')}.md`;
        
        const categoryPath = category || '4. dev · design · qa';
        const standardsDir = path.join(__dirname, '../../../[standards .md]', categoryPath);
        const filepath = path.join(standardsDir, filename);

        // Создаем директорию если не существует
        await fs.mkdir(standardsDir, { recursive: true });
        
        await fs.writeFile(filepath, content, 'utf-8');

        res.json({ 
          success: true, 
          message: 'Standard created successfully',
          id: path.basename(filename, '.md'),
          title: title,
          filename,
          path: filepath
        });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // POST /mcp/commands - выполнение MCP команд через HTTP
    this.app.post('/mcp/commands', async (req, res) => {
      try {
        const { command, args } = req.body;
        
        // Вызываем MCP команду
        const result = await this.handleMCPCommand(command, args);
        res.json({ success: true, result });
      } catch (error) {
        res.status(500).json({ success: false, error: error.message });
      }
    });

    // Запускаем HTTP сервер на порту 3001
    this.app.listen(3001, () => {
      console.log('✅ Standards HTTP API running on http://localhost:3001');
    });
  }

  /**
   * Обработчик MCP команд через HTTP API
   */
  async handleMCPCommand(commandName, args) {
    try {
      switch (commandName) {
        case "read-from-cache":
          return await this.handleReadFromCache(args);
        case "standards-resolver":
          return await this.handleStandardsResolver(args);
        case "suggest-standards":
          return await this.handleSuggestStandards(args);
        case "validate-compliance":
          return await this.handleValidateCompliance(args);
        case "standards-navigator":
          return await this.handleStandardsNavigator(args);
        default:
          throw new Error(`Unknown command: ${commandName}`);
      }
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error in ${commandName}: ${error.message}`
        }],
        isError: true
      };
    }
  }

  async getAllStandardFiles(dir) {
    const files = [];
    
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        if (entry.isDirectory() && !entry.name.startsWith('[archive]')) {
          const subFiles = await this.getAllStandardFiles(fullPath);
          files.push(...subFiles);
        } else if (entry.isFile() && entry.name.endsWith('.md')) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      console.log(`Could not read directory ${dir}:`, error.message);
    }
    
    return files;
  }

  extractMetadata(content) {
    const metadata = {};
    
    // Извлекаем protected section
    const protectedMatch = content.match(/<!-- 🔒 PROTECTED SECTION: BEGIN -->(.*?)<!-- 🔒 PROTECTED SECTION: END -->/s);
    if (protectedMatch) {
      const protectedContent = protectedMatch[1];
      
      const patterns = {
        type: /type:\s*(.+)/,
        standard_id: /standard_id:\s*(.+)/,
        logical_id: /logical_id:\s*(.+)/,
        updated: /updated:\s*(.+)/,
        version: /version:\s*(.+)/,
        status: /status:\s*(.+)/,
        tags: /tags:\s*(.+)/
      };
      
      for (const [key, pattern] of Object.entries(patterns)) {
        const match = protectedContent.match(pattern);
        if (match) {
          metadata[key] = match[1].trim();
        }
      }
    }
    
    return metadata;
  }

  setupHandlers() {
    // Регистрация доступных инструментов
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "read-from-cache",
          description: "Reads file content from DuckDB cache instead of disk",
          inputSchema: {
            type: "object",
            properties: {
              filePath: { 
                type: "string",
                description: "Path to the file to read from cache"
              },
              fileName: { 
                type: "string",
                description: "Name of the file to read from cache"
              }
            }
          }
        },
        {
          name: "standards-resolver",
          description: "Resolves abstract standard addresses to actual content",
          inputSchema: {
            type: "object",
            properties: {
              address: { 
                type: "string",
                description: "Abstract address like abstract://standard:registry"
              },
              format: { 
                type: "string", 
                enum: ["full", "summary", "checklist"],
                default: "full",
                description: "Output format for the standard content"
              },
              context: { 
                type: "string",
                description: "Optional context for filtering content"
              }
            },
            required: ["address"]
          }
        },
        {
          name: "suggest-standards",
          description: "Suggests relevant standards based on context/JTBD",
          inputSchema: {
            type: "object",
            properties: {
              jtbd: { 
                type: "string",
                description: "Job-to-be-Done description"
              },
              taskType: { 
                type: "string",
                enum: ["development", "analysis", "design", "process", "quality"],
                description: "Type of task being performed"
              },
              currentContent: { 
                type: "string",
                description: "Optional current work content for context"
              },
              priority: { 
                type: "string", 
                enum: ["high", "medium", "low"],
                default: "medium",
                description: "Priority level for suggestions"
              }
            },
            required: ["jtbd"]
          }
        },
        {
          name: "validate-compliance",
          description: "Validates content against relevant standards",
          inputSchema: {
            type: "object",
            properties: {
              content: { 
                type: "string",
                description: "Content to validate"
              },
              standardsToCheck: { 
                type: "array", 
                items: { type: "string" },
                description: "Specific standards to check against"
              },
              strictMode: { 
                type: "boolean", 
                default: false,
                description: "Enable strict validation mode"
              }
            },
            required: ["content"]
          }
        },
        {
          name: "standards-navigator",
          description: "Advanced search and discovery of standards",
          inputSchema: {
            type: "object",
            properties: {
              query: { 
                type: "string",
                description: "Search query"
              },
              category: { 
                type: "string",
                enum: ["core", "process", "development", "quality", "design"],
                description: "Standard category filter"
              },
              relatedTo: { 
                type: "string",
                description: "Find standards related to this one"
              },
              includeArchived: { 
                type: "boolean", 
                default: false,
                description: "Include archived standards in results"
              }
            }
          }
        },
        {
          name: "analyze-landing",
          description: "HeroesGPT landing analysis workflow - быстрый запуск полного анализа",
          inputSchema: {
            type: "object",
            properties: {
              url: { 
                type: "string",
                description: "URL лендинга для анализа"
              },
              screenshot: { 
                type: "string",
                description: "Путь к скриншоту лендинга"
              },
              content: { 
                type: "string",
                description: "Текстовый контент лендинга"
              }
            }
          }
        },
        {
          name: "extract-all-offers",
          description: "Извлечение всех оферов с лендинга по стандарту heroesGPT",
          inputSchema: {
            type: "object",
            properties: {
              landingData: { 
                type: "object",
                description: "Данные анализа лендинга"
              }
            },
            required: ["landingData"]
          }
        },
        {
          name: "create-jtbd-scenarios",
          description: "Создание JTBD сценариев по стандарту v4.0",
          inputSchema: {
            type: "object",
            properties: {
              offers: { 
                type: "array",
                description: "Массив извлеченных оферов"
              }
            },
            required: ["offers"]
          }
        },
        {
          name: "generate-heroesgpt-report", 
          description: "Генерация полного отчета по стандарту heroesGPT с автосохранением",
          inputSchema: {
            type: "object",
            properties: {
              analysisData: { 
                type: "object",
                description: "Полные данные анализа"
              }
            },
            required: ["analysisData"]
          }
        },
        {
          name: "ilya-review-challenge",
          description: "Добавляет комментарии-челленджи от Ильи Красинского к документу по стандарту 6.7",
          inputSchema: {
            type: "object",
            properties: {
              document_content: { 
                type: "string",
                description: "Текст документа для ревью"
              },
              document_type: { 
                type: "string", 
                enum: ["landing_review", "analysis", "recommendation", "strategy"],
                default: "landing_review",
                description: "Тип документа для анализа"
              },
              focus_areas: { 
                type: "array", 
                items: { type: "string" },
                description: "Конкретные области для челленджа"
              }
            },
            required: ["document_content"]
          }
        }
      ]
    }));
    
    // Обработка вызовов инструментов
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          case "read-from-cache":
            return await this.handleReadFromCache(args);
          case "standards-resolver":
            return await this.handleStandardsResolver(args);
          case "suggest-standards":
            return await this.handleSuggestStandards(args);
          case "validate-compliance":
            return await this.handleValidateCompliance(args);
          case "standards-navigator":
            return await this.handleStandardsNavigator(args);
          case "analyze-landing":
            return await this.handleAnalyzeLanding(args);
          case "extract-all-offers":
            return await this.handleExtractOffers(args);
          case "create-jtbd-scenarios":
            return await this.handleCreateJTBD(args);
          case "generate-heroesgpt-report":
            return await this.handleGenerateReport(args);
          case "ilya-review-challenge":
            return await this.handleIlyaReviewChallenge(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error in ${name}: ${error.message}`
          }],
          isError: true
        };
      }
    });
  }
  
  /**
   * JTBD: Я (кеш-ридер) хочу прочитать файл из DuckDB кеша вместо диска,
   * чтобы обеспечить быстрый доступ к данным без постоянного обращения к файловой системе.
   */
  async handleReadFromCache(args) {
    const { filePath, fileName } = args;
    const startTime = Date.now();

    try {
      // Пытаемся найти файл в кеше
      const searchPath = filePath || fileName;
      const cachedFile = await this.cacheReader.getFileFromCache(searchPath);
      
      if (cachedFile) {
        return {
          content: [{
            type: "text",
            text: `📄 File: ${cachedFile.metadata.name} (from DuckDB cache)\n` +
                  `📊 Stats: ${cachedFile.metadata.word_count} words, category: ${cachedFile.metadata.category}\n` +
                  `⚡ Source: ${cachedFile.metadata.source}\n\n` +
                  `--- Content ---\n${cachedFile.content}`
          }]
        };
      } else {
        // Кеш пустой или файл не найден
        const cacheStats = await this.cacheReader.getCacheStats();
        
        if (cacheStats.cache_available && cacheStats.total_files > 0) {
          return {
            content: [{
              type: "text", 
              text: `❌ File not found in cache: ${searchPath}\n` +
                    `📊 Cache stats: ${cacheStats.total_files} files available\n` +
                    `💡 Try searching with a different name or path`
            }]
          };
        } else {
          return {
            content: [{
              type: "text",
              text: `⚠️ DuckDB cache is empty or unavailable\n` +
                    `📊 Cache status: ${JSON.stringify(cacheStats, null, 2)}\n` +
                    `💡 Please initialize the cache first or use filesystem fallback`
            }]
          };
        }
      }
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `❌ Error reading from cache: ${error.message}`
        }],
        isError: true
      };
    }
  }
  
  /**
   * JTBD: Я (resolver) хочу преобразовать логический адрес в контент стандарта,
   * чтобы AI Assistant получил актуальную информацию.
   */
  async handleStandardsResolver(args) {
    const { address, format = "full", context } = args;
    const startTime = Date.now();
    
    try {
      // Вызываем Python-скрипт для резолвинга через UnifiedKeyResolver
      const result = await this.callPythonScript('standards_resolver.py', {
        address,
        format, 
        context
      });
      
      const duration = Date.now() - startTime;
      
      // Логируем операцию для dashboard
      await this.logMCPOperation('standards-resolver', { address, format, context }, 
                                result, duration, 'success');
      
      return {
        content: [{
          type: "text",
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      await this.logMCPOperation('standards-resolver', { address, format, context }, 
                                {}, duration, 'error', error.message);
      throw error;
    }
  }
  
  /**
   * JTBD: Я (suggester) хочу проанализировать JTBD и предложить релевантные стандарты,
   * чтобы AI Assistant использовал правильные методологии.
   */
  async handleSuggestStandards(args) {
    const { jtbd, taskType, currentContent, priority = "medium" } = args;
    
    const result = await this.callPythonScript('standards_suggester.py', {
      jtbd,
      taskType,
      currentContent,
      priority
    });
    
    return {
      content: [{
        type: "text", 
        text: JSON.stringify(result, null, 2)
      }]
    };
  }
  
  /**
   * JTBD: Я (validator) хочу проверить соответствие контента стандартам,
   * чтобы обеспечить качество создаваемых материалов.
   */
  async handleValidateCompliance(args) {
    const { content, standardsToCheck = [], strictMode = false } = args;
    
    const result = await this.callPythonScript('compliance_checker.py', {
      content,
      standardsToCheck,
      strictMode
    });
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify(result, null, 2)
      }]
    };
  }
  
  /**
   * JTBD: Я (navigator) хочу предоставить продвинутый поиск стандартов,
   * чтобы AI Assistant мог находить нужную документацию.
   */
  async handleStandardsNavigator(args) {
    const { query, category, relatedTo, includeArchived = false } = args;
    
    const result = await this.callPythonScript('standards_navigator.py', {
      query,
      category,
      relatedTo,
      includeArchived
    });
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify(result, null, 2)
      }]
    };
  }
  
  /**
   * JTBD: Я (logger) хочу логировать MCP операции для dashboard,
   * чтобы обеспечить визуализацию всех команд в реальном времени.
   */
  async logMCPOperation(toolName, parameters, result, duration, status, errorMessage = '') {
    try {
      await this.callPythonScript('mcp_dashboard_logger.py', {
        tool_name: toolName,
        parameters: parameters,
        result: result,
        duration_ms: duration,
        status: status,
        error_message: errorMessage
      });
    } catch (error) {
      // Логирование не должно ломать основную операцию
      console.error('Dashboard logging failed:', error.message);
    }
  }

  /**
   * JTBD: Я (challenge-handler) хочу добавить комментарии-челленджи от Ильи Красинского,
   * чтобы улучшить качество ревью через призму пользовательского опыта.
   */
  async handleIlyaReviewChallenge(args) {
    const startTime = Date.now();
    
    try {
      // Вызываем Python-скрипт для обработки челленджа
      const result = await this.callPythonScript('ilya_review_challenge', args);
      
      const duration = Date.now() - startTime;
      
      // Логируем операцию
      await this.logMCPOperation(
        'ilya-review-challenge',
        args,
        result,
        duration,
        result.success ? 'success' : 'error',
        result.error || ''
      );
      
      return {
        content: result.content || [{
          type: "text",
          text: result.enhanced_content || result.error || "Челлендж завершен"
        }]
      };
      
    } catch (error) {
      const duration = Date.now() - startTime;
      
      await this.logMCPOperation(
        'ilya-review-challenge',
        args,
        {},
        duration,
        'error',
        error.message
      );
      
      return {
        content: [{
          type: "text",
          text: `Ошибка при выполнении челленджа: ${error.message}`
        }],
        isError: true
      };
    }
  }

  /**
   * JTBD: Я (bridge) хочу вызвать Python-скрипт для выполнения операций,
   * чтобы использовать существующую инфраструктуру кеша и резольвера.
   */
  async callPythonScript(scriptName, args) {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(__dirname, 'python_backends', scriptName);
      const pythonProcess = spawn('python3', [scriptPath, JSON.stringify(args)]);
      
      let stdout = '';
      let stderr = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python script failed: ${stderr}`));
        } else {
          try {
            const result = JSON.parse(stdout);
            resolve(result);
          } catch (error) {
            reject(new Error(`Failed to parse Python output: ${stdout}`));
          }
        }
      });
      
      pythonProcess.on('error', (error) => {
        reject(new Error(`Failed to start Python script: ${error.message}`));
      });
    });
  }
  
  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Standards MCP Server running on stdio");
  }
}

// Запуск сервера
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new StandardsMCPServer();
  server.run().catch(console.error);
}

export default StandardsMCPServer;