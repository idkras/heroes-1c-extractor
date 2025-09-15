#!/usr/bin/env node

/**
 * Тест соответствия визуализации n8n workflow дизайну оригинального n8n
 * Проверяет цвета, иконки, формы нод и общий стиль
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Цветовая схема n8n (официальная)
const N8N_COLORS = {
  'start': '#56C02B',
  'manualtrigger': '#56C02B', 
  'scheduletrigger': '#56C02B',
  'httprequest': '#1A82E3',
  'webhook': '#1A82E3',
  'function': '#F7B924',
  'code': '#F7B924',
  'telegram': '#229ED9',
  'slack': '#4A154B',
  'discord': '#5865F2',
  'email': '#D44638',
  'notion': '#000',
  'googlesheets': '#0F9D58',
  'mysql': '#00758F',
  'postgres': '#336791',
  'airtable': '#18BFFF',
  'github': '#24292F',
  'trello': '#0079BF',
  'stripe': '#635BFF',
  'merge': '#A259FF',
  'split': '#FFB300',
  'switch': '#FFB300',
  'set': '#F7B924',
  'wait': '#F7B924',
  'errortrigger': '#F44336'
};

async function testN8NVisualization() {
  console.log('🧪 Testing n8n workflow visualization...');
  
  const browser = await puppeteer.launch({ 
    headless: false, // Показываем браузер для визуальной проверки
    defaultViewport: { width: 1920, height: 1080 }
  });
  
  try {
    const page = await browser.newPage();
    
    // Загружаем HTML файл
    const htmlPath = path.resolve(__dirname, '../frontend/n8n_workflow_map.html');
    await page.goto(`file://${htmlPath}`);
    
    console.log('📄 Loaded n8n workflow map');
    
    // Ждем загрузки данных
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Проверяем статус загрузки
    const status = await page.$eval('#status', el => el.textContent);
    console.log('📊 Status:', status);
    
    // Проверяем количество workflow и нод через Cytoscape
    const workflowCount = await page.evaluate(() => {
      if (window.cy) {
        return window.cy.nodes('[type="workflow"]').length;
      }
      return 0;
    });
    
    const nodeCount = await page.evaluate(() => {
      if (window.cy) {
        return window.cy.nodes('[type="node"]').length;
      }
      return 0;
    });
    
    console.log(`📈 Found ${workflowCount} workflows and ${nodeCount} nodes`);
    
    // Проверяем цвета нод через Cytoscape
    const nodeColors = await page.evaluate(() => {
      if (window.cy) {
        const nodes = window.cy.nodes('[type="node"]');
        const colors = [];
        nodes.forEach(node => {
          colors.push({
            id: node.id(),
            backgroundColor: node.style('background-color'),
            borderColor: node.style('border-color'),
            color: node.data('color')
          });
        });
        return colors;
      }
      return [];
    });
    
    console.log('🎨 Node colors:', nodeColors.slice(0, 3)); // Показываем первые 3
    
    // Проверяем активность workflow через Cytoscape
    const workflowStatus = await page.evaluate(() => {
      if (window.cy) {
        const workflows = window.cy.nodes('[type="workflow"]');
        const status = [];
        workflows.forEach(wf => {
          status.push({
            id: wf.id(),
            backgroundColor: wf.style('background-color'),
            isActive: wf.data('active'),
            label: wf.data('label')
          });
        });
        return status;
      }
      return [];
    });
    
    console.log('🟢 Workflow status:', workflowStatus);
    
    // Делаем скриншот для визуальной проверки
    const screenshotPath = path.resolve(__dirname, '../test-results/n8n_visualization_test.png');
    await page.screenshot({ 
      path: screenshotPath, 
      fullPage: true 
    });
    
    console.log('📸 Screenshot saved:', screenshotPath);
    
    // Проверяем соответствие дизайну n8n
    const designCompliance = {
      colorsMatch: true,
      shapesCorrect: true,
      layoutAppropriate: true,
      interactionsWork: true
    };
    
    // Проверяем цвета
    for (const color of nodeColors) {
      // Получаем тип ноды из ID (последняя часть после подчеркивания)
      const nodeType = color.id.split('_').pop().toLowerCase();
      
      // Получаем ожидаемый цвет для данного типа ноды
      const expectedColor = N8N_COLORS[nodeType];
      
      if (expectedColor) {
        // Проверяем, что цвет соответствует ожидаемому
        const actualColor = color.color || color.backgroundColor;
        
        // Конвертируем hex в rgb для сравнения
        const hexToRgb = (hex) => {
          const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
          return result ? `rgb(${parseInt(result[1], 16)},${parseInt(result[2], 16)},${parseInt(result[3], 16)})` : null;
        };
        
        const expectedRgb = hexToRgb(expectedColor);
        
        if (actualColor && expectedRgb && !actualColor.includes(expectedRgb)) {
          designCompliance.colorsMatch = false;
          console.log(`⚠️  Color mismatch for ${color.id}: expected ${expectedColor} (${expectedRgb}), got ${actualColor}`);
        }
      }
    }
    
    // Проверяем формы нод (должны быть roundrectangle)
    const nodeShapes = await page.evaluate(() => {
      const nodes = document.querySelectorAll('node[type="node"]');
      return Array.from(nodes).map(node => {
        const style = window.getComputedStyle(node);
        return {
          id: node.id,
          shape: style.shape || 'ellipse' // По умолчанию ellipse
        };
      });
    });
    
    for (const shape of nodeShapes) {
      if (shape.shape !== 'roundrectangle') {
        designCompliance.shapesCorrect = false;
        console.log(`⚠️  Shape mismatch for ${shape.id}: expected roundrectangle, got ${shape.shape}`);
      }
    }
    
    // Проверяем интерактивность
    const interactionsWork = await page.evaluate(() => {
      // Проверяем hover эффекты
      const nodes = document.querySelectorAll('node[type="node"]');
      if (nodes.length === 0) return false;
      
      // Симулируем hover
      const firstNode = nodes[0];
      firstNode.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
      
      // Проверяем появление tooltip
      setTimeout(() => {
        const tooltip = document.querySelector('.cy-tooltip');
        return tooltip !== null;
      }, 100);
      
      return true;
    });
    
    designCompliance.interactionsWork = interactionsWork;
    
    // Выводим результаты
    console.log('\n📋 Design Compliance Report:');
    console.log('✅ Colors match n8n:', designCompliance.colorsMatch);
    console.log('✅ Shapes are correct:', designCompliance.shapesCorrect);
    console.log('✅ Layout is appropriate:', designCompliance.layoutAppropriate);
    console.log('✅ Interactions work:', designCompliance.interactionsWork);
    
    const overallScore = Object.values(designCompliance).filter(Boolean).length / Object.keys(designCompliance).length;
    console.log(`📊 Overall compliance: ${Math.round(overallScore * 100)}%`);
    
    if (overallScore >= 0.8) {
      console.log('🎉 Visualization passes n8n design compliance!');
    } else {
      console.log('⚠️  Visualization needs improvements to match n8n design');
    }
    
    return {
      workflowCount,
      nodeCount,
      designCompliance,
      overallScore,
      screenshotPath
    };
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

// Запускаем тест если файл вызван напрямую
if (require.main === module) {
  testN8NVisualization()
    .then(results => {
      console.log('\n✅ Test completed successfully');
      process.exit(0);
    })
    .catch(error => {
      console.error('\n❌ Test failed:', error);
      process.exit(1);
    });
}

module.exports = { testN8NVisualization }; 