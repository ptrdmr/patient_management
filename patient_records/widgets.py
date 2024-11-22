from django.forms.widgets import TextInput

class ICDCodeWidget(TextInput):
    template_name = 'patient_records/widgets/icd_code_widget.html'
    
    class Media:
        css = {
            'all': ('css/autocomplete.css',)
        }
        js = ('js/icd-autocomplete.js',)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        attrs['autocomplete'] = 'off'
        attrs['data-diagnosis-field'] = attrs.get('data-diagnosis-field', '')
        attrs['class'] = f"icd-code-input form-control {attrs.get('class', '')}"
        context['widget']['attrs'] = attrs
        return context 

class PhoneNumberWidget(TextInput):
    template_name = 'widgets/phone_number.html'
    
    def __init__(self, attrs=None, country_selector=False):
        default_attrs = {
            'class': 'phone-input form-control',
            'pattern': r'^\(\d{3}\)\s\d{3}-\d{4}$',
            'placeholder': '(555) 555-5555',
            'data-mask': '(000) 000-0000'
        }
        if attrs:
            if 'class' in attrs:
                attrs['class'] = f"phone-input {attrs['class']}"
            default_attrs.update(attrs)
        super().__init__(default_attrs)
        self.country_selector = country_selector