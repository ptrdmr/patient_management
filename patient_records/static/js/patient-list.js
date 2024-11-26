class PatientListManager {
    constructor() {
        this.container = document.querySelector('.patient-list');
        this.state = {
            isLoading: false,
            currentPage: parseInt(new URLSearchParams(window.location.search).get('page')) || 1,
            searchQuery: new URLSearchParams(window.location.search).get('search') || '',
            sortOption: new URLSearchParams(window.location.search).get('sort') || 'date'
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
            if (pageLink && !pageLink.parentElement.classList.contains('disabled')) {
                e.preventDefault();
                const page = parseInt(pageLink.dataset.page);
                if (!isNaN(page)) {
                    await this.loadPage(page);
                }
            }
        });
    }

    async loadPage(page) {
        if (this.state.isLoading) return;

        try {
            this.state.isLoading = true;
            this.showLoader();

            // Build URL with current search and sort parameters
            const params = new URLSearchParams(window.location.search);
            params.set('page', page);
            
            // Update URL without reloading the page
            window.history.pushState({}, '', `${window.location.pathname}?${params.toString()}`);
            
            // Fetch the new page
            const response = await fetch(`?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                // Create a temporary container to parse the HTML
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.html;
                
                // Find the table and pagination in the new content
                const newTable = tempDiv.querySelector('.data-table');
                const newPagination = tempDiv.querySelector('.pagination');
                
                if (newTable && newPagination) {
                    // Update the table content
                    const currentTable = this.container.querySelector('.data-table');
                    if (currentTable) {
                        currentTable.replaceWith(newTable);
                    }
                    
                    // Update the pagination
                    const currentPagination = document.querySelector('.pagination');
                    if (currentPagination) {
                        currentPagination.replaceWith(newPagination);
                    } else {
                        this.container.appendChild(newPagination);
                    }
                    
                    this.state.currentPage = page;
                } else {
                    throw new Error('Invalid response format');
                }
            } else {
                throw new Error(data.error || 'Failed to load page');
            }

        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('Error loading page. Please try again.');
        } finally {
            this.hideLoader();
            this.state.isLoading = false;
        }
    }

    showLoader() {
        const loader = document.createElement('div');
        loader.className = 'pagination-loader';
        loader.innerHTML = '<div class="spinner"></div>';
        document.body.appendChild(loader);
    }

    hideLoader() {
        const loader = document.querySelector('.pagination-loader');
        if (loader) {
            loader.remove();
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        this.container.prepend(errorDiv);
        
        // Remove error after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.patient-list')) {
        window.patientListManager = new PatientListManager();
    }
}); 