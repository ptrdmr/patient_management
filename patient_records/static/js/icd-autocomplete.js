document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (!form) {
        console.error('No form found');
        return;
    }
    
    form.addEventListener('input', async function(e) {
        if (!e.target.matches('.icd-code-input')) return;
        
        const input = e.target;
        const wrapper = input.closest('.icd-code-wrapper');
        const resultsDiv = wrapper.querySelector('.autocomplete-results');
        
        console.log('Input event on ICD field:', input.value);
        
        const query = input.value.trim();
        if (query.length < 1) {
            resultsDiv.style.display = 'none';
            return;
        }
        
        try {
            const response = await fetch(`/api/icd-lookup/?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('API response:', data);
            
            if (data.error) {
                console.error('API error:', data.error);
                return;
            }
            
            resultsDiv.innerHTML = data.results.map(result => `
                <div class="autocomplete-item" data-code="${result.code}" data-description="${result.description}">
                    ${result.value}
                </div>
            `).join('');
            
            resultsDiv.style.display = data.results.length ? 'block' : 'none';
            
            // Add click handlers for results
            resultsDiv.querySelectorAll('.autocomplete-item').forEach(item => {
                item.addEventListener('click', function() {
                    input.value = this.dataset.code;
                    const diagnosisField = document.querySelector('[name="diagnosis"]');
                    if (diagnosisField) {
                        diagnosisField.value = this.dataset.description;
                    }
                    resultsDiv.style.display = 'none';
                });
            });
            
        } catch (error) {
            console.error('Error fetching ICD codes:', error);
            resultsDiv.style.display = 'none';
        }
    });
}); 