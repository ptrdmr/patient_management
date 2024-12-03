// Global variables
let patientId;

document.addEventListener('DOMContentLoaded', function() {
    const tabContainer = document.querySelector('.tab-container');
    if (tabContainer) {
        patientId = tabContainer.dataset.patientId;
        initializeTabs();
    }
});

function initializeTabs() {
    const tabContainer = document.querySelector('.tab-container');
    const tabs = tabContainer.querySelectorAll('.tab');
    const contentArea = tabContainer.querySelector('.tab-content');

    // Load initial active tab
    const activeTab = tabContainer.querySelector('.tab.active');
    if (activeTab) {
        loadTabContent(activeTab.dataset.tab);
    }

    // Add click handlers to tabs
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            loadTabContent(tab.dataset.tab);
        });
    });
}

async function loadTabContent(tabName) {
    const contentArea = document.querySelector('.tab-content');
    if (!contentArea) return;

    try {
        const response = await fetch(`/patient/${patientId}/tab/${tabName}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        
        if (data.success) {
            contentArea.innerHTML = data.html;
            initializeCollapsibles();
            initializePagination();
        }
    } catch (error) {
        console.error('Error loading tab content:', error);
        contentArea.innerHTML = '<p class="error-message">Error loading content. Please try again.</p>';
    }
}

function addRecord(type) {
    const url = `/patient/${patientId}/${type}/add/`;
    showFormModal(url, `Add ${type}`);
}

function editRecord(type, id) {
    const url = `/patient/${patientId}/${type}/${id}/edit/`;
    showFormModal(url, `Edit ${type}`);
}

function showFormModal(url, title) {
    const modal = new bootstrap.Modal(document.getElementById('recordModal'), {
        backdrop: true,
        keyboard: true
    });
    const modalTitle = document.querySelector('#recordModal .modal-title');
    const modalBody = document.querySelector('#recordModal .modal-body');

    modalTitle.textContent = title;
    
    fetch(url)
        .then(response => response.text())
        .then(html => {
            modalBody.innerHTML = html;
            
            const form = modalBody.querySelector('form');
            if (form) {
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    try {
                        const response = await fetch(url, {
                            method: 'POST',
                            body: new FormData(form),
                            headers: {
                                'X-Requested-With': 'XMLHttpRequest'
                            }
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            modal.hide();
                            const activeTab = document.querySelector('.tab.active');
                            if (activeTab) {
                                loadTabContent(activeTab.dataset.tab);
                            } else {
                                window.location.reload();
                            }
                        } else {
                            const errorDiv = modalBody.querySelector('.error-message') || document.createElement('div');
                            errorDiv.className = 'alert alert-danger error-message';
                            errorDiv.textContent = data.error || 'An error occurred. Please try again.';
                            form.prepend(errorDiv);
                        }
                    } catch (error) {
                        console.error('Error submitting form:', error);
                    }
                });
            }
            
            modal.show();
        })
        .catch(error => {
            console.error('Error loading form:', error);
        });
}
function initializeCollapsibles() {
    const cards = document.querySelectorAll('.collapsible');
    cards.forEach(card => {
        const header = card.querySelector('.card-header');
        const content = card.querySelector('.card-content');
        if (header && content) {
            header.addEventListener('click', () => {
                content.classList.toggle('active');
            });
        }
    });
}

function initializePagination() {
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            const activeTab = document.querySelector('.tab.active');
            if (activeTab) {
                loadTabContent(activeTab.dataset.tab, page);
            }
        });
    });
}
