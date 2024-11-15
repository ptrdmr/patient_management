export function setupModalForm(form, onSuccess) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                window.modalManager.closeModal();
                if (typeof onSuccess === 'function') {
                    onSuccess(data);
                } else {
                    window.location.reload();
                }
            } else {
                const data = await response.json();
                showFormErrors(form, data.errors);
            }
        } catch (error) {
            console.error('Form submission error:', error);
        }
    });
} 