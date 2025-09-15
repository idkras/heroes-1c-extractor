/**
 * Система комментариев и навигации по содержанию для стандарта диагностики
 * Позволяет добавлять комментарии к выделенному тексту и просматривать содержание документа
 */

// Глобальное хранилище комментариев и текущего состояния
let comments = [];
let currentHeading = null;
let tableOfContents = [];

// Инициализация систем комментариев и навигации
function initCommentsSystem() {
    // Создаем структуру боковой панели
    createSidebarStructure();
    
    // Загрузка существующих комментариев из localStorage
    loadCommentsFromStorage();
    
    // Генерируем содержание документа
    generateTableOfContents();
    
    // Отображение существующих комментариев
    renderComments();
    
    // Обработка выделения текста для добавления комментария
    setupTextSelectionHandler();
    
    // Настройка отслеживания прокрутки для обновления текущего заголовка
    setupScrollTracking();
}

// Создание структуры боковой панели
function createSidebarStructure() {
    // Находим контейнер для боковой панели
    const sidebarPanel = document.getElementById('sidebar-panel');
    if (!sidebarPanel) return;
    
    // Очищаем контейнер на случай повторной инициализации
    sidebarPanel.innerHTML = '';
    
    // Создаем контейнер для содержания с заголовком и возможностью скрытия
    const tocContainer = document.getElementById('toc-container');
    if (tocContainer) {
        // Создаем заголовок раздела содержания
        const tocHeader = document.createElement('div');
        tocHeader.className = 'toc-header';
        tocHeader.innerHTML = 'Содержание <span class="toc-toggle">скрыть ▼</span>';
        tocContainer.appendChild(tocHeader);
        
        // Создаем контейнер для содержимого оглавления
        const tocContent = document.createElement('div');
        tocContent.className = 'toc-content';
        tocContainer.appendChild(tocContent);
        
        // Обработчик переключения видимости оглавления
        const tocToggle = tocHeader.querySelector('.toc-toggle');
        tocToggle.addEventListener('click', function() {
            tocContent.classList.toggle('collapsed');
            this.textContent = tocContent.classList.contains('collapsed') ? 'показать ▶' : 'скрыть ▼';
        });
    }
    
    // Создаем разделитель между содержанием и комментариями
    const divider = document.createElement('div');
    divider.className = 'comments-divider';
    sidebarPanel.appendChild(divider);
    
    // Создаем контейнер для комментариев с заголовком
    const commentsContainer = document.getElementById('comments-container');
    if (commentsContainer) {
        // Создаем заголовок раздела комментариев
        const commentsHeader = document.createElement('div');
        commentsHeader.className = 'comments-header';
        commentsHeader.textContent = 'Комментарии';
        commentsContainer.appendChild(commentsHeader);
    }
}

// Генерация содержания документа
function generateTableOfContents() {
    const contentElement = document.getElementById('markdown-content');
    const tocContainer = document.getElementById('toc-container');
    if (!contentElement || !tocContainer) return;
    
    // Ищем контейнер для содержимого оглавления
    const tocContent = tocContainer.querySelector('.toc-content');
    if (!tocContent) return;
    
    // Очищаем контейнер и массив содержания
    tocContent.innerHTML = '';
    tableOfContents = [];
    
    // Находим все заголовки h2-h4
    const headings = contentElement.querySelectorAll('h2, h3, h4');
    
    // Создаем список для содержания
    const tocList = document.createElement('ul');
    
    // Добавляем заголовки в содержание
    headings.forEach((heading, index) => {
        // Создаем ID для заголовка, если его нет
        if (!heading.id) {
            heading.id = 'heading-' + index;
        }
        
        // Добавляем заголовок в массив содержания
        tableOfContents.push({
            id: heading.id,
            text: heading.textContent,
            level: parseInt(heading.tagName.substring(1))
        });
        
        // Создаем элемент списка
        const listItem = document.createElement('li');
        
        // Создаем ссылку
        const link = document.createElement('a');
        link.href = '#' + heading.id;
        link.textContent = heading.textContent;
        link.className = 'toc-level-' + heading.tagName.substring(1);
        
        // Обработчик клика по ссылке
        link.addEventListener('click', function(e) {
            e.preventDefault();
            heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
            // Добавляем хэш в URL без перезагрузки страницы
            history.pushState(null, null, '#' + heading.id);
        });
        
        listItem.appendChild(link);
        tocList.appendChild(listItem);
        
        // Добавляем атрибуты для доступности и SEO
        heading.setAttribute('tabindex', '0');
    });
    
    // Добавляем список в контейнер
    tocContent.appendChild(tocList);
}

// Отслеживание прокрутки для подсветки активного элемента в оглавлении
function setupScrollTracking() {
    window.addEventListener('scroll', function() {
        if (tableOfContents.length === 0) return;
        
        // Находим текущий заголовок
        let currentHeadingIndex = 0;
        const scrollPosition = window.scrollY;
        
        for (let i = 0; i < tableOfContents.length; i++) {
            const headingElement = document.getElementById(tableOfContents[i].id);
            if (headingElement && headingElement.offsetTop <= scrollPosition + 50) {
                currentHeadingIndex = i;
            } else {
                break;
            }
        }
        
        // Подсвечиваем активный элемент в содержании
        const tocContent = document.querySelector('.toc-content');
        if (tocContent) {
            // Убираем подсветку у всех ссылок
            const allLinks = tocContent.querySelectorAll('a');
            allLinks.forEach(link => link.classList.remove('active'));
            
            // Добавляем подсветку активной ссылке
            const activeHeadingId = tableOfContents[currentHeadingIndex].id;
            const activeLink = tocContent.querySelector(`a[href="#${activeHeadingId}"]`);
            if (activeLink) {
                activeLink.classList.add('active');
            }
        }
    });
}

// Обработка выделения текста для добавления комментария
function setupTextSelectionHandler() {
    const contentElement = document.getElementById('markdown-content');
    if (!contentElement) return;
    
    contentElement.addEventListener('mouseup', function() {
        const selection = window.getSelection();
        if (selection.toString().trim().length > 0) {
            // Получаем выделенный текст
            const selectedText = selection.toString().trim();
            
            // Подсвечиваем выделенный текст
            const range = selection.getRangeAt(0);
            const span = document.createElement('span');
            span.className = 'highlight-for-comment';
            range.surroundContents(span);
            
            // Показываем инлайн-форму для добавления комментария
            showInlineCommentForm(selectedText, span);
        }
    });
}

// Показать инлайн-форму для добавления комментария
function showInlineCommentForm(selectedText, highlightedSpan) {
    const commentsContainer = document.getElementById('comments-container');
    if (!commentsContainer) return;
    
    // Создаем временный комментарий с формой
    const commentElement = document.createElement('div');
    commentElement.className = 'comment-item';
    
    // Добавляем цитату выделенного текста
    const quote = document.createElement('div');
    quote.className = 'comment-quote';
    quote.textContent = selectedText.length > 100 
        ? selectedText.substring(0, 100) + '...' 
        : selectedText;
    commentElement.appendChild(quote);
    
    // Создаем инлайн-форму редактирования
    const form = document.createElement('div');
    form.className = 'comment-inline-form';
    
    // Добавляем текстовое поле для комментария
    const textarea = document.createElement('textarea');
    textarea.placeholder = 'Введите комментарий...';
    form.appendChild(textarea);
    
    // Обработчики автосохранения
    textarea.addEventListener('blur', function() {
        if (textarea.value.trim().length > 0) {
            // Сохраняем комментарий
            addComment(selectedText, textarea.value.trim(), highlightedSpan);
            commentElement.remove();
        } else {
            // Если комментарий пустой, удаляем выделение
            if (highlightedSpan && highlightedSpan.parentNode) {
                const text = document.createTextNode(highlightedSpan.textContent);
                highlightedSpan.parentNode.replaceChild(text, highlightedSpan);
            }
            commentElement.remove();
        }
    });
    
    commentElement.appendChild(form);
    
    // Добавляем элемент в начало контейнера
    commentsContainer.insertBefore(commentElement, commentsContainer.firstChild);
    
    // Фокусируемся на поле ввода
    textarea.focus();
}

// Добавление нового комментария
function addComment(quote, text) {
    const comment = {
        id: Date.now(),
        quote: quote,
        text: text,
        date: new Date().toISOString(),
        author: 'Вы'
    };
    
    // Добавляем комментарий в массив
    comments.push(comment);
    
    // Сохраняем в localStorage
    saveCommentsToStorage();
    
    // Обновляем отображение
    renderComments();
    
    // Выделяем текст, к которому относится комментарий
    highlightCommentedText(quote, comment.id);
}

// Выделение текста, к которому относится комментарий
function highlightCommentedText(quote, commentId) {
    const contentElement = document.getElementById('markdown-content');
    if (!contentElement) return;
    
    // Упрощенный подход к выделению - ищем текст и оборачиваем его
    const textNodes = getAllTextNodes(contentElement);
    
    for (const node of textNodes) {
        const nodeText = node.nodeValue;
        if (nodeText.includes(quote)) {
            // Создаем элемент для выделения
            const span = document.createElement('span');
            span.className = 'has-comment';
            span.dataset.commentId = commentId;
            span.title = 'Нажмите для просмотра комментария';
            span.textContent = quote;
            
            // Заменяем текстовый узел на элемент с выделением
            const beforeText = nodeText.substring(0, nodeText.indexOf(quote));
            const afterText = nodeText.substring(nodeText.indexOf(quote) + quote.length);
            
            const fragment = document.createDocumentFragment();
            if (beforeText) fragment.appendChild(document.createTextNode(beforeText));
            fragment.appendChild(span);
            if (afterText) fragment.appendChild(document.createTextNode(afterText));
            
            node.parentNode.replaceChild(fragment, node);
            
            // Добавляем обработчик клика для просмотра комментария
            span.addEventListener('click', function() {
                scrollToComment(commentId);
            });
            
            // Останавливаемся после первого найденного совпадения
            break;
        }
    }
}

// Получение всех текстовых узлов в элементе
function getAllTextNodes(element) {
    const textNodes = [];
    
    function getTextNodes(node) {
        if (node.nodeType === 3) { // Текстовый узел
            textNodes.push(node);
        } else if (node.nodeType === 1) { // Элемент
            for (let i = 0; i < node.childNodes.length; i++) {
                getTextNodes(node.childNodes[i]);
            }
        }
    }
    
    getTextNodes(element);
    return textNodes;
}

// Прокрутка к комментарию
function scrollToComment(commentId) {
    const commentElement = document.querySelector(`.comment-item[data-id="${commentId}"]`);
    if (commentElement) {
        commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        commentElement.classList.add('highlight');
        
        // Удаляем подсветку через некоторое время
        setTimeout(() => {
            commentElement.classList.remove('highlight');
        }, 2000);
    }
}

// Отображение комментариев
function renderComments() {
    const commentsContainer = document.getElementById('comments-container');
    if (!commentsContainer) return;
    
    // Очищаем контейнер
    commentsContainer.innerHTML = '';
    
    if (comments.length === 0) {
        // Если комментариев нет, показываем сообщение
        commentsContainer.innerHTML = '<p class="text-muted small">Выделите текст для добавления комментария</p>';
        return;
    }
    
    // Сортируем комментарии по дате (новые вверху)
    comments.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    // Добавляем каждый комментарий
    comments.forEach(comment => {
        const commentElement = document.createElement('div');
        commentElement.className = 'comment-item';
        commentElement.dataset.id = comment.id;
        
        // Цитата
        const quote = document.createElement('div');
        quote.className = 'comment-quote';
        quote.textContent = comment.quote.length > 100 
            ? comment.quote.substring(0, 100) + '...' 
            : comment.quote;
        commentElement.appendChild(quote);
        
        // Текст комментария
        const text = document.createElement('div');
        text.className = 'comment-text';
        text.textContent = comment.text;
        commentElement.appendChild(text);
        
        // Мета-информация
        const meta = document.createElement('div');
        meta.className = 'comment-meta';
        
        // Дата
        const date = document.createElement('span');
        date.textContent = formatDate(comment.date);
        meta.appendChild(date);
        
        // Действия
        const actions = document.createElement('div');
        actions.className = 'comment-actions';
        
        // Кнопка удаления
        const deleteButton = document.createElement('button');
        deleteButton.innerHTML = '<i class="bi bi-trash"></i>';
        deleteButton.title = 'Удалить комментарий';
        deleteButton.addEventListener('click', function() {
            removeComment(comment.id);
        });
        actions.appendChild(deleteButton);
        
        meta.appendChild(actions);
        commentElement.appendChild(meta);
        
        // Добавляем комментарий в контейнер
        commentsContainer.appendChild(commentElement);
    });
}

// Удаление комментария
function removeComment(commentId) {
    // Удаляем комментарий из массива
    comments = comments.filter(comment => comment.id !== commentId);
    
    // Сохраняем в localStorage
    saveCommentsToStorage();
    
    // Обновляем отображение
    renderComments();
    
    // Удаляем выделение в тексте
    const highlightedElement = document.querySelector(`.has-comment[data-comment-id="${commentId}"]`);
    if (highlightedElement) {
        const parent = highlightedElement.parentNode;
        const text = document.createTextNode(highlightedElement.textContent);
        parent.replaceChild(text, highlightedElement);
    }
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Сохранение комментариев в localStorage
function saveCommentsToStorage() {
    localStorage.setItem('diagnostics-comments', JSON.stringify(comments));
}

// Загрузка комментариев из localStorage
function loadCommentsFromStorage() {
    const savedComments = localStorage.getItem('diagnostics-comments');
    if (savedComments) {
        comments = JSON.parse(savedComments);
    }
}

// Настройка мобильной кнопки для комментариев
function setupMobileCommentsButton() {
    // Проверяем, есть ли мобильный вид
    if (window.innerWidth <= 992) {
        // Создаем кнопку для мобильного доступа к комментариям
        const button = document.createElement('button');
        button.id = 'comments-toggle';
        button.innerHTML = '<i class="bi bi-chat-text-fill"></i>';
        button.title = 'Показать комментарии';
        
        // Получаем панель комментариев
        const commentsPanel = document.getElementById('comments-panel');
        if (commentsPanel) {
            // Добавляем обработчик клика
            button.addEventListener('click', function() {
                if (commentsPanel.style.display === 'none' || !commentsPanel.style.display) {
                    commentsPanel.style.display = 'block';
                    button.innerHTML = '<i class="bi bi-x-lg"></i>';
                    button.title = 'Скрыть комментарии';
                } else {
                    commentsPanel.style.display = 'none';
                    button.innerHTML = '<i class="bi bi-chat-text-fill"></i>';
                    button.title = 'Показать комментарии';
                }
            });
            
            // Добавляем кнопку в body
            document.body.appendChild(button);
        }
    }
}