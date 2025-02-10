document.addEventListener('DOMContentLoaded', function() {
    // Get patient ID from URL
    const patientId = window.location.pathname.split('/')[2];
    let vitalsTrendChart = null;

    // Initialize the dashboard
    initializeDashboard();

    function initializeDashboard() {
        setupVitalsChart();
        
        // Set up date range inputs
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 30);
        
        document.getElementById('startDate').value = thirtyDaysAgo.toISOString().split('T')[0];
        document.getElementById('endDate').value = today.toISOString().split('T')[0];
        
        // Add refresh button click handler
        document.querySelector('.refresh-btn').addEventListener('click', refreshDashboardData);
        
        // Add All Time button click handler
        document.querySelector('.all-time-btn').addEventListener('click', function() {
            document.getElementById('startDate').value = '';
            document.getElementById('endDate').value = '';
            refreshDashboardData();
        });
        
        // Initial data load
        refreshDashboardData();
        
        // Refresh data every 5 minutes
        setInterval(refreshDashboardData, 300000);
    }

    function refreshDashboardData() {
        console.log('Refreshing dashboard data...');
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        let url = `/api/patients/${patientId}/dashboard-metrics/`;
        if (startDate && endDate) {
            url += `?start_date=${startDate}&end_date=${endDate}`;
        }
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Dashboard data:', data);
                
                // Always update metrics if they exist, regardless of success flag
                if (data.metrics) {
                    updateMetricValue('total_visits', data.metrics.total_visits);
                    updateMetricValue('active_medications', data.metrics.active_medications);
                    updateMetricValue('recent_labs', data.metrics.recent_labs);
                    updateMetricValue('pending_tasks', data.metrics.pending_tasks);
                }
                
                // Always update latest values if they exist
                if (data.latest_values) {
                    updateMetricValue('bp', data.latest_values.bp || '--/--');
                    updateMetricValue('hr', data.latest_values.hr || '--');
                    updateMetricValue('glucose', data.latest_values.glucose ? `${data.latest_values.glucose} mg/dL` : '--');
                    updateMetricValue('wbc', data.latest_values.wbc ? `${data.latest_values.wbc} K/µL` : '--');
                    updateMetricValue('weight', data.latest_values.weight ? `${data.latest_values.weight} lbs` : '--');
                    updateMetricValue('bmi', data.latest_values.bmi || '--');
                }
                
                // Update vitals chart if data exists
                if (data.vitals_data) {
                    updateVitalsChart(data.vitals_data);
                }
                
                // Update activities if they exist
                if (data.activities) {
                    updateActivitiesList(data.activities);
                }
                
                // Update alerts if they exist
                if (data.alerts) {
                    updateAlertsList(data.alerts);
                }
                
                // If there was an error, show it
                if (!data.success && data.error) {
                    console.error('API Error:', data.error);
                }
            })
            .catch(error => {
                console.error('Error fetching dashboard data:', error);
                // Don't reset values to '--' on error, keep existing values
            });
    }

    function updateMetricValue(metric, value) {
        const element = document.querySelector(`[data-metric="${metric}"]`);
        if (element && value !== undefined && value !== null) {
            element.textContent = value;
        }
    }

    function setupVitalsChart() {
        const ctx = document.getElementById('vitalsTrendChart');
        if (!ctx) {
            console.warn('Vitals trend chart canvas not found');
            return;
        }

        vitalsTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Systolic BP',
                    borderColor: '#dc3545',
                    data: [],
                    fill: false
                }, {
                    label: 'Diastolic BP',
                    borderColor: '#0d6efd',
                    data: [],
                    fill: false
                }, {
                    label: 'Heart Rate',
                    borderColor: '#20c997',
                    data: [],
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                day: 'MMM D'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Value'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    function updateVitalsChart(vitalsData) {
        if (!vitalsTrendChart) {
            console.warn('Vitals trend chart not initialized');
            return;
        }

        vitalsTrendChart.data.labels = vitalsData.map(item => item.date);
        vitalsTrendChart.data.datasets[0].data = vitalsData.map(item => item.systolic);
        vitalsTrendChart.data.datasets[1].data = vitalsData.map(item => item.diastolic);
        vitalsTrendChart.data.datasets[2].data = vitalsData.map(item => item.heart_rate);
        
        vitalsTrendChart.update();
    }

    function updateActivitiesList(activities) {
        const container = document.querySelector('.activity-list');
        if (!container) return;

        if (!activities || activities.length === 0) {
            container.innerHTML = '<p>No recent activity</p>';
            return;
        }

        const html = activities.map(activity => `
            <div class="activity-item">
                <span class="activity-time">${formatDate(activity.timestamp)}</span>
                <span class="activity-type">${activity.action} - ${activity.description}</span>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    function updateAlertsList(alerts) {
        const container = document.querySelector('.alerts-list');
        if (!container) return;

        if (!alerts || alerts.length === 0) {
            container.innerHTML = '<p>No active alerts</p>';
            return;
        }

        const html = alerts.map(alert => `
            <div class="alert-item alert-${alert.severity}">
                <i class="fas fa-exclamation-circle"></i>
                <span class="alert-message">${alert.message}</span>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
}); 