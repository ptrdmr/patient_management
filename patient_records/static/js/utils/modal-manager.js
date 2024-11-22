class ModalManager {
    constructor() {
        this.modal = document.getElementById('baseModal');
        if (!this.modal) {
            console.error('Modal element not found! Make sure the modal HTML is in the page.');
            return;
        }
        this.activeElement = null;
        this.setupListeners();
    }

    setupListeners() {
        // Close on overlay or close button click
        this.modal.querySelectorAll('[data-modal-close]').forEach(element => {
            element.addEventListener('click', () => this.closeModal());
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.closeModal();
            }
        });

        // Trap focus within modal when open
        this.modal.addEventListener('keydown', (e) => {
            if (!this.isOpen()) return;
            
            if (e.key === 'Tab') {
                this.handleTabKey(e);
            }
        });
    }

    async openModal(options = {}) {
        if (!this.modal) return;

        try {
            // Set title
            const titleElement = this.modal.querySelector('.modal-title');
            if (titleElement) {
                titleElement.textContent = options.title || '';
            }

            // Set content
            const contentContainer = this.modal.querySelector('.modal-content');
            if (contentContainer) {
                contentContainer.innerHTML = options.content || '';
            }

            // Set footer
            const footerContainer = this.modal.querySelector('.modal-footer');
            if (footerContainer) {
                footerContainer.innerHTML = options.footer || '';
            }

            // Show modal
            this.modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';

            // Store currently focused element
            this.activeElement = document.activeElement;

            // Focus first focusable element
            const focusable = this.getFocusableElements();
            if (focusable.length) focusable[0].focus();

        } catch (error) {
            console.error('Error opening modal:', error);
        }
    }

    closeModal() {
        if (!this.isOpen()) return;

        this.modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';

        // Restore focus to triggering element
        if (this.activeElement) {
            this.activeElement.focus();
            this.activeElement = null;
        }

        // Clear content
        this.modal.querySelector('.modal-content').innerHTML = '';
        this.modal.querySelector('.modal-footer').innerHTML = '';
    }

    isOpen() {
        return this.modal.getAttribute('aria-hidden') === 'false';
    }

    getFocusableElements() {
        return Array.from(this.modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ));
    }

    handleTabKey(e) {
        const focusable = this.getFocusableElements();
        const firstFocusable = focusable[0];
        const lastFocusable = focusable[focusable.length - 1];

        if (e.shiftKey) {
            if (document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            }
        } else {
            if (document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    }

    showLoading() {
        const content = this.modal.querySelector('.modal-content');
        if (content) {
            content.innerHTML = '<div class="loading-spinner"></div>';
        }
    }

    hideLoading() {
        const content = this.modal.querySelector('.modal-content');
        const spinner = content.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Initialize modal manager
document.addEventListener('DOMContentLoaded', () => {
    window.modalManager = new ModalManager();
}); 