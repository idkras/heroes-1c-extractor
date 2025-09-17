/**
 * @fileoverview N8N Timestamp Processor для Google Sheets
 * @version 1.0.0
 * @author AI Assistant
 * @license MIT
 * 
 * JTBD: Когда разработчик использует n8n для обработки timestamp данных,
 * он хочет корректно форматировать ISO timestamp в читаемый формат для Google Sheets,
 * чтобы избежать проблем с отображением времени в таблицах.
 */

/**
 * Безопасное форматирование timestamp в читаемый формат
 * 
 * JTBD: Когда функция получает timestamp в любом формате,
 * она хочет вернуть его в формате "YYYY-MM-DD HH:MM:SS" для Google Sheets,
 * чтобы обеспечить корректное отображение времени.
 * 
 * @param {string|number|Date|null} timestamp - Входной timestamp
 * @returns {string} Отформатированный timestamp в формате "YYYY-MM-DD HH:MM:SS"
 * 
 * @example
 * safeFormatTimestamp("2025-01-27T11:45:00.000Z") // "2025-01-27 11:45:00"
 * safeFormatTimestamp("2025-01-27 12:00:00") // "2025-01-27 12:00:00"
 * safeFormatTimestamp(1640995200) // "2022-01-01 00:00:00"
 * safeFormatTimestamp(null) // текущее время
 */
function safeFormatTimestamp(timestamp) {
  try {
    // Если timestamp пустой или null
    if (!timestamp) {
      return getCurrentUTCTime();
    }
    
    let date;
    
    // Если timestamp уже в нужном формате "YYYY-MM-DD HH:MM:SS" (с валидацией)
    if (typeof timestamp === 'string' && timestamp.includes(' ') && !timestamp.includes('T')) {
      // Валидируем компоненты даты
      const dateRegex = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/;
      const match = timestamp.match(dateRegex);
      
      if (match) {
        const [, year, month, day, hours, minutes, seconds] = match;
        const yearNum = parseInt(year);
        const monthNum = parseInt(month);
        const dayNum = parseInt(day);
        const hoursNum = parseInt(hours);
        const minutesNum = parseInt(minutes);
        const secondsNum = parseInt(seconds);
        
        // Проверяем корректность компонентов
        if (yearNum >= 1900 && yearNum <= 2100 &&
            monthNum >= 1 && monthNum <= 12 &&
            dayNum >= 1 && dayNum <= 31 &&
            hoursNum >= 0 && hoursNum <= 23 &&
            minutesNum >= 0 && minutesNum <= 59 &&
            secondsNum >= 0 && secondsNum <= 59) {
          
          // Простая проверка: если компоненты корректны, возвращаем как есть
          return timestamp;
        }
      }
    }
    
    // Если timestamp - число (Unix timestamp)
    if (typeof timestamp === 'number') {
      // Определяем: секунды или миллисекунды
      if (timestamp < 10000000000) {
        // Секунды (до 2286 года)
        date = new Date(timestamp * 1000);
      } else {
        // Миллисекунды
        date = new Date(timestamp);
      }
    } else {
      // Строка или другой формат - пробуем парсить
      date = new Date(timestamp);
    }
    
    // Проверяем валидность даты
    if (isNaN(date.getTime())) {
      throw new Error('Некорректная дата');
    }
    
    // Форматируем в UTC для избежания timezone проблем
    return formatDateToUTC(date);
    
  } catch (error) {
    // Fallback на текущее время при ошибке
    return getCurrentUTCTime();
  }
}

/**
 * Получение текущего времени в UTC формате
 * 
 * JTBD: Когда функция нуждается в текущем времени,
 * она хочет получить его в UTC формате для консистентности.
 * 
 * @returns {string} Текущее время в формате "YYYY-MM-DD HH:MM:SS"
 */
function getCurrentUTCTime() {
  const now = new Date();
  return formatDateToUTC(now);
}

/**
 * Форматирование даты в UTC формат
 * 
 * JTBD: Когда функция получает объект Date,
 * она хочет отформатировать его в строку UTC для Google Sheets.
 * 
 * @param {Date} date - Объект Date для форматирования
 * @returns {string} Отформатированная дата в формате "YYYY-MM-DD HH:MM:SS"
 */
function formatDateToUTC(date) {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, '0');
  const day = date.getUTCDate().toString().padStart(2, '0');
  const hours = date.getUTCHours().toString().padStart(2, '0');
  const minutes = date.getUTCMinutes().toString().padStart(2, '0');
  const seconds = date.getUTCSeconds().toString().padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * Основная функция обработки данных для n8n
 * 
 * JTBD: Когда n8n получает данные с timestamp,
 * он хочет обработать их и вернуть в корректном формате для Google Sheets,
 * чтобы обеспечить правильное отображение времени.
 * 
 * @param {Object|Array} inputData - Входные данные из n8n
 * @returns {Array} Обработанные данные с отформатированными timestamp
 */
function processTimestampData(inputData) {
  try {
    // Проверяем, что данные существуют
    if (!inputData) {
      throw new Error('Входные данные пустые');
    }
    
    // Преобразуем в массив если нужно
    const dataArray = Array.isArray(inputData) ? inputData : [inputData];
    
    // Обрабатываем данные с проверками
    const processedData = dataArray.map((record, index) => {
      try {
        if (!record || typeof record !== 'object') {
          // Пропускаем некорректные записи
          return null;
        }
        
        const formattedTimestamp = safeFormatTimestamp(record.timestamp);
        
        return {
          ...record,
          timestamp: formattedTimestamp,
          _processed_at: getCurrentUTCTime(),
          _original_timestamp: record.timestamp || 'not_provided'
        };
        
      } catch (error) {
        // Обработка ошибок для отдельных записей
        return {
          ...record,
          timestamp: getCurrentUTCTime(),
          _error: error.message,
          _processed_at: getCurrentUTCTime()
        };
      }
    }).filter(record => record !== null); // Убираем null записи
    
    return processedData;
    
  } catch (error) {
    // Критическая ошибка - возвращаем fallback данные
    return [{
      timestamp: getCurrentUTCTime(),
      _error: error.message,
      _processed_at: getCurrentUTCTime(),
      _fallback: true
    }];
  }
}

// Экспорт для использования в n8n
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    safeFormatTimestamp,
    processTimestampData,
    getCurrentUTCTime,
    formatDateToUTC
  };
}

// Экспорт для ES6 модулей
if (typeof exports !== 'undefined') {
  exports.safeFormatTimestamp = safeFormatTimestamp;
  exports.processTimestampData = processTimestampData;
  exports.getCurrentUTCTime = getCurrentUTCTime;
  exports.formatDateToUTC = formatDateToUTC;
}
