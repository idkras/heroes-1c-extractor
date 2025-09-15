/**
 * DuckDB Integration для MCP сервера
 * Обеспечивает чтение файлов из кеша вместо диска
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

class DuckDBCacheReader {
  constructor() {
    this.pythonScript = path.join(__dirname, 'cache_reader.py');
    this.connected = false;
  }

  /**
   * Подключение к DuckDB кешу через Python CLI
   */
  async connect() {
    try {
      const result = await this.execPython(['stats']);
      if (result.success && result.stats && result.stats.cache_available) {
        this.connected = true;
        console.log('✅ Connected to DuckDB cache');
        return true;
      } else {
        throw new Error(result.error || 'Cache not available');
      }
    } catch (error) {
      console.warn('⚠️ Could not connect to DuckDB cache:', error.message);
      this.connected = false;
      return false;
    }
  }

  /**
   * Выполнение Python скрипта для работы с кешем
   */
  async execPython(args) {
    return new Promise((resolve, reject) => {
      const python = spawn('python', [this.pythonScript, ...args], {
        cwd: path.dirname(path.dirname(path.dirname(__dirname)))
      });
      
      let output = '';
      let error = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        error += data.toString();
      });
      
      python.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output.trim());
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse JSON: ${output}`));
          }
        } else {
          reject(new Error(`Python script failed: ${error || output}`));
        }
      });
    });
  }

  /**
   * Получение файла из кеша по пути
   */
  async getFileFromCache(filePath) {
    if (!this.connected) {
      await this.connect();
    }

    if (!this.connected) {
      return null;
    }

    try {
      const result = await this.execPython(['read', filePath]);
      
      if (result.success && result.file) {
        console.log(`✅ File found in cache: ${result.file.name} (${result.file.word_count} words)`);
        return {
          content: result.file.content,
          metadata: {
            name: result.file.name,
            path: result.file.path,
            word_count: result.file.word_count,
            category: result.file.category,
            source: 'duckdb_cache'
          }
        };
      }

      return null;
    } catch (error) {
      console.warn('⚠️ Error reading from DuckDB cache:', error.message);
      return null;
    }
  }

  /**
   * Получение списка всех файлов из кеша
   */
  async getAllFilesFromCache() {
    if (!this.connected) {
      await this.connect();
    }

    if (!this.connected) {
      return [];
    }

    try {
      const result = await this.execPython(['list']);
      
      if (result.success && result.files) {
        console.log(`✅ Found ${result.files.length} files in cache`);
        return result.files;
      }

      return [];
    } catch (error) {
      console.warn('⚠️ Error listing files from DuckDB cache:', error.message);
      return [];
    }
  }

  /**
   * Поиск файлов в кеше
   */
  async searchInCache(query) {
    if (!this.connected) {
      await this.connect();
    }

    if (!this.connected) {
      return [];
    }

    try {
      const stmt = this.db.prepare(`
        SELECT id, name, path, category, word_count, description
        FROM standards 
        WHERE name LIKE ? OR description LIKE ? OR content LIKE ?
        ORDER BY word_count DESC
        LIMIT 10
      `);
      
      const searchPattern = `%${query}%`;
      const results = stmt.all(searchPattern, searchPattern, searchPattern);
      
      console.log(`✅ Search found ${results.length} matches for: ${query}`);
      
      return results.map(row => ({
        id: row.id,
        name: row.name,
        path: row.path,
        category: row.category,
        word_count: row.word_count,
        description: row.description,
        source: 'duckdb_cache'
      }));
    } catch (error) {
      console.warn('⚠️ Error searching in DuckDB cache:', error.message);
      return [];
    }
  }

  /**
   * Проверка состояния кеша
   */
  async getCacheStats() {
    try {
      const result = await this.execPython(['stats']);
      
      if (result.success && result.stats) {
        return result.stats;
      }
      
      return { error: result.error || 'Failed to get stats', cache_available: false };
    } catch (error) {
      return { error: error.message, cache_available: false };
    }
  }

  /**
   * Закрытие соединения
   */
  close() {
    if (this.db) {
      this.db.close();
      this.connected = false;
      console.log('🔒 DuckDB cache connection closed');
    }
  }
}

export { DuckDBCacheReader };