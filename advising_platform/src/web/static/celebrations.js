/**
 * Celebrations and Progress Tracking API Client
 * 
 * This module provides a client for interacting with the Advising Diagnostics
 * Progress Tracking API, allowing the display of achievements, milestones and
 * activity tracking.
 */

const CelebrationsAPI = {
    // API Configuration
    apiBaseUrl: 'http://localhost:5001/api',
    apiKey: 'advising-diagnostics', // Используйте реальный ключ в продакшене
    
    /**
     * Инициализирует систему отслеживания прогресса и достижений
     */
    init: function() {
        this.loadSystemStatus();
        this.setupEventListeners();
        
        // Инициализируем систему отслеживания действий
        this.actionsTracker.init();
    },
    
    /**
     * Настраивает обработчики событий
     */
    setupEventListeners: function() {
        // Обработчики для празднования достижений
        document.querySelectorAll('.celebrate-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const achievement = e.target.closest('.celebrate-btn').dataset.achievement;
                this.showCelebration(achievement);
            });
        });
        
        // Закрытие окна празднования
        const closeButton = document.getElementById('celebration-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                this.hideCelebration();
            });
        }
        
        // Система оценок
        document.querySelectorAll('#system-rating .star').forEach(star => {
            star.addEventListener('click', (e) => {
                const rating = parseInt(e.target.closest('.star').dataset.rating);
                this.submitRating('system', rating);
            });
        });
    },
    
    /**
     * Загружает текущий статус системы с сервера
     */
    loadSystemStatus: async function() {
        try {
            const response = await this.apiRequest('/progress');
            
            if (response) {
                // Обновляем интерфейс статистики
                this.updateStatistics(response);
                
                // Обновляем счетчики достижений
                this.updateAchievementsCounter(response.achievements);
                
                // Загружаем полный список достижений
                this.loadAchievements();
                
                // Загружаем активность
                this.loadActivity();
            }
        } catch (error) {
            console.error('Ошибка при загрузке статуса системы:', error);
        }
    },
    
    /**
     * Загружает список достижений с сервера
     */
    loadAchievements: async function() {
        try {
            const response = await this.apiRequest('/achievements');
            
            if (response && response.achievements) {
                this.updateAchievementsList(response.achievements);
            }
        } catch (error) {
            console.error('Ошибка при загрузке списка достижений:', error);
        }
    },
    
    /**
     * Загружает статистику активности с сервера
     */
    loadActivity: async function() {
        try {
            const response = await this.apiRequest('/activity?days=7');
            
            if (response && response.activity) {
                this.updateActivityStats(response.activity);
            }
        } catch (error) {
            console.error('Ошибка при загрузке активности:', error);
        }
    },
    
    /**
     * Отправляет оценку на сервер
     * @param {string} category - Категория оценки
     * @param {number} rating - Значение оценки (1-5)
     */
    submitRating: async function(category, rating) {
        try {
            const response = await this.apiRequest(`/track?action_type=rating&category=${category}&value=${rating}`);
            
            // Обновляем отображение звезд
            this.updateStarRating(rating, true);
            
            // Если оценка 5 звезд, запускаем конфетти
            if (rating === 5) {
                this.triggerConfetti();
            }
            
            console.log(`Система оценена на ${rating} звезд`);
        } catch (error) {
            console.error('Ошибка при отправке оценки:', error);
        }
    },
    
    /**
     * Обновляет отображение звездного рейтинга
     * @param {number} rating - Значение рейтинга (1-5)
     * @param {boolean} isClick - Был ли рейтинг установлен кликом
     */
    updateStarRating: function(rating, isClick) {
        document.querySelectorAll('#system-rating .star').forEach(star => {
            const starRating = parseInt(star.dataset.rating);
            
            if (starRating <= rating) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });
    },
    
    /**
     * Обновляет статистику системы на странице
     * @param {Object} data - Данные о статусе системы
     */
    updateStatistics: function(data) {
        // Обновляем счетчики
        this.animateCounter('standards-counter', 0, data.standards.total);
        this.animateCounter('validated-counter', 0, data.standards.valid);
        this.animateCounter('achievements-counter', 0, data.achievements.unlocked);
        
        // Обновляем прогресс-бары
        this.updateProgressBar('standards-progress', 'standards-progress-bar', 
                             data.standards.valid, data.standards.total);
        this.updateProgressBar('projects-progress', 'projects-progress-bar', 
                             data.projects.completed, data.projects.total);
        this.updateProgressBar('api-progress', 'api-progress-bar', 
                             data.api.implemented, data.api.total);
        
        // Обновляем круговой прогресс
        this.updateCircleProgress(data.system_progress);
    },
    
    /**
     * Обновляет счетчик достижений
     * @param {Object} achievementsData - Данные о достижениях
     */
    updateAchievementsCounter: function(achievementsData) {
        if (achievementsData) {
            const unlockedCount = achievementsData.unlocked || 0;
            this.animateCounter('achievements-counter', 0, unlockedCount);
        }
    },
    
    /**
     * Обновляет список достижений на странице
     * @param {Array} achievements - Список достижений
     */
    updateAchievementsList: function(achievements) {
        // Отсортировать достижения: сначала разблокированные, затем в процессе, затем заблокированные
        achievements.sort((a, b) => {
            if (a.unlocked && !b.unlocked) return -1;
            if (!a.unlocked && b.unlocked) return 1;
            if (a.progress > 0 && b.progress === 0) return -1;
            if (a.progress === 0 && b.progress > 0) return 1;
            return 0;
        });
        
        // Создать HTML для каждого достижения
        const milestonesContainer = document.querySelector('.progress-card .progress-body .row');
        if (!milestonesContainer) return;
        
        // Очищаем текущее содержимое
        milestonesContainer.innerHTML = '';
        
        // Добавляем достижения (максимум 6)
        achievements.slice(0, 6).forEach(achievement => {
            const percentage = Math.min(100, Math.round((achievement.progress / achievement.max_progress) * 100));
            const statusClass = achievement.unlocked ? 'active' : (achievement.progress > 0 ? '' : 'locked');
            const statusBadge = achievement.unlocked ? 
                               '<span class="badge badge-achievement milestone-badge">Выполнено</span>' : 
                               (achievement.progress > 0 ? 
                                `<span class="badge badge-progress milestone-badge">В процессе: ${percentage}%</span>` : 
                                '<span class="badge badge-locked milestone-badge">Заблокировано</span>');
            
            const milestoneHTML = `
                <div class="col-md-6">
                    <div class="milestone ${statusClass}" id="milestone-${achievement.id}">
                        <div class="milestone-header">
                            <div class="milestone-title">${achievement.name}</div>
                            ${statusBadge}
                        </div>
                        <div class="milestone-description">${achievement.description}</div>
                        <div class="progress milestone-progress">
                            <div class="progress-bar ${achievement.unlocked ? 'bg-success' : (achievement.progress > 0 ? 'bg-warning' : 'bg-secondary')}" 
                                 role="progressbar" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                </div>
            `;
            
            milestonesContainer.insertAdjacentHTML('beforeend', milestoneHTML);
        });
        
        // Обновляем обработчики событий для новых элементов
        this.setupEventListeners();
    },
    
    /**
     * Обновляет статистику активности на странице
     * @param {Array} activityData - Данные о активности
     */
    updateActivityStats: function(activityData) {
        // Суммируем статистику за последние дни
        const totalStats = {
            standards_created: 0,
            standards_validated: 0,
            standards_archived: 0
        };
        
        activityData.forEach(day => {
            totalStats.standards_created += day.standards_created || 0;
            totalStats.standards_validated += day.standards_validated || 0;
            totalStats.standards_archived += day.standards_archived || 0;
        });
        
        // Обновляем отображение счетчиков
        const standardsCounter = document.querySelector('.flip-counter:nth-child(1) .flip-number-value');
        const validatedCounter = document.querySelector('.flip-counter:nth-child(2) .flip-number-value');
        const archivedCounter = document.querySelector('.flip-counter:nth-child(3) .flip-number-value');
        
        if (standardsCounter) standardsCounter.textContent = totalStats.standards_created;
        if (validatedCounter) validatedCounter.textContent = totalStats.standards_validated;
        if (archivedCounter) archivedCounter.textContent = totalStats.standards_archived;
    },
    
    /**
     * Показывает окно празднования достижения
     * @param {string} achievement - ID достижения
     */
    showCelebration: function(achievement) {
        const overlay = document.getElementById('celebration-overlay');
        const title = document.getElementById('celebration-title');
        const description = document.getElementById('celebration-description');
        const reward = document.getElementById('celebration-reward');
        
        if (!overlay || !title || !description || !reward) return;
        
        // Настраиваем содержимое в зависимости от достижения
        if (achievement === 'founder') {
            title.textContent = 'Основатель системы!';
            description.textContent = 'Вы успешно создали первый стандарт и заложили фундамент системы.';
            reward.textContent = '+500 очков опыта';
        } else if (achievement === 'architect') {
            title.textContent = 'Архитектор процессов!';
            description.textContent = 'Вы успешно структурировали и систематизировали процессы.';
            reward.textContent = '+750 очков опыта';
        }
        
        // Показываем overlay
        overlay.classList.add('show');
        
        // Запускаем эффект конфетти
        this.triggerConfetti();
    },
    
    /**
     * Скрывает окно празднования
     */
    hideCelebration: function() {
        const overlay = document.getElementById('celebration-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    },
    
    /**
     * Запускает эффект конфетти
     */
    triggerConfetti: function() {
        if (typeof confetti !== 'function') return;
        
        confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 }
        });
        
        // Дополнительные конфетти с разной задержкой для эффекта
        setTimeout(() => {
            confetti({
                particleCount: 50,
                angle: 60,
                spread: 55,
                origin: { x: 0 }
            });
        }, 250);
        
        setTimeout(() => {
            confetti({
                particleCount: 50,
                angle: 120,
                spread: 55,
                origin: { x: 1 }
            });
        }, 400);
    },
    
    /**
     * Анимирует счетчик от начального до конечного значения
     * @param {string} elementId - ID элемента с счетчиком
     * @param {number} start - Начальное значение
     * @param {number} end - Конечное значение
     * @param {number} duration - Продолжительность анимации в мс
     * @param {string} suffix - Суффикс для добавления к значению (например, '%')
     */
    animateCounter: function(elementId, start, end, duration = 1500, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        let current = start;
        const increment = (end - start) / (duration / 16);
        const timer = setInterval(() => {
            current += increment;
            
            if (current >= end) {
                clearInterval(timer);
                current = end;
            }
            
            element.textContent = Math.round(current).toLocaleString() + suffix;
        }, 16);
    },
    
    /**
     * Обновляет прогресс-бар
     * @param {string} textElementId - ID элемента с текстом прогресса
     * @param {string} barElementId - ID элемента прогресс-бара
     * @param {number} value - Текущее значение
     * @param {number} total - Максимальное значение
     */
    updateProgressBar: function(textElementId, barElementId, value, total) {
        const textElement = document.getElementById(textElementId);
        const barElement = document.getElementById(barElementId);
        
        if (!textElement || !barElement) return;
        
        const percentage = (value / total) * 100;
        
        textElement.textContent = `${value}/${total}`;
        barElement.style.width = `${percentage}%`;
    },
    
    /**
     * Обновляет круговой прогресс-бар
     * @param {number} percentage - Процент выполнения
     */
    updateCircleProgress: function(percentage) {
        const circle = document.getElementById('progress-circle-value');
        const percentageText = document.getElementById('progress-percentage');
        
        if (!circle || !percentageText) return;
        
        const radius = circle.getAttribute('r');
        const circumference = 2 * Math.PI * radius;
        
        // Анимируем текст процента
        this.animateCounter('progress-percentage', 0, percentage, 1500, '%');
        
        // Анимируем круговой прогресс-бар
        let currentPercentage = 0;
        const increment = percentage / (1500 / 16);
        
        const timer = setInterval(() => {
            currentPercentage += increment;
            
            if (currentPercentage >= percentage) {
                clearInterval(timer);
                currentPercentage = percentage;
            }
            
            const dashoffset = circumference - (circumference * currentPercentage) / 100;
            circle.style.strokeDasharray = `${circumference} ${circumference}`;
            circle.style.strokeDashoffset = dashoffset;
        }, 16);
    },
    
    /**
     * Отправляет запрос к API
     * @param {string} endpoint - Эндпоинт API
     * @param {Object} options - Опции запроса
     * @returns {Promise<Object>} - Ответ от API
     */
    apiRequest: async function(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json'
            }
        };
        
        const url = `${this.apiBaseUrl}${endpoint}`;
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            return null;
        }
    },
    
    /**
     * Система отслеживания действий пользователя и автоматического обновления прогресса
     */
    actionsTracker: {
        // Конфигурация отслеживания действий
        trackedActions: {
            standards: {
                create: { selector: '.create-standard-btn', type: 'click' },
                edit: { selector: '.edit-standard-btn', type: 'click' },
                validate: { selector: '.validate-standard-btn', type: 'click' },
                archive: { selector: '.archive-btn', type: 'click' }
            },
            projects: {
                create: { selector: '.create-project-btn', type: 'click' },
                complete: { selector: '.complete-project-btn', type: 'click' }
            },
            api: {
                call: { selector: 'a[href*="/api/"]', type: 'click' }
            },
            git: {
                sync: { selector: '.git-sync-btn', type: 'click' }
            }
        },
        
        /**
         * Инициализирует систему отслеживания действий
         */
        init: function() {
            this.setupActionTrackers();
            this.setupMutationObserver();
        },
        
        /**
         * Настраивает обработчики для отслеживания действий
         */
        setupActionTrackers: function() {
            const self = this;
            
            // Для каждой категории действий
            Object.entries(this.trackedActions).forEach(([actionType, actions]) => {
                // Для каждого действия в категории
                Object.entries(actions).forEach(([action, config]) => {
                    // Находим элементы на странице
                    document.querySelectorAll(config.selector).forEach(element => {
                        // Добавляем обработчик события
                        element.addEventListener(config.type, async function(e) {
                            // Отслеживаем действие через API
                            await self.trackAction(actionType, action, element.dataset);
                        });
                    });
                });
            });
        },
        
        /**
         * Настраивает MutationObserver для отслеживания изменений DOM
         * и добавления обработчиков к новым элементам
         */
        setupMutationObserver: function() {
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.addedNodes.length) {
                        // При добавлении новых элементов в DOM проверяем их
                        // и добавляем обработчики, если нужно
                        this.setupActionTrackers();
                    }
                });
            });
            
            // Настраиваем наблюдение за всем документом
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        },
        
        /**
         * Отслеживает действие пользователя через API
         * @param {string} actionType - Тип действия (standards, projects, api, git)
         * @param {string} action - Конкретное действие (create, edit, validate и т.д.)
         * @param {Object} data - Дополнительные данные о действии
         */
        trackAction: async function(actionType, action, data = {}) {
            try {
                // Формируем запрос к API для отслеживания действия
                const queryParams = new URLSearchParams({
                    action_type: actionType,
                    action: action
                });
                
                // Добавляем дополнительные параметры из data
                Object.entries(data).forEach(([key, value]) => {
                    queryParams.append(key, value);
                });
                
                // Отправляем запрос на отслеживание действия
                const response = await CelebrationsAPI.apiRequest(`/track?${queryParams.toString()}`);
                
                // Если получены новые достижения, показываем их
                if (response && response.achievements && response.achievements.length > 0) {
                    // Получаем первое достижение из списка
                    const achievement = response.achievements[0];
                    
                    // Отображаем празднование
                    CelebrationsAPI.showCelebration(achievement.id);
                    
                    // Обновляем интерфейс
                    CelebrationsAPI.loadSystemStatus();
                }
                
                console.log(`Действие отслежено: ${actionType}.${action}`, response);
            } catch (error) {
                console.error('Ошибка при отслеживании действия:', error);
            }
        }
    }
};

// Инициализируем систему после загрузки страницы
document.addEventListener('DOMContentLoaded', function() {
    CelebrationsAPI.init();
});