document.addEventListener('DOMContentLoaded', function() {
    // Get the dropdown menu items
    const recordDetailsDropdown = document.querySelectorAll('#recordDetailsDropdown + .dropdown-menu .dropdown-item');
    const patientOverview = document.getElementById('patientOverview');
    const detailContent = document.getElementById('detailContent');
    let currentSection = null;

    // Add click event listeners to dropdown items
    recordDetailsDropdown.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.dataset.section;
            
            // Don't reload if clicking the same section
            if (currentSection === section) return;
            
            // Update UI state
            currentSection = section;
            patientOverview.style.display = 'none';
            detailContent.style.display = 'block';
            
            // Show loading state
            detailContent.innerHTML = '<div class="loading-spinner">Loading...</div>';
            
            // Load the content
            fetch(`/patient/${getPatientId()}/section/${section}/`)
                .then(response => response.text())
                .then(html => {
                    detailContent.innerHTML = html;
                    initializeSection(section);
                })
                .catch(error => {
                    console.error('Error loading section:', error);
                    detailContent.innerHTML = '<div class="alert alert-danger">Error loading content. Please try again.</div>';
                });
        });
    });

    // Add event listener to show overview when clicking patient name or home
    document.querySelector('.header-info h1').addEventListener('click', function() {
        showOverview();
    });

    function showOverview() {
        currentSection = null;
        patientOverview.style.display = 'block';
        detailContent.style.display = 'none';
    }

    // Helper function to get patient ID from the URL or data attribute
    function getPatientId() {
        const urlParts = window.location.pathname.split('/');
        return urlParts[urlParts.indexOf('patient') + 1];
    }

    // Initialize section-specific functionality
    function initializeSection(section) {
        switch(section) {
            case 'visits':
                initializeVisitsSection();
                break;
            case 'medications':
                initializeMedicationsSection();
                break;
            case 'vitals':
                initializeVitalsSection();
                break;
            // Add other section initializations as needed
        }
    }

    // Section-specific initializations
    function initializeVisitsSection() {
        // Initialize visit-specific features
        const visitRows = document.querySelectorAll('.visit-row');
        visitRows.forEach(row => {
            row.addEventListener('click', function() {
                const visitId = this.dataset.visitId;
                window.location.href = `/patient/${getPatientId()}/visit/${visitId}/`;
            });
        });
    }

    function initializeMedicationsSection() {
        // Initialize medication-specific features
        const medRows = document.querySelectorAll('.medication-row');
        medRows.forEach(row => {
            row.addEventListener('click', function() {
                const medId = this.dataset.medId;
                showMedicationDetails(medId);
            });
        });
    }

    function initializeVitalsSection() {
        // Initialize vitals-specific features
        const vitalsChart = document.getElementById('vitalsChart');
        if (vitalsChart) {
            initializeVitalsChart(vitalsChart);
        }
    }
});

// Add CSS styles for the loading spinner only
const style = document.createElement('style');
style.textContent = `
    .loading-spinner {
        text-align: center;
        padding: 2rem;
        color: #666;
    }
`;
document.head.appendChild(style);
