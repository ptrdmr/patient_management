class FormModal {
    constructor() {
        this.modalManager = window.modalManager;
        if (!this.modalManager) {
            console.error('Modal manager not initialized!');
        }
    }

    async show(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const html = await response.text();
            
            this.modalManager.openModal({
                title: options.title || 'Form',
                content: html,
                footer: `
                    <button type="button" class="btn secondary" data-modal-close>Cancel</button>
                    <button type="submit" form="modal-form" class="btn primary">Save</button>
                `
            });

            const form = document.getElementById('modal-form');
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const formData = new FormData(form);
                    
                    try {
                        const submitResponse = await fetch(form.action, {
                            method: form.method,
                            body: formData,
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        });
                        
                        if (submitResponse.ok) {
                            const data = await submitResponse.json();
                            this.modalManager.closeModal();
                            if (options.onSuccess) {
                                options.onSuccess(data);
                            } else {
                                window.location.reload();
                            }
                        } else {
                            const errorData = await submitResponse.json();
                            // Handle form errors
                            const errorContainer = form.querySelector('.form-errors');
                            if (errorContainer) {
                                errorContainer.style.display = 'block';
                                const errorList = errorContainer.querySelector('.error-list');
                                errorList.innerHTML = Object.values(errorData).map(error => 
                                    `<li>${error}</li>`
                                ).join('');
                            }
                        }
                    } catch (error) {
                        console.error('Form submission error:', error);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading form:', error);
        }
    }
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    window.formModal = new FormModal();
}); 