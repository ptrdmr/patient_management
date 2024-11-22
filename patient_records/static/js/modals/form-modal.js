class FormModal {
    constructor() {
        this.modal = document.getElementById('baseModal');
        this.modalContent = this.modal.querySelector('.modal-content');
        this.modalTitle = this.modal.querySelector('.modal-title');
    }

    async show(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'text/html,application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            let content;
            
            if (contentType && contentType.includes('application/json')) {
                content = await response.json();
                if (content.error) {
                    throw new Error(content.error);
                }
                this.modalContent.innerHTML = content.html || '';
            } else {
                content = await response.text();
                this.modalContent.innerHTML = content;
            }
            
            this.modalTitle.textContent = options.title || 'Edit Record';
            this.modal.classList.add('active');
            
            const form = this.modalContent.querySelector('form');
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    await this.handleSubmit(form, options.onSuccess);
                });
            }
        } catch (error) {
            console.error('Error loading form:', error);
            alert('Failed to load form');
        }
    }

    async handleSubmit(form, onSuccess) {
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();
            
            if (data.success) {
                window.modalManager.closeModal(this.modal);
                if (typeof onSuccess === 'function') {
                    onSuccess(data);
                }
            } else if (data.html) {
                // Replace form content with updated HTML (containing validation errors)
                this.modalContent.innerHTML = data.html;
                
                // Reattach submit handler to new form
                const newForm = this.modalContent.querySelector('form');
                if (newForm) {
                    newForm.addEventListener('submit', async (e) => {
                        e.preventDefault();
                        await this.handleSubmit(newForm, onSuccess);
                    });
                }
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert('Failed to submit form');
        }
    }
}

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', () => {
    window.formModal = new FormModal();

    // Handle collapsible cards
    document.querySelectorAll('.collapsible .card-header').forEach(header => {
        header.addEventListener('click', function() {
            const card = this.closest('.collapsible');
            const content = card.querySelector('.card-content');
            const icon = card.querySelector('.collapse-icon');
            
            // Toggle content visibility
            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.style.transform = 'rotate(180deg)';
            } else {
                content.style.display = 'none';
                icon.style.transform = 'rotate(0deg)';
            }
        });
    });
}); 