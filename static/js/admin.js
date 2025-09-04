/* Admin Panel JavaScript */

// Global variables
let charts = {};

// Initialize admin panel
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeModals();
    setupEventListeners();
    
    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.animationDelay = (index * 0.1) + 's';
        card.classList.add('fade-in');
    });
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap modals
function initializeModals() {
    const modalElements = document.querySelectorAll('.modal');
    modalElements.forEach(modalEl => {
        new bootstrap.Modal(modalEl);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Real-time search functionality
    const searchInputs = document.querySelectorAll('input[type="search"], input[id*="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });
    
    // Auto-refresh data every 5 minutes
    setInterval(autoRefresh, 5 * 60 * 1000);
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle search functionality
function handleSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const targetTable = event.target.getAttribute('data-target') || 'tbody tr';
    const rows = document.querySelectorAll(targetTable);
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const shouldShow = text.includes(searchTerm);
        row.style.display = shouldShow ? '' : 'none';
        
        // Add highlight effect
        if (shouldShow && searchTerm) {
            row.classList.add('table-warning');
        } else {
            row.classList.remove('table-warning');
        }
    });
    
    // Update results count
    updateResultsCount(rows, searchTerm);
}

// Update search results count
function updateResultsCount(rows, searchTerm) {
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    const countElement = document.getElementById('results-count');
    
    if (countElement) {
        if (searchTerm) {
            countElement.textContent = `نمایش ${visibleRows.length} از ${rows.length} نتیجه`;
            countElement.style.display = 'block';
        } else {
            countElement.style.display = 'none';
        }
    }
}

// Auto-refresh functionality
function autoRefresh() {
    const currentPage = window.location.pathname;
    
    // Only refresh dashboard and analytics pages
    if (currentPage === '/' || currentPage.includes('analytics')) {
        showNotification('به‌روزرسانی خودکار داده‌ها...', 'info');
        
        // Refresh charts data
        refreshCharts();
    }
}

// Refresh chart data
async function refreshCharts() {
    try {
        // Update users by level chart
        const usersData = await fetchData('/api/chart-data/users_by_level');
        if (charts.usersByLevel && usersData) {
            updateChartData(charts.usersByLevel, usersData);
        }
        
        // Update progress chart
        const progressData = await fetchData('/api/chart-data/progress_by_section');
        if (charts.progress && progressData) {
            updateChartData(charts.progress, progressData);
        }
        
        // Update daily activity chart
        const activityData = await fetchData('/api/chart-data/daily_activity');
        if (charts.dailyActivity && activityData) {
            updateDailyActivityChart(activityData);
        }
        
        showNotification('داده‌ها به‌روزرسانی شد', 'success');
    } catch (error) {
        console.error('Error refreshing charts:', error);
        showNotification('خطا در به‌روزرسانی داده‌ها', 'error');
    }
}

// Fetch data from API
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return null;
    }
}

// Update chart data
function updateChartData(chart, newData) {
    if (chart && chart.data && chart.data.datasets && chart.data.datasets[0]) {
        chart.data.datasets[0].data = Object.values(newData);
        chart.update('none'); // No animation for better performance
    }
}

// Update daily activity chart
function updateDailyActivityChart(data) {
    const chart = charts.dailyActivity;
    if (!chart || !data) return;
    
    const dailyUsers = data.daily_users || [];
    const dailyProgress = data.daily_progress || [];
    
    chart.data.labels = dailyUsers.map(item => item[0]);
    chart.data.datasets[0].data = dailyUsers.map(item => item[1]);
    chart.data.datasets[1].data = dailyProgress.map(item => item[1]);
    chart.update('none');
}

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    const alertClass = type === 'error' ? 'danger' : type;
    const alertHTML = `
        <div class="alert alert-${alertClass} alert-dismissible fade show notification-alert" role="alert">
            <i class="bi bi-${getNotificationIcon(type)}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Create container if it doesn't exist
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = 'position: fixed; top: 80px; left: 20px; z-index: 1050; min-width: 300px;';
        document.body.appendChild(container);
    }
    
    // Add notification
    const alertElement = document.createElement('div');
    alertElement.innerHTML = alertHTML;
    container.appendChild(alertElement.firstElementChild);
    
    // Auto-remove notification
    if (duration > 0) {
        setTimeout(() => {
            const alert = container.querySelector('.notification-alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

// Get notification icon based on type
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Export data functionality
function exportData(type = 'csv', data = null) {
    if (!data) {
        showNotification('هیچ داده‌ای برای صادرات وجود ندارد', 'warning');
        return;
    }
    
    const filename = `telegram_bot_data_${new Date().toISOString().split('T')[0]}.${type}`;
    
    if (type === 'csv') {
        exportToCSV(data, filename);
    } else if (type === 'json') {
        exportToJSON(data, filename);
    }
    
    showNotification(`داده‌ها در فایل ${filename} صادر شد`, 'success');
}

// Export to CSV
function exportToCSV(data, filename) {
    const csvContent = convertToCSV(data);
    downloadFile(csvContent, filename, 'text/csv;charset=utf-8;');
}

// Export to JSON
function exportToJSON(data, filename) {
    const jsonContent = JSON.stringify(data, null, 2);
    downloadFile(jsonContent, filename, 'application/json;charset=utf-8;');
}

// Convert data to CSV format
function convertToCSV(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return '';
    }
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    
    const csvRows = data.map(row => {
        return headers.map(header => {
            let value = row[header];
            // Escape quotes and wrap in quotes if necessary
            if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
                value = '"' + value.replace(/"/g, '""') + '"';
            }
            return value;
        }).join(',');
    });
    
    return csvHeaders + '\n' + csvRows.join('\n');
}

// Download file
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
}

// Format numbers for display
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Format dates for display
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('fa-IR', options);
}

// Validate form data
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Show loading state
function showLoading(element, text = 'در حال بارگذاری...') {
    const loadingHTML = `
        <div class="text-center py-4 loading-state">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">${text}</span>
            </div>
            <div class="mt-2">${text}</div>
        </div>
    `;
    
    if (element) {
        element.innerHTML = loadingHTML;
    }
}

// Hide loading state
function hideLoading(element, originalContent = '') {
    if (element) {
        const loadingState = element.querySelector('.loading-state');
        if (loadingState) {
            loadingState.remove();
        }
        
        if (originalContent) {
            element.innerHTML = originalContent;
        }
    }
}

// Confirm action with modal
function confirmAction(message, onConfirm, onCancel = null) {
    const confirmed = confirm(message);
    if (confirmed && typeof onConfirm === 'function') {
        onConfirm();
    } else if (!confirmed && typeof onCancel === 'function') {
        onCancel();
    }
}

// Utility function to get URL parameters
function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Utility function to update URL parameters
function updateUrlParameter(key, value) {
    const url = new URL(window.location);
    url.searchParams.set(key, value);
    window.history.pushState({}, '', url);
}

// Error handling
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', event.error);
    showNotification('خطایی در سیستم رخ داده است', 'error');
});

// Unhandled promise rejection handling
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled Promise Rejection:', event.reason);
    showNotification('خطایی در پردازش درخواست رخ داده است', 'error');
});

// Export functions for use in other scripts
window.AdminJS = {
    showNotification,
    exportData,
    formatNumber,
    formatDate,
    validateForm,
    showLoading,
    hideLoading,
    confirmAction,
    getUrlParameter,
    updateUrlParameter
};
