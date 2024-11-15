class ConfirmationModal {
    constructor() {
        this.modalManager = window.modalManager;
    }

    show(options = {}) {
        const { 
            title = 'Confirm Action',
            message = 'Are you sure?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            onConfirm = () => {},
            onCancel = () => {}
        } = options;

        this.modalManager.openModal({
            title,
            content: `
                <div class="confirmation-modal">
                    <p>${message}</p>
                </div>
            `,
            footer: `
                <button class="btn secondary" data-modal-close>${cancelText}</button>
                <button class="btn danger" data-action="confirm">${confirmText}</button>
            `
        });

        const modalContent = this.modalManager.modal.querySelector('.modal-content');
        modalContent.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="confirm"]')) {
                onConfirm();
                this.modalManager.closeModal();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.confirmationModal = new ConfirmationModal();
}); 