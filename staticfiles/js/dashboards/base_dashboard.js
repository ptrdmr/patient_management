class BaseDashboard {
    constructor() {
        this.initializeControls();
        this.initializeRefreshButton();
        this.updateLastUpdateTime();
    }

    initializeControls() {
        // Initialize date range picker
        const startDate = document.getElementById('startDate');
        const endDate = document.getElementById('endDate');

        // Set default date range (last 30 days)
        const today = new Date();
        const thirtyDaysAgo = new Date(today);
        thirtyDaysAgo.setDate(today.getDate() - 30);

        startDate.value = this.formatDate(thirtyDaysAgo);
        endDate.value = this.formatDate(today);

        // Add event listeners
        startDate.addEventListener('change', () => this.onDateRangeChange());
        endDate.addEventListener('change', () => this.onDateRangeChange());
    }

    initializeRefreshButton() {
        const refreshButton = document.querySelector('.refresh-data');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => this.refreshData());
        }
    }

    formatDate(date) {
        return date.toISOString().split('T')[0];
    }

    updateLastUpdateTime() {
        const lastUpdateElement = document.getElementById('lastUpdateTime');
        if (lastUpdateElement) {
            const now = new Date();
            lastUpdateElement.textContent = now.toLocaleString();
        }
    }

    onDateRangeChange() {
        // This method should be overridden by specific dashboard implementations
        console.log('Date range changed');
        this.refreshData();
    }

    async refreshData() {
        try {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            // Show loading state
            this.showLoading();

            // Fetch new data
            await this.fetchDashboardData(startDate, endDate);

            // Update last update time
            this.updateLastUpdateTime();

            // Hide loading state
            this.hideLoading();
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            this.showError('Failed to refresh dashboard data');
            this.hideLoading();
        }
    }

    async fetchDashboardData(startDate, endDate) {
        // This method should be overridden by specific dashboard implementations
        throw new Error('fetchDashboardData must be implemented by child class');
    }

    showLoading() {
        // Add loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">Updating dashboard...</div>
        `;
        document.querySelector('.dashboard-container').appendChild(loadingOverlay);
    }

    hideLoading() {
        // Remove loading overlay
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    showError(message) {
        // Show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.textContent = message;
        
        const dashboardContent = document.querySelector('.dashboard-content');
        dashboardContent.insertBefore(errorDiv, dashboardContent.firstChild);

        // Remove error after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    // Utility method for making API calls
    async fetchAPI(endpoint, options = {}) {
        const response = await fetch(endpoint, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }

        return response.json();
    }
} 