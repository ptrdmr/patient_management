class OverviewDashboard extends BaseDashboard {
    constructor() {
        super();
        console.log('Initializing Overview Dashboard');
        this.vitalsChart = null;
        this.initializeCharts();
    }

    async initializeCharts() {
        console.log('Initializing charts');
        try {
            // Initialize vitals chart
            const ctx = document.getElementById('vitalsChart').getContext('2d');
            this.vitalsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Blood Pressure (Systolic)',
                            borderColor: 'rgb(255, 99, 132)',
                            data: []
                        },
                        {
                            label: 'Blood Pressure (Diastolic)',
                            borderColor: 'rgb(54, 162, 235)',
                            data: []
                        },
                        {
                            label: 'Heart Rate',
                            borderColor: 'rgb(75, 192, 192)',
                            data: []
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
            console.log('Chart initialized successfully');

            // Initial data fetch
            await this.refreshData();
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    }

    async fetchDashboardData(startDate, endDate) {
        console.log('Fetching dashboard data for range:', startDate, 'to', endDate);
        try {
            const data = await this.fetchAPI(`/api/dashboard/overview/?start_date=${startDate}&end_date=${endDate}`);
            console.log('Received dashboard data:', data);
            this.updateDashboard(data);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            throw error;
        }
    }

    updateDashboard(data) {
        console.log('Updating dashboard with data:', data);
        try {
            // Update metrics
            this.updateMetrics(data.metrics);
            
            // Update vitals chart
            this.updateVitalsChart(data.vitals);
            
            // Update activity list
            this.updateActivityList(data.activities);
            
            // Update alerts
            this.updateAlerts(data.alerts);
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }

    updateMetrics(metrics) {
        console.log('Updating metrics:', metrics);
        // Update each metric value
        Object.entries(metrics).forEach(([key, value]) => {
            const element = document.querySelector(`.metric-value[data-metric="${key}"]`);
            if (element) {
                element.textContent = value;
                console.log(`Updated metric ${key} to ${value}`);
            } else {
                console.warn(`Metric element not found for key: ${key}`);
            }
        });
    }

    updateVitalsChart(vitalsData) {
        console.log('Updating vitals chart with data:', vitalsData);
        try {
            // Update chart datasets
            this.vitalsChart.data.labels = vitalsData.dates;
            this.vitalsChart.data.datasets[0].data = vitalsData.systolic;
            this.vitalsChart.data.datasets[1].data = vitalsData.diastolic;
            this.vitalsChart.data.datasets[2].data = vitalsData.heartRate;
            this.vitalsChart.update();
            console.log('Chart updated successfully');
        } catch (error) {
            console.error('Error updating vitals chart:', error);
        }
    }

    updateActivityList(activities) {
        console.log('Updating activity list:', activities);
        const activityList = document.querySelector('.activity-list');
        if (!activityList) {
            console.warn('Activity list element not found');
            return;
        }

        // Clear existing activities
        activityList.innerHTML = '';

        // Add new activities
        activities.forEach(activity => {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-item';
            activityItem.innerHTML = `
                <span class="activity-time">${new Date(activity.timestamp).toLocaleString()}</span>
                <span class="activity-type">${activity.action}</span>
                <span class="activity-description">${activity.description}</span>
            `;
            activityList.appendChild(activityItem);
        });
    }

    updateAlerts(alerts) {
        console.log('Updating alerts:', alerts);
        const alertsList = document.querySelector('.alerts-list');
        if (!alertsList) {
            console.warn('Alerts list element not found');
            return;
        }

        // Clear existing alerts
        alertsList.innerHTML = '';

        // Add new alerts
        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item alert-${alert.severity}`;
            alertItem.innerHTML = `
                <i class="fas fa-exclamation-circle"></i>
                <span class="alert-message">${alert.message}</span>
            `;
            alertsList.appendChild(alertItem);
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing dashboard');
    window.dashboard = new OverviewDashboard();
}); 