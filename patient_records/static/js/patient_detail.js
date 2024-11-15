function addItem(type) {
    if (!window.formModal) {
        console.error('FormModal not initialized!');
        return;
    }
    
    window.formModal.show(`/patient/${patientId}/${type}/add/`, {
        title: `Add ${type}`,
        onSuccess: (data) => {
            if (typeof loadTabContent === 'function') {
                loadTabContent(type);
            } else {
                window.location.reload();
            }
        }
    });
}

function editItem(type, id) {
    if (!window.formModal) {
        console.error('FormModal not initialized!');
        return;
    }
    
    window.formModal.show(`/patient/${patientId}/${type}/${id}/edit/`, {
        title: `Edit ${type}`,
        onSuccess: (data) => {
            if (typeof loadTabContent === 'function') {
                loadTabContent(type);
            } else {
                window.location.reload();
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const tabContainer = document.querySelector('.tab-container');
    if (!tabContainer) {
        console.error('Tab container not found');
        return;
    }

    const patientId = tabContainer.dataset.patientId;
    if (!patientId) {
        console.error('Patient ID not found');
        return;
    }

    const tabs = tabContainer.querySelectorAll('.tab');
    const contentArea = tabContainer.querySelector('.tab-content');
    if (!contentArea) return;

    function initializeCollapsibles() {
        const cards = document.querySelectorAll('.collapsible');
        if (!cards.length) return;

        cards.forEach(card => {
            const header = card.querySelector('.card-header');
            const content = card.querySelector('.card-content');
            const icon = header?.querySelector('.collapse-icon');
            
            if (header && content) {
                header.addEventListener('click', () => {
                    const isHidden = content.style.display === 'none';
                    content.style.display = isHidden ? 'block' : 'none';
                    if (icon) {
                        icon.textContent = isHidden ? '▲' : '▼';
                    }
                });
            }
        });
    }

    async function loadTabContent(tabName, page = 1) {
        const contentArea = tabContainer.querySelector('.tab-content');
        if (!contentArea) return;

        try {
            const response = await fetch(`/patient/${patientId}/tab/${tabName}/?page=${page}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data.success) {
                contentArea.innerHTML = data.html;
                initializeCollapsibles();
                initializePagination();
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error loading tab content:', error);
            contentArea.innerHTML = '<p class="error-message">Error loading content. Please try again.</p>';
        }
    }

    function initializePagination() {
        const paginationLinks = document.querySelectorAll('.page-link');
        paginationLinks.forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                const activeTab = tabContainer.querySelector('.tab.active');
                if (activeTab) {
                    await loadTabContent(activeTab.dataset.tab, page);
                    // Scroll to top of content area
                    tabContainer.querySelector('.tab-content')?.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', async (e) => {
            e.preventDefault();
            
            // Update active state
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            await loadTabContent(tab.dataset.tab);
        });
    });

    // Load initial tab content
    const activeTab = tabContainer.querySelector('.tab.active');
    if (activeTab) {
        loadTabContent(activeTab.dataset.tab);
    }

    // Initialize pagination for initial load
    initializePagination();
});