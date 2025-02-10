class NotificationSystem {
    constructor(options = {}) {
        this.container = document.getElementById('notification-container');
        this.defaultDuration = options.duration || 5000; // Default 5 seconds
        this.initialize();
    }

    initialize() {
        // Set up event delegation for close buttons
        this.container.addEventListener('click', (e) => {
            if (e.target.closest('.notification__close')) {
                const notification = e.target.closest('.notification');
                this.dismissNotification(notification);
            }
        });
    }

    show(message, type = 'info', duration = this.defaultDuration) {
        const notification = this.createNotification(message, type);
        this.container.appendChild(notification);
        
        // Trigger reflow for animation
        notification.offsetHeight;
        
        // Set up auto-dismiss
        if (duration !== null) {
            setTimeout(() => {
                if (notification.parentNode) {
                    this.dismissNotification(notification);
                }
            }, duration);
        }

        return notification;
    }

    createNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification--${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'polite');
        
        notification.innerHTML = `
            <div class="notification__icon">
                ${this.getIconForType(type)}
            </div>
            <div class="notification__content">
                <p class="notification__message">${message}</p>
            </div>
            <button class="notification__close" aria-label="Close notification">
                <i class="fas fa-times"></i>
            </button>
        `;

        return notification;
    }

    getIconForType(type) {
        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };
        return icons[type] || icons.info;
    }

    dismissNotification(notification) {
        notification.classList.add('notification--removing');
        notification.addEventListener('animationend', () => {
            notification.remove();
        });
    }

    // Convenience methods for different notification types
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Initialize the notification system
const notifications = new NotificationSystem();

// Export for use in other modules
window.notifications = notifications;

// Example usage:
// notifications.success('Operation completed successfully');
// notifications.error('An error occurred');
// notifications.warning('Please review your input');
// notifications.info('New updates available'); 