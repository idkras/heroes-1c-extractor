// Playwright тесты для валидации данных 1С
// Автоматизирует проверку веб-интерфейса и результатов извлечения

const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('1C Data Extraction Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Настройка для тестов
    await page.goto('http://localhost:8000'); // Предполагаемый веб-интерфейс
  });

  test('TC-002: Flower Data Extraction - Web Interface', async ({ page }) => {
    // Проверяем веб-интерфейс для извлечения данных о цветах
    
    // 1. Проверяем наличие кнопки извлечения данных
    await expect(page.locator('[data-testid="extract-flower-data"]')).toBeVisible();
    
    // 2. Запускаем извлечение данных
    await page.click('[data-testid="extract-flower-data"]');
    
    // 3. Ждем завершения процесса
    await expect(page.locator('[data-testid="extraction-progress"]')).toBeVisible();
    await expect(page.locator('[data-testid="extraction-complete"]')).toBeVisible({ 
      timeout: 30000 
    });
    
    // 4. Проверяем результаты
    await expect(page.locator('[data-testid="flower-results"]')).toBeVisible();
    
    // 5. Проверяем наличие данных о цветах
    const flowerData = await page.locator('[data-testid="flower-item"]').all();
    expect(flowerData.length).toBeGreaterThan(0);
    
    // 6. Проверяем конкретные цветы
    const flowerNames = await page.locator('[data-testid="flower-name"]').allTextContents();
    const expectedFlowers = ['роз', 'тюльпан', 'хризантем', 'гвоздик'];
    
    for (const expectedFlower of expectedFlowers) {
      const found = flowerNames.some(name => 
        name.toLowerCase().includes(expectedFlower)
      );
      expect(found).toBeTruthy();
    }
  });

  test('TC-007: Parquet Data Quality - File Validation', async ({ page }) => {
    // Проверяем качество данных в Parquet файлах
    
    // 1. Переходим к разделу Parquet данных
    await page.click('[data-testid="parquet-data-tab"]');
    
    // 2. Проверяем наличие критических таблиц
    const criticalTables = [
      '_DOCUMENTJOURNAL5354',
      '_DOCUMENTJOURNAL5287', 
      '_DOCUMENTJOURNAL5321',
      '_DOCUMENT138',
      '_DOCUMENT156'
    ];
    
    for (const table of criticalTables) {
      await expect(page.locator(`[data-testid="table-${table}"]`)).toBeVisible();
      
      // Проверяем, что таблица не пустая
      const rowCount = await page.locator(`[data-testid="table-${table}"] tbody tr`).count();
      expect(rowCount).toBeGreaterThan(0);
    }
    
    // 3. Проверяем наличие данных о цветах в таблицах
    await page.click('[data-testid="search-flowers"]');
    await page.fill('[data-testid="search-input"]', 'роз');
    await page.click('[data-testid="search-button"]');
    
    const searchResults = await page.locator('[data-testid="search-results"]').count();
    expect(searchResults).toBeGreaterThan(0);
  });

  test('TC-010: DuckDB Analytics - SQL Queries', async ({ page }) => {
    // Проверяем аналитические возможности DuckDB
    
    // 1. Переходим к разделу аналитики
    await page.click('[data-testid="analytics-tab"]');
    
    // 2. Проверяем наличие SQL интерфейса
    await expect(page.locator('[data-testid="sql-query-input"]')).toBeVisible();
    
    // 3. Выполняем тестовые SQL запросы
    const testQueries = [
      {
        query: "SELECT COUNT(*) FROM flowers WHERE name LIKE '%роз%'",
        expectedResult: "> 0"
      },
      {
        query: "SELECT COUNT(*) FROM stores WHERE has_flowers = true",
        expectedResult: "> 0"
      },
      {
        query: "SELECT COUNT(*) FROM sales WHERE date >= '2025-01-01'",
        expectedResult: "> 0"
      }
    ];
    
    for (const testQuery of testQueries) {
      await page.fill('[data-testid="sql-query-input"]', testQuery.query);
      await page.click('[data-testid="execute-query"]');
      
      // Ждем выполнения запроса
      await expect(page.locator('[data-testid="query-results"]')).toBeVisible();
      
      // Проверяем результат
      const result = await page.locator('[data-testid="query-result-count"]').textContent();
      expect(parseInt(result)).toBeGreaterThan(0);
    }
  });

  test('TC-011: Full Business Chain - End-to-End Validation', async ({ page }) => {
    // Проверяем полную цепочку цветочного бизнеса
    
    // 1. Проверяем закупки
    await page.click('[data-testid="purchases-tab"]');
    await expect(page.locator('[data-testid="purchase-list"]')).toBeVisible();
    
    const purchaseItems = await page.locator('[data-testid="purchase-item"]').count();
    expect(purchaseItems).toBeGreaterThan(0);
    
    // 2. Проверяем перемещения между магазинами
    await page.click('[data-testid="transfers-tab"]');
    await expect(page.locator('[data-testid="transfer-list"]')).toBeVisible();
    
    const transferItems = await page.locator('[data-testid="transfer-item"]').count();
    expect(transferItems).toBeGreaterThan(0);
    
    // 3. Проверяем продажи
    await page.click('[data-testid="sales-tab"]');
    await expect(page.locator('[data-testid="sales-list"]')).toBeVisible();
    
    const salesItems = await page.locator('[data-testid="sales-item"]').count();
    expect(salesItems).toBeGreaterThan(0);
    
    // 4. Проверяем остатки
    await page.click('[data-testid="inventory-tab"]');
    await expect(page.locator('[data-testid="inventory-list"]')).toBeVisible();
    
    const inventoryItems = await page.locator('[data-testid="inventory-item"]').count();
    expect(inventoryItems).toBeGreaterThan(0);
  });

  test('TC-012: Store Analysis - All Stores Validation', async ({ page }) => {
    // Проверяем анализ по всем магазинам
    
    // 1. Переходим к аналитике по магазинам
    await page.click('[data-testid="store-analysis-tab"]');
    
    // 2. Проверяем список всех магазинов
    await expect(page.locator('[data-testid="store-list"]')).toBeVisible();
    
    const stores = await page.locator('[data-testid="store-item"]').count();
    expect(stores).toBeGreaterThan(0);
    
    // 3. Проверяем данные по каждому магазину
    for (let i = 0; i < Math.min(stores, 5); i++) {
      await page.locator(`[data-testid="store-item"]:nth-child(${i + 1})`).click();
      
      // Проверяем наличие цветов в магазине
      await expect(page.locator('[data-testid="store-flowers"]')).toBeVisible();
      
      const flowerCount = await page.locator('[data-testid="store-flower-item"]').count();
      expect(flowerCount).toBeGreaterThan(0);
      
      // Проверяем продажи магазина
      await expect(page.locator('[data-testid="store-sales"]')).toBeVisible();
      
      const salesCount = await page.locator('[data-testid="store-sale-item"]').count();
      expect(salesCount).toBeGreaterThan(0);
    }
  });

  test('TC-013: Daily Analysis - Day-by-Day Validation', async ({ page }) => {
    // Проверяем анализ по дням
    
    // 1. Переходим к аналитике по дням
    await page.click('[data-testid="daily-analysis-tab"]');
    
    // 2. Выбираем период
    await page.fill('[data-testid="date-from"]', '2025-01-01');
    await page.fill('[data-testid="date-to"]', '2025-01-31');
    await page.click('[data-testid="apply-date-filter"]');
    
    // 3. Проверяем данные по дням
    await expect(page.locator('[data-testid="daily-data"]')).toBeVisible();
    
    const dailyItems = await page.locator('[data-testid="daily-item"]').count();
    expect(dailyItems).toBeGreaterThan(0);
    
    // 4. Проверяем наличие цветов каждый день
    for (let i = 0; i < Math.min(dailyItems, 5); i++) {
      await page.locator(`[data-testid="daily-item"]:nth-child(${i + 1})`).click();
      
      // Проверяем цветы в наличии
      await expect(page.locator('[data-testid="daily-flowers"]')).toBeVisible();
      
      const dailyFlowerCount = await page.locator('[data-testid="daily-flower-item"]').count();
      expect(dailyFlowerCount).toBeGreaterThan(0);
      
      // Проверяем продажи за день
      await expect(page.locator('[data-testid="daily-sales"]')).toBeVisible();
      
      const dailySalesCount = await page.locator('[data-testid="daily-sale-item"]').count();
      expect(dailySalesCount).toBeGreaterThan(0);
    }
  });

  test('Performance: Large Data Processing', async ({ page }) => {
    // Проверяем производительность обработки больших данных
    
    const startTime = Date.now();
    
    // 1. Запускаем обработку всех данных
    await page.click('[data-testid="process-all-data"]');
    
    // 2. Ждем завершения
    await expect(page.locator('[data-testid="processing-complete"]')).toBeVisible({ 
      timeout: 300000 // 5 минут
    });
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    // 3. Проверяем время обработки (должно быть < 30 минут)
    expect(processingTime).toBeLessThan(30 * 60 * 1000);
    
    // 4. Проверяем результаты
    await expect(page.locator('[data-testid="results-summary"]')).toBeVisible();
    
    const totalRecords = await page.locator('[data-testid="total-records"]').textContent();
    expect(parseInt(totalRecords)).toBeGreaterThan(0);
    
    console.log(`Processing time: ${processingTime / 1000}s`);
    console.log(`Total records: ${totalRecords}`);
  });
});
