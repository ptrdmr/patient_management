/**
 * Form Modal Component
 * Handles form submission in a modal context with AJAX support
 */

class FormModal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        if (!this.modal) {
            console.error(`Modal with ID ${modalId} not found`);
            return;
        }
        
        this.form = this.modal.querySelector('form');
        this.submitBtn = this.modal.querySelector('[type="submit"]');
        this.cancelBtn = this.modal.querySelector('[data-dismiss="modal"]');
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        if (this.cancelBtn) {
            this.cancelBtn.addEventListener('click', () => this.handleCancel());
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        try {
            this.submitBtn.disabled = true;
            this.submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show success message
                if (window.showNotification) {
                    window.showNotification('Success', data.message || 'Form submitted successfully', 'success');
                }
                
                // Handle redirect if provided
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    // Close modal and refresh page
                    this.close();
                    window.location.reload();
                }
            } else {
                // Handle validation errors
                this.handleErrors(data.errors);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            if (window.showNotification) {
                window.showNotification('Error', 'An error occurred while submitting the form', 'error');
            }
        } finally {
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = 'Save';
        }
    }

    handleErrors(errors) {
        // Clear previous errors
        this.form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        this.form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });
        
        // Display new errors
        Object.entries(errors).forEach(([field, messages]) => {
            const input = this.form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                feedback.textContent = Array.isArray(messages) ? messages[0] : messages;
                input.parentNode.appendChild(feedback);
            }
        });
    }

    handleCancel() {
        this.close();
    }

    close() {
        // Use Bootstrap's modal hide method
        const bsModal = bootstrap.Modal.getInstance(this.modal);
        if (bsModal) {
            bsModal.hide();
        }
    }
}

// Export for use in other modules
window.FormModal = FormModal; 