class PatientListManager {
    constructor() {
        this.container = document.querySelector('.patient-list');
        this.searchForm = document.querySelector('#patient-search-form');
        this.clearFiltersBtn = document.querySelector('#clearFilters');
        this.state = {
            isLoading: false,
            currentPage: parseInt(new URLSearchParams(window.location.search).get('page')) || 1,
            searchQuery: new URLSearchParams(window.location.search).get('search') || '',
            sortOption: new URLSearchParams(window.location.search).get('sort_by') || '-updated_at'
        };

        this.init();
    }

    init() {
        if (!this.container) {
            console.error('Patient list container not found');
            return;
        }

        this.attachEventListeners();
    }

    attachEventListeners() {
        // Pagination click events
        document.addEventListener('click', async (e) => {
            if (this.state.isLoading) return;

            const pageLink = e.target.closest('.page-link');
            if (pageLink) {
                e.preventDefault();
                const page = parseInt(pageLink.dataset.page);
                if (!isNaN(page)) {
                    await this.loadPage(page);
                }
            }

            // Handle patient ID click
            const patientId = e.target.closest('.patient-id');
            if (patientId) {
                this.togglePatientId(patientId);
            }
        });

        // Search form submission
        if (this.searchForm) {
            this.searchForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(this.searchForm);
                const params = new URLSearchParams(formData);
                await this.loadPage(1, params);
            });

            // Handle enter key in search input
            const searchInput = this.searchForm.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.addEventListener('keypress', async (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const formData = new FormData(this.searchForm);
                        const params = new URLSearchParams(formData);
                        await this.loadPage(1, params);
                    }
                });
            }
        }

        // Clear filters
        if (this.clearFiltersBtn) {
            this.clearFiltersBtn.addEventListener('click', () => {
                this.searchForm.reset();
                window.location.href = window.location.pathname;
            });
        }
    }

    togglePatientId(element) {
        const fullId = element.dataset.fullId;
        const currentText = element.textContent.trim();
        
        if (currentText.startsWith('...')) {
            element.textContent = fullId;
        } else {
            element.textContent = '...' + fullId.slice(-4);
        }
    }

    async loadPage(page, searchParams = null) {
        if (this.state.isLoading) return;

        try {
            this.state.isLoading = true;
            loadingManager.showGlobalLoading('Loading patients...');

            // Build URL with current search and sort parameters
            const params = searchParams || new URLSearchParams(window.location.search);
            params.set('page', page);
            
            // Update URL without reloading the page
            const newUrl = `${window.location.pathname}?${params.toString()}`;
            window.history.pushState({}, '', newUrl);
            
            // Fetch the new page
            const response = await fetch(newUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                    'X-CSRFToken': utils.getCSRFToken()
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            if (!data.html) {
                throw new Error('Invalid response format');
            }

            // Create a temporary container and insert the HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = data.html;

            // Always update the entire container content
            this.container.innerHTML = tempDiv.innerHTML;
            this.state.currentPage = page;

        } catch (error) {
            console.error('Error loading page:', error);
            notifications.error('Error loading patients. Please try again.');
            
            // Show a user-friendly message in the container
            this.container.innerHTML = `
                <div class="alert alert-danger">
                    <p>Unable to load patients. Please try refreshing the page.</p>
                </div>
            `;
            
            // Revert URL if there was an error
            const params = new URLSearchParams(window.location.search);
            params.set('page', this.state.currentPage);
            window.history.pushState({}, '', `${window.location.pathname}?${params.toString()}`);
        } finally {
            loadingManager.hideGlobalLoading();
            this.state.isLoading = false;
        }
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.patient-list')) {
        window.patientListManager = new PatientListManager();
    }
}); 