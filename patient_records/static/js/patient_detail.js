// Main initialization when document loads
document.addEventListener('DOMContentLoaded', function() {
    initializeMainTabs();
    loadInitialTab();
});

// Initialize main tab navigation
function initializeMainTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

// Switch between main tabs
function switchTab(tabName) {
    // Update tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });

    // Load tab content if needed
    loadTabContent(tabName);
}

// Load tab content via AJAX
function loadTabContent(tabName) {
    const container = document.getElementById(`${tabName}-container`);
    if (!container || container.children.length > 1) return; // Skip if already loaded

    container.innerHTML = '<div class="loading-spinner"></div>';

    fetch(`/patient/${patientId}/tab/${tabName}/`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = data.html;
            initializeTabPagination(tabName);
        })
        .catch(error => {
            console.error('Error loading tab data:', error);
            container.innerHTML = '<p class="error">Error loading data. Please try again.</p>';
        });
}

// Initialize pagination and collapsible elements for a tab
function initializeTabPagination(tabName) {
    const container = document.querySelector(`.${tabName}-data`);
    if (!container) return;
    
    // Initialize lab tabs if this is the labs container
    if (tabName === 'labs') {
        initializeLabTabs();
    }

    // Add click handlers for collapsible elements
    const collapsibles = container.querySelectorAll('.data-card.collapsible');
    collapsibles.forEach(element => {
        const header = element.querySelector('.card-header');
        if (header) {
            header.addEventListener('click', function() {
                toggleCollapse(this);
            });
        }
    });

    // Add pagination click handler
    container.addEventListener('click', (e) => {
        if (e.target.classList.contains('page-link') && !e.target.classList.contains('active')) {
            e.preventDefault();
            const page = e.target.dataset.page;
            if (page) {
                loadTabPage(tabName, page);
            }
        }
    });
}

// Initialize lab-specific tabs
function initializeLabTabs() {
    console.log("Initializing lab tabs");
    const container = document.querySelector('.labs-data');
    if (!container) {
        console.log("No labs container found");
        return;
    }

    const tabButtons = container.querySelectorAll('.lab-tab');
    const tabContents = container.querySelectorAll('.lab-content');

    console.log(`Found ${tabButtons.length} tab buttons and ${tabContents.length} content sections`);

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = `${button.dataset.tab}-labs`;
            const content = document.getElementById(tabId);
            if (content) {
                content.classList.add('active');
            }
        });
    });
}

// Load a specific page of tab content
function loadTabPage(tabName, page) {
    const container = document.getElementById(`${tabName}-container`);
    if (!container) return;

    container.innerHTML = '<div class="loading-spinner"></div>';

    fetch(`/patient/${patientId}/tab/${tabName}/?page=${page}`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = data.html;
            initializeTabPagination(tabName);
        })
        .catch(error => {
            console.error('Error loading tab data:', error);
            container.innerHTML = '<p class="error">Error loading data. Please try again.</p>';
        });
}

// Toggle collapsible elements
function toggleCollapse(header) {
    const content = header.nextElementSibling;
    const icon = header.querySelector('.collapse-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        if (icon) icon.style.transform = 'rotate(180deg)';
    } else {
        content.style.display = 'none';
        if (icon) icon.style.transform = 'rotate(0deg)';
    }
}

// Load initial tab based on URL hash or default to first tab
function loadInitialTab() {
    const hash = window.location.hash.slice(1) || 'clinical';
    switchTab(hash);
}