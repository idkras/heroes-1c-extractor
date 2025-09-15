/**
 * Скрипт для обработки Medium-style документов с комментариями на полях
 * Автор: AI Assistant
 * Дата: 20 мая 2025
 */

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация обработчиков для комментариев
    initializeComments();
    
    // Инициализация модального окна комментариев
    initializeCommentModal();
    
    // Обработчики для кнопок действий
    initializeActionButtons();
    
    // Преобразование предлогов и союзов в неразрывные пробелы
    addNonBreakingSpaces();
});

/**
 * Инициализирует обработчики для комментариев
 */
function initializeComments() {
    const comments = document.querySelectorAll('.comment');
    const paragraphs = document.querySelectorAll('.main-content p');
    
    // Устанавливаем связи между параграфами и комментариями
    comments.forEach(comment => {
        const paragraphId = comment.dataset.paragraphId;
        if (paragraphId) {
            const relatedParagraph = document.getElementById(paragraphId);
            if (relatedParagraph) {
                relatedParagraph.classList.add('has-comment');
                
                // Добавляем обработчик для подсветки комментария при наведении на параграф
                relatedParagraph.addEventListener('mouseover', () => {
                    comment.classList.add('active');
                    relatedParagraph.classList.add('active-comment');
                });
                
                relatedParagraph.addEventListener('mouseout', () => {
                    comment.classList.remove('active');
                    relatedParagraph.classList.remove('active-comment');
                });
                
                // Добавляем обработчик для подсветки параграфа при наведении на комментарий
                comment.addEventListener('mouseover', () => {
                    relatedParagraph.classList.add('active-comment');
                    comment.classList.add('active');
                });
                
                comment.addEventListener('mouseout', () => {
                    relatedParagraph.classList.remove('active-comment');
                    comment.classList.remove('active');
                });
            }
        }
    });
    
    // Создаем уникальные ID для параграфов, у которых их нет
    paragraphs.forEach((paragraph, index) => {
        if (!paragraph.id) {
            paragraph.id = `paragraph-${index}`;
        }
        
        // Добавляем обработчик для выбора параграфа для комментирования
        paragraph.addEventListener('click', () => {
            showCommentModal(paragraph.id);
        });
    });
}

/**
 * Инициализирует модальное окно для добавления комментариев
 */
function initializeCommentModal() {
    const modal = document.querySelector('.comment-form-modal');
    const cancelButton = modal.querySelector('.cancel-button');
    const form = modal.querySelector('#comment-form');
    
    // Закрытие модального окна при нажатии кнопки "Отмена"
    cancelButton.addEventListener('click', () => {
        modal.classList.add('hidden');
    });
    
    // Закрытие модального окна при клике вне его содержимого
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
    
    // Обработка отправки формы
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const paragraphId = form.querySelector('#paragraph-id-input').value;
        const author = form.querySelector('#comment-author').value;
        const text = form.querySelector('#comment-text').value;
        
        // Создаем новый комментарий
        addNewComment(paragraphId, author, text);
        
        // Сбрасываем форму и скрываем модальное окно
        form.reset();
        modal.classList.add('hidden');
        
        // Сохраняем комментарий на сервере
        saveComment(paragraphId, author, text);
    });
}

/**
 * Показывает модальное окно для добавления комментария к выбранному параграфу
 * @param {string} paragraphId - ID параграфа
 */
function showCommentModal(paragraphId) {
    const modal = document.querySelector('.comment-form-modal');
    const paragraphIdInput = modal.querySelector('#paragraph-id-input');
    
    paragraphIdInput.value = paragraphId;
    modal.classList.remove('hidden');
    
    // Устанавливаем фокус на поле ввода автора
    modal.querySelector('#comment-author').focus();
}

/**
 * Добавляет новый комментарий к параграфу
 * @param {string} paragraphId - ID параграфа
 * @param {string} author - Автор комментария
 * @param {string} text - Текст комментария
 */
function addNewComment(paragraphId, author, text) {
    const commentsContainer = document.querySelector('.side-comments');
    const paragraph = document.getElementById(paragraphId);
    
    // Если параграф не найден, прерываем выполнение
    if (!paragraph) return;
    
    // Добавляем класс комментария к параграфу
    paragraph.classList.add('has-comment');
    
    // Создаем элемент комментария
    const commentElement = document.createElement('div');
    commentElement.className = 'comment';
    commentElement.dataset.paragraphId = paragraphId;
    
    // Создаем текущую дату
    const now = new Date();
    const formattedDate = now.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
    });
    
    // Заполняем HTML комментария
    commentElement.innerHTML = `
        <div class="comment-header">
            <span class="comment-author">${author}</span>
            <span class="comment-date">${formattedDate}</span>
        </div>
        <div class="comment-body">
            ${text}
        </div>
    `;
    
    // Добавляем обработчики для подсветки
    commentElement.addEventListener('mouseover', () => {
        paragraph.classList.add('active-comment');
        commentElement.classList.add('active');
    });
    
    commentElement.addEventListener('mouseout', () => {
        paragraph.classList.remove('active-comment');
        commentElement.classList.remove('active');
    });
    
    // Добавляем комментарий в контейнер
    commentsContainer.appendChild(commentElement);
    
    // Добавляем обработчики для параграфа
    paragraph.addEventListener('mouseover', () => {
        commentElement.classList.add('active');
        paragraph.classList.add('active-comment');
    });
    
    paragraph.addEventListener('mouseout', () => {
        commentElement.classList.remove('active');
        paragraph.classList.remove('active-comment');
    });
}

/**
 * Сохраняет комментарий на сервере
 * @param {string} paragraphId - ID параграфа
 * @param {string} author - Автор комментария
 * @param {string} text - Текст комментария
 */
function saveComment(paragraphId, author, text) {
    const documentPath = document.querySelector('.action-button.edit-button').dataset.documentPath;
    
    // Создаем объект с данными комментария
    const commentData = {
        document_path: documentPath,
        paragraph_id: paragraphId,
        author: author,
        text: text,
        date: new Date().toISOString()
    };
    
    // Отправляем запрос на сервер
    fetch('/api/comments/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(commentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Комментарий успешно сохранен');
        } else {
            console.error('Ошибка при сохранении комментария:', data.error);
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке запроса:', error);
    });
}

/**
 * Инициализирует обработчики для кнопок действий
 */
function initializeActionButtons() {
    const editButton = document.querySelector('.action-button.edit-button');
    const archiveButton = document.querySelector('.action-button.archive-button');
    const addCommentButton = document.querySelector('.action-button.add-comment-button');
    
    if (editButton) {
        editButton.addEventListener('click', () => {
            const documentPath = editButton.dataset.documentPath;
            window.location.href = `/edit?path=${encodeURIComponent(documentPath)}`;
        });
    }
    
    if (archiveButton) {
        archiveButton.addEventListener('click', () => {
            const documentPath = archiveButton.dataset.documentPath;
            
            if (confirm('Вы уверены, что хотите архивировать этот документ?')) {
                // Отправляем запрос на архивацию
                fetch('/api/documents/archive', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ document_path: documentPath })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Документ успешно архивирован');
                        window.location.href = '/documents';
                    } else {
                        alert(`Ошибка при архивации документа: ${data.error}`);
                    }
                })
                .catch(error => {
                    console.error('Ошибка при отправке запроса:', error);
                    alert('Произошла ошибка при архивации документа');
                });
            }
        });
    }
    
    if (addCommentButton) {
        addCommentButton.addEventListener('click', () => {
            // Выбираем первый параграф для комментирования
            const firstParagraph = document.querySelector('.main-content p');
            if (firstParagraph) {
                showCommentModal(firstParagraph.id);
            }
        });
    }
}

/**
 * Заменяет предлоги и союзы на неразрывные пробелы
 */
function addNonBreakingSpaces() {
    const contentElements = document.querySelectorAll('.main-content p, .main-content li, .main-content h1, .main-content h2, .main-content h3, .main-content h4');
    
    // Список предлогов и союзов для замены на неразрывные пробелы
    const prepositionsAndConjunctions = [
        ' в ', ' без ', ' до ', ' для ', ' за ', ' из ', ' к ', ' на ', ' над ',
        ' о ', ' об ', ' от ', ' по ', ' под ', ' при ', ' про ', ' с ', ' у ',
        ' а ', ' и ', ' но ', ' или ', ' ни ', ' как ', ' что ', ' если '
    ];
    
    contentElements.forEach(element => {
        let content = element.innerHTML;
        
        // Заменяем обычные пробелы на неразрывные
        prepositionsAndConjunctions.forEach(word => {
            const regexp = new RegExp(word, 'g');
            content = content.replace(regexp, word.replace(' ', '&nbsp;').replace(' ', '&nbsp;'));
        });
        
        element.innerHTML = content;
    });
}

/**
 * Проверяет синхронизацию документа с кешем
 */
function checkDocumentSync() {
    const documentPath = document.querySelector('.action-button.edit-button').dataset.documentPath;
    
    fetch(`/api/documents/check-sync?path=${encodeURIComponent(documentPath)}`)
        .then(response => response.json())
        .then(data => {
            const syncStatus = document.querySelector('.sync-status');
            const syncIcon = document.querySelector('.sync-icon');
            const syncMessage = document.querySelector('.sync-message');
            
            if (data.success) {
                syncStatus.className = 'sync-status sync-status-success';
                syncIcon.innerHTML = '✓';
                syncMessage.textContent = 'Документ синхронизирован с кешем';
            } else {
                syncStatus.className = 'sync-status sync-status-error';
                syncIcon.innerHTML = '⚠️';
                syncMessage.textContent = data.error || 'Ошибка синхронизации';
            }
        })
        .catch(error => {
            console.error('Ошибка при проверке синхронизации:', error);
        });
}

// Запускаем проверку синхронизации при загрузке документа
document.addEventListener('DOMContentLoaded', function() {
    checkDocumentSync();
});