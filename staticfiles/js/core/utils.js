// Utility functions for the patient records system

// CSRF token handling
const getCSRFToken = () => {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
};

// API request helper
const apiRequest = async (url, options = {}) => {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        credentials: 'same-origin'
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        notifications.error('An error occurred while processing your request');
        throw error;
    }
};

// Form data handling
const serializeForm = (form) => {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    return data;
};

// Date formatting
const formatDate = (date) => {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

const formatDateTime = (date) => {
    return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Loading state management
const setLoading = (element, isLoading) => {
    if (isLoading) {
        element.classList.add('loading');
        element.setAttribute('disabled', 'disabled');
    } else {
        element.classList.remove('loading');
        element.removeAttribute('disabled');
    }
};

// Debounce function for search inputs etc.
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Modal handling
const showModal = (modalId, content = '') => {
    const modal = document.getElementById(modalId);
    if (modal) {
        if (content) {
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.innerHTML = content;
            }
        }
        modal.classList.add('show');
        document.body.classList.add('modal-open');
    }
};

const hideModal = (modalId) => {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    }
};

// Error handling
const handleError = (error, customMessage = 'An error occurred') => {
    console.error(error);
    notifications.error(customMessage);
};

// Export utilities
window.utils = {
    getCSRFToken,
    apiRequest,
    serializeForm,
    formatDate,
    formatDateTime,
    setLoading,
    debounce,
    showModal,
    hideModal,
    handleError
}; 