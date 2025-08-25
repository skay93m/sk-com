/**
 * Analytics Dashboard JavaScript
 * Handles chart initialization and dashboard interactions
 */

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeAnalyticsDashboard();
});

/**
 * Initialize the analytics dashboard
 */
function initializeAnalyticsDashboard() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeDailyViewsChart();
        initializeResponseTimeChart();
    }
    
    // Set up auto-refresh
    setupAutoRefresh();
}

/**
 * Initialize Daily Views Chart (Line Chart)
 */
function initializeDailyViewsChart() {
    const dailyCanvas = document.getElementById('dailyViewsChart');
    if (!dailyCanvas) return;
    
    const dailyCtx = dailyCanvas.getContext('2d');
    
    // Get data from template (this will be injected by Django)
    const dailyData = window.dailyViewsData || [];

    new Chart(dailyCtx, {
        type: 'line',
        data: {
            labels: dailyData.map(d => d.date),
            datasets: [{
                label: 'Daily Views',
                data: dailyData.map(d => d.views),
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Initialize Response Time Distribution Chart (Doughnut Chart)
 */
function initializeResponseTimeChart() {
    const responseCanvas = document.getElementById('responseTimeChart');
    if (!responseCanvas) return;
    
    const responseCtx = responseCanvas.getContext('2d');
    
    // Use dynamic data if available, otherwise fallback to sample data
    const responseTimeData = window.responseTimeData || [70, 25, 5];
    
    new Chart(responseCtx, {
        type: 'doughnut',
        data: {
            labels: ['Fast (<200ms)', 'Good (200-500ms)', 'Slow (>500ms)'],
            datasets: [{
                data: responseTimeData,
                backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        fontSize: 10
                    }
                }
            }
        }
    });
}

/**
 * Set up auto-refresh functionality
 */
function setupAutoRefresh() {
    // Auto-refresh every 30 seconds (optional)
    const autoRefreshInterval = 30000; // 30 seconds
    
    setTimeout(function() {
        // Only refresh if the user hasn't been inactive
        if (document.visibilityState === 'visible') {
            location.reload();
        }
    }, autoRefreshInterval);
}

/**
 * Initialize metric cards with animations
 */
function initializeMetricCards() {
    const metricCards = document.querySelectorAll('.analytics-dashboard .card');
    
    // Add intersection observer for animation on scroll
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1
        });
        
        metricCards.forEach(card => {
            observer.observe(card);
        });
    }
}

/**
 * Utility function to format numbers for display
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Utility function to update real-time metrics
 */
function updateRealTimeMetrics() {
    // This function can be called to update metrics without full page refresh
    fetch('/analytics/api/real-time-data/')
        .then(response => response.json())
        .then(data => {
            // Update metric displays
            updateMetricDisplay('total-views', data.totalViews);
            updateMetricDisplay('today-views', data.todayViews);
            updateMetricDisplay('unique-visitors', data.uniqueVisitors);
            updateMetricDisplay('avg-response-time', data.avgResponseTime + 'ms');
        })
        .catch(error => {
            console.warn('Failed to update real-time metrics:', error);
        });
}

/**
 * Update individual metric display
 */
function updateMetricDisplay(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = formatNumber(value);
        
        // Add a brief highlight animation
        element.classList.add('metric-updated');
        setTimeout(() => {
            element.classList.remove('metric-updated');
        }, 1000);
    }
}

/**
 * Initialize tooltip functionality for charts
 */
function initializeTooltips() {
    // Enable Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Export functions for potential external use
window.AnalyticsDashboard = {
    updateRealTimeMetrics,
    formatNumber,
    initializeMetricCards,
    initializeTooltips
};
