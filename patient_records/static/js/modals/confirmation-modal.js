class ConfirmationModal {
    constructor() {
        this.modal = document.getElementById('baseModal');
        this.modalTitle = this.modal.querySelector('.modal-title');
        this.modalContent = this.modal.querySelector('.modal-content');
        this.modalFooter = this.modal.querySelector('.modal-footer');
        this.currentOnConfirm = null;
    }

    show(options) {
        const {
            title = 'Confirm Action',
            message = 'Are you sure?',
            confirmText = 'Delete',
            cancelText = 'Cancel',
            confirmClass = 'danger',
            onConfirm = () => {},
            onCancel = () => {}
        } = options;

        this.currentOnConfirm = onConfirm;  // Store the callback

        this.modalTitle.textContent = title;
        this.modalContent.innerHTML = `<p>${message}</p>`;
        
        // Create footer buttons
        this.modalFooter.innerHTML = `
            <button class="btn secondary" data-action="cancel">${cancelText}</button>
            <button class="btn ${confirmClass}" data-action="confirm">${confirmText}</button>
        `;

        // Add event listeners
        const confirmButton = this.modalFooter.querySelector('[data-action="confirm"]');
        const cancelButton = this.modalFooter.querySelector('[data-action="cancel"]');
        
        confirmButton.addEventListener('click', this.handleConfirm.bind(this));
        cancelButton.addEventListener('click', () => {
            onCancel();
            this.hide();
        });

        this.modal.classList.add('active');
    }

    async handleConfirm() {
        if (this.currentOnConfirm) {
            await this.currentOnConfirm();
        }
        this.hide();
    }

    hide() {
        this.modal.classList.remove('active');
        this.modalFooter.innerHTML = '';
        this.currentOnConfirm = null;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    window.confirmationModal = new ConfirmationModal();
}); 