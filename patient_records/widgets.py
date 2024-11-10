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