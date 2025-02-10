class LoadingManager {
    constructor() {
        this.initialize();
        this.loadingCount = 0;
    }

    initialize() {
        // Add loading overlay template to body
        const overlayTemplate = `
            <div class="loading-overlay" style="display: none;">
                <div class="spinner spinner--lg"></div>
                <span class="loading-text">Loading...</span>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', overlayTemplate);
        
        // Store references
        this.globalOverlay = document.querySelector('.loading-overlay');
    }

    // Show loading state on a specific element
    showLoading(element, options = {}) {
        const {
            overlay = false,
            text = 'Loading...',
            spinnerSize = 'sm',
            type = 'primary'
        } = options;

        element.classList.add('loading');

        if (overlay) {
            const loadingOverlay = document.createElement('div');
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = `
                <div class="spinner spinner--${spinnerSize} spinner--${type}"></div>
                <span class="loading-text">${text}</span>
            `;
            element.appendChild(loadingOverlay);
        }

        return () => this.hideLoading(element);
    }

    // Hide loading state from a specific element
    hideLoading(element) {
        element.classList.remove('loading');
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Show global loading overlay
    showGlobalLoading(text = 'Loading...') {
        this.loadingCount++;
        if (this.loadingCount === 1) {
            const textElement = this.globalOverlay.querySelector('.loading-text');
            if (textElement) {
                textElement.textContent = text;
            }
            this.globalOverlay.style.display = 'flex';
            document.body.classList.add('loading');
        }
    }

    // Hide global loading overlay
    hideGlobalLoading() {
        this.loadingCount = Math.max(0, this.loadingCount - 1);
        if (this.loadingCount === 0) {
            this.globalOverlay.style.display = 'none';
            document.body.classList.remove('loading');
        }
    }

    // Create a loading button
    createLoadingButton(button, text = 'Loading...') {
        const originalText = button.innerHTML;
        button.classList.add('loading');
        button.setAttribute('disabled', 'disabled');
        
        return () => {
            button.classList.remove('loading');
            button.removeAttribute('disabled');
            button.innerHTML = originalText;
        };
    }

    // Create skeleton loading
    createSkeleton(type = 'text', count = 1) {
        const container = document.createElement('div');
        container.className = 'skeleton-container';

        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = `skeleton skeleton-${type}`;
            container.appendChild(skeleton);
        }

        return container;
    }

    // Create progress bar
    createProgressBar(container, initialProgress = 0) {
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.innerHTML = '<div class="progress-bar__fill"></div>';
        container.appendChild(progressBar);

        const fill = progressBar.querySelector('.progress-bar__fill');
        fill.style.width = `${initialProgress}%`;

        return {
            setProgress: (progress) => {
                fill.style.width = `${progress}%`;
            },
            remove: () => {
                progressBar.remove();
            }
        };
    }

    // Add loading dots to element
    addLoadingDots(element) {
        element.classList.add('loading-dots');
        return () => element.classList.remove('loading-dots');
    }
}

// Initialize loading manager
window.loadingManager = new LoadingManager();

// Example usage:
/*
// Button loading
const button = document.querySelector('.submit-button');
const stopLoading = loadingManager.createLoadingButton(button);
// Later: stopLoading();

// Container loading with overlay
const container = document.querySelector('.data-container');
const stopContainerLoading = loadingManager.showLoading(container, {
    overlay: true,
    text: 'Loading data...',
    spinnerSize: 'lg'
});
// Later: stopContainerLoading();

// Global loading
loadingManager.showGlobalLoading('Processing...');
// Later: loadingManager.hideGlobalLoading();

// Skeleton loading
const skeletons = loadingManager.createSkeleton('text', 3);
container.appendChild(skeletons);
// Later: skeletons.remove();

// Progress bar
const { setProgress, remove } = loadingManager.createProgressBar(container);
setProgress(50);
// Later: remove();
*/ 