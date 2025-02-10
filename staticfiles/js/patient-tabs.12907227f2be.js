class PatientTabManager {
    constructor(options = {}) {
        this.options = {
            tabContainer: options.tabContainer || document.querySelector('.tab-container'),
            contentContainer: options.contentContainer || document.querySelector('.tab-content'),
            itemsPerPage: options.itemsPerPage || 10
        };

        this.state = {
            currentTab: null,
            isLoading: false,
            currentPage: 1,
            totalItems: 0
        };

        this.init();
    }

    init() {
        if (!this.options.tabContainer || !this.options.contentContainer) {
            console.error('Required containers not found');
            return;
        }

        this.patientId = this.options.tabContainer.dataset.patientId;
        this.attachEventListeners();
        this.loadInitialTab();
    }

    attachEventListeners() {
        // Tab click events
        this.options.tabContainer.addEventListener('click', async (e) => {
            const tabLink = e.target.closest('.tab');
            if (tabLink && !this.state.isLoading) {
                e.preventDefault();
                const tabName = tabLink.dataset.tab;
                await this.switchTab(tabName);
            }
        });

        // Pagination click events
        this.options.contentContainer.addEventListener('click', async (e) => {
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

    async switchTab(tabName) {
        if (this.state.isLoading || this.state.currentTab === tabName) return;

        try {
            this.state.isLoading = true;
            this.showLoader();

            // Update active tab
            this.updateActiveTab(tabName);
            
            // Reset pagination state
            this.state.currentPage = 1;
            
            // Load content
            await this.loadContent(tabName, 1);
            
        } catch (error) {
            console.error('Error switching tab:', error);
            this.showError('Error loading content. Please try again.');
        } finally {
            this.state.isLoading = false;
            this.hideLoader();
        }
    }

    async loadPage(page) {
        if (this.state.isLoading || !this.state.currentTab) return;

        try {
            this.state.isLoading = true;
            this.showLoader();
            
            await this.loadContent(this.state.currentTab, page);
            
        } catch (error) {
            console.error('Error loading page:', error);
            this.showError('Error loading page. Please try again.');
        } finally {
            this.state.isLoading = false;
            this.hideLoader();
        }
    }

    async loadContent(tabName, page) {
        const url = `/patient/${this.patientId}/tab/${tabName}/?page=${page}`;
        
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || 'Failed to load content');
        }

        // Update content with the HTML from the response
        this.options.contentContainer.innerHTML = data.html;
        
        // Update state
        this.state.currentTab = tabName;
        this.state.currentPage = page;
        
        // Initialize collapsible cards
        this.initializeCollapsibleCards();
        
        // Update total items count from the newly rendered content
        const paginationInfo = this.options.contentContainer.querySelector('.pagination-info');
        if (paginationInfo) {
            const match = paginationInfo.textContent.match(/of (\d+) total records/);
            this.state.totalItems = match ? parseInt(match[1]) : 0;
        }
    }

    updateActiveTab(tabName) {
        const tabs = this.options.tabContainer.querySelectorAll('.tab');
        tabs.forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
    }

    initializeCollapsibleCards() {
        const cards = this.options.contentContainer.querySelectorAll('.data-card.collapsible');
        cards.forEach(card => {
            const header = card.querySelector('.card-header');
            const content = card.querySelector('.card-content');
            const icon = card.querySelector('.collapse-icon');
            
            if (header && content) {
                header.addEventListener('click', () => {
                    content.classList.toggle('active');
                    if (icon) {
                        icon.style.transform = content.classList.contains('active') ? 'rotate(180deg)' : '';
                    }
                });
            }
        });
    }

    showLoader() {
        const loader = document.createElement('div');
        loader.className = 'tab-loader';
        loader.innerHTML = '<div class="spinner"></div>';
        this.options.contentContainer.appendChild(loader);
    }

    hideLoader() {
        const loader = this.options.contentContainer.querySelector('.tab-loader');
        if (loader) {
            loader.remove();
        }
    }

    showError(message) {
        this.options.contentContainer.innerHTML = `
            <div class="error-message">
                ${message}
                <button class="btn-link retry-button" onclick="window.patientTabManager.retryLastAction()">
                    Retry
                </button>
            </div>
        `;
    }

    async retryLastAction() {
        if (this.state.currentTab) {
            await this.loadPage(this.state.currentPage);
        } else {
            await this.loadInitialTab();
        }
    }

    loadInitialTab() {
        const activeTab = this.options.tabContainer.querySelector('.tab.active');
        if (activeTab) {
            this.switchTab(activeTab.dataset.tab);
        }
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const tabContainer = document.querySelector('.tab-container');
    if (tabContainer) {
        window.patientTabManager = new PatientTabManager({
            tabContainer: tabContainer,
            contentContainer: document.querySelector('.tab-content')
        });
    }
}); 