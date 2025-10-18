/**
 * Chart.js yardımcı fonksiyonları
 * Dashboard ve raporlama için grafik utilities
 */

// Renk paleti
const chartColors = {
    primary: '#2563eb',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#0ea5e9',
    purple: '#8b5cf6',
    pink: '#ec4899',
    indigo: '#6366f1',
    teal: '#14b8a6',
    orange: '#f97316'
};

// Varsayılan Chart.js ayarları
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 13;
Chart.defaults.color = '#64748b';

/**
 * Pie/Doughnut chart oluştur
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - {label1: value1, label2: value2, ...}
 * @param {string} type - 'pie' veya 'doughnut'
 */
function createPieChart(canvasId, data, type = 'doughnut') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);
    const colors = Object.values(chartColors).slice(0, labels.length);

    return new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    cornerRadius: 8
                }
            }
        }
    });
}

/**
 * Bar chart oluştur
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - {label1: value1, label2: value2, ...}
 * @param {string} orientation - 'vertical' veya 'horizontal'
 */
function createBarChart(canvasId, data, orientation = 'vertical') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Adet',
                data: values,
                backgroundColor: chartColors.primary,
                borderRadius: 8,
                barThickness: orientation === 'horizontal' ? 30 : undefined
            }]
        },
        options: {
            indexAxis: orientation === 'horizontal' ? 'y' : 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        display: orientation === 'vertical'
                    }
                },
                x: {
                    grid: {
                        display: orientation === 'horizontal'
                    }
                }
            }
        }
    });
}

/**
 * Line chart oluştur
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - {date1: value1, date2: value2, ...}
 * @param {string} label - Dataset etiketi
 */
function createLineChart(canvasId, data, label = 'Değer') {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = Object.keys(data);
    const values = Object.values(data);

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                borderColor: chartColors.success,
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: chartColors.success,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8,
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Multi-line chart oluştur
 * @param {string} canvasId - Canvas element ID
 * @param {array} datasets - [{label, data, color}, ...]
 */
function createMultiLineChart(canvasId, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colorList = Object.values(chartColors);
    const chartDatasets = datasets.map((dataset, index) => ({
        label: dataset.label,
        data: Object.values(dataset.data),
        borderColor: dataset.color || colorList[index % colorList.length],
        backgroundColor: `${dataset.color || colorList[index % colorList.length]}20`,
        tension: 0.4,
        fill: false,
        pointRadius: 3,
        pointBackgroundColor: dataset.color || colorList[index % colorList.length]
    }));

    const labels = Object.keys(datasets[0].data);

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: chartDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
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
 * Stacked bar chart oluştur
 * @param {string} canvasId - Canvas element ID
 * @param {array} datasets - [{label, data, color}, ...]
 * @param {array} labels - X axis labels
 */
function createStackedBarChart(canvasId, datasets, labels) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const colorList = Object.values(chartColors);
    const chartDatasets = datasets.map((dataset, index) => ({
        label: dataset.label,
        data: dataset.data,
        backgroundColor: dataset.color || colorList[index % colorList.length],
        borderRadius: 8
    }));

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: chartDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    stacked: true
                },
                y: {
                    stacked: true,
                    beginAtZero: true
                }
            }
        }
    });
}

// Export fonksiyonlar (ES6 modules kullanılıyorsa)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        createPieChart,
        createBarChart,
        createLineChart,
        createMultiLineChart,
        createStackedBarChart,
        chartColors
    };
}


