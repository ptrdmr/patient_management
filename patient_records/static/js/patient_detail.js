// Move patientId to global scope
let patientId;

document.addEventListener('DOMContentLoaded', function() {
    const tabContainer = document.querySelector('.tab-container');
    if (!tabContainer) {
        console.error('Tab container not found');
        return;
    }

    patientId = tabContainer.dataset.patientId;
    if (!patientId) {
        console.error('Patient ID not found in tab container data');
        return;
    }

    const tabs = tabContainer.querySelectorAll('.tab');
    const contentArea = tabContainer.querySelector('.tab-content');
    if (!contentArea) {
        console.error('Content area not found');
        return;
    }

    // Initialize with the active tab
    const activeTab = tabContainer.querySelector('.tab.active');
    if (activeTab) {
        console.log('Loading initial tab:', activeTab.dataset.tab);
        loadTabContent(activeTab.dataset.tab);
    } else {
        console.warn('No active tab found');
    }

    // Add click handlers to tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active states
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Load content for the selected tab
            loadTabContent(tab.dataset.tab);
        });
    });

    async function loadTabContent(tabName, page = 1) {
        if (!contentArea) {
            console.error('Content area not available');
            return;
        }

        try {
            const params = new URLSearchParams(window.location.search);
            console.log('Loading tab:', tabName);
            
            // Handle pagination for all tab types
            switch(tabName) {
                case 'cmp_labs':
                case 'cbc_labs':
                case 'medications':
                case 'clinical':
                case 'overview':
                case 'history':
                    params.set('page', page);
                    break;
                default:
                    console.warn('Unknown tab type:', tabName);
                    break;
            }

            const url = `/patient/${patientId}/tab/${tabName}/?${params.toString()}`;
            console.log('Fetching:', url);

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                contentArea.innerHTML = data.html;
                console.log('Content updated');
                initializeCollapsibles();
                initializePagination();
                console.log('Components initialized');
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Error loading tab content:', error);
            contentArea.innerHTML = '<p class="error-message">Error loading content. Please try again.</p>';
        }
    }

    function initializeCollapsibles() {
        const cards = document.querySelectorAll('.collapsible');
        if (!cards.length) return;

        cards.forEach(card => {
            const header = card.querySelector('.card-header');
            const content = card.querySelector('.card-content, .collapsible-content');
            const icon = header?.querySelector('.collapse-icon');
            
            if (header && content) {
                header.addEventListener('click', () => {
                    content.classList.toggle('active');
                    if (icon) {
                        icon.style.transform = content.classList.contains('active') ? 'rotate(180deg)' : 'rotate(0deg)';
                    }
                });
            }
        });
    }

    function initializePagination() {
        const paginationLinks = document.querySelectorAll('.page-link');
        paginationLinks.forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                const prefix = link.dataset.prefix; // Get the pagination prefix (cmp or cbc)
                const activeTab = tabContainer.querySelector('.tab.active');
                
                if (activeTab) {
                    const params = new URLSearchParams(window.location.search);
                    if (prefix) {
                        // Update only the specific lab type's page
                        params.set(`${prefix}_page`, page);
                    } else {
                        params.set('page', page);
                    }
                    
                    await loadTabContent(activeTab.dataset.tab);
                    // Update URL without reload
                    const newUrl = `${window.location.pathname}?${params.toString()}`;
                    window.history.pushState({}, '', newUrl);
                    
                    // Scroll to the specific lab section if it exists
                    if (prefix) {
                        const labSection = document.querySelector(`.lab-section[data-type="${prefix}"]`);
                        if (labSection) {
                            labSection.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                }
            });
        });
    }
});

// These functions can now access patientId
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