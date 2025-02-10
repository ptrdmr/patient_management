document.addEventListener('DOMContentLoaded', function() {
    console.log('Phone input script loaded');
    const phoneInputs = document.querySelectorAll('.phone-input');
    console.log('Found phone inputs:', phoneInputs);

    phoneInputs.forEach(input => {
        console.log('Setting up phone input:', input);
        let lastValue = '';

        input.addEventListener('input', function(e) {
            console.log('Input event fired:', e.target.value);
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';

            if (value.length <= 10) {
                if (value.length > 6) {
                    formattedValue = `(${value.slice(0,3)}) ${value.slice(3,6)}-${value.slice(6)}`;
                } else if (value.length > 3) {
                    formattedValue = `(${value.slice(0,3)}) ${value.slice(3)}`;
                } else if (value.length > 0) {
                    formattedValue = `(${value}`;
                }

                if (formattedValue !== lastValue) {
                    e.target.value = formattedValue;
                    lastValue = formattedValue;
                }
            } else {
                e.target.value = lastValue;
            }
        });
    });
}); 