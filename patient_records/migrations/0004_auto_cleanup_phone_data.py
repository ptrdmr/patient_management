from django.db import migrations

def cleanup_phone_data(apps, schema_editor):
    Provider = apps.get_model('patient_records', 'Provider')
    
    for provider in Provider.objects.all():
        # Clean up phone number
        if provider.phone:
            # Remove any non-digit characters
            cleaned = ''.join(filter(str.isdigit, provider.phone))
            if len(cleaned) == 10:
                provider.phone = f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
            else:
                provider.phone = '000-000-0000'  # Default if invalid
        else:
            provider.phone = '000-000-0000'  # Default if None
            
        # Clean up fax number if present
        if provider.fax:
            cleaned = ''.join(filter(str.isdigit, provider.fax))
            if len(cleaned) == 10:
                provider.fax = f"{cleaned[:3]}-{cleaned[3:6]}-{cleaned[6:]}"
            else:
                provider.fax = None  # Remove invalid fax numbers
                
        # Clean up zip code
        if provider.zip:  # Using the old field name
            cleaned = ''.join(filter(str.isdigit, provider.zip))
            if len(cleaned) == 5:
                provider.zip = cleaned
            elif len(cleaned) == 9:
                provider.zip = f"{cleaned[:5]}-{cleaned[5:]}"
            else:
                provider.zip = '00000'  # Default if invalid
        else:
            provider.zip = '00000'  # Default if None
            
        provider.save()

class Migration(migrations.Migration):
    dependencies = [
        ('patient_records', '0003_auto_cleanup_state_data'),
    ]

    operations = [
        migrations.RunPython(cleanup_phone_data),
    ] 