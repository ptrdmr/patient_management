document.addEventListener('DOMContentLoaded', () => {
    const diagnosisForm = document.querySelector('form');
    if (diagnosisForm) {
        setupAutoComplete(diagnosisForm);
    }
});

function setupAutoComplete(form) {
    const icdInput = form.querySelector('input[name="icd_code"]');
    if (!icdInput) return;

    const resultsDiv = icdInput.parentElement.querySelector('.autocomplete-results');
    if (!resultsDiv) return;

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
                        form.querySelector('input[name="diagnosis"]').value = description.trim();
                        resultsDiv.style.display = 'none';
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

// Make function globally available
window.setupAutoComplete = setupAutoComplete; 