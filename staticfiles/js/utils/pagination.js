class PaginationManager {
    constructor(options = {}) {
        this.options = {
            itemsPerPage: options.itemsPerPage || 10,
            container: options.container || document.querySelector('.pagination-container'),
            dataContainer: options.dataContainer || document.querySelector('.data-container'),
            loadMoreButton: options.loadMoreButton || document.querySelector('.load-more'),
            onPageChange: options.onPageChange || null,
            totalItems: options.totalItems || 0,
            currentPage: options.currentPage || 1,
            debounceDelay: options.debounceDelay || 300
        };

        this.state = {
            isLoading: false,
            lastClickTime: 0
        };

        this.init();
    }

    init() {
        if (!this.options.container || !this.options.dataContainer) {
            console.error('Required containers not found');
            return;
        }

        this.attachEventListeners();
        this.updatePaginationUI();
    }

    attachEventListeners() {
        this.options.container.addEventListener('click', (e) => {
            const target = e.target;
            if (target.matches('.page-link')) {
                e.preventDefault();
                this.handlePageClick(target);
            }
        });

        if (this.options.loadMoreButton) {
            this.options.loadMoreButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadMore();
            });
        }

        // Prevent double clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('.page-link')) {
                const currentTime = new Date().getTime();
                if (currentTime - this.state.lastClickTime < this.options.debounceDelay) {
                    e.preventDefault();
                    return;
                }
                this.state.lastClickTime = currentTime;
            }
        }, true);
    }

    async handlePageClick(target) {
        if (this.state.isLoading) return;

        const page = parseInt(target.dataset.page);
        if (isNaN(page)) return;

        this.state.isLoading = true;
        this.showLoader();

        try {
            if (this.options.onPageChange) {
                await this.options.onPageChange(page);
            }
            this.options.currentPage = page;
            this.updatePaginationUI();
        } catch (error) {
            console.error('Error changing page:', error);
        } finally {
            this.hideLoader();
            this.state.isLoading = false;
        }
    }

    async loadMore() {
        if (this.state.isLoading) return;

        this.state.isLoading = true;
        this.showLoader();

        try {
            const nextPage = this.options.currentPage + 1;
            if (this.options.onPageChange) {
                await this.options.onPageChange(nextPage, true);
            }
            this.options.currentPage = nextPage;
            this.updatePaginationUI();
        } catch (error) {
            console.error('Error loading more items:', error);
        } finally {
            this.hideLoader();
            this.state.isLoading = false;
        }
    }

    updatePaginationUI() {
        const totalPages = Math.ceil(this.options.totalItems / this.options.itemsPerPage);
        const currentPage = this.options.currentPage;

        let html = '<ul class="pagination">';

        // Previous button
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}" 
                   ${currentPage === 1 ? 'tabindex="-1" aria-disabled="true"' : ''}>
                    Previous
                </a>
            </li>
        `;

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (
                i === 1 || // First page
                i === totalPages || // Last page
                (i >= currentPage - 2 && i <= currentPage + 2) // Pages around current
            ) {
                html += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">
                            ${i}
                        </a>
                    </li>
                `;
            } else if (
                (i === currentPage - 3 && currentPage > 4) ||
                (i === currentPage + 3 && currentPage < totalPages - 3)
            ) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }

        // Next button
        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}"
                   ${currentPage === totalPages ? 'tabindex="-1" aria-disabled="true"' : ''}>
                    Next
                </a>
            </li>
        `;

        html += '</ul>';

        this.options.container.innerHTML = html;

        // Update load more button visibility
        if (this.options.loadMoreButton) {
            this.options.loadMoreButton.style.display = 
                currentPage < totalPages ? 'block' : 'none';
        }
    }

    showLoader() {
        const loader = document.createElement('div');
        loader.className = 'pagination-loader';
        loader.innerHTML = '<div class="spinner"></div>';
        this.options.dataContainer.appendChild(loader);
    }

    hideLoader() {
        const loader = this.options.dataContainer.querySelector('.pagination-loader');
        if (loader) {
            loader.remove();
        }
    }

    updateTotalItems(total) {
        this.options.totalItems = total;
        this.updatePaginationUI();
    }
} 