/**
 * Form Validation Module
 * Provides comprehensive client-side validation with real-time feedback
 */

class FormValidator {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            realTime: true,
            showSuccess: true,
            validateOnBlur: true,
            validateOnInput: true,
            ...options
        };
        this.setupValidation();
    }

    setupValidation() {
        // Validate on blur
        if (this.options.validateOnBlur) {
            this.form.addEventListener('blur', (e) => {
                if (e.target.matches('input, select, textarea')) {
                    this.validateField(e.target);
                }
            }, true);
        }

        // Real-time validation
        if (this.options.validateOnInput) {
            this.form.addEventListener('input', (e) => {
                if (this.shouldValidateOnInput(e.target)) {
                    this.validateField(e.target);
                }
            });
        }

        // Form submission
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (await this.validateForm()) {
                this.handleSubmit(e);
            }
        });
    }

    shouldValidateOnInput(field) {
        return field.matches('input[type="email"], input[type="tel"], input[pattern], input[type="number"]') ||
               field.hasAttribute('data-validate-live');
    }

    async validateForm() {
        let isValid = true;
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        for (const field of fields) {
            if (!await this.validateField(field)) {
                isValid = false;
            }
        }

        return isValid;
    }

    async validateField(field) {
        const wrapper = field.closest('.field-wrapper') || field.parentElement;
        const errorElement = wrapper.querySelector('.field-error') || this.createErrorElement(wrapper);
        let isValid = true;
        let errorMessage = '';

        // Clear previous state
        field.classList.remove('is-invalid', 'is-valid');
        errorElement.textContent = '';

        // Required field validation
        if (field.required && !field.value.trim()) {
            isValid = false;
            errorMessage = field.dataset.requiredMessage || 'This field is required';
        }

        // Custom validation rules
        if (isValid && field.dataset.validationRules) {
            const result = await this.runCustomValidation(field);
            if (!result.isValid) {
                isValid = false;
                errorMessage = result.message;
            }
        }

        // Pattern validation
        if (isValid && field.pattern && field.value) {
            const pattern = new RegExp(field.pattern);
            if (!pattern.test(field.value)) {
                isValid = false;
                errorMessage = field.dataset.patternMessage || 'Invalid format';
            }
        }

        // Range validation
        if (isValid && field.type === 'number' && field.value) {
            const value = parseFloat(field.value);
            if (field.min && value < parseFloat(field.min)) {
                isValid = false;
                errorMessage = field.dataset.minMessage || `Value must be at least ${field.min}`;
            }
            if (field.max && value > parseFloat(field.max)) {
                isValid = false;
                errorMessage = field.dataset.maxMessage || `Value must be no more than ${field.max}`;
            }
        }

        // Update UI
        this.updateFieldUI(field, isValid, errorMessage);
        return isValid;
    }

    async runCustomValidation(field) {
        const rules = JSON.parse(field.dataset.validationRules);
        for (const rule of rules) {
            switch (rule.type) {
                case 'async':
                    const response = await fetch(rule.url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken()
                        },
                        body: JSON.stringify({ value: field.value })
                    });
                    const data = await response.json();
                    if (!data.isValid) {
                        return { isValid: false, message: data.message };
                    }
                    break;
                case 'regex':
                    const pattern = new RegExp(rule.pattern);
                    if (!pattern.test(field.value)) {
                        return { isValid: false, message: rule.message };
                    }
                    break;
                case 'custom':
                    if (typeof window[rule.function] === 'function') {
                        const result = await window[rule.function](field.value);
                        if (!result.isValid) {
                            return result;
                        }
                    }
                    break;
            }
        }
        return { isValid: true };
    }

    updateFieldUI(field, isValid, errorMessage) {
        const wrapper = field.closest('.field-wrapper') || field.parentElement;
        const errorElement = wrapper.querySelector('.field-error');
        
        if (!isValid) {
            field.classList.add('is-invalid');
            errorElement.textContent = errorMessage;
            this.showFieldError(wrapper, errorMessage);
        } else if (this.options.showSuccess) {
            field.classList.add('is-valid');
            this.showFieldSuccess(wrapper);
        }
    }

    createErrorElement(wrapper) {
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error invalid-feedback';
        wrapper.appendChild(errorElement);
        return errorElement;
    }

    showFieldError(wrapper, message) {
        const feedback = wrapper.querySelector('.invalid-feedback') || this.createErrorElement(wrapper);
        feedback.textContent = message;
        feedback.style.display = 'block';
    }

    showFieldSuccess(wrapper) {
        const field = wrapper.querySelector('input, select, textarea');
        field.classList.add('is-valid');
        const feedback = wrapper.querySelector('.valid-feedback');
        if (feedback) {
            feedback.style.display = 'block';
        }
    }

    async handleSubmit(e) {
        const submitButton = this.form.querySelector('[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        try {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';
            
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action, {
                method: this.form.method,
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            // Check if response is JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (data.success) {
                    this.showFormSuccess(data.message || 'Successfully saved!');
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                } else {
                    this.handleErrors(data.errors);
                }
            } else {
                // Handle regular redirect
                if (response.redirected) {
                    window.location.href = response.url;
                } else if (response.ok) {
                    // If no redirect but successful, reload the page
                    window.location.reload();
                } else {
                    this.showFormError('An error occurred while saving. Please try again.');
                }
            }
        } catch (error) {
            this.showFormError('An error occurred while saving. Please try again.');
            console.error('Form submission error:', error);
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    }

    handleErrors(errors) {
        if (typeof errors === 'string') {
            this.showFormError(errors);
            return;
        }
        
        Object.entries(errors).forEach(([fieldName, fieldErrors]) => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.updateFieldUI(field, false, Array.isArray(fieldErrors) ? fieldErrors[0] : fieldErrors);
            }
        });
        
        this.showFormError('Please correct the errors below.');
    }

    showFormSuccess(message) {
        this.showFormMessage('success', message);
    }

    showFormError(message) {
        this.showFormMessage('danger', message);
    }

    showFormMessage(type, message) {
        let alertDiv = this.form.querySelector('.alert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.className = 'alert mt-3';
            this.form.insertBefore(alertDiv, this.form.firstChild);
        }
        
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        alertDiv.style.display = 'block';
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                alertDiv.style.display = 'none';
            }, 5000);
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }
}

// Export for use in other modules
export default FormValidator; 