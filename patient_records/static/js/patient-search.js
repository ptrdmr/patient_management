document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('patientSearchForm');
    const clearButton = document.getElementById('clearFilters');
    const searchPanel = document.querySelector('.search-panel');
    
    // Initialize ICD autocomplete
    const icdInput = searchForm.querySelector('input[name="icd_code"]');
    const diagnosisInput = searchForm.querySelector('input[name="diagnosis_text"]');
    const resultsDiv = searchForm.querySelector('.autocomplete-results');
    
    if (icdInput && diagnosisInput && resultsDiv) {
        icdInput.addEventListener('input', async (e) => {
            const query = e.target.value.trim();
            if (query.length < 1) {
                resultsDiv.style.display = 'none';
                return;
            }

            try {
                const response = await fetch(`/api/icd-lookup/?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.results?.length > 0) {
                    resultsDiv.innerHTML = data.results
                        .map(result => `
                            <div class="autocomplete-item">
                                ${result.code} - ${result.description}
                            </div>
                        `)
                        .join('');
                    resultsDiv.style.display = 'block';

                    // Add click handlers
                    resultsDiv.querySelectorAll('.autocomplete-item').forEach(item => {
                        item.addEventListener('click', () => {
                            const [code, description] = item.textContent.split(' - ');
                            icdInput.value = code.trim();
                            diagnosisInput.value = description.trim();
                            resultsDiv.style.display = 'none';
                            
                            // Clear ICD code field after a short delay
                            setTimeout(() => {
                                icdInput.value = '';
                            }, 100);
                        });
                    });
                }
            } catch (error) {
                console.error('Error fetching ICD codes:', error);
                resultsDiv.style.display = 'none';
            }
        });

        // Close results when clicking outside
        document.addEventListener('click', (e) => {
            if (!icdInput.parentElement.contains(e.target)) {
                resultsDiv.style.display = 'none';
            }
        });
    }

    // Toggle search panel
    const searchHeader = document.querySelector('.search-header');
    if (searchHeader) {
        searchHeader.addEventListener('click', () => {
            const advancedSearch = document.getElementById('advancedSearch');
            const toggleIcon = searchHeader.querySelector('.toggle-icon');
            
            if (advancedSearch.classList.contains('show')) {
                advancedSearch.classList.remove('show');
                toggleIcon.textContent = '▶';
            } else {
                advancedSearch.classList.add('show');
                toggleIcon.textContent = '▼';
            }
        });
    }

    // Handle form submission
    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(searchForm);
            formData.delete('icd_code'); // Remove ICD code from search parameters
            await updateResults(formData);
        });
    }

    // Clear filters
    if (clearButton) {
        clearButton.addEventListener('click', () => {
            searchForm.reset();
            updateResults(new FormData());
        });
    }

    // Update URL with search params
    function updateURL(params) {
        const url = new URL(window.location);
        for (const [key, value] of params.entries()) {
            if (value && key !== 'icd_code') {
                url.searchParams.set(key, value);
            } else {
                url.searchParams.delete(key);
            }
        }
        window.history.pushState({}, '', url);
    }

    // Update results via AJAX
    async function updateResults(formData) {
        try {
            const params = new URLSearchParams(formData);
            updateURL(params);

            const response = await fetch(`${window.location.pathname}?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            if (data.html) {
                document.querySelector('.patient-list').innerHTML = data.html;
                
                // Update pagination if it exists
                const paginationContainer = document.querySelector('.pagination');
                if (paginationContainer && data.pagination) {
                    paginationContainer.innerHTML = data.pagination;
                }

                // Update results info
                const resultsInfo = document.querySelector('.results-info');
                if (resultsInfo && data.results_info) {
                    resultsInfo.innerHTML = data.results_info;
                }
            }
        } catch (error) {
            console.error('Error updating results:', error);
        }
    }

    // Handle pagination clicks
    document.addEventListener('click', async (e) => {
        const pageLink = e.target.closest('.page-link');
        if (pageLink && !pageLink.parentElement.classList.contains('active')) {
            e.preventDefault();
            const url = new URL(pageLink.href);
            const formData = new FormData(searchForm);
            formData.delete('icd_code'); // Remove ICD code from pagination requests
            formData.set('page', url.searchParams.get('page'));
            await updateResults(formData);
        }
    });

    // Restore form state from URL params
    const urlParams = new URLSearchParams(window.location.search);
    for (const [key, value] of urlParams.entries()) {
        if (key !== 'icd_code') { // Don't restore ICD code
            const input = searchForm.querySelector(`[name="${key}"]`);
            if (input) input.value = value;
        }
    }
}); 