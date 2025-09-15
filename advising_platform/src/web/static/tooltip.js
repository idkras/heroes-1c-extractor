/**
 * Contextual Help Tooltip System
 * 
 * This script adds interactive tooltips to the diagnostic document,
 * providing context, definitions, and examples for metrics and terms.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Metrics glossary - contains definitions for all metrics used in the document
    const metricsGlossary = {
        'acq costs': 'Затраты на привлечение (acquisition costs) - все расходы на маркетинг и рекламу.',
        'users': 'Пользователи - количество людей, зарегистрировавшихся в сервисе.',
        'c1': 'Конверсия из регистрации в первое целевое действие. Диапазон: 0-100%',
        'buyers': 'Плательщики - пользователи, совершившие хотя бы одну покупку.',
        'payments': 'Платежи - количество успешных транзакций.',
        'revenue': 'Выручка - общий доход без учета возвратов и комиссий.',
        'gross profit': 'Валовая прибыль = выручка - прямые расходы на производство/доставку.',
        'profit net': 'Чистая прибыль после вычета всех расходов и налогов.',
        'ebitda': 'Прибыль до вычета процентов, налогов и амортизации.',
        'cac': 'Customer Acquisition Cost - стоимость привлечения одного клиента.',
        'ltv': 'Lifetime Value - пожизненная ценность клиента, сумма прибыли от всех покупок.',
        'ampu': 'Average Monthly Payment per User - средний ежемесячный платеж на пользователя.',
        'amppu': 'Average Monthly Payment per Paying User - средний платеж на платящего пользователя.',
        'c2m': 'Конверсия из первой в повторную покупку в течение месяца.',
        'c3m': 'Конверсия из второй в третью покупку в течение месяца.',
        'cpuser': 'Cost Per User - стоимость привлечения одного пользователя (регистрации).',
        'av payment count': 'Среднее количество платежей на одного платящего пользователя.',
        'margin': 'Маржинальность - процент прибыли от выручки.'
    };

    // Formula glossary - contains key formulas used in the document
    const formulaGlossary = {
        'cac': 'CAC = общие затраты на маркетинг / количество новых клиентов',
        'ampu': 'AMPU = AMPPU × C1',
        'gross profit': 'Gross Profit = Revenue - COGS (стоимость проданных товаров)',
        'av payment count': 'Av. Payment Count = 1 + C2m + C2m × C3m + ...',
        'ltv': 'LTV = AMPPU × Av. Payment Count × Margin',
        'cac': 'CAC = CPUser / C1'
    };

    // Terms glossary - contains definitions for special terms
    const termsGlossary = {
        'когортный анализ': 'Метод анализа, группирующий пользователей по времени регистрации или первой покупки.',
        'rick.ai': 'Аналитическая платформа для сбора и анализа метрик бизнеса.',
        'unit-экономика': 'Экономика отдельной единицы продукта или клиента.',
        'стейкхолдеры': 'Заинтересованные лица, влияющие на проект или компанию.',
        'jtbd': 'Jobs To Be Done - методология, сфокусированная на задачах, которые пользователь пытается решить.',
        'gtd': 'Getting Things Done - методология управления задачами и проектами.',
        'definition of done': 'Четкие критерии завершенности задачи или проекта.',
        'executive summary': 'Краткое изложение ключевых выводов и рекомендаций отчета.'
    };

    // Create tooltip container
    const tooltipContainer = document.createElement('div');
    tooltipContainer.className = 'tooltip-container';
    tooltipContainer.style.cssText = `
        position: fixed;
        background: #f8f9fa;
        border: 1px solid #ddd;
        padding: 10px 15px;
        border-radius: 4px;
        max-width: 300px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        display: none;
        z-index: 1000;
        font-size: 14px;
        line-height: 1.5;
        color: #333;
        transition: opacity 0.3s;
    `;
    document.body.appendChild(tooltipContainer);

    // Add CSS for highlighting metrics
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .metric-highlight {
            text-decoration: dotted underline;
            cursor: help;
        }
        .formula-highlight {
            background-color: rgba(255, 255, 0, 0.2);
            padding: 0 2px;
            border-radius: 2px;
            cursor: help;
        }
        .term-highlight {
            font-style: italic;
            cursor: help;
        }
    `;
    document.head.appendChild(styleElement);

    // Highlight all metrics in the document
    highlightTextInDocument(metricsGlossary, 'metric-highlight');
    
    // Highlight all formulas in the document
    highlightTextInDocument(formulaGlossary, 'formula-highlight');
    
    // Highlight all special terms in the document
    highlightTextInDocument(termsGlossary, 'term-highlight');

    // Add event listeners for all highlighted elements
    document.addEventListener('mouseover', function(e) {
        if (e.target.classList.contains('metric-highlight')) {
            showTooltip(e.target, metricsGlossary[e.target.textContent.trim().toLowerCase()], 'Метрика');
        }
        else if (e.target.classList.contains('formula-highlight')) {
            showTooltip(e.target, formulaGlossary[e.target.textContent.trim().toLowerCase()], 'Формула');
        }
        else if (e.target.classList.contains('term-highlight')) {
            showTooltip(e.target, termsGlossary[e.target.textContent.trim().toLowerCase()], 'Термин');
        }
    });

    document.addEventListener('mouseout', function(e) {
        if (e.target.classList.contains('metric-highlight') || 
            e.target.classList.contains('formula-highlight') ||
            e.target.classList.contains('term-highlight')) {
            hideTooltip();
        }
    });

    // Function to highlight all instances of keys in the document
    function highlightTextInDocument(glossary, className) {
        const textNodes = getTextNodesIn(document.body);
        
        textNodes.forEach(function(node) {
            const text = node.nodeValue;
            
            // Skip nodes that are already inside a code block or highlighted
            if (isInsideCodeOrHighlight(node)) return;
            
            for (let term in glossary) {
                // Create case insensitive regex
                const regex = new RegExp('\\b' + term + '\\b', 'gi');
                
                if (regex.test(text)) {
                    const fragments = text.split(regex);
                    if (fragments.length === 1) continue; // No matches found
                    
                    const container = document.createElement('span');
                    
                    for (let i = 0; i < fragments.length; i++) {
                        container.appendChild(document.createTextNode(fragments[i]));
                        
                        // Add highlighted term between fragments (except after the last one)
                        if (i < fragments.length - 1) {
                            const highlight = document.createElement('span');
                            highlight.className = className;
                            highlight.textContent = text.match(regex)[i];
                            container.appendChild(highlight);
                        }
                    }
                    
                    node.parentNode.replaceChild(container, node);
                    return; // Stop after first replacement (to avoid issues with DOM mutation)
                }
            }
        });
    }

    // Helper function to get all text nodes in an element
    function getTextNodesIn(node) {
        const textNodes = [];
        
        function getTextNodes(node) {
            if (node.nodeType === 3) {
                textNodes.push(node);
            } else if (node.nodeType === 1 && node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE') {
                for (let i = 0; i < node.childNodes.length; i++) {
                    getTextNodes(node.childNodes[i]);
                }
            }
        }
        
        getTextNodes(node);
        return textNodes;
    }

    // Check if a node is inside a code block or already highlighted
    function isInsideCodeOrHighlight(node) {
        let parent = node.parentNode;
        while (parent) {
            if (parent.nodeName === 'CODE' || parent.nodeName === 'PRE' || 
                parent.classList && (
                    parent.classList.contains('metric-highlight') || 
                    parent.classList.contains('formula-highlight') || 
                    parent.classList.contains('term-highlight')
                )) {
                return true;
            }
            parent = parent.parentNode;
        }
        return false;
    }

    // Show tooltip at the correct position
    function showTooltip(element, text, category) {
        tooltipContainer.innerHTML = `<strong>${category}:</strong> ${text}`;
        tooltipContainer.style.display = 'block';
        
        const rect = element.getBoundingClientRect();
        tooltipContainer.style.left = rect.left + 'px';
        tooltipContainer.style.top = (rect.bottom + 10) + 'px';
        
        // Make sure tooltip is within viewport
        const tooltipRect = tooltipContainer.getBoundingClientRect();
        if (tooltipRect.right > window.innerWidth) {
            tooltipContainer.style.left = (window.innerWidth - tooltipRect.width - 10) + 'px';
        }
        if (tooltipRect.bottom > window.innerHeight) {
            tooltipContainer.style.top = (rect.top - tooltipRect.height - 10) + 'px';
        }
    }

    // Hide tooltip
    function hideTooltip() {
        tooltipContainer.style.display = 'none';
    }
});