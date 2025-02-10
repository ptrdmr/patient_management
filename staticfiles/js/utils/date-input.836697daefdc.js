document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(input => {
        // Set default value to today for new entry forms
        if (!input.value && !input.hasAttribute('data-no-default')) {
            input.valueAsDate = new Date();
        }

        // Add keyboard shortcut for today's date (press 't')
        input.addEventListener('keydown', (e) => {
            if (e.key.toLowerCase() === 't' && !input.readOnly && !input.disabled) {
                e.preventDefault();
                input.valueAsDate = new Date();
            }
        });

        // Ensure future dates aren't selected for past-only fields
        if (!input.id.startsWith('dc_') && !input.id.startsWith('due_') && !input.id.startsWith('target_')) {
            input.addEventListener('change', (e) => {
                const selectedDate = new Date(e.target.value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);

                if (selectedDate > today) {
                    alert('Future dates are not allowed for this field.');
                    e.target.valueAsDate = today;
                }
            });
        }
    });
}); 