/**
 * Скрипт для создания туннеля для доступа к локальному серверу извне
 * Использует библиотеку localtunnel
 * 
 * Туннель создается для порта 5000 (diagnostics viewer)
 */

const localtunnel = require('localtunnel');
const fs = require('fs');
const http = require('http');
const path = require('path');

// Название поддомена
const SUBDOMAIN = 'diagnostics-viewer';
const PORT = 5000;

(async () => {
  try {
    // Создаем туннель
    const tunnel = await localtunnel({ port: PORT, subdomain: SUBDOMAIN });
    
    console.log('========================================================================');
    console.log('🚀 Публичный URL создан! ');
    console.log('📱 Для мобильного тестирования используйте:');
    console.log(`   ${tunnel.url}`);
    console.log('💻 Локальный URL:');
    console.log(`   http://localhost:${PORT}`);
    console.log('⚠️ Туннель будет работать, пока этот скрипт запущен.');
    console.log('   Нажмите Ctrl+C для завершения.');
    console.log('========================================================================');
    
    // Проверяем доступность туннеля
    console.log('🔍 Проверка доступности туннеля...');
    
    // Читаем index.html и обновляем ссылки, если нужно
    try {
      const indexPath = path.join(__dirname, 'index.html');
      if (fs.existsSync(indexPath)) {
        let indexContent = fs.readFileSync(indexPath, 'utf8');
        const linkPattern = /https:\/\/[^"]+\.loca\.lt/g;
        const hasExternalLinks = linkPattern.test(indexContent);
        
        if (hasExternalLinks) {
          indexContent = indexContent.replace(linkPattern, tunnel.url);
          fs.writeFileSync(indexPath, indexContent);
          console.log(`Ссылка в index.html обновлена: ${linkPattern} -> ${tunnel.url}`);
        } else {
          console.log('Ссылки в index.html не требуют обновления');
        }
      }
    } catch (err) {
      console.error('Ошибка при обновлении ссылок в index.html:', err);
    }
    
    // Проверка, не требует ли туннель авторизации
    console.log('🔍 Проверка доступности туннеля и отсутствия запроса пароля...');
    console.log(`🔍 Проверка доступности URL: ${tunnel.url}`);
    
    http.get(tunnel.url, (res) => {
      if (res.statusCode === 200) {
        console.log('✅ URL доступен и не требует пароля');
      } else {
        console.log(`⚠️ URL вернул статус ${res.statusCode}`);
      }
    }).on('error', (err) => {
      console.error('❌ Ошибка при проверке URL:', err.message);
    });
    
    // Обработка закрытия туннеля
    tunnel.on('close', () => {
      console.log('Туннель закрыт');
      process.exit(0);
    });
  } catch (error) {
    console.error('Ошибка при создании туннеля:', error.message);
    process.exit(1);
  }
})();